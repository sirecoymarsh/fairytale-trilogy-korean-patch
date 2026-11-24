#!/usr/bin/env python3
"""Inspect only the PE/font/code-page pipeline; never decode game scripts."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import pefile
from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_INVALID


INTERESTING_IMPORTS = {
    "CreateFontA",
    "DrawTextA",
    "GetACP",
    "GetCPInfo",
    "GetGlyphOutlineA",
    "GetTextExtentPoint32A",
    "GetTextMetricsA",
    "IsDBCSLeadByteEx",
    "LCMapStringA",
    "LCMapStringW",
    "MultiByteToWideChar",
    "TextOutA",
    "WideCharToMultiByte",
}

KNOWN_FONT_BYTES = {
    "MS_GOTHIC_CP932": "ＭＳ ゴシック".encode("cp932"),
    "MS_MINCHO_CP932": "ＭＳ 明朝".encode("cp932"),
    "MS_GOTHIC_ASCII": b"MS Gothic",
    "MS_MINCHO_ASCII": b"MS Mincho",
    "MALGUN_GOTHIC_ASCII": b"Malgun Gothic",
    "BATANG_ASCII": b"Batang",
}


def section_for_rva(pe: pefile.PE, rva: int):
    for section in pe.sections:
        start = section.VirtualAddress
        end = start + max(section.Misc_VirtualSize, section.SizeOfRawData)
        if start <= rva < end:
            return section
    return None


def raw_offset_to_rva(pe: pefile.PE, raw_offset: int) -> int:
    for section in pe.sections:
        start = section.PointerToRawData
        end = start + section.SizeOfRawData
        if start <= raw_offset < end:
            return section.VirtualAddress + raw_offset - start
    return raw_offset


def find_all(data: bytes, needle: bytes):
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return
        yield pos
        pos += 1


def operand_references_absolute(insn, absolute_va: int) -> bool:
    if insn.id == 0:  # Capstone skip-data pseudo-instruction.
        return False
    for op in insn.operands:
        if op.type == X86_OP_IMM and op.imm == absolute_va:
            return True
        if op.type == X86_OP_MEM:
            mem = op.mem
            if (
                mem.base == X86_REG_INVALID
                and mem.index == X86_REG_INVALID
                and mem.disp == absolute_va
            ):
                return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    data = args.exe.read_bytes()
    pe = pefile.PE(data=data, fast_load=False)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    md.skipdata = True

    sections = []
    executable_sections = []
    for section in pe.sections:
        name = section.Name.rstrip(b"\0").decode("ascii", errors="replace")
        item = {
            "name": name,
            "rva": section.VirtualAddress,
            "raw_offset": section.PointerToRawData,
            "raw_size": section.SizeOfRawData,
            "virtual_size": section.Misc_VirtualSize,
            "characteristics": section.Characteristics,
        }
        sections.append(item)
        if section.Characteristics & 0x20000000:
            executable_sections.append(section)

    imports = {}
    for desc in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        dll = desc.dll.decode("ascii", errors="replace")
        for imp in desc.imports:
            if not imp.name:
                continue
            name = imp.name.decode("ascii", errors="replace")
            if name in INTERESTING_IMPORTS:
                imports[name] = {
                    "dll": dll,
                    "iat_va": imp.address,
                    "iat_rva": imp.address - image_base,
                }

    all_insns = []
    for section in executable_sections:
        code = section.get_data()
        start_va = image_base + section.VirtualAddress
        all_insns.extend(md.disasm(code, start_va))

    call_sites = {}
    for name, imp in imports.items():
        iat_va = imp["iat_va"]
        matches = []
        thunks = []
        for index, insn in enumerate(all_insns):
            if insn.mnemonic == "jmp" and operand_references_absolute(insn, iat_va):
                thunks.append(insn.address)
            if insn.mnemonic != "call":
                continue
            if not operand_references_absolute(insn, iat_va):
                continue
            lo = max(0, index - 28)
            hi = min(len(all_insns), index + 4)
            context = [
                {
                    "address": x.address,
                    "bytes": x.bytes.hex(" "),
                    "mnemonic": x.mnemonic,
                    "op_str": x.op_str,
                }
                for x in all_insns[lo:hi]
            ]
            matches.append({"call_va": insn.address, "context": context})
        thunk_matches = []
        for index, insn in enumerate(all_insns):
            if insn.mnemonic != "call":
                continue
            if not any(operand_references_absolute(insn, thunk) for thunk in thunks):
                continue
            lo = max(0, index - 28)
            hi = min(len(all_insns), index + 4)
            context = [
                {
                    "address": x.address,
                    "bytes": x.bytes.hex(" "),
                    "mnemonic": x.mnemonic,
                    "op_str": x.op_str,
                }
                for x in all_insns[lo:hi]
            ]
            thunk_matches.append({"call_va": insn.address, "context": context})
        pointer_hits = []
        for raw_offset in find_all(data, struct.pack("<I", iat_va)):
            rva = raw_offset_to_rva(pe, raw_offset)
            section = section_for_rva(pe, rva)
            pointer_hits.append(
                {
                    "raw_offset": raw_offset,
                    "rva": rva,
                    "va": image_base + rva,
                    "section": (
                        section.Name.rstrip(b"\0").decode("ascii", errors="replace")
                        if section
                        else None
                    ),
                }
            )
        call_sites[name] = {
            "direct_indirect_calls": matches,
            "import_thunks": thunks,
            "thunk_calls": thunk_matches,
            "iat_pointer_occurrences": pointer_hits,
        }

    font_strings = []
    for label, needle in KNOWN_FONT_BYTES.items():
        for raw_offset in find_all(data, needle):
            rva = raw_offset_to_rva(pe, raw_offset)
            va = image_base + rva
            refs = []
            for insn in all_insns:
                if operand_references_absolute(insn, va):
                    refs.append(
                        {
                            "address": insn.address,
                            "bytes": insn.bytes.hex(" "),
                            "mnemonic": insn.mnemonic,
                            "op_str": insn.op_str,
                        }
                    )
            pointer_hits = []
            for pointer_raw_offset in find_all(data, struct.pack("<I", va)):
                pointer_rva = raw_offset_to_rva(pe, pointer_raw_offset)
                pointer_section = section_for_rva(pe, pointer_rva)
                pointer_hits.append(
                    {
                        "raw_offset": pointer_raw_offset,
                        "rva": pointer_rva,
                        "va": image_base + pointer_rva,
                        "section": (
                            pointer_section.Name.rstrip(b"\0").decode(
                                "ascii", errors="replace"
                            )
                            if pointer_section
                            else None
                        ),
                    }
                )
            section = section_for_rva(pe, rva)
            font_strings.append(
                {
                    "label": label,
                    "raw_offset": raw_offset,
                    "rva": rva,
                    "va": va,
                    "length": len(needle),
                    "nul_terminated": data[
                        raw_offset + len(needle) : raw_offset + len(needle) + 1
                    ]
                    == b"\0",
                    "section": (
                        section.Name.rstrip(b"\0").decode("ascii", errors="replace")
                        if section
                        else None
                    ),
                    "references": refs,
                    "pointer_occurrences": pointer_hits,
                }
            )

    result = {
        "path": str(args.exe),
        "machine": pe.FILE_HEADER.Machine,
        "is_pe32_plus": pe.PE_TYPE == pefile.OPTIONAL_HEADER_MAGIC_PE_PLUS,
        "image_base": image_base,
        "entrypoint_rva": pe.OPTIONAL_HEADER.AddressOfEntryPoint,
        "sections": sections,
        "interesting_imports": imports,
        "call_sites": call_sites,
        "known_font_strings": font_strings,
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

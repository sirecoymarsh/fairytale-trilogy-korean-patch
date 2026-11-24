from pathlib import Path
import base64
import io
import json
import os
import re
import shutil
import struct
import subprocess

import numpy as np
from PIL import Image

from assets import ROOT, live, read, parse_archive, read_entry, entry_map, sha
from install import encode, current_hash

GAME = "Encore"
BANK = "grpe"
NAME = "2231.wcg"
KEY = BANK + "/" + NAME
BEFORE_BANK = "0af7c940f5d401ac0ea6d7c3e42427589cbe87cfe5f31581278c35eef8b69f24"
BEFORE_IMAGE = "7a56e3bf6efb3605ea559f46d9c55bb0db33bde457c8d60a6b2eda3fcaac5382"
ART = ROOT / "art/Encore/grpe/2231"
AUDIT = ROOT / "audit"
TARGET = live(GAME) / "grpe.xfl"
BACKUP = ROOT / "rollback/Encore/grpe.before-nurse-sign.xfl"
STAGE = ROOT / "staging/Encore/grpe.xfl"
SCRATCH = ROOT / "tmp/nurse-sign"


def write_bytes(path, data):
    pending = path.with_name(path.name + ".hospital-tmp")
    pending.write_bytes(data)
    os.replace(pending, path)


def write_json(path, data):
    write_bytes(path, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf8"))


def check_idle():
    procs = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$ErrorActionPreference='Stop'; $root='Y:\\GAME\\Fairytale Encore\\'; "
         "Get-Process | Where-Object { $_.Path -and $_.Path.StartsWith($root,[StringComparison]::OrdinalIgnoreCase) } | Select-Object -ExpandProperty Id"],
        check=True, capture_output=True)
    if procs.stdout.strip():
        raise RuntimeError("The game is running. Installation is waiting for the live archive to become available.")


def build_archive(src, pending, replacement):
    original = parse_archive(src).entries
    assert len(original) == 190 and sum(e.name == NAME for e in original) == 1
    expected = {}
    with src.open("rb") as old, pending.open("wb") as out:
        out.write(old.read(12))
        offset = 0
        for e in original:
            size = len(replacement) if e.name == NAME else e.size
            out.write(e.raw_name + struct.pack("<II", offset, size))
            offset += size
        for e in original:
            old.seek(e.absolute_offset)
            old_bytes = old.read(e.size)
            assert len(old_bytes) == e.size
            if e.name == NAME:
                assert sha(old_bytes) == BEFORE_IMAGE
                new_bytes = replacement
            else:
                new_bytes = old_bytes
            expected[e.name] = sha(new_bytes)
            out.write(new_bytes)
    rebuilt = parse_archive(pending).entries
    assert [e.raw_name for e in rebuilt] == [e.raw_name for e in original]
    with pending.open("rb") as inp:
        for e in rebuilt:
            inp.seek(e.absolute_offset)
            assert sha(inp.read(e.size)) == expected[e.name]
    return len(rebuilt) - 1


def check_images(persisted):
    def rgba(path):
        with Image.open(path) as im:
            return np.array(im.convert("RGBA"))
    def mask(fname):
        with Image.open(ART / fname) as im:
            return np.array(im.convert("L")) > 0
    old = rgba(AUDIT / "full/Encore/grpe/2231.png")
    clean = rgba(ART / "clean.png")
    rendered = rgba(ART / "final.png")
    saved = rgba(persisted)
    layer = rgba(ART / "target-layer.png")
    erasure, owned = mask("source-mask.png"), mask("ownership.png")
    ink = layer[:, :, 3] > 0
    assert np.array_equal(saved, rendered)
    assert np.array_equal(clean[~erasure], old[~erasure])
    assert np.array_equal(rendered[~ink], clean[~ink])
    assert np.array_equal(owned, erasure | ink)
    assert np.array_equal(saved[~owned], old[~owned])
    assert np.array_equal(old[:, :, 3], saved[:, :, 3])
    assert tuple(saved.shape) == (720, 1280, 4)
    for zone in (erasure, ink):
        ys, xs = np.where(zone)
        assert xs.min() >= 474 and xs.max() < 652 and ys.min() >= 0 and ys.max() < 140
    return dict(geometry=[1280,720], pixels_erased=int(np.any(old!=clean,axis=2).sum()),
                pixels_drawn=int(np.any(rendered!=clean,axis=2).sum()),
                source_mask_pixels=int(erasure.sum()), target_mask_pixels=int(ink.sum()),
                owned_pixels=int(owned.sum()), protected_pixels=int((~owned).sum()),
                outside_owned_changes=0, alpha_changed_pixels=0, roundtrip_mismatched_pixels=0)


def update_review(proof, persisted):
    directory = AUDIT / "cg_japanese_review"
    findings_path = directory / "findings.json"
    findings = read(findings_path)
    row = next(x for x in findings["findings"] if x["game"]==GAME and x["asset"]==KEY)
    row.update(status="resolved", source_ja="ナースステーション", target_ko="간호사실",
               title="병원 복도의 ‘간호사실’ 간판",
               detail="「돈 키호테, 달리다」의 병원 카운터 위에 ‘간호사실’이 보인다. 벽의 기울기와 초록색 수채 자국을 살려 옮겼다.",
               original_sha256=BEFORE_IMAGE, sha256=proof["installed_entry_sha256"],
               sources_identical_to_disc={GAME:False})
    findings["confirmed"] = sum(r["status"]=="confirmed" for r in findings["findings"])
    findings["resolved"] = sum(r["status"]=="resolved" for r in findings["findings"])
    findings["archive_fingerprints"][GAME][BANK].update(sha256=proof["installed_bank_sha256"],matches_last_install=True)
    findings["verification"] = "현재 설치본 이미지와 GSC 호출을 대조했고, 간호사실 간판은 교체한 설치 아카이브에서 다시 추출해 확인했다."
    assert findings["confirmed"]==4 and findings["resolved"]==1
    with Image.open(persisted) as img:
        with io.BytesIO() as buf:
            img.convert("RGB").crop(tuple(row["crop"])).save(buf, format="PNG")
            image = "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode("ascii")
    page = directory / "index.html"
    html = page.read_text("utf8")
    records_tag = re.compile(r'(<script id="records" type="application/json">)(.*?)(</script>)',re.S)
    match = records_tag.search(html)
    records = json.loads(match.group(2))
    display = next(x for x in records if x["game"]==GAME and x["asset"]==KEY)
    if "before_image" not in display:
        assert display["status"]=="confirmed"
        display["before_image"] = display["image"]
    display.update(row, image=image)
    json_text = json.dumps(records,ensure_ascii=False,separators=(",",":"))
    html = html[:match.start(2)] + json_text + html[match.end(2):]
    html = html.replace("앙코르에서 1장, 심포니에서 4장에 일본어가 남아 있다.",
                        "앙코르의 병원 간판을 ‘간호사실’로 한국어화했다. 심포니에는 일본어가 확인된 이미지 4장이 남아 있다.")
    html = html.replace("게임 파일을 변경하지 않은 정적 조사다.", "앙코르 간판은 설치 아카이브에서 다시 추출해 확인했다.")
    if 'id="resolved"' not in html:
        section = '<h2>한국어화한 이미지</h2><div class="tablewrap"><table><thead><tr><th>작품</th><th>이미지</th><th>비교 보기</th></tr></thead><tbody id="resolved"></tbody></table></div>\n'
        html = html.replace('<h2>일본어가 확인된 이미지</h2>', section+'<h2>일본어가 확인된 이미지</h2>',1)
    if 'id="original-image"' not in html:
        html = html.replace('<button id="fit"', '<button id="original-image" type="button" hidden>일본어 원본 보기</button><button id="fit"',1)
        html = html.replace('current=i;const r=rows[i];', """current=i;const r=rows[i];const t=document.getElementById('original-image');t.hidden=!r.before_image;t.textContent='일본어 원본 보기';t.setAttribute('aria-pressed','false');""",1)
        toggle = """document.getElementById('original-image').addEventListener('click',ev=>{const t=ev.currentTarget,r=rows[current],show=t.getAttribute('aria-pressed')!=='true';if(!r.before_image)return;t.setAttribute('aria-pressed',String(show));t.textContent=show?'한국어 설치본 보기':'일본어 원본 보기';photo.alt=show?'병원 간판 일본어 원본':'병원 간판 한국어 설치본';photo.onload=null;photo.src=show?r.before_image:r.image;});\n"""
        html = html.replace("document.getElementById('fit').addEventListener(",toggle+"document.getElementById('fit').addEventListener(",1)
    assert 'id="resolved"' in html and 'id="original-image"' in html and len(records)==len(findings["findings"])
    write_json(findings_path, findings)
    write_bytes(page, html.encode("utf8"))


def main():
    original_key = read("audit/index.json")[GAME][KEY]
    assert original_key["sha"]==BEFORE_IMAGE and original_key["size"]==[1280,720]
    assert not (live(GAME)/KEY).exists()
    current = current_hash(TARGET)
    if current != BEFORE_BANK:
        assert BACKUP.is_file() and current_hash(BACKUP)==BEFORE_BANK
    check_idle()
    encoded = read("audit/encoded.json")
    new = encode({GAME:{KEY:{}}},encoded)[GAME][KEY]
    wcg = ROOT/new["file"]
    assert sha(wcg.read_bytes())==new["sha256"] and new["sha256"]!=BEFORE_IMAGE
    pending = STAGE.with_name("grpe.nurse-pending.xfl")
    original = TARGET if current==BEFORE_BANK else BACKUP
    siblings = build_archive(original, pending, wcg.read_bytes())
    after = current_hash(pending)
    assert after!=BEFORE_BANK and current in (BEFORE_BANK,after)
    if current_hash(STAGE) not in (BEFORE_BANK,after):
        raise ValueError("Unexpected staging archive")
    if not BACKUP.exists():
        try:
            os.link(TARGET,BACKUP)
        except OSError:
            shutil.copyfile(TARGET,BACKUP)
    assert current_hash(BACKUP)==BEFORE_BANK
    if current!=after:
        incoming = TARGET.with_name("grpe.nurse-incoming")
        shutil.copyfile(pending,incoming)
        assert current_hash(incoming)==after
        check_idle()
        assert current_hash(TARGET)==BEFORE_BANK
        os.replace(incoming,TARGET)
    os.replace(pending,STAGE)
    entry_map.cache_clear()
    assert current_hash(TARGET)==after and sha(read_entry(TARGET,NAME))==new["sha256"]
    entry = entry_map(TARGET)[NAME]
    decoded = ART/("installed-"+new["sha256"][:12]+".png")
    if not decoded.exists():
        jobs = SCRATCH/"installed-decode.tsv"
        jobs.write_text("\t".join(map(str,[TARGET,entry.absolute_offset,entry.size,decoded,0]))+"\n","utf-8-sig")
        subprocess.run([str(ROOT/"tools/RasterBatch.exe"),str(jobs)],check=True)
    pixels = check_images(decoded)
    method = "원본 벽면 질감을 인접한 같은 벽에서 복원하고, 생성한 한글 수채 글씨를 원근에 맞춰 조판했다."
    proof = dict(game=GAME, entry=KEY, source_ja="ナースステーション", target_ko="간호사실",
                 translator_model="Codex internal", method=method, script="1311.gsc", command_offset=14, opcode=15,
                 original_entry_sha256=BEFORE_IMAGE, installed_entry_sha256=new["sha256"], previous_bank_sha256=BEFORE_BANK,
                 installed_bank_sha256=after, verified_unchanged_other_entries=siblings, archive_count=siblings+1,
                 installed_png=str(decoded), backup=str(BACKUP), **pixels)
    encoded[GAME][KEY] = new
    reports = read("audit/install.json")
    bank = reports[GAME]["banks"][BANK]
    if bank["installed_sha256"]==BEFORE_BANK:
        reports[GAME]["changed_image_states"]["new"]+=1
        bank["changed_entries"]+=1
    else:
        assert bank["installed_sha256"]==after
    bank["installed_sha256"] = after
    subset = [(k,v["sha256"]) for k,v in encoded[GAME].items() if k.startswith(BANK+"/")]
    bank["asset_set_sha256"] = sha(repr(sorted(subset)).encode())
    propsfile = AUDIT/"props.json"
    props = read(propsfile) if propsfile.exists() else {}
    props.setdefault(GAME,{})[KEY] = {k:proof[k] for k in ("source_ja","target_ko","translator_model","method","geometry","outside_owned_changes","pixels_erased","pixels_drawn")}
    write_json(propsfile,props)
    write_json(AUDIT/"encoded.json",encoded)
    write_json(AUDIT/"install.json",reports)
    write_json(AUDIT/"hospital_sign.json",proof)
    progress = read("progress.json")
    progress["status"][GAME] = reports[GAME]
    progress["hospital_sign"] = {k:proof[k] for k in ("game","entry","target_ko","installed_entry_sha256","verified_unchanged_other_entries","installed_png")}
    write_json(ROOT/"progress.json",progress)
    update_review(proof,decoded)
    print(json.dumps({k:proof[k] for k in ("target_ko","installed_entry_sha256","installed_bank_sha256","verified_unchanged_other_entries","outside_owned_changes","roundtrip_mismatched_pixels","installed_png")},ensure_ascii=False))


if __name__=="__main__":
    main()

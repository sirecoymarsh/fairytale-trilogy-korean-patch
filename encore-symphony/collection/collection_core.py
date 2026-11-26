"""Portable access to the project's existing codeX codecs.

op/page/archive routines reuse qol/menu_scripts.py and qol/build_options.py.
"""
from pathlib import Path
from functools import lru_cache
import json, struct, sys
HERE = Path(__file__).resolve().parent
ADAPTER = HERE / 'adapter'
if not ADAPTER.is_dir(): ADAPTER = HERE.parents[1] / 'requiem' / 'adapter'
sys.path.insert(0, str(ADAPTER))
from xfl_tool import parse_archive
from gsc_codec import parse_gsc
from build_scenario_catalog import parse_commands
FMT = {r['opcode']: (r['format'], r['name']) for r in
       json.loads((ADAPTER / 'command_formats.json').read_text('utf-8'))['commands']}

@lru_cache(maxsize=64)
def entry_map(path): return {e.name: e for e in parse_archive(path).entries}

def read_entry(path, name):
    e = entry_map(path)[name]
    with Path(path).open('rb') as f:
        f.seek(e.absolute_offset); data = f.read(e.size)
    if len(data) != e.size: raise ValueError('Truncated archive entry: ' + name)
    return data

def op(k, *args):
    fmt = FMT.get(k, ('hh' if k >> 12 == 15 else 'hhh', ''))[0]
    return struct.pack('<H' + fmt, k, *args)

def const(var, val): return op(0x1800, 1, var, val) + op(0xf100, 0, 1)

def pages(p, stride):
    length = p.header[5]
    table = struct.unpack('<' + 'I' * (length // 4), p.trailing[:length])
    word = lambda i: struct.unpack_from('<h', p.trailing, length + 2 * i)[0]
    for t in table[2:]:
        count = word(t)
        if count % stride: raise ValueError('Invalid gallery row')
        for row in range(0, count, stride):
            i = t + 1 + row; values = [word(i + k) for k in range(stride)]
            if values[0] >= 0: yield i, values

def archive(src, dest, changes):
    obj = parse_archive(src); dest.parent.mkdir(parents=True, exist_ok=True)
    if not changes.keys() <= {e.name for e in obj.entries}: raise ValueError('Unknown archive entry')
    stage = dest.with_suffix('.new')
    with src.open('rb') as inp, stage.open('wb') as out:
        out.write(inp.read(12)); offset = 0
        for e in obj.entries:
            size = len(changes[e.name]) if e.name in changes else e.size
            out.write(e.raw_name + struct.pack('<II', offset, size)); offset += size
        for e in obj.entries:
            if e.name in changes: out.write(changes[e.name]); continue
            inp.seek(e.absolute_offset); remaining = e.size
            while remaining:
                chunk = inp.read(min(4194304, remaining))
                if not chunk: raise ValueError('Truncated archive')
                out.write(chunk); remaining -= len(chunk)
    stage.replace(dest); entry_map.cache_clear()
    for name, data in changes.items():
        if read_entry(dest, name) != data: raise ValueError('Archive verification failed')

import sys, os, hashlib, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'P:\AI\Codex\projects\fairytale-requiem-ko\adapter')
from pathlib import Path
import xfl_tool as X

KO = Path(r'Y:\GAME\Fairytale Collection\Games\Requiem')
JP = Path(r'Y:\GAME\H Games\FairyTale Requiem\フェアリーテイル・レクイエム')
OUT = Path(sys.argv[1])
SKIP = {'scr.xfl', 'bgm.xfl', 'voice.xfl', 'wav.xfl'}

def read(arc, e):
    with open(arc.source, 'rb') as h:
        h.seek(e.absolute_offset); return h.read(e.size)

report = []
for kp in sorted(KO.glob('*.xfl')):
    if kp.name in SKIP: continue
    jp = JP / kp.name
    ka = X.parse_archive(kp)
    ja = {e.name: e for e in X.parse_archive(jp).entries} if jp.exists() else {}
    jarc = X.parse_archive(jp) if jp.exists() else None
    n = 0
    for e in ka.entries:
        data = read(ka, e)
        o = ja.get(e.name)
        if o is not None and o.size == e.size and read(jarc, o) == data:
            continue
        dst = OUT / kp.stem / e.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        n += 1
        report.append({'archive': kp.name, 'name': e.name, 'new': o is None, 'size': e.size})
    print(kp.name, 'changed', n)
# loose override folders
for d in ('grpe', 'grpo'):
    for f in (KO / d).glob('*'):
        dst = OUT / ('loose_' + d) / f.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(f.read_bytes())
        report.append({'archive': 'loose/' + d, 'name': f.name, 'new': True, 'size': f.stat().st_size})
json.dump(report, open(OUT / 'changed_entries.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total', len(report), sum(r['size'] for r in report) / 1048576, 'MB')

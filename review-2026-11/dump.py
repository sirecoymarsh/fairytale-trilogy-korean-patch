import sys, json, struct
from pathlib import Path
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from gsc_codec import parse_gsc
sys.stdout.reconfigure(encoding='utf-8')

def read_xfl(path):
    data = Path(path).read_bytes()
    assert data[:4] == b"LB\x01\x00"
    tsize, n = struct.unpack_from("<II", data, 4)
    start = 12 + tsize
    out = {}
    for i in range(n):
        row = data[12 + i*0x28: 12 + (i+1)*0x28]
        name = row[:0x20].split(b"\0",1)[0].decode("cp932")
        off, size = struct.unpack_from("<II", row, 0x20)
        out[name] = data[start+off:start+off+size]
    return out

GAMES = {
 "Requiem": (r"Y:\GAME\H Games\FairyTale Requiem\フェアリーテイル・レクイエム\scr.xfl", r"Y:\GAME\Fairytale Collection\Games\Requiem\scr.xfl"),
 "Encore": (r"Y:\AI\Codex\projects\fairytale-symphony-encore-ko\original\Encore\Files\scr.xfl", r"Y:\GAME\Fairytale Collection\Games\Encore\scr.xfl"),
 "Symphony": (r"Y:\AI\Codex\projects\fairytale-symphony-encore-ko\original\Symphony\Files\scr.xfl", r"Y:\GAME\Fairytale Collection\Games\Symphony\scr.xfl"),
}
outdir = Path(r"Y:\AI\claude-work\fairytale-review")
for g,(o,k) in GAMES.items():
    ox, kx = read_xfl(o), read_xfl(k)
    stats = dict(entries_o=len(ox), entries_k=len(kx), gsc=0, same_count=0, cnt_mismatch=[], cmd_diff=[], rows=0, changed=0, decode_err=0)
    rows = []
    for name in ox:
        if not name.lower().endswith(".gsc"): continue
        if name not in kx: stats["cnt_mismatch"].append(name+":missing"); continue
        po, pk = parse_gsc(ox[name]), parse_gsc(kx[name])
        stats["gsc"] += 1
        if po.command != pk.command: stats["cmd_diff"].append(name)
        if len(po.strings) != len(pk.strings):
            stats["cnt_mismatch"].append(f"{name}:{len(po.strings)}->{len(pk.strings)}"); continue
        for i,(a,b) in enumerate(zip(po.strings, pk.strings)):
            try: ja = a.decode("cp932")
            except: ja = a.decode("cp932", "replace")
            try: ko = b.decode("cp949")
            except:
                ko = b.decode("cp949","replace"); stats["decode_err"] += 1
            rows.append(dict(scene=name, slot=i, ja=ja, ko=ko, changed=(a!=b)))
            stats["rows"] += 1; stats["changed"] += (a!=b)
    with open(outdir/f"{g}.jsonl","w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    stats["cmd_diff_n"] = len(stats["cmd_diff"]); stats["cmd_diff"] = stats["cmd_diff"][:10]
    print(g, json.dumps(stats, ensure_ascii=False))

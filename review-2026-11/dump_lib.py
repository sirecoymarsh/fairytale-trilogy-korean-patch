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

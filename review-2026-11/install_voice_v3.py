"""말투 고침 v3 (848칸) 를 4곳 scr.xfl 에 넣는다. 각 곳의 지금 파일 위에 따로 만든다
(통합판은 0000.gsc 명령이 단독판과 달라서 — 11-23 07:53/08:01 바뀜, 그대로 보존).
python install_voice_v3.py build   → build/v3/... 만들고 검사만
python install_voice_v3.py install → 백업 → 임시 파일 → os.replace → 해시·칸 대조"""
import json, sys, os, shutil, hashlib, struct
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from gsc_codec import parse_gsc, rebuild_gsc
sys.stdout.reconfigure(encoding='utf-8')
W = Path(r"Y:\AI\claude-work\fairytale-review")
T = {('Requiem', 'standalone'): r"P:\AI\Codex\projects\fairytale-requiem-ko\runtime\trial_ko\scr.xfl",
     ('Requiem', 'collection'): r"Y:\GAME\Fairytale Collection\Games\Requiem\scr.xfl",
     ('Symphony', 'standalone'): r"Y:\GAME\Fairytale Symphony\scr.xfl",
     ('Symphony', 'collection'): r"Y:\GAME\Fairytale Collection\Games\Symphony\scr.xfl"}
E = json.load(open(W / 'voice_edits_v3.json', encoding='utf-8'))
by = defaultdict(lambda: defaultdict(list))
for e in E: by[e['game']][e['scene'] + '.gsc'].append(e)

def sha(b): return hashlib.sha256(b).hexdigest().upper()
def read(data):
    assert data[:4] == b"LB\x01\x00"
    ts, n = struct.unpack_from("<II", data, 4); start = 12 + ts; ents = []
    for i in range(n):
        row = data[12 + i * 0x28:12 + (i + 1) * 0x28]; off, size = struct.unpack_from("<II", row, 0x20)
        ents.append([row[:0x20], data[start + off:start + off + size]])
    return ents
def pack(ents):
    out = bytearray(b"LB\x01\x00" + struct.pack("<II", len(ents) * 0x28, len(ents))); off = 0
    for raw, p in ents: out += raw + struct.pack("<II", off, len(p)); off += len(p)
    for raw, p in ents: out += p
    return bytes(out)

def build(g, which, path):
    data = Path(path).read_bytes(); ents = read(data)
    assert pack(ents) == data, 'round-trip'
    idx = {raw.split(b"\0", 1)[0].decode("cp932"): i for i, (raw, p) in enumerate(ents)}
    n = 0
    for scene, es in by[g].items():
        i = idx[scene]; parts = parse_gsc(ents[i][1]); strs = list(parts.strings)
        for e in es:
            cur = strs[e['slot']].decode('cp949')
            assert cur == e['old'], (g, which, scene, e['slot'], 'old mismatch', cur, e['old'])
            strs[e['slot']] = e['new'].encode('cp949'); n += 1
        newb = rebuild_gsc(parts, tuple(strs)); p2 = parse_gsc(newb)
        assert p2.command == parts.command and len(p2.strings) == len(parts.strings)
        diff = sorted(k for k, (a, b) in enumerate(zip(parts.strings, p2.strings)) if a != b)
        assert diff == sorted(e['slot'] for e in es), (scene, diff)
        ents[i][1] = newb
    out = pack(ents)
    e2 = read(out); e0 = read(data)
    assert len(e2) == len(e0) and all(e2[k][0] == e0[k][0] for k in range(len(e0)))
    changed = sorted(e2[k][0].split(b"\0", 1)[0].decode('cp932') for k in range(len(e0)) if e2[k][1] != e0[k][1])
    assert set(changed) == set(by[g]), (set(changed) ^ set(by[g]))
    od = W / 'build' / 'v3' / g / which; od.mkdir(parents=True, exist_ok=True); (od / 'scr.xfl').write_bytes(out)
    return dict(path=path, before=sha(data), built=str(od / 'scr.xfl'), after=sha(out), cells=n, gsc=len(changed))

def verify(g, path, backup):
    """넣은 파일: v3 칸은 new, 나머지 모든 칸·명령은 백업과 같아야 한다."""
    A, B = read(Path(backup).read_bytes()), read(Path(path).read_bytes())
    want = {(e['scene'] + '.gsc', e['slot']): e['new'] for e in E if e['game'] == g}
    ok = other = 0
    for (ra, pa), (rb, pb) in zip(A, B):
        name = ra.split(b"\0", 1)[0].decode('cp932'); assert ra == rb
        if pa == pb: continue
        qa, qb = parse_gsc(pa), parse_gsc(pb); assert qa.command == qb.command
        for k, (x, y) in enumerate(zip(qa.strings, qb.strings)):
            if x == y: continue
            if (name, k) in want and y.decode('cp949') == want[(name, k)]: ok += 1
            else: other += 1
    return ok, other, len(want)

if __name__ == '__main__':
    mode = sys.argv[1]
    rep = {f'{g}/{w}': build(g, w, p) for (g, w), p in T.items()}
    for k, r in rep.items(): print(k, r['before'][:12], '->', r['after'][:12], r['cells'], 'cells', r['gsc'], 'gsc')
    if mode == 'install':
        log = {}
        for (g, w), p in T.items():
            r = rep[f'{g}/{w}']; p = Path(p)
            assert sha(p.read_bytes()) == r['before'], (p, 'changed since build')
            bd = W / 'backup_v3pre' / g / w; bd.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bd / 'scr.xfl'); assert sha((bd / 'scr.xfl').read_bytes()) == r['before']
            tmp = p.with_name('scr.xfl.v3-new'); shutil.copyfile(r['built'], tmp); assert sha(tmp.read_bytes()) == r['after']
            os.replace(tmp, p); assert sha(p.read_bytes()) == r['after']
            ok, other, want = verify(g, p, bd / 'scr.xfl')
            print('installed', g, w, r['before'][:12], '->', r['after'][:12], f'| v3 칸 {ok}/{want}, 그 밖 바뀐 칸 {other}')
            assert ok == want and other == 0
            log[str(p)] = dict(before=r['before'], after=r['after'], backup=str(bd / 'scr.xfl'), cells=ok)
        json.dump(log, open(W / 'install_log_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

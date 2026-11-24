"""제미나이 말맛 답 받기: 심은 결함 적중 → 검사기 → 원래 꼴(^n)로 되돌려 배치·글자 검사 → 검토 문서.
쓰는 법: python receive_mallmat.py
나오는 것: mallmat_candidates.json (넣을 후보, 아직 아무 데도 안 넣음), P:\AI\fairytale-review\말맛_제미나이답_검토.md"""
import json, sys, re, glob, os, importlib.util
from collections import Counter, defaultdict
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from scenario_layout import line_widths, required_runtime_lines
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
PK = r"P:\AI\fairytale-mallmat-gemini"
R = json.load(open(W + '/mallmat_receiver.json', encoding='utf-8'))
BACK = {b['id']: b for b in R['back']}
CAN = {c['id']: c for c in R['canary']}
flat = lambda s: s.replace('^n', ' / ')
unflat = lambda s: s.replace(' / ', '^n')
for b in R['back']:
    assert unflat(flat(b['new'])) == b['new'], b['id']

spec = importlib.util.spec_from_file_location('chk', PK + r'\검사.py'); chk = importlib.util.module_from_spec(spec)
sys.argv = ['검사.py', '전부']; spec.loader.exec_module(chk)   # __main__ 블록은 안 돈다
files = sorted(glob.glob(PK + r'\답\답_[0-9][0-9].json'))
print('답 파일', len(files), '/ 9')
err = sum(chk.check(os.path.basename(f)[2:4])[0] for f in files)
print('검사기 오류 합계', err)

ans = []
for f in files:
    ans += json.load(open(f, encoding='utf-8-sig'))
byid = {a['id']: a for a in ans}

print('\n── 심은 결함 6칸 ──')
hit = 0
for i, c in CAN.items():
    a = byid.get(i)
    ok = bool(a) and c['after'].strip() not in a['제안']
    hit += ok
    print(f"  {'잡음' if ok else '놓침'} {i} {c['why']} 「{c['after'].strip()}」" + (f" → {a['제안'][:60]} [{a['종류']}]" if a else ''))
print(f'  적중 {hit}/6 — 놓친 것이 많으면 그 묶음은 안 읽은 것으로 보고 다시 맡긴다')

cands, probs = [], []
for a in ans:
    i = a['id']
    if i in CAN or i not in BACK: continue
    b = BACK[i]; new = unflat(a['제안']); p = []
    if flat(b['new']) != a['지금']: p.append('지금 불일치')
    if re.findall(r'\^[a-zA-Z][0-9]*', new) != re.findall(r'\^[a-zA-Z][0-9]*', b['new']): p.append('제어 기호')
    try: new.encode('cp949')
    except UnicodeEncodeError: p.append('cp949')
    wn, wo = max(line_widths(new)), max(line_widths(b['new']))
    if (wn > 1000 and wn > wo) or required_runtime_lines(new) > max(3, required_runtime_lines(b['new'])): p.append(f'배치 {wn}')
    rec = dict(id=i, game=b['game'], scene=b['scene'], slot=b['slot'], cat=b['cat'], kind=a['종류'], why=a['까닭'], cur=b['new'], new=new, ja=None, probs=p)
    (probs if p else cands).append(rec)
json.dump(dict(cands=cands, probs=probs), open(W + '/mallmat_candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('\n후보', len(cands), '문제', len(probs), Counter(c['kind'] for c in cands), Counter(c['cat'] for c in cands))

# 검토 문서 (종류별)
items = json.load(open(PK + r'\검사_자료.json', encoding='utf-8'))['items']
L = ['# 제미나이 말맛 답 검토 (아직 게임에 안 넣음)', '',
     f'- 답 {len(ans)}건 중 심은 결함 {len([a for a in ans if a["id"] in CAN])}건(적중 {hit}/6), 넣을 후보 {len(cands)}건, 걸린 것 {len(probs)}건.', '']
g = defaultdict(list)
for c in cands: g[c['kind']].append(c)
for k in ('혼잣말투', '권유명령', '말씨기색', '어미어색', '기타'):
    if not g[k]: continue
    L += [f'## {k} ({len(g[k])})', '']
    for c in g[k]:
        L += [f"**{c['id']}** {items[c['id']]['화자']} — {c['why']}", f"- 원문: {items[c['id']]['원문']}",
              f"- 지금: {flat(c['cur'])}", f"- 제안: {flat(c['new'])}", '']
if probs:
    L += ['## 걸린 것', ''] + [f"- {p['id']} {p['probs']}: {flat(p['new'])}" for p in probs]
open(r'P:\AI\fairytale-review\말맛_제미나이답_검토.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('문서 P:\\AI\\fairytale-review\\말맛_제미나이답_검토.md')

"""v2 + 제미나이 말맛 답(거른 것) + Claude 추가 고침 → voice_edits_v3.json, 반영 문서"""
import json, sys, re
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from scenario_layout import line_widths, required_runtime_lines
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
CTRL = re.compile(r'\^[a-zA-Z][0-9]*')
E = json.load(open(W + '/voice_edits_v2.json', encoding='utf-8'))
C = json.load(open(W + '/mallmat_candidates.json', encoding='utf-8'))
iid = lambda e: f"{e['game'][0]}{e['scene']}-{e['slot']}"
idx = {iid(e): e for e in E}
rows = {}
for g in ('Requiem', 'Symphony'):
    for r in map(json.loads, open(f'{W}/{g}.jsonl', encoding='utf-8')):
        rows[f"{g[0]}{r['scene'][:4]}-{r['slot']}"] = r

REJECT = {
    'R1135-56': '앨리스가 망연히 혼자 꺼낸 말(뒤 지문) — 「꿈인가?」가 맞다',
    'R1416-99': '「둬 줘」는 자연스러운 부탁꼴 — 「둬」는 명령으로 기운다',
}
# 제미나이 안을 받되 Claude 가 손본 것 (from, to — 제미나이 제안 글 위에)
ADJUST = {
    'R1102-101': ('글쎄.', '어디 보자.'),          # 「간단해.」 다음이라 의심하는 「글쎄」보다
    'R1134-156': ('어……? 어, 없다고?', '뭐……? 어, 없다고?'),  # 「어」 두 번 겹침
}
# 받는 쪽에서 직접 넣는 것 (v2 글 위에)
MINE = {
    'R1410-45': [('정말 그랬던', '그랬던'), ('연습해……', '연습하자……')],   # 제미나이 안 + 화면 폭(정말은 원문에 없음)
    'R1717-235': [('누구셔?', '누구야?')],          # 심은 결함 칸이라 답에서 빠진 진짜 고침
    'R1211-110': [('『응, 조심할게……』', '『네, 조심할게요……』')],   # 원문 『はい、気をつけます』 인용은 존댓말 그대로
    'R1207-98': [('그렇구나, 그……', '그러니까, 그……')],            # 군말 そうね
    'R1112-272': [('응, 응. 그건', '으, 응. 그건')],                   # え、ええ 말더듬
    'R1134-147': [('응, 응. 그랬어', '으, 응. 그랬어')],
    'R1207-71': [('응, 응.', '으, 응.')],
    'R1217-32': [('응, 응……', '으, 응……')],
    'R1913-36': [('응, 응……', '으, 응……')],
    'R1203-220': [('──응, 응, 그래.', '──으, 응, 그래.')],
}
log = []
for c in C['cands'] + C['probs']:
    i = c['id']
    if i in REJECT or i in MINE:
        continue
    new = c['new']
    if i in ADJUST:
        a, b = ADJUST[i]; assert a in new, (i, a); new = new.replace(a, b)
    log.append((i, 'gemini' + ('+adj' if i in ADJUST else ''), c['kind'], idx[i]['new'], new))
    idx[i]['new'] = new; idx[i]['src2'] = 'mallmat-gemini'
for i, pairs in MINE.items():
    new = idx[i]['new']
    for a, b in pairs:
        assert a in new, (i, a); new = new.replace(a, b)
    log.append((i, 'claude', '', idx[i]['new'], new))
    idx[i]['new'] = new; idx[i]['src2'] = 'mallmat-claude'

bad = 0
for e in E:
    p = []
    if rows[iid(e)]['ko'] != e['old']: p.append('old mismatch')
    if CTRL.findall(e['old']) != CTRL.findall(e['new']): p.append('control')
    try: e['new'].encode('cp949')
    except UnicodeEncodeError: p.append('cp949')
    wn, wo = max(line_widths(e['new'])), max(line_widths(e['old']))
    if (wn > 1000 and wn > wo) or required_runtime_lines(e['new']) > max(3, required_runtime_lines(e['old'])): p.append(f'layout {wn}')
    if e['new'] == e['old']: p.append('no change')
    if p: bad += 1; print('!!', iid(e), p)
json.dump(E, open(W + '/voice_edits_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('v3', len(E), '바뀐 칸', len(log), '문제', bad)

f = lambda s: s.replace('^n', ' / ')
L = ['# 말투 고침 v3 — 제미나이 말맛 점검 반영 (2026-11-23, 아직 게임에 안 넣음)', '',
     f'- 제미나이 답 48건: 심은 결함 6/6 적중, 받음 {sum(1 for x in log if x[1].startswith("gemini"))}(그중 Claude가 손봄 {len(ADJUST)}), 안 받음 {len(REJECT)}.',
     f'- Claude 추가 {len(MINE)}칸: 제미나이 버릇을 848줄 전체에서 다시 찾아 나온 것과, 화면 폭·심은 칸 사정으로 직접 넣은 것.',
     f'- 고칠 칸 수는 v2와 같은 {len(E)}칸이다(말끝만 다시 다듬음). 넣을 칸 `voice_edits_v3.json`.', '',
     '## 안 받은 것', ''] + [f'- **{i}** {why}: 제미나이 안 「{f(next(c["new"] for c in C["cands"] if c["id"] == i))}」' for i, why in REJECT.items()] + \
    ['', '## 바뀐 칸 전부', '']
for i, src, kind, a, b in log:
    L += [f"**{i}** ({src}{' · ' + kind if kind else ''})", f"- 원문: {f(rows[i]['ja'])}", f'- v2: {f(a)}', f'- v3: {f(b)}', '']
open(r'P:\AI\fairytale-review\말투고침_v3_말맛반영_20261123.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('문서 P:\\AI\\fairytale-review\\말투고침_v3_말맛반영_20261123.md')

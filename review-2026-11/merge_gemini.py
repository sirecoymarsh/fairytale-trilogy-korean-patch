"""제미나이 검수(11-23) 반영: 기존 737칸 수정·제외 + 빠진 칸 추가 + 지문 인용 7칸 → voice_edits_v2.json"""
import json, sys, re
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from scenario_layout import line_widths, required_runtime_lines
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
CTRL = re.compile(r'\^[a-zA-Z][0-9]*')
G = json.load(open(r'P:/AI/fairytale-review/제미나이_말투검토_20261123.json', encoding='utf-8'))
E = json.load(open(W + '/voice_edits_final.json', encoding='utf-8'))
rows = {}
for g in ('Requiem', 'Symphony'):
    for r in map(json.loads, open(f'{W}/{g}.jsonl', encoding='utf-8')):
        rows[(g, r['scene'][:4], r['slot'])] = r
key = lambda x: (x['game'], x['scene'], x['slot'])
idx = {key(e): e for e in E}
for e in E: e.setdefault('src', 'claude')

# 1) 제외
for d in G['edits_to_drop']:
    idx.pop(key(d))
# 2) 기존 칸 수정 (선택 다듬기는 받지 않음)
for m in G['edits_to_modify']:
    if m.get('optional'):
        continue
    e = idx[key(m)]
    e['new'] = m['suggested']; e['src'] = 'gemini-fix'
# 3) 빠진 칸 추가 (제미나이 안, 한 칸만 Claude가 바꿈)
MINE = {('Requiem', '1207', 54): '뭘까?'}
for a in G['missed_slots_to_add']:
    k = key(a)
    assert k not in idx
    new = MINE.get(k, a['suggested'])
    idx[k] = dict(cat=a['cat'], game=a['game'], scene=a['scene'], slot=a['slot'], ja=a['ja'], old=a['old'], new=new, jreg='', src='gemini-add', group=a['group'])
# 4) 지문 속 인용 (Claude 추가)
QUOTE = {
    ('Requiem', '1139', 64, 'odette'): [('다 읽어 둘게요, 하고', '다 읽어 둘게, 하고')],
    ('Requiem', '1207', 72, 'rapunzel'): [('그렇군요, 하고', '그렇구나, 하고')],
    ('Requiem', '1602', 52, 'alice_R'): [('『뭐, 저도 그런 시절이 있었지요』라거나', '『뭐, 나도 그런 시절이 있었지』라거나'), ('『이제는 완전히 졸업했지만요』라고', '『이제는 완전히 졸업했지만』이라고')],
    ('Requiem', '1602', 80, 'alice_R'): [('정답이죠? 하고', '정답이지? 하고')],
    ('Requiem', '1701', 63, 'black'): [('즐거우셨을까요」', '즐거우셨을까」')],
    ('Requiem', '1804', 61, 'odette'): [('미안해요, 하고', '미안해, 하고')],
    ('Symphony', '1002', 84, 'alice_S'): [('「그래요」 하고', '「그래」 하고')],
}
for (g, s, n, cat), pairs in QUOTE.items():
    r = rows[(g, s, n)]; new = r['ko']
    for a, b in pairs:
        assert a in new, (s, n, a)
        new = new.replace(a, b)
    assert (g, s, n) not in idx
    idx[(g, s, n)] = dict(cat=cat, game=g, scene=s, slot=n, ja=r['ja'], old=r['ko'], new=new, jreg='', src='claude-quote')

out = sorted(idx.values(), key=lambda e: (e['game'], e['scene'], e['slot']))
bad = 0
for e in out:
    cur = rows[key(e)]['ko']; p = []
    if cur != e['old']: p.append('old mismatch')
    if CTRL.findall(e['old']) != CTRL.findall(e['new']): p.append('control')
    try: e['new'].encode('cp949')
    except UnicodeEncodeError: p.append('cp949')
    wn, wo = max(line_widths(e['new'])), max(line_widths(e['old']))
    if (wn > 1000 and wn > wo) or required_runtime_lines(e['new']) > max(3, required_runtime_lines(e['old'])): p.append(f'layout {wn}')
    if e['new'] == e['old']: p.append('no change')
    if p: bad += 1; print('!!', e['cat'], e['scene'], e['slot'], p)
json.dump(out, open(W + '/voice_edits_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('total', len(out), dict(Counter(e['src'] for e in out)), 'problems', bad)
print(dict(Counter(e['cat'] for e in out)))

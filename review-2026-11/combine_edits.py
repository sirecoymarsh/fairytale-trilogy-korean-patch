"""말씨(fix_register_auto.json)와 2인칭(person_patches.json) 고침을 하나로 묶고 검사한다."""
import json, sys, re
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from scenario_layout import line_widths, required_runtime_lines
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
CTRL = re.compile(r'\^[a-zA-Z][0-9]*')

rows = {}
for g in ('Requiem', 'Symphony'):
    for r in map(json.loads, open(f'{W}/{g}.jsonl', encoding='utf-8')):
        rows[(g, r['scene'][:4], r['slot'])] = r

edits = []
REG = json.load(open(W + '/fix_register_auto.json', encoding='utf-8'))
GAME = {'alice_R': 'Requiem', 'alice_S': 'Symphony', 'rapunzel': 'Requiem', 'odette': 'Requiem'}
for cat, ls in REG.items():
    for r in ls:
        if r['new'] == r['ko']:
            continue
        edits.append(dict(cat=cat, game=GAME[cat], scene=r['scene'], slot=r['slot'], ja=r['ja'], old=r['ko'], new=r['new'], jreg=r['jreg']))

PP = json.load(open(W + '/person_patches.json', encoding='utf-8'))
miss = 0
for key, pairs in PP.items():
    cat, sc, sl = key.split('|')
    r = rows[('Requiem', sc, int(sl))]
    new = r['ko']
    for a, b in pairs:
        if a not in new:
            print('!! miss', key, a); miss += 1
        new = new.replace(a, b)
    edits.append(dict(cat=cat, game='Requiem', scene=sc, slot=int(sl), ja=r['ja'], old=r['ko'], new=new, jreg=''))

keys = [(e['game'], e['scene'], e['slot']) for e in edits]
assert len(keys) == len(set(keys)), 'duplicate edit'
bad = 0
for e in edits:
    cur = rows[(e['game'], e['scene'], e['slot'])]['ko']
    probs = []
    if cur != e['old']: probs.append('old mismatch')
    if CTRL.findall(e['old']) != CTRL.findall(e['new']): probs.append('control codes')
    try: e['new'].encode('cp949')
    except UnicodeEncodeError: probs.append('cp949')
    if max(line_widths(e['new'])) > 1000 or required_runtime_lines(e['new']) > 3: probs.append(f"layout {max(line_widths(e['new']))}/{required_runtime_lines(e['new'])}")
    if e['new'] == e['old']: probs.append('no change')
    if probs:
        bad += 1; print('!!', e['cat'], e['scene'], e['slot'], probs)
json.dump(edits, open(W + '/voice_edits_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('edits', len(edits), dict(Counter(e['cat'] for e in edits)), 'misses', miss, 'problems', bad)

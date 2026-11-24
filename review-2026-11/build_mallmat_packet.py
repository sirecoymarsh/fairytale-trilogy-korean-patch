"""제미나이 「말맛」 검수 의뢰 묶음 만들기 (11-23).
v2 848칸 + 심은 결함 6칸 → P:\AI\fairytale-review\제미나이_말맛의뢰_20261123
심은 결함 열쇠와 받는 쪽 자료는 Y: 작업 폴더에만 둔다."""
import json, sys, re, difflib, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
OUT = r"P:\AI\fairytale-mallmat-gemini"   # 옛 해요체 검토본이 든 fairytale-review 와 떨어진 곳
BATCH = 100

E = json.load(open(W + '/voice_edits_v2.json', encoding='utf-8'))
cur, ja = {}, {}
for g in ('Requiem', 'Symphony'):
    for r in map(json.loads, open(f'{W}/{g}.jsonl', encoding='utf-8')):
        k = (g, r['scene'][:4], r['slot'])
        cur[k] = r['ko']; ja[k] = r['ja']
for e in E:
    k = (e['game'], e['scene'], e['slot'])
    assert cur[k] == e['old'], k
    cur[k] = e['new']
SEQ = {g: json.load(open(f'{W}/msgseq_{g}.json', encoding='utf-8')) for g in ('Requiem', 'Symphony')}

def flat(s): return s.replace('^n', ' / ')

def resolve(g, sc, i):
    """seq[i] 의 화자 표시. app 이면 앞 msg 의 화자를 잇는다."""
    seq = SEQ[g][sc]; j = i
    while j > 0 and seq[j]['kind'] == 'app': j -= 1
    spk = seq[j]['spk']
    if not spk: return '(지문)'
    return cur.get((g, sc, spk), '?').strip() or '(지문)'

def ctx(g, sc, slot):
    seq = SEQ[g][sc]
    idx = [i for i, m in enumerate(seq) if m['slot'] == slot]
    if not idx: return None, [], []
    i = idx[0]
    def ent(j):
        m = seq[j]; lab = resolve(g, sc, j)
        if m['kind'] == 'app': lab += '·이어짐'
        return [lab, flat(cur[(g, sc, m['slot'])])]
    return resolve(g, sc, i) + ('·이어짐' if seq[i]['kind'] == 'app' else ''), \
        [ent(j) for j in range(max(0, i - 2), i)], [ent(j) for j in range(i + 1, min(len(seq), i + 2))]

def spans(old, new):
    """바꾼 자리(새 글 기준, ^n 은 ' / ' 로 편 글) 앞뒤 몇 글자."""
    old, new = flat(old), flat(new)
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    out = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal': continue
        s, t = max(0, b1 - 5), min(len(new), b2 + 2)
        if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], t)
        else: out.append([s, t])
    return [new[s:t].strip(' /') for s, t in out], out

KIND = {'alice_R': '말끝', 'alice_S': '말끝', 'rapunzel': '말끝', 'odette': '말끝·1인칭',
        'gerda': '2인칭', 'black': '2인칭', 'odile': '2인칭', 'tink': '2인칭', 'doctor': '2인칭·말끝', 'typo': '오타'}
items, back = [], []
for e in sorted(E, key=lambda e: (e['game'] != 'Requiem', e['scene'], e['slot'])):
    g, sc, sl = e['game'], e['scene'], e['slot']
    spk, before, after = ctx(g, sc, sl)
    if spk is None:
        print('!! no message', g, sc, sl); spk = '?'
    look, rng = spans(e['old'], e['new'])
    kind = '지문 속 인용' if e['src'] == 'claude-quote' else KIND[e['cat']]
    iid = f"{g[0]}{sc}-{sl}"
    items.append(dict(id=iid, 화자=spk, 바꾼것=kind, 원문=flat(e['ja']), 지금=flat(e['new']), 살필곳=look, 앞=before, 뒤=after))
    back.append(dict(id=iid, game=g, scene=sc, slot=sl, cat=e['cat'], src=e['src'], new=e['new'], old=e['old'], rng=rng))

# ── 심은 결함 6칸 (받은 답이 실제로 읽었는지 보려는 것) ──
def pick(pred, n, used):
    r = []
    for it in items:
        if it['id'] in used or len(r) >= n: continue
        if pred(it): r.append(it)
    return r
used, canary = set(), []
def seed(it, a, b, why):
    assert a in it['지금'], (it['id'], a)
    i0 = it['지금'].find(a); orig = it['지금']
    it['지금'] = it['지금'].replace(a, b, 1); used.add(it['id'])
    for o in items:   # 이웃 줄 문맥에 진짜 글이 보이면 심은 것이 드러난다
        for c in o['앞'] + o['뒤']:
            if c[1] == orig: c[1] = it['지금']
    now = it['지금']
    looks = [l if l in now else l.replace(a, b) for l in it['살필곳']]   # 살필곳에 옛 글이 남으면 답이 샌다
    looks = [l for l in looks if l in now]
    win = now[max(0, i0 - 3):i0 + len(b)].strip(' /')
    if not any(win in l for l in looks):   # 심은 자리도 살필곳에 (다른 줄과 같은 꼴로)
        looks.append(win)
    it['살필곳'] = sorted(looks, key=lambda l: now.find(l))
    canary.append(dict(id=it['id'], before=a, after=b, why=why, 지금=it['지금']))
# ① 권유(ましょう)를 명령으로
for it in pick(lambda x: 'ましょう' in x['원문'] and re.search(r'[가-힣]자[\.\!…]', x['지금']) and x['id'][1:3] in ('12',), 1, used):
    m = re.search(r'([가-힣])자([\.\!…])', it['지금']); seed(it, m.group(0), m.group(1) + '라' + m.group(2), '권유→명령')
# ② 상대에게 묻는 「~어?」를 혼잣말 「~나?」로
SS = lambda c: (ord(c) - 0xAC00) % 28 == 20   # 받침 ㅆ
for it in pick(lambda x: x['바꾼것'] == '말끝' and any(SS(m.group(1)) for m in re.finditer(r'([가-힣])어\?', x['지금'])) and x['id'] > 'R1130', 2, used):
    m = next(m for m in re.finditer(r'([가-힣])어\?', it['지금']) if SS(m.group(1))); seed(it, m.group(0), m.group(1) + '나?', '물음→혼잣말')
# ③ 깨진 말끝
for it in pick(lambda x: x['바꾼것'] == '말끝' and re.search(r'[가-힣]이야\.', x['지금']) and x['id'] > 'R1400', 2, used):
    m = re.search(r'([가-힣])이야\.', it['지금']); seed(it, m.group(0), m.group(1) + '이다야.', '깨진 말끝')
# ④ 인칭 어긋남(나→저)
for it in pick(lambda x: x['화자'] == '앨리스' and '나는 ' in x['지금'] and x['id'] > 'R1600', 1, used):
    seed(it, '나는 ', '저는 ', '1인칭 어긋남')
assert len(canary) == 6, canary
for c in canary:   # 심은 글의 진짜 판이 묶음 어디에도 안 남았는지
    real = next(x for x in back if x['id'] == c['id'])['new']
    assert not any(flat(real) in (cx[1] for cx in o['앞'] + o['뒤']) or (o['id'] == c['id'] and o['지금'] == flat(real)) for o in items), c['id']

RULES = [
    "모든 줄은 이미 반말로 정해졌다. 요·니다를 붙이거나 해요체로 되돌리지 말 것.",
    "1인칭·2인칭(나/당신/너 등)과 원문 높임에 따른 「-시-」는 그대로 둘 것.",
    "고칠 수 있는 것은 「살필곳」의 말끝과 그 앞 두세 글자뿐. 나머지 낱말·줄바꿈( / )·문장부호는 그대로.",
    "원문에 없는 감탄사·부사·뜻을 더하지 말 것(「어머」는 원문에 あら・まあ가 있을 때만).",
    "한국어로 확실히 더 자연스러워지는 줄만 적는다. 취향 차이는 적지 않는다. 고칠 것이 없으면 빈 답 [] 이 정상이다.",
    "「지금」은 묶음 파일의 글을 한 글자도 바꾸지 말고 그대로 옮겨 적을 것(대조에 쓴다).",
    "묶음 파일은 고치지 말고 답 파일만 쓸 것. 다 쓰면 python 검사.py <묶음번호> 로 확인.",
]
if os.path.exists(OUT + r'\묶음'): shutil.rmtree(OUT + r'\묶음')
os.makedirs(OUT + r'\묶음'); os.makedirs(OUT + r'\답', exist_ok=True)
assert not os.listdir(OUT + r'\답'), '답 폴더에 이미 답이 있다 — 지우기 전에 확인'
nb = (len(items) + BATCH - 1) // BATCH
for b in range(nb):
    chunk = items[b * BATCH:(b + 1) * BATCH]
    head = json.dumps(dict(묶음=f'{b+1:02d}', 답_파일=f'답/답_{b+1:02d}.json', 규칙=RULES), ensure_ascii=False, indent=1)[:-2]
    NL = chr(10)
    body = (',' + NL).join(json.dumps(it, ensure_ascii=False) for it in chunk)
    open(f'{OUT}/묶음/묶음_{b+1:02d}.json', 'w', encoding='utf-8').write(head + ',' + NL + ' "줄": [' + NL + body + NL + ']}' + NL)
json.dump(dict(rules=RULES, items={it['id']: it for it in items}), open(f'{OUT}/검사_자료.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(dict(canary=canary, back=back), open(W + '/mallmat_receiver.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('items', len(items), 'batches', nb, Counter(it['바꾼것'] for it in items))
print('speakers', Counter(it['화자'] for it in items).most_common(15))
for c in canary: print('canary', c['id'], c['why'], c['before'], '→', c['after'])

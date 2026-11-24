"""답 파일 검사기.  쓰는 법:  python 검사.py 03      (답/답_03.json 을 묶음 03 과 대조)
                          python 검사.py 전부    (있는 답 파일 모두)
오류가 있으면 끝에 「오류 N」을 찍고 1 로 끝난다. 「주의」는 범위 밖 손질 등 — 까닭이 맞으면 그대로 둬도 된다."""
import json, sys, re, os, difflib
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, '검사_자료.json'), encoding='utf-8'))
ITEMS = D['items']
KINDS = {'혼잣말투', '권유명령', '말씨기색', '어미어색', '기타'}
# 문장 끝 존댓말 (「~니까」 까닭은 존댓말이 아니다: ㅂ받침 뒤만)
POL = re.compile(r'(요|세요|셔요|죠|시오|소서|십시오|습니다|습니까|[갑답랍럽릅입합봅옵줍씁깁십읍]니다|[갑답랍럽릅입합봅옵줍씁깁십읍]니까)(?=[\.\?!…~,」』\)─\s♪]*(?: / |$))')
PRON = re.compile(r'(?<![가-힣])(나는|나도|나를|나한테|나에게|나의|내가|난|날|나|내|저는|저도|저를|저한테|저에게|저의|제가|전|저|제|너는|너도|너를|너한테|너에게|너의|네가|넌|널|너|네|너희|당신|자네|그대)(?![가-힣])')
HON = re.compile(r'(시|셨|세|십|셔|으시|드리|드려|드릴|말씀|계시|계셨)')
KANA = re.compile(r'[぀-ヿ一-鿿]')
CTRL = re.compile(r'\^[a-zA-Z][0-9]*')

def windows(cur, looks):
    w = []
    for l in looks:
        i = cur.find(l)
        while i >= 0:
            w.append((max(0, i - 3), i + len(l) + 3)); i = cur.find(l, i + 1)
    return w

def check(num):
    bf = os.path.join(HERE, '묶음', f'묶음_{num}.json')
    af = os.path.join(HERE, '답', f'답_{num}.json')
    batch = {it['id'] for it in json.load(open(bf, encoding='utf-8'))['줄']}
    if not os.path.exists(af):
        print(f'[{num}] 답 파일 없음: {af}'); return 1, 0
    try:
        ans = json.load(open(af, encoding='utf-8-sig'))
    except Exception as ex:
        print(f'[{num}] JSON 오류: {ex}'); return 1, 0
    if not isinstance(ans, list):
        print(f'[{num}] 답은 목록([...])이어야 한다'); return 1, 0
    err = warn = 0; seen = set()
    for n, a in enumerate(ans):
        def E(msg):
            nonlocal err; err += 1; print(f'[{num}] 오류 {a.get("id", n)}: {msg}')
        def Wn(msg):
            nonlocal warn; warn += 1; print(f'[{num}] 주의 {a.get("id", n)}: {msg}')
        if not isinstance(a, dict) or set(a) != {'id', '지금', '제안', '까닭', '종류'}:
            E('칸은 id·지금·제안·까닭·종류 다섯 개여야 한다'); continue
        i = a['id']
        if i not in batch: E('이 묶음에 없는 id'); continue
        if i in seen: E('같은 id 를 두 번 적음'); continue
        seen.add(i)
        it = ITEMS[i]; cur, sug = it['지금'], a['제안']
        if a['지금'] != cur: E('「지금」이 묶음의 글과 다르다 — 묶음에서 그대로 옮길 것'); continue
        if a['종류'] not in KINDS: E(f'종류는 {sorted(KINDS)} 가운데 하나')
        if not sug.strip() or sug == cur: E('제안이 비었거나 지금과 같다'); continue
        if not a['까닭'].strip(): E('까닭이 비었다')
        if cur.count(' / ') != sug.count(' / '): E('줄바꿈( / ) 수가 바뀜')
        if CTRL.findall(cur) != CTRL.findall(sug): E('^ 제어 기호가 바뀜')
        if KANA.search(sug): E('제안에 가나·한자가 있다')
        try: sug.encode('cp949')
        except UnicodeEncodeError as ex: E(f'게임에서 못 쓰는 글자: {sug[ex.start]!r}')
        if a['종류'] != '기타':
            if len(POL.findall(sug)) > len(POL.findall(cur)): E('존댓말 말끝이 늘었다 — 반말은 고정')
            if sorted(PRON.findall(sug)) != sorted(PRON.findall(cur)): E(f'인칭이 바뀌었다 {sorted(PRON.findall(cur))} → {sorted(PRON.findall(sug))} — 바꿔야 하면 종류 「기타」로')
            if len(HON.findall(sug)) < len(HON.findall(cur)): Wn('높임 「-시-」 쪽 글자가 줄었다 — 원문에 높임이 없는지 확인')
        win = windows(cur, it['살필곳'])
        sm = difflib.SequenceMatcher(None, cur, sug, autojunk=False)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == 'equal': continue
            if not any(s <= a1 and a2 <= t for s, t in win):
                Wn(f'살필곳 밖 손질: 「{cur[max(0,a1-4):a2+4]}」 → 「{sug[max(0,b1-4):b2+4]}」'); break
    print(f'[{num}] 답 {len(ans)}건 · 오류 {err} · 주의 {warn}')
    return err, len(ans)

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '전부'
    # 「전부」는 묶음 폴더의 모든 묶음을 본다 — 답 파일이 빠진 묶음도 오류로 센다
    nums = sorted(f[3:5] for f in os.listdir(os.path.join(HERE, '묶음')) if re.fullmatch(r'묶음_\d\d\.json', f)) if arg == '전부' else [f'{int(arg):02d}']
    tot = sum(check(n)[0] for n in nums)
    print(f'합계 오류 {tot}')
    sys.exit(1 if tot else 0)

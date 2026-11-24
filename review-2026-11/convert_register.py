"""해요체/합쇼체 → 반말, 저 → 나 1차 변환. 손으로 볼 줄에는 표시를 단다."""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
W = r"Y:\AI\claude-work\fairytale-review"
END = r'(?=[\.\?!…~,，」』）\)─\s♪]|\^n|$)'

# (pattern, replacement) — 순서가 중요: 긴 것 먼저
RULES = [
    (r'아니에요' + END, '아니야'),
    (r'이에요' + END, '이야'),
    (r'예요' + END, '야'),
    (r'잖아요' + END, '잖아'),
    (r'(었|았|했|겠|있|없|였)나요' + END, r'\1어'),
    (r'인가요' + END, '인가'),
    (r'(건|는|은|ㄴ|던)가요' + END, r'\1가'),
    (r'군요' + END, '구나'),
    (r'이죠' + END, '이지'),
    (r'죠' + END, '지'),
    (r'지요' + END, '지'),
    (r'주세요' + END, '줘'),
    (r'안녕하세요' + END, '안녕'),
    (r'하세요' + END, '해'),
    (r'보세요' + END, '봐'),
    (r'마세요' + END, '마'),
    (r'들어오세요' + END, '들어와'),
    (r'오세요' + END, '와'),
    (r'가세요' + END, '가'),
    (r'드세요' + END, '먹어'),
    (r'아니요' + END, '아니'),
    (r'저기요' + END, '저기'),
    (r'정말요' + END, '정말'),
    (r'안녕하신가요' + END, '안녕'),
    (r'안녕히 계세요' + END, '안녕'),
    (r'어떠세요' + END, '어때'),
    (r'(왜 )?그러세요' + END, r'\1그래'),
    (r'앉으세요' + END, '앉아'),
    (r'계세요' + END, '계셔'),
    (r'누구세요' + END, '누구셔'),
    (r'죄송해요' + END, '미안해'),
    (r'죄송하지만', '미안하지만'),
    (r'(었|았|였)답니다' + END, r'\1어'),
    (r'있답니다' + END, '있어'),
    (r'없답니다' + END, '없어'),
    (r'좋답니다' + END, '좋아'),
    (r'(?<=[가-힣])랍니다' + END, '야'),
    (r'(?<=[가-힣])이요' + END, ''),
    (r'(?<=[가-힣])요' + END, ''),          # 나머지 「~요」는 떼기
]
FP = [
    (r'(?<![가-힣])저는', '나는'), (r'(?<![가-힣])저도', '나도'), (r'(?<![가-힣])제가', '내가'),
    (r'(?<![가-힣])저를', '나를'), (r'(?<![가-힣])저한테', '나한테'), (r'(?<![가-힣])저에게', '나에게'),
    (r'(?<![가-힣])저의', '나의'), (r'(?<![가-힣])저랑', '나랑'), (r'(?<![가-힣])저와', '나와'),
    (r'(?<![가-힣])저만', '나만'), (r'(?<![가-힣])제게', '내게'), (r'(?<![가-힣])저희', '우리'),
    (r'(?<![가-힣])저야', '나야'),
    (r'(?<![가-힣])저(?=(보다|처럼|까지|부터|라면|였|만큼|로서))', '나'), (r'(?<![가-힣])제(?= [가-힣])', '내'),
]
YES = [(r'응, 네(?=[,\.!…])', '으, 응'), (r'네, 네(?=[,\.!…])', '응, 응'), (r'(?<![가-힣])네(?=[,\.!…?])', '응')]
FLAG = re.compile(r'([습갑답랍럽릅입합봅옵줍씁깁십읍]니[다까]|세요|셔요|시오|주셨|주시|하시|하셨|계시|계셨|드리|드릴|드려|말씀|여쭙|뵙|셨|으시|(?<![가-힣])저(?=[,…\.\s!?]|$))')

OV = json.load(open(W + '/register_overrides.json', encoding='utf-8')) if __import__('os').path.exists(W + '/register_overrides.json') else {}
PATCH = json.load(open(W + '/register_patches.json', encoding='utf-8'))
def convert(ko, do_fp=True):
    s = ko
    # 받침 ㅆ 뒤의 「~나요」(과거·완료 의문) → 「~어」: 졌나요→졌어, 났나요→났어
    s = re.sub(r'([가-힣])나요' + END, lambda m: m.group(1) + '어' if (ord(m.group(1)) - 0xAC00) % 28 == 20 else m.group(0), s)
    for p, r in RULES:
        s = re.sub(p, r, s)
    if do_fp:
        for p, r in FP:
            s = re.sub(p, r, s)
    for p, r in YES:
        s = re.sub(p, r, s)
    return s

if __name__ == '__main__':
    T = json.load(open(W + '/fix_targets_register.json', encoding='utf-8'))
    out = {}
    for cat, ls in T.items():
        res = []
        for l in ls:
            key = f"{cat}|{l['scene']}|{l['slot']}"
            new = OV[key] if key in OV else convert(l['ko'])
            for a, b in PATCH.get(key, []):
                if a not in new:
                    print('!! patch miss', key, a)
                new = new.replace(a, b)
            flags = sorted(set(m.group(0) for m in FLAG.finditer(new)))
            res.append(dict(l, new=new, flags=flags))
        out[cat] = res
        print(cat, len(res), 'flagged', sum(1 for r in res if r['flags']), 'unchanged', sum(1 for r in res if r['new'] == r['ko']))
    json.dump(out, open(W + '/fix_register_auto.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

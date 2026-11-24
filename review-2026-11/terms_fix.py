import json,sys,re
sys.stdout.reconfigure(encoding='utf-8')
Q=r'(」|』|"|\'|’|”)?'
# 성경 -> 성서 : 받침 ㅇ -> 받침 없음
SEONG=[('으로','로'),('이었','였'),('이에요','예요'),('이야','야'),('이라','라'),('이란','란'),('이다','다'),('이니','니'),('이구나','구나'),('이자','이자'),('이고','이고'),('이나','나'),('이든','든'),('이랑','랑'),('이지','지'),('이','가'),('을','를'),('은','는'),('과','와')]
def fix_seong(t):
    def rep(m):
        q=m.group(1) or ''; rest=t[m.end():]
        for a,b in SEONG:
            if rest.startswith(a): return '성서'+q+b, len(a)
        return '성서'+q, 0
    out=''; i=0
    for m in re.finditer(r'성경'+Q,t):
        if m.start()<i: continue
        s,skip=rep(m); out+=t[i:m.start()]+s; i=m.end()+skip
    return out+t[i:]
# 할머니 -> 할머님 : 받침 없음 -> 받침 ㅁ
HAL=[('가','이'),('를','을'),('는','은'),('와','과'),('로','으로'),('랑','이랑'),('나','이나'),('네','이네'),('야','이야'),('라','이라'),('였','이었'),('예요','이에요')]
def fix_hal(t):
    def rep(m):
        q=m.group(1) or ''; rest=t[m.end():]
        for a,b in HAL:
            if rest.startswith(a): return '할머님'+q+b, len(a)
        return '할머님'+q, 0
    out=''; i=0
    for m in re.finditer(r'할머니'+Q,t):
        s,skip=rep(m); out+=t[i:m.start()]+s; i=m.end()+skip
    return out+t[i:]
edits={}
def add(g,r,new,why):
    if new!=r['ko']: edits.setdefault(g,[]).append(dict(scene=r['scene'],slot=r['slot'],ja=r['ja'],old=r['ko'],new=new,why=why))
for g in ['Requiem','Encore','Symphony']:
    rows=[json.loads(l) for l in open(rf'Y:\AI\claude-work\fairytale-review\{g}.jsonl',encoding='utf-8')]
    for r in rows:
        if not r['changed']: continue
        new=r['ko']; why=[]
        if '聖書' in r['ja'] and '성경' in new: new=fix_seong(new); why.append('聖書=성서')
        if g=='Requiem' and 'ゴーテル' in r['ja'] and re.search('고델|괴텔',new): new=re.sub('고델|괴텔','고텔',new); why.append('ゴーテル=고텔')
        if g=='Requiem' and 'おばあさま' in r['ja'] and '할머니' in new and not re.search(r'(?<!お)ばあさん|おばあさん|おばあちゃん|婆さん',r['ja']):
            new=fix_hal(new); why.append('おばあさま=할머님')
        elif g=='Requiem' and 'おばあさま' in r['ja'] and '할머니' in new: why.append('MANUAL-할머니')
        if why: add(g,r,new,why)
json.dump(edits,open(r'Y:\AI\claude-work\fairytale-review\terms_edits_auto.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for g,v in edits.items():
    print('=====',g,len(v))
    for e in v:
        o=e['old'].replace('^n',' / '); n=e['new'].replace('^n',' / ')
        # show only diff windows
        import difflib
        sm=difflib.SequenceMatcher(None,o,n)
        parts=[f"{o[max(0,i1-6):i2+5]}→{n[max(0,j1-6):j2+5]}" for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag!='equal']
        print(f" {e['scene'][:4]}-{e['slot']} {e['why']}: "+' | '.join(parts))

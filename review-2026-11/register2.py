import json,sys,re,collections,importlib.util,io,contextlib
sys.stdout.reconfigure(encoding='utf-8')
src=open(r"Y:\AI\claude-work\atlach-final-1121\review2\ja_register.py",encoding='utf-8').read()
src=src.split('if __name__ == "__main__":')[0].replace('with contextlib.redirect_stdout(io.StringIO()):\n    from mech import ending','')
ns={}; exec(src,ns); ja_reg=ns['ja_reg']
KPOL=re.compile(r"(요|세요|셔요|죠|시오|소서|십시오|습니다|습니까|[갑답랍럽릅입합봅옵줍씁깁십읍]니다|[갑답랍럽릅입합봅옵줍씁깁십읍]니까)$")
def ko_reg(ko):
    t=re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',ko).replace('^n','\n')
    t=re.sub(r"[「」『』（）\(\)]","",t)
    regs=[]
    for s in re.split(r"[\.。！？!?…\n]+",t):
        s=re.sub(r"[,，、~〜♪ー―─\s]+$","",s.strip())
        if len(s)<2: continue
        regs.append("polite" if KPOL.search(s) else "plain")
    if not regs: return "neutral"
    if "polite" in regs and "plain" in regs: return "mixed"
    return regs[0]
LABELS=set()
for g in ["Requiem","Encore","Symphony"]:
    for r in map(json.loads,open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')):
        if r['changed'] and len(r['ja'])<=10 and not re.search(r'[。、？！…「」『』\^ 　（）()─]',r['ja']): LABELS.add(r['ja'])
LABELS-={'はい','いいえ','右サイド','そうです','行かない','自分で食べる','グレーテルにあげる'}
summary={}
for g in ["Requiem","Encore","Symphony"]:
    rows=[json.loads(l) for l in open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')]
    st=collections.defaultdict(collections.Counter); lines=[]
    prev=None
    for r in rows:
        if not r['changed']: prev=None; continue
        if r['ja'] in LABELS: prev=r['ja']; continue
        spk=prev; prev=None
        if not spk: continue
        ja=re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',r['ja']).replace('^n','')
        j=ja_reg(ja); k=ko_reg(r['ko'])
        if j in('neutral',) or k=='neutral': continue
        st[spk][(j,k)]+=1
        if (j=='plain' and k=='polite') or (j=='polite' and k=='plain'):
            lines.append(dict(game=g,speaker=spk,scene=r['scene'],slot=r['slot'],ja_reg=j,ko_reg=k,ja=r['ja'],ko=r['ko']))
    print('=====',g)
    for spk,c in sorted(st.items(),key=lambda x:-sum(x[1].values())):
        tot=sum(c.values())
        if tot<15: continue
        print(f"  {spk}: 판정 {tot}줄 | 원문 반말 {c[('plain','plain')]+c[('plain','polite')]+c[('plain','mixed')]} 중 → 한국어 존댓말 {c[('plain','polite')]} | 원문 존대 {c[('polite','polite')]+c[('polite','plain')]+c[('polite','mixed')]} 중 → 한국어 반말 {c[('polite','plain')]}")
    json.dump(lines,open(rf"Y:\AI\claude-work\fairytale-review\register2_{g}.json",'w',encoding='utf-8'),ensure_ascii=False,indent=0)

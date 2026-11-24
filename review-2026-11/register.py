import json,sys,re,collections
sys.stdout.reconfigure(encoding='utf-8')
LABELS=set()
for g in ["Requiem","Encore","Symphony"]:
    for r in map(json.loads,open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')):
        if r['changed'] and len(r['ja'])<=10 and not re.search(r'[。、？！…「」『』\^ 　（）()──]',r['ja']): LABELS.add(r['ja'])
LABELS-= {'はい','いいえ','右サイド'}
def clean(s): return re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',s).replace('^n','\n')
POL_J=re.compile(r'(です|ます|でした|ました|ません|ましょう|でしょう|ください|ございます|ませ|下さい|ですか|ますか|ですね|ますね|ですよ|ますよ|ですわ|ますわ|ですの|でしょうか|まして|ですけど|ますけど|ですが|ますが|ません?か)[、。？！…!?─ー）」』\s]*$')
POL_K=re.compile(r'(요|니다|니까|세요|십시오|죠|시오|소서|지요|까요)[\.\?!…~─\-」』）\)\s,]*$')
def sents(t):
    parts=re.split(r'(?<=[。？！?!])|\n',t)
    return [p.strip() for p in parts if p.strip()]
res={}
for g in ["Requiem","Encore","Symphony"]:
    rows=[json.loads(l) for l in open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')]
    stat=collections.defaultdict(lambda: collections.Counter()); ex=collections.defaultdict(list)
    prev=None
    for r in rows:
        if not r['changed']: prev=None; continue
        if r['ja'] in LABELS: prev=(r['ja'],r['ko']); continue
        spk=prev[0] if prev else None; prev=None
        if not spk: continue
        ja,ko=clean(r['ja']),clean(r['ko'])
        # judge last sentence only
        js,ks=sents(ja),sents(ko)
        if not js or not ks: continue
        jp=bool(POL_J.search(js[-1])); kp=bool(POL_K.search(ks[-1]))
        jp_any=any(POL_J.search(s) for s in js)
        kp_any=any(POL_K.search(s) for s in ks)
        stat[spk][(jp_any,kp_any)]+=1
        if jp_any!=kp_any: ex[spk].append((r['scene'],r['slot'],ja.replace('\n',' / ')[:70],ko.replace('\n',' / ')[:80]))
    print('=====',g)
    for spk,c in sorted(stat.items(),key=lambda x:-sum(x[1].values())):
        tot=sum(c.values())
        if tot<10: continue
        jpol=c[(True,True)]+c[(True,False)]; mis1=c[(True,False)]; mis2=c[(False,True)]
        print(f"  {spk}: lines {tot}, ja-polite {jpol}, ja존대→ko반말 {mis1}, ja반말→ko존대 {mis2}")
    json.dump({k:v for k,v in ex.items()},open(rf"Y:\AI\claude-work\fairytale-review\register_{g}.json",'w',encoding='utf-8'),ensure_ascii=False,indent=1)

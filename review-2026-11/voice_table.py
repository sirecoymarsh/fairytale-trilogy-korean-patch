import json,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
W=r"Y:\AI\claude-work\fairytale-review"
D=json.load(open(rf'{W}\voice_lines.json',encoding='utf-8'))
def pct(a,b): return f"{round(100*a/b):>3}" if b else '  -'
def top(c,n=3): return ','.join(f"{k}{v}" for k,v in c.most_common(n)) or '-'
for g,L in D.items():
    by=collections.defaultdict(list)
    for l in L: by[l['spk']].append(l)
    print('#####',g)
    for spk,ls in sorted(by.items(),key=lambda x:-len(x[1])):
        if len(ls)<30: continue
        print(f"== {spk}({ls[0]['spk_ko']}) {len(ls)}줄")
        blks=collections.defaultdict(list)
        for l in ls: blks[l['blk'] if g!='Symphony' else ('A' if l['scene']<'1009' else 'B' if l['scene']<'1017' else 'C')].append(l)
        for b in sorted(blks):
            x=blks[b]; sp=[l for l in x if not l['thought']]
            jr=collections.Counter(l['jreg'] for l in sp if l['jreg']!='neutral'); kr=collections.Counter(l['kreg'] for l in sp if l['kreg']!='neutral')
            jfp=collections.Counter(f for l in x for f in l['jfp']); kfp=collections.Counter(f for l in x for f in l['kfp'])
            jsp=collections.Counter(f for l in sp for f in l['jsp']); ksp=collections.Counter(f for l in sp for f in l['ksp'])
            ke=collections.Counter(l['kend'] for l in sp if l['kend'])
            print(f"  {b}: n{len(x):>4} | 원문존대%{pct(jr['polite'],sum(jr.values()))} 번역존대%{pct(kr['polite'],sum(kr.values()))} | 1인칭 {top(jfp)} → {top(kfp)} | 2인칭 {top(jsp)} → {top(ksp)} | 끝 {top(ke,4)}")

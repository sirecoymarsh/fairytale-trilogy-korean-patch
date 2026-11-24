import json,sys,re,random
sys.stdout.reconfigure(encoding='utf-8')
D=json.load(open(r'Y:\AI\claude-work\fairytale-review\voice_lines.json',encoding='utf-8'))
def peek(g,spk,lo='0000',hi='9999',cond=lambda l:True,n=10,seed=1,w=95):
    ls=[l for l in D[g] if l['spk']==spk and lo<=l['scene']<=hi and cond(l)]
    random.seed(seed); s=sorted(random.sample(ls,min(n,len(ls))),key=lambda l:(l['scene'],l['slot']))
    print(f"--- {g} {spk} {lo}-{hi} ({len(ls)}줄 중 {len(s)})")
    for l in s:
        print(f" {l['scene']}-{l['slot']} [{l['jreg'][:3]}/{l['kreg'][:3]}] {l['ja'].replace('^n',' ')[:w]}\n      → {l['ko'].replace('^n',' ')[:w+10]}")
if __name__=='__main__':
    exec(sys.argv[1])

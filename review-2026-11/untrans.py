import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
JP = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff\uff01-\uff5e]')
for g in ["Requiem","Encore","Symphony"]:
    rows=[json.loads(l) for l in open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')]
    un=[r for r in rows if not r['changed'] and JP.search(r['ja'])]
    bad=[r for r in rows if r['changed'] and '\ufffd' in r['ko']]
    print("=====",g,"unchanged-with-JP:",len(un),"decode-bad:",len(bad))
    c=collections.Counter(r['scene'] for r in un)
    print(" by scene:", c.most_common(15))
    for r in un[:25]: print("  U",r['scene'],r['slot'],repr(r['ja'][:70]))
    for r in bad[:10]: print("  B",r['scene'],r['slot'],repr(r['ja'][:50]),'=>',repr(r['ko'][:50]))

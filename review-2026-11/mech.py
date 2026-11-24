import json,sys,re,collections
sys.stdout.reconfigure(encoding='utf-8')
CTRL=re.compile(r'\^[a-zA-Z][0-9]*')
RUBY=re.compile(r'\|[^\[\]|]+\[[^\]]+\]')
KANA=re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')
out={}
for g in ["Requiem","Encore","Symphony"]:
    rows=[json.loads(l) for l in open(rf"Y:\AI\claude-work\fairytale-review\{g}.jsonl",encoding='utf-8')]
    res=collections.Counter(); ex=collections.defaultdict(list)
    for r in rows:
        if not r['changed']: continue
        ja,ko=r['ja'],r['ko']
        cj,ck=CTRL.findall(ja),CTRL.findall(ko)
        cj2=[c for c in cj if c!='^n']; ck2=[c for c in ck if c!='^n']
        if cj2!=ck2: res['ctrl_non_n_mismatch']+=1; ex['ctrl'].append(r)
        if cj.count('^n')!=ck.count('^n'): res['n_count_diff']+=1
        if ja.endswith('^n')!=ko.endswith('^n'): res['trailing_n_diff']+=1; ex['trail'].append(r)
        if KANA.search(re.sub(r'\[[^\]]*\]','',ko)): res['kana_kanji_left']+=1; ex['kana'].append(r)
        if '|' in ko and not RUBY.search(ko): res['broken_ruby']+=1; ex['ruby'].append(r)
        if ko.count('[')!=ko.count(']'): res['bracket_unbalanced']+=1; ex['br'].append(r)
        if ja.strip() and not ko.strip(): res['empty_ko']+=1; ex['empty'].append(r)
        # 3+ lines by explicit ^n
        if ck.count('^n')>=3 and not ko.endswith('^n'): res['4plus_explicit_lines']+=1; ex['lines'].append(r)
    print('==',g,dict(res))
    for k,v in ex.items():
        for r in v[:6]: print('  ',k,r['scene'],r['slot'],repr(r['ja'][:70]),'=>',repr(r['ko'][:80]))

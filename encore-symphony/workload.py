from assets import *
from itertools import combinations
def main():
    data=read('audit/index.json');keys={}
    for g,rows in data.items():keys[g]={k:v['sha'] for k,v in rows.items() if 'size' in v}
    req={}
    for bank in RJ.glob('grp*.xfl'):
        with bank.open('rb') as f:
            for e in entry_map(bank).values():
                f.seek(e.absolute_offset)
                for key,b in flatten(bank.stem,e.name,f.read(e.size)):
                    if b.startswith(b'WG'):req[key]=sha(b)
    keys={'Requiem':req,**keys};report={}
    for lane,fn in [('all_WCG',lambda k:True),('system_panels',lambda k:k.startswith('grps/') and '.lwg/' in k),('title_buttons',lambda k:k.startswith('grpo/')),('library',lambda k:k.startswith('grpo_lib/')),('map',lambda k:k.startswith('grpo_map/'))]:
        sets={g:{v for k,v in rec.items() if fn(k)} for g,rec in keys.items()};distinct=set.union(*sets.values());distribution=Counter(tuple(g for g,s in sets.items() if h in s) for h in distinct)
        report[lane]=dict(slots={g:sum(fn(k) for k in v) for g,v in keys.items()},unique_per_game={g:len(v) for g,v in sets.items()},unique_across_three=len(distinct),exclusive_membership={' + '.join(k):v for k,v in distribution.items()},pairwise_shared={a+' + '+b:len(sets[a]&sets[b]) for a,b in combinations(sets,2)},union_two=len(sets['Encore']|sets['Symphony']),shared_by_three=len(set.intersection(*sets.values())))
    save('audit/workload.json',report)
    for k,v in report.items(): print(k,v)
if __name__=='__main__':main()

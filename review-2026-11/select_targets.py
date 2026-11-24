import json,sys,collections,re
sys.stdout.reconfigure(encoding='utf-8')
W=r"Y:\AI\claude-work\fairytale-review"
D=json.load(open(W+'/voice_lines.json',encoding='utf-8'))
NOUNYO=re.compile(r'(중요|필요|주요|강요|동요|소요|개요|수요|요요|노요|교요|민요|가요|화요|월요|금요|토요|일요|목요|수요)$')
def ko_sents(ko):
    t=re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',ko).replace('^n','\n')
    t=re.sub(r'[「」『』（）\(\)]','',t)
    out=[]
    for s in re.split(r'[\.。！？!?…\n]+',t):
        s=re.sub(r'[,，、~〜♪ー―─\s]+$','',s.strip())
        if len(s)>=2: out.append(s)
    return out
def is_pol(s):
    if NOUNYO.search(s): return False
    return bool(re.search(r'(요|[습갑답랍럽릅입합봅옵줍씁깁십읍]니다|[습갑답랍럽릅입합봅옵줍씁깁십읍]니까|세요|죠|시오|소서)$',s))
def kpol(ko): return any(is_pol(s) for s in ko_sents(ko))
JEO=re.compile(r'(?<![가-힣])(저는|제가|저도|저를|저한테|저에게|저의|저랑|저와|저만|저야말로|저로서는|전 |제 (?=[가-힣]))')
def kjeo(ko): return bool(JEO.search(ko.replace('^n',' ')))
def scene_major(L,spk):
    c=collections.defaultdict(collections.Counter)
    for l in L:
        if l['spk']==spk and l['jreg'] in('polite','plain'): c[l['scene']][l['jreg']]+=1
    return {s:('polite' if cc['polite']>cc['plain'] else 'plain') for s,cc in c.items()}
EXCL={('1001',22),('1416',206),('1421',79),('1703',376)}
def select(L,spk,scope=lambda s:True):
    mj=scene_major(L,spk); out=[]
    for l in L:
        if l['spk']!=spk or not scope(l['scene']): continue
        if not (kpol(l['ko']) or kjeo(l['ko'])): continue
        m=mj.get(l['scene'],'plain')
        if l['jreg']=='polite': continue
        if l['jreg'] in('mixed','neutral') and m=='polite': continue
        if spk=='ラプンツェル' and m=='polite': continue
        if l['ko'].lstrip('　 ').startswith(('『','「')) and l['ko'].rstrip().endswith(('』','」')): continue
        if (l['scene'],l['slot']) in EXCL: continue
        out.append(l)
    return out
T={'alice_R':select(D['Requiem'],'アリス'),'alice_S':select(D['Symphony'],'アリス'),
   'rapunzel':select(D['Requiem'],'ラプンツェル',lambda s: s[:2] in ('12','18','19')),
   'odette':select(D['Requiem'],'オデット')}
for k,v in T.items(): print(k,len(v),dict(collections.Counter(l['scene'][:2] for l in v)))
json.dump({k:[dict(scene=l['scene'],slot=l['slot'],spk=l['spk'],jreg=l['jreg'],thought=l['thought'],ja=l['ja'],ko=l['ko']) for l in v] for k,v in T.items()},open(W+'/fix_targets_register.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)

from pathlib import Path
from PIL import Image
import hashlib, json, numpy as np

ROOT=Path(__file__).resolve().parent
N=ROOT/'work'/'library_newspaper_0223_faithful_v2'
B=ROOT/'work'/'library_book_0011_faithful_v2'

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def arr(p): return np.array(Image.open(p).convert('RGBA'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()

checks=[]
def check(name,ok,detail=None):
    checks.append({'name':name,'pass':bool(ok),'detail':detail})

nm=load(N/'manifest.json'); bm=load(B/'manifest.json')
for label,root,m in [('newspaper',N,nm),('book',B,bm)]:
    check(label+'_review_only',m['status']=='USER_REVIEW_REQUIRED_NOT_INSTALLED' and not m['contract']['installed'])
    for k,pstr in m['files'].items():
        p=Path(pstr); check(label+'_'+k+'_exists',p.exists(),str(p))
        if p.exists(): check(label+'_'+k+'_sha',sha(p)==m['sha256'][k])

ns=arr(Path(nm['files']['source'])); nc=arr(Path(nm['files']['candidate'])); ncl=arr(Path(nm['files']['clean']))
nom=np.array(Image.open(nm['files']['owned_mask']).convert('L'))>0
npm=np.array(Image.open(nm['files']['paper_mask']).convert('L'))>8
check('newspaper_dimensions',ns.shape==(600,1126,4)==nc.shape==ncl.shape)
check('newspaper_outside_owned_exact',np.array_equal(ns[~nom],nc[~nom]))
check('newspaper_clean_outside_owned_exact',np.array_equal(ns[~nom],ncl[~nom]))
check('newspaper_old_paper_removed_in_clean',float(np.mean(np.all(ns[npm]==ncl[npm],axis=1)))<0.001)
check('newspaper_original_silhouette_bbox',list(Image.fromarray(npm.astype('uint8')*255).getbbox()),list(Image.fromarray(npm.astype('uint8')*255).getbbox()))
for k,v in nm['typesetting'].items():
    if isinstance(v,dict): check('newspaper_'+k+'_no_overflow',v.get('remaining')==0,v)

bs=arr(Path(bm['files']['source'])); bc=arr(Path(bm['files']['candidate'])); bcl=arr(Path(bm['files']['clean']))
bom=np.array(Image.open(bm['files']['owned_mask']).convert('L'))>0
bink=np.array(Image.open(bm['files']['removed_text_mask']).convert('L'))>0
check('book_dimensions',bs.shape==(568,150,4)==bc.shape==bcl.shape)
check('book_outside_owned_exact',np.array_equal(bs[~bom],bc[~bom]))
check('book_clean_outside_owned_exact',np.array_equal(bs[~bom],bcl[~bom]))
check('book_top_red_cap_exact',np.array_equal(bs[:80],bc[:80]))
check('book_bottom_red_cap_exact',np.array_equal(bs[454:],bc[454:]))
check('book_blue_rules_exact',np.array_equal(bs[55:82],bc[55:82]) and np.array_equal(bs[434:455],bc[434:455]))
check('book_old_title_removed_in_clean',float(np.mean(np.all(bs[bink]==bcl[bink],axis=1)))<0.001)
check('book_no_full_canvas_plate',int(bom.sum())<int(bom.size*0.25),int(bom.sum()))

result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks}
out=ROOT/'work'/'library_faithful_v2_validation.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'passed':sum(x['pass'] for x in checks),'total':len(checks),'output':str(out)},ensure_ascii=False,indent=2))
if result['status']!='PASS':
    print(json.dumps([x for x in checks if not x['pass']],ensure_ascii=False,indent=2)); raise SystemExit(1)

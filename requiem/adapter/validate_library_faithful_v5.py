from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parent
N=ROOT/'work'/'library_newspaper_0223_readable_v3'
B=ROOT/'work'/'library_book_0011_glyph_cleanup_v8'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
checks=[]
def ck(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
for label,root,m in [('newspaper',N,load(N/'manifest.json')),('book',B,load(B/'manifest.json'))]:
 ck(label+'_review_only',m['status']=='USER_REVIEW_REQUIRED_NOT_INSTALLED' and not m['contract']['installed'])
 for k,pstr in m['files'].items():
  p=Path(pstr); ck(label+'_'+k+'_exists',p.exists(),str(p));
  if p.exists():ck(label+'_'+k+'_sha',sha(p)==m['sha256'][k])
nm=load(N/'manifest.json'); ns=arr(Path(nm['files']['source'])); nc=arr(Path(nm['files']['candidate'])); ncl=arr(Path(nm['files']['clean'])); nom=np.array(Image.open(nm['files']['owned_mask']).convert('L'))>0; npm=np.array(Image.open(nm['files']['paper_mask']).convert('L'))>8
ck('newspaper_dimensions',ns.shape==(600,1126,4)==nc.shape==ncl.shape)
ck('newspaper_outside_owned_exact',np.array_equal(ns[~nom],nc[~nom]))
ck('newspaper_clean_outside_owned_exact',np.array_equal(ns[~nom],ncl[~nom]))
ck('newspaper_old_paper_removed_before_rebuild',float(np.mean(np.all(ns[npm]==ncl[npm],axis=1)))<0.001)
ck('newspaper_horizontal_layout',nm['contract'].get('korean_horizontal_reading_layout') is True)
ck('newspaper_title_top_left',nm['typesetting']['headline']['x']==316 and nm['typesetting']['headline']['y']==80 and nm['typesetting']['headline']['width']<=492,nm['typesetting']['headline'])
ck('newspaper_all_text_fit',nm['validation']['all_text_regions_fit_without_overflow'])
ck('newspaper_top_lines_reasonable',1<=nm['typesetting']['top_article']['lines']<=9,nm['typesetting']['top_article'])
ck('newspaper_bottom_lines_reasonable',1<=nm['typesetting']['bottom_article']['lines']<=9,nm['typesetting']['bottom_article'])
bm=load(B/'manifest.json'); bs=arr(Path(bm['files']['source'])); bc=arr(Path(bm['files']['candidate'])); bcl=arr(Path(bm['files']['clean'])); bom=np.array(Image.open(bm['files']['owned_mask']).convert('L'))>0; bink=np.array(Image.open(bm['files']['removed_text_mask']).convert('L'))>0
ck('book_dimensions',bs.shape==(568,150,4)==bc.shape==bcl.shape)
ck('book_outside_owned_exact',np.array_equal(bs[~bom],bc[~bom]))
ck('book_clean_outside_owned_exact',np.array_equal(bs[~bom],bcl[~bom]))
ck('book_red_caps_exact',np.array_equal(bs[:80],bc[:80]) and np.array_equal(bs[454:],bc[454:]))
ck('book_blue_rules_exact',np.array_equal(bs[55:82],bc[55:82]) and np.array_equal(bs[434:455],bc[434:455]))
ck('book_old_title_removed_before_typeset',float(np.mean(np.all(bs[bink]==bcl[bink],axis=1)))<0.01)
ck('book_source_round_print_style',bm['contract'].get('per_book_typeface_profile')=='alice_round_gulim_burgundy')
ck('book_alice_specific_round_profile',bm['contract'].get('per_book_typeface_profile')=='alice_round_gulim_burgundy')
ck('book_no_rectangular_face_replacement',bm['contract'].get('no_rectangular_paper_face_replacement') is True)
ck('book_glyph_shaped_cleanup',bm['contract'].get('glyph_shaped_cleanup_only') is True and bm['validation'].get('clean_change_is_glyph_shaped') is True)
result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks}
out=ROOT/'work'/'library_faithful_v5_validation.json'; out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'passed':sum(x['pass'] for x in checks),'total':len(checks),'output':str(out)},ensure_ascii=False,indent=2))
if result['status']!='PASS':print([x for x in checks if not x['pass']]);raise SystemExit(1)


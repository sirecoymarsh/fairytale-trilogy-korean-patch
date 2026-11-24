#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
import numpy as np,cv2
from PIL import Image
import xfl_tool
ROOT=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
SRC=ROOT/'runtime/trial_ko/grpe.xfl'
A=ROOT/'staging/grpe_title_logo_korean_v1_a/grpe.ko-gallery-title-logo-v1.xfl'
B=ROOT/'staging/grpe_title_logo_korean_v1_b/grpe.ko-gallery-title-logo-v1.xfl'
TOOL=ROOT/'adapter/UiAssetTool.exe'
WORK=ROOT/'staging/grpe_title_logo_korean_v1_independent_validation'
OUT=ROOT/'audit/grpe_title_logo_korean_v1_independent_validation.json'
EXPECTED_SRC='14C139A133D71AE85D2746C0B499B2D162C546438917EF3AE7F957AB2C24AF0F'
EXPECTED_OUT='1507AEF748969562C7EE730C4EEABEAA9737063BA1FB73E475FCAD1AE8E95178'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def read_entry(arc,name):
 e=next(x for x in arc.entries if x.name==name)
 with arc.source.open('rb') as f:f.seek(e.absolute_offset);b=f.read(e.size)
 if len(b)!=e.size:raise RuntimeError('short read')
 return b
def main():
 if WORK.exists():shutil.rmtree(WORK)
 WORK.mkdir(parents=True)
 hs,h1,h2=sha(SRC),sha(A),sha(B)
 if hs!=EXPECTED_SRC or h1!=EXPECTED_OUT or h2!=EXPECTED_OUT or h1!=h2:raise RuntimeError('whole archive hash contract')
 sa,aa,ba=map(xfl_tool.parse_archive,(SRC,A,B))
 names=[e.name for e in sa.entries]
 if names!=[e.name for e in aa.entries] or names!=[e.name for e in ba.entries]:raise RuntimeError('entry order drift')
 changes=[];non_target_exact=True
 with SRC.open('rb') as fs,A.open('rb') as fa,B.open('rb') as fb:
  for se,ae,be in zip(sa.entries,aa.entries,ba.entries):
   fs.seek(se.absolute_offset);fa.seek(ae.absolute_offset);fb.seek(be.absolute_offset)
   sh=hashlib.sha256(fs.read(se.size)).digest();ah=hashlib.sha256(fa.read(ae.size)).digest();bh=hashlib.sha256(fb.read(be.size)).digest()
   if ah!=bh:raise RuntimeError('A/B entry mismatch '+se.name)
   if sh!=ah:changes.append(se.name)
 if changes!=['9101.lwg']:raise RuntimeError('unexpected archive delta '+repr(changes))
 for tag,arc in [('source',sa),('candidate',aa)]:
  lwg=WORK/f'{tag}.lwg';lwg.write_bytes(read_entry(arc,'9101.lwg'))
  d=WORK/tag;subprocess.run([str(TOOL),'lwg-extract-png',str(lwg),str(d)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
 sp=sorted((WORK/'source').glob('*.png'));cp=sorted((WORK/'candidate').glob('*.png'))
 if len(sp)!=8 or [p.name for p in sp]!=[p.name for p in cp]:raise RuntimeError('state closure')
 # Geometric allowed region independent of the builder's own diff mask.
 allowed=np.zeros((720,1280),np.uint8);poly=np.array([[240,150],[582,150],[596,157],[597,282],[589,296],[241,296],[236,284],[236,158]],np.int32);cv2.fillPoly(allowed,[poly],255);allowed=cv2.dilate(allowed,np.ones((9,9),np.uint8),iterations=1)>0
 states=[];cand_hashes=[]
 for s,c in zip(sp,cp):
  si=np.array(Image.open(s).convert('RGBA'));ci=np.array(Image.open(c).convert('RGBA'));diff=np.any(si!=ci,axis=2)
  # Target pixels must be confined to the plaque interior and all alpha is immutable.
  outside=int((diff&~allowed).sum());alpha=bool(np.array_equal(si[:,:,3],ci[:,:,3]))
  # Decorative star's actual connected component is never text-owned.
  gray=cv2.cvtColor(si[:,:,:3],cv2.COLOR_RGB2GRAY);sm=np.zeros(gray.shape,np.uint8);sm[240:309,250:315]=(gray[240:309,250:315]<150).astype(np.uint8)
  sn,sl,ss,_=cv2.connectedComponentsWithStats(sm,8);star_core=(sl==(1+int(np.argmax(ss[1:,cv2.CC_STAT_AREA])))).astype(np.uint8)*255;star_core=cv2.dilate(star_core,np.ones((7,7),np.uint8),iterations=1)>0
  star=bool(np.array_equal(si[star_core],ci[star_core]))
  # Source-authored ribbon's main red component and its outline/antialias stay exact.
  hsv=cv2.cvtColor(si[:,:,:3],cv2.COLOR_RGB2HSV);rx0,ry0,rx1,ry1=(370,272,610,337);sub=hsv[ry0:ry1,rx0:rx1];red=((sub[:,:,1]>75)&((sub[:,:,0]<18)|(sub[:,:,0]>170))&(sub[:,:,2]>45)).astype(np.uint8)*255
  rn,rl,rs,_=cv2.connectedComponentsWithStats(red,8);red=(rl==(1+int(np.argmax(rs[1:,cv2.CC_STAT_AREA])))).astype(np.uint8)*255;red=cv2.dilate(red,np.ones((11,11),np.uint8),iterations=1)>0
  ribbon=bool(np.array_equal(si[ry0:ry1,rx0:rx1][red],ci[ry0:ry1,rx0:rx1][red]))
  states.append({'state':s.name,'dimensions':list(Image.open(c).size),'changed_pixels':int(diff.sum()),'changed_bbox':None if not diff.any() else [int(np.where(diff)[1].min()),int(np.where(diff)[0].min()),int(np.where(diff)[1].max())+1,int(np.where(diff)[0].max())+1],'outside_allowed_pixels':outside,'alpha_exact':alpha,'star_exact':star,'red_ribbon_and_outline_exact':ribbon})
  cand_hashes.append(hashlib.sha256(ci.tobytes()).hexdigest())
 if not all(x['outside_allowed_pixels']==0 and x['alpha_exact'] and x['star_exact'] and x['red_ribbon_and_outline_exact'] for x in states):raise RuntimeError('independent pixel contract')
 if len(set(cand_hashes))!=8:raise RuntimeError('animation flattened')
 # Independently inspect builder-persisted text-free frames for dark source-glyph residue.
 clean=[]
 for p in sorted((ROOT/'staging/grpe_title_logo_korean_v1_assets/evidence').glob('clean_[0-9][0-9].png')):
  a=np.array(Image.open(p).convert('RGB'));g=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
  top=int((g[150:232,255:590]<170).sum());bottom=int((g[215:272,315:590]<170).sum())
  clean.append({'state':p.name,'top_dark_pixels':top,'bottom_dark_pixels':bottom})
 if len(clean)!=8 or max(x['top_dark_pixels'] for x in clean)>0 or max(x['bottom_dark_pixels'] for x in clean)>0:raise RuntimeError('clean plate residue gate')
 report={'schema':'fairytale-requiem-grpe-title-logo-independent-validation-v1','status':'PASS_STATIC_RUNTIME_PENDING','completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'archives':{'source':{'path':str(SRC),'sha256':hs,'entry_count':len(names)},'candidate_a':{'path':str(A),'sha256':h1},'candidate_b':{'path':str(B),'sha256':h2},'changed_entries':changes,'entry_order_exact':True,'a_b_byte_identical':h1==h2},'state_validation':states,'clean_plate_validation':clean,'checks':{'only_9101_lwg_changed':changes==['9101.lwg'],'state_closure_8':len(states)==8,'state_animation_not_flattened':len(set(cand_hashes))==8,'outside_geometric_allowlist_exact':all(x['outside_allowed_pixels']==0 for x in states),'alpha_exact':all(x['alpha_exact'] for x in states),'star_exact':all(x['star_exact'] for x in states),'ribbon_exact':all(x['red_ribbon_and_outline_exact'] for x in states),'clean_plate_source_ink_removed':len(clean)==8 and max(x['top_dark_pixels'] for x in clean)==0 and max(x['bottom_dark_pixels'] for x in clean)==0},'runtime_status':'pending'}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':report['status'],'archive_sha256':h1,'changed_entries':changes,'states':len(states),'checks':report['checks']},ensure_ascii=False))
if __name__=='__main__':main()


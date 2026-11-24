#!/usr/bin/env python3
"""Build the Korean Fairytale Requiem title logo in grpe 9101.lwg.

The eight 9101 frames are a closed animated runtime state family.  Each frame is
localized independently so its source animation stays intact.  The Japanese glyphs
are removed with one coherent source-authored parchment slab; the ornate border,
four-point star, English ribbon, alpha, and all geometry stay authored.
"""
from __future__ import annotations
import hashlib,json,shutil,struct,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
import xfl_tool

ROOT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE=ROOT/'runtime/trial_ko/grpe.xfl'
SOURCE_SHA='14C139A133D71AE85D2746C0B499B2D162C546438917EF3AE7F957AB2C24AF0F'
SOURCE_LWG_SHA='E46A2A2059FDAF82933BD35164DF878629A7240BDC46786C2CF91D0DBC82CC15'
TOOL=ROOT/'adapter/UiAssetTool.exe'
DONOR=ROOT/'staging/ui_other_banks_audit_v1/exported_png/grpo_lib/0209.png'
FONT=ROOT/'tools/fonts/title_candidates/YeonSung-Regular.ttf'
FONT_LICENSE=ROOT/'tools/fonts/title_candidates/OFL.txt'
STAGE=ROOT/'staging/grpe_title_logo_korean_v1_assets'
AUDIT=ROOT/'audit/grpe_title_logo_korean_v1_build.json'
TEXT_TOP='\ud398\uc5b4\ub9ac\ud14c\uc77c'
TEXT_BOTTOM='\ub808\ud034\uc5e0'
ROIS={'top':(255,150,590,232),'bottom':(315,215,590,290)}
DONOR_XY={'top':(120,340),'bottom':(120,340)}

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def run(*args):
 return subprocess.run([str(x) for x in args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
def fit(fontp,text,maxw,maxh,start=90):
 for sz in range(start,15,-1):
  f=ImageFont.truetype(str(fontp),sz);b=f.getbbox(text)
  if b[2]-b[0]<=maxw and b[3]-b[1]<=maxh:return f
 raise RuntimeError(text)
def bez(draw,pts,fill,width=2):
 p=np.array(pts,float); arr=[]
 for t in np.linspace(0,1,50):arr.append(tuple(((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]).tolist()))
 draw.line(arr,fill=fill,width=width,joint='curve')
def extract_entry(arc:xfl_tool.Archive,name:str,out:Path):
 e=next(e for e in arc.entries if e.name==name)
 with arc.source.open('rb') as f:f.seek(e.absolute_offset);data=f.read(e.size)
 if len(data)!=e.size:raise RuntimeError('short read '+name)
 out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
def render(source:Image.Image,donor:Image.Image):
 S=np.array(source.convert('RGB'));D=np.array(donor.convert('RGB'));h,w=S.shape[:2]
 # One coherent blank paper slab covers the complete title-face interior.  This is
 # deliberately not a connected-component patch quilt.
 x0,y0,x1,y1=226,137,605,306;dx,dy=120,340
 patch=D[dy:dy+(y1-y0),dx:dx+(x1-x0)].copy()
 if patch.shape[:2]!=(y1-y0,x1-x0):raise RuntimeError('coherent donor slab bounds')
 mask=np.zeros((h,w),np.uint8)
 poly=np.array([[240,150],[582,150],[596,157],[597,282],[589,296],[241,296],[236,284],[236,158]],np.int32)
 cv2.fillPoly(mask,[poly],255)
 # Preserve the source star, ribbon, English subtitle, and their complete outlines.
 cv2.rectangle(mask,(250,240),(315,309),0,-1)
 hsv=cv2.cvtColor(S,cv2.COLOR_RGB2HSV);rr=np.zeros((h,w),np.uint8);rx0,ry0,rx1,ry1=(370,272,610,337)
 sub=hsv[ry0:ry1,rx0:rx1];red=((sub[:,:,1]>75)&((sub[:,:,0]<18)|(sub[:,:,0]>170))&(sub[:,:,2]>45)).astype(np.uint8)*255
 n,labels,stats,_=cv2.connectedComponentsWithStats(red,8)
 if n>1:red=(labels==(1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA])))).astype(np.uint8)*255
 red=cv2.dilate(red,np.ones((11,11),np.uint8),iterations=1);rr[ry0:ry1,rx0:rx1]=red;mask[rr>0]=0
 # Match the clean paper to this frame's authored parchment tone in Lab.
 gray=cv2.cvtColor(S,cv2.COLOR_RGB2GRAY);bg=(mask>0)&(gray>185)&(hsv[:,:,1]<75)
 if int(bg.sum())<1000:raise RuntimeError('insufficient paper reference pixels')
 pl=cv2.cvtColor(patch,cv2.COLOR_RGB2LAB).astype(np.float32);tl=cv2.cvtColor(S,cv2.COLOR_RGB2LAB).astype(np.float32)
 pm,ps=pl.reshape(-1,3).mean(0),pl.reshape(-1,3).std(0)+1;tm,ts=tl[bg].mean(0),tl[bg].std(0)+1
 adj=cv2.cvtColor(np.clip((pl-pm)*(ts/ps)+tm,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB)
 clean=S.copy();soft=cv2.GaussianBlur(mask,(0,0),0.8).astype(np.float32)/255
 r=clean[y0:y1,x0:x1].astype(np.float32);clean[y0:y1,x0:x1]=np.clip(r*(1-soft[y0:y1,x0:x1,None])+adj*soft[y0:y1,x0:x1,None],0,255).astype(np.uint8)
 clean_img=Image.fromarray(clean,'RGB');canvas=clean_img.copy();draw=ImageDraw.Draw(canvas);ink=(55,51,52)
 f1=fit(FONT,TEXT_TOP,310,64,92);f2=fit(FONT,TEXT_BOTTOM,235,64,96)
 draw.text((425,184),TEXT_TOP,font=f1,fill=ink,anchor='mm');draw.text((458,251),TEXT_BOTTOM,font=f2,fill=ink,anchor='mm')
 bez(draw,[(272,206),(257,218),(267,224),(279,216)],ink,2);bez(draw,[(558,204),(579,203),(580,188),(570,187)],ink,2);bez(draw,[(552,274),(575,286),(580,272),(570,268)],ink,2)
 # Restore the complete source ribbon component after target typesetting so the
 # decorative flourish cannot alter even antialiased ribbon/outline pixels.
 canvas_rgb=np.array(canvas.convert('RGB'));canvas_rgb[rr>0]=S[rr>0];canvas=Image.fromarray(canvas_rgb,'RGB')
 src=np.array(source.convert('RGBA'));dst=np.array(canvas.convert('RGBA'));owned=np.any(src!=dst,axis=2);ys,xs=np.where(owned)
 return clean_img,canvas,owned,{'font_top_size':f1.size,'font_bottom_size':f2.size,'background_strategy':'single_coherent_source_authored_slab','no_patch_quilt':True,'donor_slabs':{'interior':{'source':str(DONOR),'x':dx,'y':dy,'width':x1-x0,'height':y1-y0}},'protected':{'star_dark_component':'source-exact','ribbon_and_outline_component':'source-exact after target typesetting','border':'outside interior polygon exact'},'owned_pixels':int(owned.sum()),'owned_bbox':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]}
def write_archive(source:Path,arc:xfl_tool.Archive,replacements:dict[str,bytes],out:Path):
 sizes={e.name:len(replacements[e.name]) if e.name in replacements else e.size for e in arc.entries};out.parent.mkdir(parents=True,exist_ok=True)
 with source.open('rb') as src,out.open('wb') as dst:
  dst.write(xfl_tool.MAGIC);dst.write(struct.pack('<II',len(arc.entries)*xfl_tool.ENTRY_SIZE,len(arc.entries)));off=0
  for e in arc.entries:dst.write(e.raw_name);dst.write(struct.pack('<II',off,sizes[e.name]));off+=sizes[e.name]
  for e in arc.entries:
   if e.name in replacements:dst.write(replacements[e.name]);continue
   src.seek(e.absolute_offset);left=e.size
   while left:
    b=src.read(min(8*1024*1024,left))
    if not b:raise RuntimeError('short copy '+e.name)
    dst.write(b);left-=len(b)
def archive_delta(source:Path,candidate:Path):
 a=xfl_tool.parse_archive(source);b=xfl_tool.parse_archive(candidate);changes=[]
 if [e.name for e in a.entries]!=[e.name for e in b.entries]:raise RuntimeError('entry order drift')
 with source.open('rb') as fa,candidate.open('rb') as fb:
  for ea,eb in zip(a.entries,b.entries):
   fa.seek(ea.absolute_offset);fb.seek(eb.absolute_offset);ha=hashlib.sha256(fa.read(ea.size)).digest();hb=hashlib.sha256(fb.read(eb.size)).digest()
   if ha!=hb:changes.append(ea.name)
 return changes

def main():
 if sha(SOURCE)!=SOURCE_SHA:raise RuntimeError('frozen integrated grpe source mismatch')
 if STAGE.exists():shutil.rmtree(STAGE)
 STAGE.mkdir(parents=True);arc=xfl_tool.parse_archive(SOURCE)
 src_lwg=STAGE/'source/9101.lwg';extract_entry(arc,'9101.lwg',src_lwg)
 if sha(src_lwg)!=SOURCE_LWG_SHA:raise RuntimeError('9101 source mismatch')
 src_frames=STAGE/'source/frames';run(TOOL,'lwg-extract-png',src_lwg,src_frames)
 pngs=sorted(src_frames.glob('*.png'))
 if len(pngs)!=8:raise RuntimeError('9101 state closure not 8')
 frames=[Image.open(p).convert('RGBA') for p in pngs]
 # 9101 is an eight-frame title animation. The logo is stable, but the surrounding
 # art changes by state, so clean and typeset every frame independently.
 state_deltas=[];base=np.array(frames[0])
 for p0,im in zip(pngs,frames):
  a=np.array(im);d=np.any(a!=base,axis=2);state_deltas.append({'state':p0.name,'pixels_vs_frame_0':int(d.sum())})
 rendered=[];donor=Image.open(DONOR).convert('RGB')
 for p0,im in zip(pngs,frames):
  clean,candidate,owned,detail=render(im,donor);rendered.append({'name':p0.name,'source':im,'clean':clean,'candidate':candidate,'owned':owned,'detail':detail})
 ev=STAGE/'evidence';ev.mkdir();rep=rendered[0]
 rep['clean'].save(ev/'clean_plate.png');rep['candidate'].save(ev/'candidate_full.png');rep['source'].crop((190,105,620,345)).save(ev/'source_logo_crop.png');rep['clean'].crop((190,105,620,345)).save(ev/'clean_logo_crop.png');rep['candidate'].crop((190,105,620,345)).save(ev/'candidate_logo_crop.png')
 union_owned=np.logical_or.reduce([r['owned'] for r in rendered]);Image.fromarray((union_owned*255).astype(np.uint8)).save(ev/'owned_mask.png')
 clean_checks={}
 for idx,r in enumerate(rendered):
  r['clean'].save(ev/f'clean_{idx:02d}.png');r['candidate'].save(ev/f'candidate_{idx:02d}.png');Image.fromarray((r['owned']*255).astype(np.uint8)).save(ev/f'owned_mask_{idx:02d}.png')
  clean_arr=np.array(r['clean']);source_arr=np.array(r['source'].convert('RGB'));state_checks={}
  for key,(x0,y0,x1,y1) in ROIS.items():
   src_gray=cv2.cvtColor(source_arr[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY);cln_gray=cv2.cvtColor(clean_arr[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY);mask=r['owned'][y0:y1,x0:x1]
   state_checks[key]={'source_dark_owned_pixels':int(((src_gray<170)&mask).sum()),'clean_dark_owned_pixels':int(((cln_gray<170)&mask).sum())}
  clean_checks[r['name']]=state_checks
 cand_dir=STAGE/'candidate_frames';shutil.copytree(src_frames,cand_dir)
 rendered_by_name={r['name']:r for r in rendered}
 for p0 in cand_dir.glob('*.png'):rendered_by_name[p0.name]['candidate'].save(p0)
 lwg_a=STAGE/'build_a/9101.ko-title-logo-v1.lwg';lwg_b=STAGE/'build_b/9101.ko-title-logo-v1.lwg';lwg_a.parent.mkdir();lwg_b.parent.mkdir();run(TOOL,'lwg-pack-png',cand_dir,lwg_a);run(TOOL,'lwg-pack-png',cand_dir,lwg_b)
 if sha(lwg_a)!=sha(lwg_b):raise RuntimeError('LWG A/B mismatch')
 control_lwg=STAGE/'control/9101.roundtrip.lwg';control_lwg.parent.mkdir();run(TOOL,'lwg-roundtrip',src_lwg,control_lwg)
 dirs={}
 for n,p in [('control',control_lwg),('a',lwg_a),('b',lwg_b)]:
  d=STAGE/f'persisted_{n}';run(TOOL,'lwg-extract-png',p,d);dirs[n]=d
 control_pngs=sorted(dirs['control'].glob('*.png'));a_pngs=sorted(dirs['a'].glob('*.png'));b_pngs=sorted(dirs['b'].glob('*.png'))
 state_names=[p.name for p in src_frames.glob('*.png')]
 if sorted(state_names)!=sorted(p.name for p in a_pngs):raise RuntimeError('persisted state names drift')
 persisted=[]
 for ca,aa,bb in zip(control_pngs,a_pngs,b_pngs):
  c=np.array(Image.open(ca).convert('RGBA'));a=np.array(Image.open(aa).convert('RGBA'));b=np.array(Image.open(bb).convert('RGBA'));owned=rendered_by_name[aa.name]['owned']
  persisted.append({'state':aa.name,'dimensions':list(Image.open(aa).size),'a_b_pixels_exact':bool(np.array_equal(a,b)),'protected_exact_vs_control':bool(np.array_equal(a[~owned],c[~owned])),'alpha_exact_vs_control':bool(np.array_equal(a[:,:,3],c[:,:,3]))})
 if not all(x['a_b_pixels_exact'] and x['protected_exact_vs_control'] and x['alpha_exact_vs_control'] for x in persisted):raise RuntimeError('persisted pixel contract failed')
 outs=[]
 for tag,lwg in [('a',lwg_a),('b',lwg_b)]:
  out=ROOT/f'staging/grpe_title_logo_korean_v1_{tag}/grpe.ko-gallery-title-logo-v1.xfl';write_archive(SOURCE,arc,{'9101.lwg':lwg.read_bytes()},out);outs.append({'tag':tag,'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'delta_entries':archive_delta(SOURCE,out)})
 if outs[0]['sha256']!=outs[1]['sha256'] or outs[0]['delta_entries']!=['9101.lwg'] or outs[1]['delta_entries']!=['9101.lwg']:raise RuntimeError('grpe archive contract failed')
 report={'schema':'fairytale-requiem-grpe-title-logo-korean-build-v1','status':'PASS_STATIC_RUNTIME_PENDING','completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'source':{'path':str(SOURCE),'sha256':sha(SOURCE),'entry_count':len(arc.entries),'inherits_gallery_headers_v1':True},'consumer':{'entry':'9101.lwg','state_count':8,'source_states_pixel_identical':False,'source_states_distinct_preserved':True,'state_deltas':state_deltas,'all_states_localized':True},'translation':{'top':TEXT_TOP,'bottom':TEXT_BOTTOM,'preserved':['ornate plaque border','four-point star','Fairytale Requiem English ribbon','screen geometry','eight-frame title animation']},'font':{'path':str(FONT),'sha256':sha(FONT),'license':str(FONT_LICENSE)},'source_lwg':{'path':str(src_lwg),'sha256':sha(src_lwg),'bytes':src_lwg.stat().st_size},'candidate_lwg_a':{'path':str(lwg_a),'sha256':sha(lwg_a),'bytes':lwg_a.stat().st_size},'candidate_lwg_b':{'path':str(lwg_b),'sha256':sha(lwg_b),'bytes':lwg_b.stat().st_size},'lwg_a_b_byte_identical':sha(lwg_a)==sha(lwg_b),'typesetting':rep['detail'],'clean_plate_checks':clean_checks,'persisted_states':persisted,'outputs':outs,'checks':{'source_frozen':sha(SOURCE)==SOURCE_SHA,'only_9101_lwg_changed':all(o['delta_entries']==['9101.lwg'] for o in outs),'grpe_a_b_byte_identical':outs[0]['sha256']==outs[1]['sha256'],'all_states_closed':len(persisted)==8,'source_states_distinct_preserved':len({hashlib.sha256(np.array(r['candidate']).tobytes()).hexdigest() for r in rendered})==8,'all_persisted_pixel_contracts':all(x['a_b_pixels_exact'] and x['protected_exact_vs_control'] and x['alpha_exact_vs_control'] for x in persisted)},'runtime_status':'pending_user_review'}
 AUDIT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':report['status'],'sha256':outs[0]['sha256'],'changed':['9101.lwg'],'lwg_sha256':sha(lwg_a),'font_sizes':[detail['font_top_size'],detail['font_bottom_size']]},ensure_ascii=False))
if __name__=='__main__':main()

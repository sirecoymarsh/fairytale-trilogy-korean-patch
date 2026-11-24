#!/usr/bin/env python3
from __future__ import annotations
import argparse,ctypes,hashlib,importlib.util,json,time
from ctypes import wintypes
from pathlib import Path
import cv2,numpy as np

def load(path:Path):
 spec=importlib.util.spec_from_file_location('cap',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def match(image,t):
 a=cv2.cvtColor(np.asarray(image.convert('RGB')),cv2.COLOR_RGB2BGR)[27:747,1:1281]
 b=cv2.cvtColor(t[:,:,:3],cv2.COLOR_RGB2BGR); mask=((t[:,:,3]>=200)*255).astype(np.uint8)
 r=cv2.matchTemplate(a,b,cv2.TM_SQDIFF_NORMED,mask=mask); v,_,loc,_=cv2.minMaxLoc(r); return float(v),[int(loc[0]),int(loc[1])]

def sha(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest().upper()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--pid',type=int,required=True); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--helper',type=Path,required=True); a=ap.parse_args(); project=a.project.resolve(); root=a.root.resolve(); cap=load(a.helper.resolve()); hwnd=cap.unique_window(a.pid,5)
 steps=[]; templates=[]; td=project/'staging'/'ui_master_component_donor'/'decoded_png'
 for i in range(1,9):
  t=cv2.imread(str(td/f'{i:04d}.png'),cv2.IMREAD_UNCHANGED); t=cv2.cvtColor(t,cv2.COLOR_BGRA2RGBA); templates.append(t)
 found=False; final=None
 for i in range(35):
  image,printed=cap.capture_window(hwnd); score,xy=match(image,templates[0]); steps.append({'step':i,'start_score':score,'start_xy':xy,'print_window':printed})
  if score<0.003: found=True; final=image; break
  cap.send_key(hwnd,'enter'); time.sleep(1.4)
 if not found: raise RuntimeError(f'title not found best={min(s["start_score"] for s in steps)}')
 matches=[]
 for i,t in enumerate(templates,1):
  score,xy=match(final,t); matches.append({'asset':f'{i:04d}','score':score,'top_left':xy,'client_center':[xy[0]+75,xy[1]+75]})
 outdir=project/'evidence'/'runtime'/'final_ko_rc1'; outdir.mkdir(parents=True,exist_ok=True); out=outdir/'rc1_title_menu_printwindow.png'; final.save(out)
 report={'schema':'fairytale-requiem-title-menu-runtime-rc1-v1','status':'PASS_TITLE_DETECTED','pid':a.pid,'hwnd':hwnd,'candidate_root':str(root),'steps':steps,'menu_matches':matches,'capture':str(out),'capture_sha256':sha(out)}
 rp=project/'audit'/'final_ko_rc1_title_menu_runtime.json'; rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':report['status'],'pid':a.pid,'steps':len(steps),'menu_matches':matches,'capture':str(out),'report':str(rp)},ensure_ascii=True,indent=2))
if __name__=='__main__': main()

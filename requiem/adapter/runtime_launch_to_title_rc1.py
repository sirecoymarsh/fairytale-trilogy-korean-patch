#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image

def load(path:Path):
 spec=importlib.util.spec_from_file_location('cap',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def sha(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest().upper()
def match_content(image,t):
 a=cv2.cvtColor(np.asarray(image.convert('RGB')),cv2.COLOR_RGB2BGR)[27:747,1:1281]; b=t[:,:,:3]; mask=((t[:,:,3]>=200)*255).astype(np.uint8)
 r=cv2.matchTemplate(a,b,cv2.TM_SQDIFF_NORMED,mask=mask); v,_,loc,_=cv2.minMaxLoc(r); return float(v),[int(loc[0]),int(loc[1])]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--helper',type=Path,required=True); a=ap.parse_args(); project=a.project.resolve(); root=a.root.resolve(); cap=load(a.helper.resolve())
 exes=[p for p in root.glob('*.exe') if p.name.lower()!='fr_patch_v1_1.exe'];
 if len(exes)!=1: raise RuntimeError(exes)
 exe=exes[0]; proc=subprocess.Popen([str(exe)],cwd=str(root)); template=project/'staging'/'ui_master_component_donor'/'decoded_png'/'0001.png'; steps=[]; final=None; hwnd=None
 for i in range(45):
  if proc.poll() is not None: raise RuntimeError(f'game exited before title, code={proc.returncode}, step={i}')
  try: hwnd=cap.unique_window(proc.pid,3)
  except Exception as e:
   steps.append({'step':i,'window':'transient_missing','error':str(e)}); time.sleep(.7); continue
  try: image,printed=cap.capture_window(hwnd)
  except OSError as e:
   steps.append({'step':i,'window':'stale_handle','hwnd':hwnd,'error':str(e)}); time.sleep(.5); continue
  score,xy=cap.match_template(image,template); steps.append({'step':i,'hwnd':hwnd,'score':score,'xy':xy,'print_window':printed})
  if score<0.003: final=image; break
  cap.send_key(hwnd,'enter'); time.sleep(1.35)
 if final is None: raise RuntimeError(f'title not found, best={min([s.get("score",99) for s in steps])}')
 td=project/'staging'/'ui_master_component_donor'/'decoded_png'; matches=[]
 for i in range(1,9):
  t=cv2.imread(str(td/f'{i:04d}.png'),cv2.IMREAD_UNCHANGED); sc,xy=match_content(final,t); matches.append({'asset':f'{i:04d}','score':sc,'top_left':xy,'client_center':[xy[0]+75,xy[1]+75]})
 outdir=project/'evidence'/'runtime'/'final_ko_rc1'; outdir.mkdir(parents=True,exist_ok=True); out=outdir/'rc1_title_menu_runtime.png'; final.save(out)
 report={'schema':'fairytale-requiem-launch-to-title-rc1-v1','status':'PASS_TITLE_DETECTED','pid':proc.pid,'hwnd':hwnd,'candidate_root':str(root),'executable':str(exe),'executable_sha256':sha(exe),'steps':steps,'menu_matches':matches,'capture':str(out),'capture_sha256':sha(out),'process_running':proc.poll() is None}
 rp=project/'audit'/'final_ko_rc1_launch_to_title.json'; rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':report['status'],'pid':proc.pid,'hwnd':hwnd,'step_count':len(steps),'menu_matches':matches,'capture':str(out),'report':str(rp),'process_running':report['process_running']},ensure_ascii=True,indent=2))
if __name__=='__main__': main()

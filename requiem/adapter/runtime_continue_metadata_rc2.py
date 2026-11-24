from __future__ import annotations
import argparse,cv2,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
import numpy as np

def load(path:Path):
 spec=importlib.util.spec_from_file_location('cap',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def masked_match(screen_rgb:np.ndarray,template_path:Path):
 t=cv2.imread(str(template_path),cv2.IMREAD_UNCHANGED)
 if t is None or t.shape[2]!=4:raise RuntimeError(template_path)
 s=cv2.cvtColor(screen_rgb,cv2.COLOR_RGB2BGR);rgb=t[:,:,:3];mask=((t[:,:,3]>=180)*255).astype(np.uint8)
 r=cv2.matchTemplate(s,rgb,cv2.TM_SQDIFF_NORMED,mask=mask);v,_,loc,_=cv2.minMaxLoc(r)
 return {'score':float(v),'top_left':[int(loc[0]),int(loc[1])],'template':str(template_path),'template_sha256':sha(template_path)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--helper',type=Path,required=True);a=ap.parse_args();P=a.project.resolve();root=a.root.resolve();cap=load(a.helper.resolve())
 exes=[p for p in root.glob('*.exe') if p.name.lower()!='fr_patch_v1_1.exe']
 if len(exes)!=1:raise RuntimeError(exes)
 proc=subprocess.Popen([str(exes[0])],cwd=str(root));steps=[];hwnd=None;title=None
 try:
  for i in range(45):
   if proc.poll() is not None:raise RuntimeError(f'exited before title code={proc.returncode}')
   try:hwnd=cap.unique_window(proc.pid,3);im,printed=cap.capture_window(hwnd)
   except Exception as e:steps.append({'step':i,'error':str(e)});time.sleep(.6);continue
   score,xy=cap.match_template(im,P/'staging'/'ui_master_component_donor'/'decoded_png'/'0001.png');steps.append({'step':i,'score':score,'xy':xy,'print_window':printed})
   if score<.003:title=im;break
   cap.send_key(hwnd,'enter');time.sleep(1.35)
  if title is None:raise RuntimeError('title not detected')
  cap.click(hwnd,972,236);time.sleep(2.2)
  screen,printed=cap.capture_window(hwnd);outdir=P/'evidence'/'runtime'/'final_ko_rc2'/'save_load_metadata';outdir.mkdir(parents=True,exist_ok=True);out=outdir/'rc2_continue_screen.png';screen.save(out)
  arr=np.asarray(screen.convert('RGB'))
  pairs=[]
  for stem in ('dt1_1101','dt2_0011'):
   jp=P/'staging'/'grps_save_metadata_korean_v1_source'/'png'/f'{stem}.png'
   ko=P/'staging'/'grps_save_metadata_korean_v1_a'/'persisted_png'/f'{stem}.png'
   pairs.append({'asset':stem,'japanese':masked_match(arr,jp),'korean':masked_match(arr,ko)})
  status='PASS_KOREAN_METADATA_RUNTIME' if all(x['korean']['score']<x['japanese']['score']*.25 and x['korean']['score']<.02 for x in pairs) else 'FAIL_METADATA_RUNTIME_MATCH'
  report={'schema':'fairytale-requiem-rc2-continue-metadata-runtime-v1','status':status,'candidate_root':str(root),'pid':proc.pid,'hwnd':hwnd,'title_steps':steps,'action':{'type':'click_continue','client_xy':[972,236]},'capture':str(out),'capture_sha256':sha(out),'print_window':printed,'matches':pairs}
  rp=P/'audit'/'final_ko_rc2_continue_metadata_runtime.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({'status':status,'pid':proc.pid,'capture':str(out),'matches':pairs,'report':str(rp)},ensure_ascii=True,indent=2))
  if not status.startswith('PASS'):raise SystemExit(2)
 finally:
  if proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=5)
   except:proc.kill();proc.wait(timeout=5)
if __name__=='__main__':main()

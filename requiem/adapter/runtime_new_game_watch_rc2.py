#!/usr/bin/env python3
from __future__ import annotations
import argparse,ctypes,hashlib,json,subprocess,time
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab
U=ctypes.windll.user32;KEYUP=2;VK_RETURN=0x0D

def sha(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def txt(h):
 n=U.GetWindowTextLengthW(h);b=ctypes.create_unicode_buffer(n+1);U.GetWindowTextW(h,b,len(b));return b.value
def cls(h):
 b=ctypes.create_unicode_buffer(256);U.GetClassNameW(h,b,len(b));return b.value
def children(h):
 out=[];CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(ch,l):out.append({'hwnd':int(ch),'class':cls(ch),'text':txt(ch),'visible':bool(U.IsWindowVisible(ch))});return True
 U.EnumChildWindows(h,cb,0);return out
def wins(pid):
 out=[];CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(h,l):
  p=wintypes.DWORD();U.GetWindowThreadProcessId(h,ctypes.byref(p))
  if p.value==pid and U.IsWindowVisible(h):out.append({'hwnd':int(h),'class':cls(h),'title':txt(h),'children':children(h)})
  return True
 U.EnumWindows(cb,0);return out
def capture(h,p):
 r=wintypes.RECT();U.GetWindowRect(h,ctypes.byref(r));img=ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom),all_screens=True);img.save(p);return {'path':str(p),'sha256':sha(p),'bbox':[r.left,r.top,r.right,r.bottom]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--max-actions',type=int,default=120);ap.add_argument('--delay',type=float,default=.8);a=ap.parse_args();project=a.project.resolve();root=a.root.resolve()
 exes=[p for p in root.glob('*.exe') if p.name.lower()!='fr_patch_v1_1.exe']
 if len(exes)!=1:raise RuntimeError(exes)
 exe=exes[0];proc=subprocess.Popen([str(exe)],cwd=str(root));outdir=project/'evidence'/'runtime'/'final_ko_rc2'/'new_game_error_watch';outdir.mkdir(parents=True,exist_ok=True)
 records=[];failure=None;checkpoints={0,1,2,5,10,11,12,20,40,60,80,100,a.max_actions}
 try:
  for step in range(a.max_actions+1):
   deadline=time.monotonic()+15;state=[]
   while time.monotonic()<deadline:
    if proc.poll() is not None:break
    state=wins(proc.pid)
    if state:break
    time.sleep(.2)
   if proc.poll() is not None:
    failure={'kind':'PROCESS_EXITED','step':step,'exit_code':proc.returncode};break
   modals=[w for w in state if w['class']=='#32770'];mains=[w for w in state if w['class']=='RosGameClass']
   rec={'step':step,'visible_modal_count':len(modals),'window_classes':[w['class'] for w in state]}
   if mains and (step in checkpoints or modals):rec['main_capture']=capture(mains[0]['hwnd'],outdir/f'step_{step:03d}_main.png')
   if modals:
    rec['modal']=modals[0];rec['modal_capture']=capture(modals[0]['hwnd'],outdir/f'step_{step:03d}_modal.png');failure={'kind':'ERROR_MODAL','step':step,'modal':modals[0]};records.append(rec);break
   records.append(rec)
   if step==a.max_actions:break
   if not mains:
    failure={'kind':'MAIN_WINDOW_MISSING','step':step,'windows':state};break
   h=mains[0]['hwnd'];U.SetForegroundWindow(h);time.sleep(.08);U.keybd_event(VK_RETURN,0,0,0);time.sleep(.06);U.keybd_event(VK_RETURN,0,KEYUP,0);time.sleep(a.delay)
 finally:
  was_running=proc.poll() is None
  if was_running:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
 status='PASS_NO_ERROR_MODAL' if failure is None and len(records)==a.max_actions+1 else 'FAIL'
 report={'schema':'fairytale-requiem-runtime-new-game-error-watch-rc2-v1','created_at_unix':time.time(),'status':status,'candidate_root':str(root),'executable':str(exe),'executable_sha256':sha(exe),'pid':proc.pid,'requested_actions':a.max_actions,'completed_actions':records[-1]['step'] if records else 0,'delay_seconds':a.delay,'failure':failure,'records':records,'process_terminated_after_test':True}
 rp=project/'audit'/'final_ko_rc2_new_game_error_watch.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':status,'pid':proc.pid,'completed_actions':report['completed_actions'],'modal_count':sum(x['visible_modal_count'] for x in records),'failure':failure,'report':str(rp),'evidence_root':str(outdir)},ensure_ascii=True,indent=2))
 if status!='PASS_NO_ERROR_MODAL':raise SystemExit(2)
if __name__=='__main__':main()

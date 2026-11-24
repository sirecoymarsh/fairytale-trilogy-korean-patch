#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, hashlib, json, time
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab
U=ctypes.windll.user32; K=ctypes.windll.kernel32
PROCESS_QUERY_LIMITED_INFORMATION=0x1000; KEYEVENTF_KEYUP=2; VK_RETURN=0x0D

def sha(path:Path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest().upper()

def proc_path(pid:int)->Path:
 h=K.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,False,pid)
 if not h: raise ctypes.WinError()
 try:
  n=wintypes.DWORD(32768); b=ctypes.create_unicode_buffer(n.value)
  if not K.QueryFullProcessImageNameW(h,0,b,ctypes.byref(n)): raise ctypes.WinError()
  return Path(b.value).resolve()
 finally: K.CloseHandle(h)

def text(hwnd:int)->str:
 n=U.GetWindowTextLengthW(hwnd); b=ctypes.create_unicode_buffer(n+1); U.GetWindowTextW(hwnd,b,len(b)); return b.value

def cls(hwnd:int)->str:
 b=ctypes.create_unicode_buffer(256); U.GetClassNameW(hwnd,b,len(b)); return b.value

def windows()->list[dict]:
 out=[]; CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(hwnd,_):
  if U.IsWindowVisible(hwnd):
   p=wintypes.DWORD(); U.GetWindowThreadProcessId(hwnd,ctypes.byref(p))
   out.append({'hwnd':int(hwnd),'pid':int(p.value),'class':cls(hwnd),'title':text(hwnd)})
  return True
 U.EnumWindows(cb,0); return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--pid',type=int,required=True); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--steps',type=int,default=12); a=ap.parse_args()
 project=a.project.resolve(); root=a.root.resolve(); exe=proc_path(a.pid)
 try: exe.relative_to(root)
 except ValueError: raise RuntimeError(f'wrong executable {exe}')
 mainwins=[w for w in windows() if w['pid']==a.pid and w['class']=='RosGameClass']
 if len(mainwins)!=1: raise RuntimeError(f'expected one RosGameClass: {mainwins}')
 hwnd=mainwins[0]['hwnd']; outdir=project/'evidence'/'runtime'/'final_ko_rc1'/'error_watch'; outdir.mkdir(parents=True,exist_ok=True)
 records=[]; failure=None
 for i in range(a.steps+1):
  visible=windows(); modals=[w for w in visible if w['class']=='#32770' and w['pid']==a.pid]
  r=wintypes.RECT(); U.GetWindowRect(hwnd,ctypes.byref(r)); U.SetForegroundWindow(hwnd); time.sleep(.25)
  img=ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom),all_screens=True); cap=outdir/f'step_{i:02d}.png'; img.save(cap)
  rec={'step':i,'visible_modal_count':len(modals),'visible_modals':modals,'capture':str(cap),'capture_sha256':sha(cap)}; records.append(rec)
  if modals:
   failure={'step':i,'modals':modals}; break
  if i==a.steps: break
  U.SetForegroundWindow(hwnd); time.sleep(.08); U.keybd_event(VK_RETURN,0,0,0); time.sleep(.08); U.keybd_event(VK_RETURN,0,KEYEVENTF_KEYUP,0); time.sleep(1.35)
 status='PASS_NO_ERROR_MODAL' if failure is None and len(records)==a.steps+1 else 'FAIL_MODAL_DETECTED'
 report={'schema':'fairytale-requiem-runtime-error-watch-rc1-v1','created_at_unix':time.time(),'status':status,'pid':a.pid,'hwnd':hwnd,'candidate_root':str(root),'executable':str(exe),'executable_sha256':sha(exe),'requested_steps':a.steps,'completed_actions':len(records)-1,'failure':failure,'records':records}
 out=project/'audit'/'final_ko_rc1_runtime_error_watch.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':status,'completed_actions':report['completed_actions'],'modal_count':sum(x['visible_modal_count'] for x in records),'report':str(out),'last_capture':records[-1]['capture']},ensure_ascii=True,indent=2))
 if failure: raise SystemExit(2)
if __name__=='__main__': main()


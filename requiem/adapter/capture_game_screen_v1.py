#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, hashlib, json, time, sys
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab

sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
USER32=ctypes.windll.user32
KERNEL32=ctypes.windll.kernel32
PROCESS_QUERY_LIMITED_INFORMATION=0x1000

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest().upper()

def windows_for_pid(pid:int)->list[int]:
 out=[]; CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(hwnd,_):
  p=wintypes.DWORD(); USER32.GetWindowThreadProcessId(hwnd,ctypes.byref(p))
  if p.value==pid and USER32.IsWindowVisible(hwnd): out.append(int(hwnd))
  return True
 USER32.EnumWindows(cb,0); return out

def process_path(pid:int)->Path:
 h=KERNEL32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,False,pid)
 if not h: raise ctypes.WinError()
 try:
  cap=wintypes.DWORD(32768); buf=ctypes.create_unicode_buffer(cap.value)
  if not KERNEL32.QueryFullProcessImageNameW(h,0,buf,ctypes.byref(cap)): raise ctypes.WinError()
  return Path(buf.value).resolve()
 finally: KERNEL32.CloseHandle(h)

def title(hwnd:int)->str:
 n=USER32.GetWindowTextLengthW(hwnd); b=ctypes.create_unicode_buffer(n+1); USER32.GetWindowTextW(hwnd,b,len(b)); return b.value

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--pid',type=int,required=True); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--expected-root',type=Path,required=True); ap.add_argument('--name',required=True); ap.add_argument('--wait',type=float,default=.6); a=ap.parse_args()
 project=a.project.resolve(); root=a.expected_root.resolve(); exe=process_path(a.pid)
 try: exe.relative_to(root)
 except ValueError: raise RuntimeError(f'PID executable is outside expected root: {exe}')
 wins=windows_for_pid(a.pid)
 if len(wins)!=1: raise RuntimeError(f'expected exactly one visible window for PID {a.pid}: {wins}')
 hwnd=wins[0]; USER32.SetForegroundWindow(hwnd); time.sleep(a.wait)
 r=wintypes.RECT()
 if not USER32.GetWindowRect(hwnd,ctypes.byref(r)): raise ctypes.WinError()
 bbox=(r.left,r.top,r.right,r.bottom)
 img=ImageGrab.grab(bbox=bbox,all_screens=True)
 evidence=project/'evidence'/'runtime'/'final_ko_rc1'; evidence.mkdir(parents=True,exist_ok=True)
 out=evidence/f'{a.name}.png'; img.save(out)
 rec={'schema':'fairytale-requiem-runtime-screen-observation-v1','created_at_unix':time.time(),'name':a.name,'pid':a.pid,'hwnd':hwnd,'window_title':title(hwnd),'window_bbox':list(bbox),'window_dimensions':list(img.size),'executable':str(exe),'executable_sha256':sha256(exe),'candidate_root':str(root),'capture':str(out),'capture_sha256':sha256(out),'capture_method':'foreground_screen_bbox'}
 log=project/'audit'/'final_ko_rc1_runtime_screen_observations.jsonl'
 with log.open('a',encoding='utf-8',newline='\n') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
 print(json.dumps(rec,ensure_ascii=False,indent=2))
if __name__=='__main__': main()


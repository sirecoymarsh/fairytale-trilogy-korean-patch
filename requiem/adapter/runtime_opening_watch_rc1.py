#!/usr/bin/env python3
from __future__ import annotations
import argparse,ctypes,hashlib,json,subprocess,time
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab,Image,ImageDraw
U=ctypes.windll.user32

def sha(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest().upper()
def wins(pid:int):
 out=[]; CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(hwnd,_):
  p=wintypes.DWORD(); U.GetWindowThreadProcessId(hwnd,ctypes.byref(p))
  if p.value==pid and U.IsWindowVisible(hwnd): out.append(int(hwnd))
  return True
 U.EnumWindows(cb,0); return out
def children(hwnd:int):
 out=[]; CB=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 @CB
 def cb(ch,_):
  b=ctypes.create_unicode_buffer(256); U.GetClassNameW(ch,b,len(b)); n=U.GetWindowTextLengthW(ch); t=ctypes.create_unicode_buffer(n+1); U.GetWindowTextW(ch,t,len(t)); out.append({'hwnd':int(ch),'class':b.value,'title':t.value,'visible':bool(U.IsWindowVisible(ch))}); return True
 U.EnumChildWindows(hwnd,cb,0); return out
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--root',type=Path,required=True); a=ap.parse_args(); project=a.project.resolve(); root=a.root.resolve()
 exes=[p for p in root.glob('*.exe') if p.name.lower()!='fr_patch_v1_1.exe']
 if len(exes)!=1: raise RuntimeError(exes)
 exe=exes[0]; proc=subprocess.Popen([str(exe)],cwd=str(root)); deadline=time.monotonic()+45; hwnd=None
 while time.monotonic()<deadline:
  w=wins(proc.pid)
  if len(w)==1: hwnd=w[0]; break
  if len(w)>1: raise RuntimeError(w)
  time.sleep(.25)
 if hwnd is None: raise RuntimeError('no game window')
 outdir=project/'evidence'/'runtime'/'final_ko_rc1'/'opening_watch'; outdir.mkdir(parents=True,exist_ok=True)
 start=time.monotonic(); targets=[2,7,12,17,22,27,32]; records=[]
 for i,target in enumerate(targets):
  delay=target-(time.monotonic()-start)
  if delay>0: time.sleep(delay)
  if proc.poll() is not None: break
  U.SetForegroundWindow(hwnd); time.sleep(.25); r=wintypes.RECT(); U.GetWindowRect(hwnd,ctypes.byref(r)); img=ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom),all_screens=True); p=outdir/f't_{target:02d}s.png'; img.save(p)
  records.append({'target_seconds':target,'actual_seconds':time.monotonic()-start,'capture':str(p),'capture_sha256':sha(p),'children':children(hwnd)})
 # contact sheet
 thumbs=[]
 for rec in records:
  im=Image.open(rec['capture']).convert('RGB'); im.thumbnail((320,190),Image.Resampling.LANCZOS); thumbs.append((rec['target_seconds'],im.copy()))
 sheet=Image.new('RGB',(640,220*((len(thumbs)+1)//2)),'white'); d=ImageDraw.Draw(sheet)
 for i,(sec,im) in enumerate(thumbs):
  x=(i%2)*320; y=(i//2)*220; d.text((x+5,y+3),f'{sec}s',fill='black'); sheet.paste(im,(x,y+25))
 contact=outdir/'opening_watch_contact.jpg'; sheet.save(contact,quality=75,optimize=True)
 report={'schema':'fairytale-requiem-opening-runtime-watch-rc1-v1','status':'CAPTURED_RUNTIME_SEQUENCE','pid':proc.pid,'hwnd':hwnd,'candidate_root':str(root),'executable':str(exe),'executable_sha256':sha(exe),'records':records,'contact':str(contact),'process_running':proc.poll() is None}
 out=project/'audit'/'final_ko_rc1_opening_runtime_watch.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':report['status'],'pid':proc.pid,'capture_count':len(records),'contact':str(contact),'report':str(out),'process_running':report['process_running']},ensure_ascii=True,indent=2))
if __name__=='__main__': main()

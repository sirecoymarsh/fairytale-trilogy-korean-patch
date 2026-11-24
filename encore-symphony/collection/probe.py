"""Observe only a newly launched edition in an isolated test folder and private desktop."""
from assemble import *
from concurrent.futures import ThreadPoolExecutor
import time,ctypes,win32gui,win32process,win32event,win32api
from trial_game import U,home,capture,click,key,windows,children
from PIL import Image
import numpy as np
def activate(h):
 tid,_=win32process.GetWindowThreadProcessId(h);me=win32api.GetCurrentThreadId();ok=U.AttachThreadInput(me,tid,True)
 try:
  U.SetForegroundWindow(h);U.SetActiveWindow(h);U.SetFocus(h)
  for m in [0x1c,6,7]:win32gui.PostMessage(h,m,0 if m==7 else 1,0)
 finally:
  if ok:U.AttachThreadInput(me,tid,False)
def fixture(w,mode):
 g=OUT/'Games'/w;d=HERE/'qa'/'Games'/w
 for p in g.rglob('*'):
  if not p.is_file():continue
  k=p.relative_to(g);dst=d/k
  if k.as_posix() in ('mov/0001.mpg','mov/0002.mpg'):
   if dst.is_file():
    assert dst.resolve().is_relative_to((HERE/'qa'/'Games').resolve()) and dst.stat().st_size==p.stat().st_size
    dst.unlink()
   continue
  if k.parts[0]=='save' or p.name=='scr.xfl':continue
  once(p,dst)
 dst=d/'save';dst.mkdir(exist_ok=True)
 for p in (g/'save').glob('*'):
  if p.is_file():shutil.copyfile(p,dst/p.name)
 shutil.copyfile((HERE/'tmp'/'bootcheck.xfl') if mode=='bootcheck' else (GAMES[w]/'scr.xfl' if mode=='native' else HERE/'qa'/'entry-archives'/w/(mode+'.xfl')),d/'scr.xfl')
 return d
def run(w,mode,seconds):
 d=fixture(w,mode);deskname='FairyCollectionCheck'+str(os.getpid())+w
 handle=U.CreateDesktopW(deskname,None,None,0,0x1ff,None);assert handle and U.SetThreadDesktop(handle)
 si=win32process.STARTUPINFO();si.lpDesktop=deskname
 pr,th,pid,_=win32process.CreateProcess(str(d/EXES[w]),None,None,None,False,0,None,str(d),si);th.Close()
 try:
  deadline=time.monotonic()+12;h=None
  while time.monotonic()<deadline and not h:
   h=home(pid);time.sleep(.1)
  assert h,(pid,windows(pid))
  activate(h);print('window',w,pid,windows(pid),flush=True)
  f=HERE/'qa'/'screens';f.mkdir(exist_ok=True);base=time.monotonic()
  for t in [1,3,6,10,15,22,35,60,100,145]:
   if t>seconds:break
   while time.monotonic()-base<t:time.sleep(.10)
   if win32process.GetExitCodeProcess(pr)!=259:print('closed',win32process.GetExitCodeProcess(pr));break
   m=[(z[2],children(z[0])) for z in windows(pid) if z[1]=='#32770']
   if m:print('dialogs',m,flush=True)
   im=capture(h);im.save(f/(w+'-'+mode+'-'+str(t)+'.png'));print(t,round(float(np.array(im)[520:680].mean()),1),flush=True)
  menu=win32gui.GetMenu(h);print('menu',menu,flush=True)
 finally:
  if win32process.GetExitCodeProcess(pr)==259:win32process.TerminateProcess(pr,0)
  win32event.WaitForSingleObject(pr,5000);pr.Close()
if __name__=='__main__':
 with ThreadPoolExecutor(1) as pool:pool.submit(run,sys.argv[1],sys.argv[2],int(sys.argv[3])).result()


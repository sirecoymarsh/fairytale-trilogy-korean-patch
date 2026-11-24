"""Drive the installed Fairytale games on private Win32 desktops and capture their client pixels."""
from pathlib import Path
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import ctypes, ctypes.wintypes as wt, hashlib, io, json, os, re, shutil, sys, time, traceback
ROOT=Path(r'Y:\AI\Codex\projects\fairytale-symphony-encore-ko')
sys.path.insert(0,str(ROOT/'qol'))
sys.path.insert(0,str(ROOT))
import psutil, win32gui,win32process,win32event,win32con,win32api
import numpy as np
from PIL import Image,ImageDraw
from assets import live
from trial_game import U,waitfor,windows,capture,click,key,children,home
AREA=ROOT/'audit'/'scenario-runtime-20261119'
TMP=ROOT/'tmp'/'scenario-runtime-20261119'
def sha(path):
 with path.open('rb') as src:return hashlib.file_digest(src,'sha256').hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def write_json(path,doc):
 tmp=path.with_name(path.name+'.new');tmp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,path)
def check_single(exe,exclude=0):
 for p in psutil.process_iter(['pid','exe']):
  if p.pid!=exclude and p.info['exe'] and os.path.normcase(p.info['exe'])==os.path.normcase(str(exe)):raise RuntimeError('게임이 이미 실행 중입니다 '+str(p.pid))
def sound_helpers():
 src=Path('P:/AI/audio-diag/audio_diag.py').read_text('utf-8-sig').split('\nenum = ctypes.c_void_p()')[0]
 env={};exec(compile(src,'audio_diag definitions','exec'),env)
 return env
def silence(env,pid,held):
 C=ctypes;ptr=C.c_void_p;u=C.c_uint32;pp=C.POINTER(ptr);by=C.byref;call=env['call']
 objects=[]
 def take(o):objects.append(o);return o
 try:
  en=take(ptr());env['ole'].CoCreateInstance(by(env['CLSID_MMDeviceEnumerator']),None,23,by(env['IID_IMMDeviceEnumerator']),by(en))
  dev=take(ptr());call(en,4,[C.c_int,C.c_int,pp],0,1,by(dev))
  mgr=take(env['activate'](dev,env['IID_IAudioSessionManager2']))
  se=take(ptr());call(mgr,5,[pp],by(se));count=C.c_int();call(se,3,[C.POINTER(C.c_int)],by(count))
  for j in range(count.value):
   ctl=take(ptr());call(se,4,[C.c_int,pp],j,by(ctl));c2=take(env['qi'](ctl,env['IID_IAudioSessionControl2']))
   p=u();call(c2,14,[C.POINTER(u)],by(p))
   if p.value!=pid:continue
   v=env['qi'](ctl,env['IID_ISimpleAudioVolume']);m=C.c_int();call(v,6,[C.POINTER(C.c_int)],by(m))
   if v.value not in held:
    held[v.value]=(v,m.value);call(v,5,[C.c_int,ptr],1,None)
   else:objects.append(v)
 finally:
  for o in reversed(objects):
   if o:env['call'](o,2,[])
def reactivate(h):
 tid,pid=win32process.GetWindowThreadProcessId(h);me=win32api.GetCurrentThreadId()
 # Only the game on the private desktop receives activation and input.
 linked=U.AttachThreadInput(me,tid,True)
 try:
  U.SetForegroundWindow(h);U.SetActiveWindow(h);U.SetFocus(h)
  win32gui.PostMessage(h,0x1c,1,0);win32gui.PostMessage(h,6,1,0);win32gui.PostMessage(h,7,0,0)
 finally:
  if linked:U.AttachThreadInput(me,tid,False)


def own_save_files(folder):return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()}
def run(work):
 assert work in ('Encore','Symphony')
 label='앙코르' if work=='Encore' else '심포니'
 state=json.loads((AREA/'설치기록.json').read_text('utf-8'))['works'][work]
 game=live(work).resolve();exe=Path(state['exe']).resolve()
 assert exe.parent==game and sha(exe)==state['files'][exe.name]['after'] and sha(game/'scr.xfl')==state['files']['scr.xfl']['after']
 check_single(exe)
 final=AREA/label;final.mkdir(parents=True,exist_ok=True);temp=TMP/work;temp.mkdir(parents=True,exist_ok=True)
 saves=game/'save';before=own_save_files(saves);backup=ROOT/'rollback'/'scenario-final-20261119'/work/'실행전_저장'
 for n,hs in before.items():
  dst=backup/n
  dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copyfile(saves/n,dst)
  assert sha(dst)==hs
 deskname='FairytaleScenario'+str(os.getpid())+work
 desk=U.CreateDesktopW(deskname,None,None,0,0x1ff,None)
 if not desk or not U.SetThreadDesktop(desk):raise OSError(ctypes.get_last_error())
 si=win32process.STARTUPINFO();si.lpDesktop=deskname
 try:audio=sound_helpers()
 except Exception as ex:print('오디오 세션',str(ex),flush=True);audio=None
 proc,thread,pid,tid=win32process.CreateProcess(str(exe),None,None,None,False,0,None,str(game),si);thread.Close()
 held={};hist=OrderedDict();counter=0
 info=dict(work=work,started=utc(),pid=pid,path=str(exe),cwd=str(game),exe_sha256=sha(exe),scr_sha256=sha(game/'scr.xfl'),steps=[],captures=[])
 def tick():
  if audio:
   try:silence(audio,pid,held)
   except OSError:pass
 def modals():
  return [(w[1],w[2],[(k[1],k[2]) for k in children(w[0]) if k[1] in ('Static','Button')]) for w in windows(pid) if w[1]=='#32770']
 def safe_game():
  if win32process.GetExitCodeProcess(proc)!=259:raise RuntimeError('게임 종료 '+str(win32process.GetExitCodeProcess(proc)))
  m=modals()
  if m:raise RuntimeError('모달 '+str(m))
 def snap():
  im=capture(h)
  return im if im.size==(1280,720) else im.resize((1280,720))
 def shot(name,im,folder=temp):
  assert re.fullmatch('[a-zA-Z0-9_-]+',name)
  dst=folder/(name+'.png');tmp=dst.with_suffix('.new');im.save(tmp,format='PNG');os.replace(tmp,dst);return dst
 def addframe(im):
  nonlocal counter
  counter+=1;b=io.BytesIO();im.save(b,format='WEBP',lossless=True,method=0)
  hist[counter]=b.getvalue()
  if len(hist)>40:hist.popitem(last=False)
  return counter
 def frame(ix):return Image.open(io.BytesIO(hist[ix])).convert('RGB')
 def sheet(numbers):
  # Full-width strips of the game's dialogue area, only the current contact sheet is kept.
  w=800;ih=160;canvas=Image.new('RGB',(w*2,(len(numbers)+1)//2*(ih+16)),(55,55,55));draw=ImageDraw.Draw(canvas)
  for j,k in enumerate(numbers):
   im=frame(k);crop=im.crop((0,464,1280,720)).resize((w,ih),Image.Resampling.LANCZOS);x=(j%2)*w;v=(j//2)*(ih+16)
   draw.text((x+4,v),str(k),fill='white');canvas.paste(crop,(x,v+16))
  return shot('contact',canvas)
 def accept(ix,ident):
  assert re.fullmatch(work[0]+r'\d{4}-\d{5}',ident)
  im=frame(ix) if ix else snap();path=shot(ident,im,final)
  info['captures']=[item for item in info['captures'] if item['id']!=ident]
  info['captures'].append(dict(id=ident,screen_event=ix,utc=utc(),path=str(path),sha256=sha(path),size=list(im.size)))
 try:
  print('RUNNING',work,pid,flush=True)
  h=waitfor(lambda:home(pid),14)
  if not h:raise RuntimeError('윈도우 없음 '+str(windows(pid)))
  tick();reactivate(h)
  info['window']=[win32gui.GetClassName(h),win32gui.GetWindowText(h),list(win32gui.GetClientRect(h))]
  ref=np.asarray(Image.open(ROOT/'qol'/'evidence'/work/'title.png').convert('RGB'),dtype='int16')[125:320:4,240:704:4]
  last=time.monotonic();end=last+240;ts=0;tries=0
  while time.monotonic()<end:
   safe_game();tick()
   im=snap();patch=np.asarray(im,dtype='int16')[125:320:4,240:704:4]
   match=float((np.abs(patch-ref).max(2)<28).mean())
   if match>.76:break
   if time.monotonic()-ts>2.1:
    tries+=1
    if tries in (2,5,8):key(h,27)
    elif tries<=6:key(h,13)
    if tries%5==0:
     shot('loading',im);print('intro',int(time.monotonic()-last),round(match,2),flush=True)
    ts=time.monotonic()
   time.sleep(.22)
  else:
   shot('title-unmatched',im);raise RuntimeError('타이틀 확인 실패 '+str(match))
  reactivate(h)
  title_ref=np.asarray(Image.open(ROOT/'qol'/'evidence'/work/'title.png').convert('RGB'),dtype='int16')[112:181:2,811:865:2]
  for _ in range(50):
   title=snap();btn=np.asarray(title,dtype='int16')[112:181:2,811:865:2]
   if (np.abs(btn-title_ref).max(2)<42).mean()>.78:break
   time.sleep(.12)
  shot('title',title,final);info['steps'].append('타이틀 실제 화면 확인')
  click(h,836,141);time.sleep(1.5);tick();im=snap();shot('latest',im);info['steps'].append('타이틀 시작 버튼')
  print('READY',work,pid,'match',round(match,3),'window',info['window'],'shot',temp/'latest.png',flush=True)
  while True:
   raw=sys.stdin.readline()
   if not raw:break
   arr=raw.strip().split()
   if not arr:continue
   try:
    kind=arr[0]
    if kind=='end':break
    if kind=='status':print(windows(pid),modals(),flush=True);continue
    if kind=='click':click(h,int(arr[1]),int(arr[2]));time.sleep(float(arr[3]) if len(arr)>3 else .8);info['steps'].append('클릭 '+' '.join(arr[1:3]))
    elif kind=='key':key(h,int(arr[1]));time.sleep(float(arr[2]) if len(arr)>2 else .7);info['steps'].append('키 '+arr[1])
    elif kind=='wait':time.sleep(float(arr[1]))
    elif kind=='step':
     n=int(arr[1]);delay=float(arr[2]) if len(arr)>2 else .8
     assert 1<=n<=36 and .10<=delay<=3.0
     ids=[]
     for j in range(n):
      safe_game();key(h,13);time.sleep(delay);im=snap();ids.append(addframe(im))
      if j%12==0:tick()
     shot('latest',im);sheet(ids);info['steps'].append('대사 진행 '+str(n)+'회')
     print('FRAMES',ids[0],ids[-1],temp/'contact.png',flush=True);continue
    elif kind=='sheet':print(sheet(list(range(int(arr[1]),int(arr[2])+1))),flush=True);continue
    elif kind=='keep':accept(int(arr[1]),arr[2]);print('KEPT',arr[2],flush=True);continue
    elif kind=='screen':
     k=int(arr[1]);shot('inspect',frame(k));print('INSPECT',k,flush=True);continue
    elif kind!='snap':raise ValueError('unknown command')
    safe_game();tick();im=snap();q=addframe(im);shot('latest',im);print('SCREEN',q,temp/'latest.png',flush=True)
   except Exception as ex:print('ERROR',repr(ex),flush=True)
 finally:
  if win32process.GetExitCodeProcess(proc)==259:
   win32process.TerminateProcess(proc,0)
  win32event.WaitForSingleObject(proc,4000);proc.Close()
  if audio:
   for v,m in held.values():
    try:audio['call'](v,5,[ctypes.c_int,ctypes.c_void_p],m,None)
    except OSError:pass
    try:audio['call'](v,2,[])
    except OSError:pass
  check_single(exe)
  changed=[]
  for n,hs in before.items():
   current=saves/n
   if not current.exists() or sha(current)!=hs:
    assert sha(backup/n)==hs
    tmp=current.with_name(current.name+'.scenario-save-restore');assert not tmp.exists()
    shutil.copyfile(backup/n,tmp);os.replace(tmp,current);changed.append(n)
  after=own_save_files(saves)
  info.update(finished=utc(),restored_save_files=changed,save_inventory_preserved=before==after,new_save_files=sorted(set(after)-set(before)),audio_sessions_muted=len(held))
  write_json(final/'실행기록.json',info);print('CLOSED',work,info['save_inventory_preserved'],flush=True)
if __name__=='__main__':
 with ThreadPoolExecutor(1) as pool:pool.submit(run,sys.argv[1]).result()

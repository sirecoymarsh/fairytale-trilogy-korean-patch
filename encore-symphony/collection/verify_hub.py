"""Interactive QA on a private desktop, backed by independent saves and the installed hub executable."""
from assemble import *
from probe import activate
from concurrent.futures import ThreadPoolExecutor
import ctypes,win32api,win32con,win32event,win32gui,win32process,time,psutil,socket,urllib.request,websocket,base64
from trial_game import U,windows,children,capture,home,click,key
from PIL import Image
QA=HERE/'qa';EVID=HERE/'qa'/'integrated';EVID.mkdir(exist_ok=True)
def run():
 installed='--film' in sys.argv
 hub=(OUT if installed else QA)/'페어리테일 통합판.exe'
 assert digest(hub)==digest(OUT/hub.name)
 si=win32process.STARTUPINFO()
 if not installed:
  dname='FairyCollectionHubQA'+str(os.getpid());desk=U.CreateDesktopW(dname,None,None,0,0x1ff,None);assert desk and U.SetThreadDesktop(desk)
  si.lpDesktop=dname
 free=socket.socket();free.bind(('127.0.0.1',0));port=free.getsockname()[1];free.close()
 env=os.environ.copy();env['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS']=f'--remote-debugging-port={port} --remote-debugging-address=127.0.0.1' + ('' if installed else ' --disable-gpu --disable-background-networking --autoplay-policy=no-user-gesture-required')
 program,arguments=str(hub),None
 if '--music' in sys.argv:
  # Use the installed window class and private saves, leaving an already-open user's copy untouched.
  import subprocess
  program=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
  arguments=subprocess.list2cmdline([program,'-NoProfile','-STA','-WindowStyle','Hidden','-File',str(QA/'music-test/gallery-window.ps1')])
  env['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS']+=' --mute-audio'
  env['TMP']=env['TEMP']=str(HERE/'tmp')
 pr,th,pid,tid=win32process.CreateProcess(program,arguments,None,None,False,0,env,str(hub.parent),si);th.Close();ws=None
 games={};seq=0
 def gp():
  for p in psutil.Process(pid).children():
   if p.name() in EXES.values() and Path(p.exe()).is_relative_to(QA/'Games'):
    games[p.pid]=p;return p
 def hostwin():
  return next((h for h,cls,t,rec in windows(pid) if 'HwndWrapper' in cls and rec[2]>320),None)
 def command(method,params={}):
  nonlocal seq
  seq+=1;ix=seq;ws.send(json.dumps(dict(id=ix,method=method,params=params)))
  while True:
   a=json.loads(ws.recv())
   if a.get('id')==ix:
    if 'error' in a:raise RuntimeError(a['error'])
    return a.get('result',{})
 def ev(expr):
  r=command('Runtime.evaluate',dict(expression=expr,returnByValue=True,awaitPromise=True))
  if 'exceptionDetails' in r:raise ValueError(str(r['exceptionDetails'])[:450])
  return r.get('result',{}).get('value')
 def wait(expr,timeout=10):
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   if ev(expr):return
   time.sleep(.15)
  raise RuntimeError('timeout '+expr)
 def hit(sel):
  p=ev("(()=>{let r=document.querySelector("+json.dumps(sel)+").getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()");assert p
  for kind in ('mouseMoved','mousePressed','mouseReleased'):
   args=dict(type=kind,x=p[0],y=p[1])
   if kind!='mouseMoved':args.update(button='left',clickCount=1)
   command('Input.dispatchMouseEvent',args)
 def photo(name):
  dst=EVID/(name+'.png');dst.write_bytes(base64.b64decode(command('Page.captureScreenshot',{'format':'png'})['data']));return dst.name
 def game(photoid):
  q=gp();assert q
  h=home(q.pid);assert h
  z=capture(h);z.save(EVID/(photoid+'.png'));return [q.name(),q.pid,windows(q.pid),z.size]
 def gameclose():
  q=gp();assert q;h=home(q.pid);win32gui.PostMessage(h,0x10,0,0)
  for j in range(40):
   if not q.is_running():return 'closed normally'
   for rect in windows(q.pid):
    if rect[1]=='#32770':
     kids=children(rect[0]);btn=next((a[0] for a in kids if a[1]=='Button' and a[3] in (6,1)),None)
     if btn:win32gui.PostMessage(btn,0xf5,0,0)
   time.sleep(.16)
  raise RuntimeError('close dialog '+str(windows(q.pid)))
 try:
  deadline=time.monotonic()+55;url=None
  while time.monotonic()<deadline:
   try:
    tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list',timeout=.8))
    url=next((t['webSocketDebuggerUrl'] for t in tabs if 'fairytale.example/index' in t.get('url','')),None)
    if url:break
   except OSError:pass
   if win32process.GetExitCodeProcess(pr)!=259:raise RuntimeError('host exited '+str(win32process.GetExitCodeProcess(pr)))
   time.sleep(.22)
  if not url:
   print('NO PAGE',windows(pid),flush=True)
   for sub in windows(pid):
    if sub[1]=='#32770':print(children(sub[0]),flush=True)
   raise RuntimeError('WebView page not loaded')
  ws=websocket.create_connection(url,timeout=8,suppress_origin=True);command('Page.enable');wait("typeof progress!=='undefined' && !!progress.Symphony")
  print('READY',pid,ev("Object.keys(catalog)"),flush=True)
  # Every command is a test operator command on this isolated private desktop.
  if installed:
   import subprocess
   ev("window.qaFilmClosed=false;host.addEventListener('message',e=>{if(e.data.type==='filmClosed')window.qaFilmClosed=true;})")
   hit("#title [aria-label='영상']");wait("section==='movies'")
   hit('.filter:nth-of-type(3)');hit(".entry[aria-label='오프닝']")
   time.sleep(8);h=hostwin()
   subprocess.run([sys.executable,'-X','utf8','-B',str(HERE/'capture_cinema.py'),str(pid),str(h)],check=True)
   width,height=win32gui.GetClientRect(h)[2:]
   key(h,27);time.sleep(.4)
   if not ev("window.qaFilmClosed"):click(h,50,round(720*(height-21)/height))
   wait("window.qaFilmClosed",8)
   print('INSTALLED MOVIE OK',hub,flush=True)
   return
  if '--doors' in sys.argv:
   results={}
   for w,label in [('Requiem','레퀴엠'),('Encore','앙코르'),('Symphony','심포니')]:
    target=QA/'Games'/w/'scr.xfl'
    assert target.resolve().is_relative_to((QA/'Games').resolve())
    shutil.copyfile(OUT/'Games'/w/'scr.xfl',target)
    original=GAMES[w]/'scr.xfl'
    assert digest(target)==digest(original)
    hit("#title [aria-label='시작']");wait("screen==='doors'");hit("#doors [aria-label='"+label+"']")
    time.sleep(9);screen=game('release-'+w);assert screen[0]==EXES[w]
    assert read_entry(target,'0000.gsc')==(OUT/'Entries'/w/'story.gsc').read_bytes()
    assert set(entry_map(target))==set(entry_map(original))
    assert all(read_entry(target,n)==read_entry(original,n) for n in entry_map(original) if n!='0000.gsc')
    returned=gameclose();wait("screen==='title' && !busy")
    results[w]=dict(native_window=screen[0],source_archive_sha256=digest(original),preserved_members=len(entry_map(original))-1,first_page='release-'+w+'.png',close=returned)
    print('DOOR OK',w,flush=True)
   jsonout(EVID/'release-doors.json',results)
   return
  env=dict(locals())
  for raw in sys.stdin:
   code=raw.strip()
   if code=='end':break
   if not code:continue
   try:print('RESULT',eval(code,env),flush=True)
   except Exception as ex:print('TEST ERROR',repr(ex),flush=True)
 finally:
  if ws:ws.close()
  try:
   q=gp()
   if q is not None and q.is_running():q.terminate();q.wait(4)
  except (OSError,psutil.Error):pass
  if win32process.GetExitCodeProcess(pr)==259:
   h=hostwin()
   if h:win32gui.PostMessage(h,0x10,0,0)
   if win32event.WaitForSingleObject(pr,3500)==258:win32process.TerminateProcess(pr,0)
  pr.Close()
if __name__=='__main__':
 with ThreadPoolExecutor(1) as pool:pool.submit(run).result()


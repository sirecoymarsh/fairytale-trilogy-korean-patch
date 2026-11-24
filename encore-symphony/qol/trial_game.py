"""Drive only a newly started isolated trial on its own Windows desktop."""
import ctypes as C, time, sys, os, struct, json
from ctypes import wintypes as T
from pathlib import Path
import win32api, win32process, win32con, win32event, win32gui, win32ui
from PIL import Image
import numpy as np
from build_options import QA, HERE, DLL, GAMES, live
U=C.WinDLL('user32',use_last_error=True)
U.CreateDesktopW.argtypes=[T.LPCWSTR,T.LPCWSTR,C.c_void_p,T.DWORD,T.DWORD,C.c_void_p];U.CreateDesktopW.restype=T.HANDLE
U.SetThreadDesktop.argtypes=[T.HANDLE];U.SetThreadDesktop.restype=T.BOOL
U.CloseDesktop.argtypes=[T.HANDLE]
def waitfor(fn,limit):
    deadline=time.monotonic()+limit
    while time.monotonic()<deadline:
        val=fn()
        if val:return val
        time.sleep(.12)
def windows(pid):
    result=[]
    def cb(h,_):
        if win32process.GetWindowThreadProcessId(h)[1]==pid and win32gui.IsWindowVisible(h):
            result.append((h,win32gui.GetClassName(h),win32gui.GetWindowText(h),win32gui.GetClientRect(h)))
        return True
    win32gui.EnumWindows(cb,None)
    return result
def capture(h):
    l,t,r,b=win32gui.GetClientRect(h);dc=win32gui.GetDC(h);src=win32ui.CreateDCFromHandle(dc);dst=src.CreateCompatibleDC()
    bmp=win32ui.CreateBitmap();bmp.CreateCompatibleBitmap(src,r,b);dst.SelectObject(bmp)
    try:
        U.PrintWindow(h,dst.GetSafeHdc(),1)
        return Image.frombytes('RGB',(r,b),bmp.GetBitmapBits(True),'raw','BGRX',0,1)
    finally:
        dst.DeleteDC();src.DeleteDC();win32gui.ReleaseDC(h,dc);win32gui.DeleteObject(bmp.GetHandle())
def click(h,x,y):
    _,_,w,hg=win32gui.GetClientRect(h);x=round(x*w/1280);y=round(y*hg/720);p=(y<<16)|x
    win32gui.PostMessage(h,0x200,0,p);time.sleep(.12)
    win32gui.PostMessage(h,0x201,1,p);time.sleep(.08);win32gui.PostMessage(h,0x202,0,p);time.sleep(.20)
def key(h,v):
    win32gui.PostMessage(h,0x100,v,1);time.sleep(.07);win32gui.PostMessage(h,0x101,v,0xc0000001)
def children(h):
    it=[];win32gui.EnumChildWindows(h,lambda c,_:it.append((c,win32gui.GetClassName(c),win32gui.GetWindowText(c),win32gui.GetDlgCtrlID(c))) or True,None);return it
def launch(game):
    d=QA/game;exe=next(d.glob('*.exe'))
    assert d.parent==HERE/'trial' and (d/DLL).exists()
    si=win32process.STARTUPINFO();si.lpDesktop=deskname
    proc,thread,pid,tid=win32process.CreateProcess(str(exe),None,None,None,False,0,None,str(d),si)
    thread.Close();return proc,pid
def home(pid):
    return next((w[0] for w in windows(pid) if w[3][2]>=600 and w[1]!='#32770'),None)
def shot(h,name):
    p=folder/(name+'.png');capture(h).save(p);return p
def main(game):
    global deskname,folder
    deskname='FairytaleQol'+str(os.getpid());desk=U.CreateDesktopW(deskname,None,None,0,0x1ff,None)
    assert desk and U.SetThreadDesktop(desk),C.get_last_error()
    folder=HERE/'evidence'/game;folder.mkdir(parents=True,exist_ok=True)
    proc,pid=launch(game)
    try:
        print('pid',pid,flush=True)
        h=waitfor(lambda:home(pid),9)
        if not h:print('windows',windows(pid),'exit',win32process.GetExitCodeProcess(proc),flush=True);return
        if 'FAIRY_QA_SCREEN' in os.environ:
            exec((HERE/'gallery_screen.py').read_text(encoding='utf-8'),dict(globals(),**locals()));return
        time.sleep(1);key(h,13);time.sleep(1);key(h,13);time.sleep(1);print('windows',windows(pid),flush=True)
        shot(h,'before-options')
        print('menu',win32gui.GetMenu(h),flush=True)
        key(h,27);time.sleep(.6);shot(h,'escape')
        print('after escape',windows(pid),flush=True)
        # Scripted branch selected by the caller. All input stays in this one window.
        if len(sys.argv)>2:
            exec((HERE/sys.argv[2]).read_text(encoding='utf-8'),dict(globals(),**locals()))
    finally:
        if win32process.GetExitCodeProcess(proc)==259:win32process.TerminateProcess(proc,0)
        win32event.WaitForSingleObject(proc,3000);proc.Close()
if __name__=='__main__':
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(1) as pool:pool.submit(main,sys.argv[1]).result()

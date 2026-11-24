def snapshot(step):
    print(step,windows(pid),flush=True)
    shot(h,step)
    _,_,w,b=win32gui.GetClientRect(h)
    dc=win32gui.GetDC(h);src=win32ui.CreateDCFromHandle(dc);dst=src.CreateCompatibleDC();bmp=win32ui.CreateBitmap();bmp.CreateCompatibleBitmap(src,w,b);dst.SelectObject(bmp)
    try:
        for flag in (0,1):
            U.PrintWindow(h,dst.GetSafeHdc(),flag)
            im=Image.frombytes('RGB',(w,b),bmp.GetBitmapBits(True),'raw','BGRX',0,1)
            print('PrintWindow',flag,im.getextrema(),flush=True)
            if np.array(im).std()>12:im.save(folder/(step+'-window.png'))
        dst.BitBlt((0,0),(w,b),src,(0,0),win32con.SRCCOPY)
        im=Image.frombytes('RGB',(w,b),bmp.GetBitmapBits(True),'raw','BGRX',0,1)
        print('direct',im.getextrema(),flush=True)
        if np.array(im).std()>12:im.save(folder/(step+'-dc.png'))
    finally:
        dst.DeleteDC();src.DeleteDC();win32gui.ReleaseDC(h,dc);win32gui.DeleteObject(bmp.GetHandle())
win32gui.PostMessage(h,0x1c,1,0);win32gui.PostMessage(h,6,1,0)
for _ in range(4):
    key(h,13);time.sleep(.55)
snapshot('native-title')
click(h,920,328);time.sleep(.6);snapshot('native-settings')
click(h,440,606);time.sleep(.6);snapshot('native-action')

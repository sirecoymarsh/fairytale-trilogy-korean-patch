import cv2
from assets import RBASE
from PIL import Image
import hashlib
from menu_scripts import MODE,READY,PENDING,MANUAL
doc=json.loads((HERE/'build.json').read_text(encoding='utf-8'))[game]['catalog']
sysfile=next((QA/game/'save').glob('*save.dat'))
def value(buf,k):return struct.unpack_from('<h',buf,0x872+2*(k-7000))[0]
def win_dialog():
    return next((v[0] for v in windows(pid) if v[1]=='#32770'),None)
def toggle(pos,yes,expected=None):
    click(h,pos,605)
    box=waitfor(win_dialog,2)
    if not box:raise RuntimeError('no dialog for '+str(pos))
    kids=children(box);caption=' '.join(s for _,c,s,_ in kids if c=='Static')
    print('button',pos,caption,flush=True)
    if expected and expected not in caption:raise RuntimeError(caption)
    ident=6 if yes else 7
    button=next((b for b,c,s,i in kids if c=='Button' and i==ident),None)
    if button is None:raise RuntimeError('unexpected dialog '+repr(kids))
    win32gui.PostMessage(button,0xf5,0,0)
    assert waitfor(lambda:not win32gui.IsWindow(box),2)
    time.sleep(.15)
    if win_dialog():raise RuntimeError(str(children(win_dialog())))
    return sysfile.read_bytes()
def title_button():
    fn=folder/'title-button.png'
    im=np.array(Image.open(fn).convert('RGBA'))
    # A small opaque interior patch avoids transparent-margin matching.
    alpha=im[:,:,3];ys,xs=np.where(alpha>250)
    left,top,right,bottom=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
    crop=im[top:bottom,left:right];mask=(crop[:,:,3]>240).astype('uint8')*255
    rgb=np.ascontiguousarray(crop[:,:,:3]);start=time.monotonic();last=0
    while time.monotonic()-start<90:
        snap=capture(h);pixels=np.array(snap);region=np.ascontiguousarray(pixels[140:490,650:1120])
        res=cv2.matchTemplate(region,rgb,cv2.TM_SQDIFF,mask=mask)
        v,_,xy,_=cv2.minMaxLoc(res);err=max(0.,v)/(np.count_nonzero(mask)*3*255**2)
        if err<.018:
            snap.save(folder/'title.png')
            return (650+xy[0]+(right-left)//2,140+xy[1]+(bottom-top)//2)
        if time.monotonic()-last>=2.5:
            last=time.monotonic()
            key(h,13)
        time.sleep(.28)
    snap.save(folder/'title-missing.png');raise RuntimeError('could not locate original settings button; score '+str(err))
win32gui.PostMessage(h,0x1c,1,0);win32gui.PostMessage(h,6,1,0)
xy=title_button();print('title settings',xy,flush=True)
click(h,*xy)
bg=Image.open(HERE/'built/art/bg.png').convert('RGB')
def settings():
    im=capture(h)
    a=np.array(im)[80:550:4,125:331:4].astype('int16')
    b=np.array(bg)[80:550:4,125:331:4].astype('int16')
    return im if np.abs(a-b).mean()<9 else None
im=waitfor(settings,6)
if not im:
    shot(h,'settings-missing');raise RuntimeError('settings did not open')
time.sleep(.65);capture(h).save(folder/'settings.png')
s0=sysfile.read_bytes();u0=toggle(440,False,'모두 열까요');assert s0==u0
u=toggle(440,True,'모두 열까요');assert value(u,MODE)==1
can=toggle(642,True,'취소');assert value(can,MODE)==0
reset=toggle(806,True,'비울까요');assert value(reset,PENDING)==1 and value(reset,MODE)==0
restore=toggle(997,True,'되돌릴까요');assert value(restore,PENDING)==0
inds=doc['cg']+[int(v) for v in doc['shadow'].values()]
assert all(value(reset,k)==0 for k in inds)
assert all(value(can,k)==value(restore,k) for k in inds)
assert all(value(s0,k)==value(reset,k)==value(restore,k) for k in (7790,7016))
assert can[:0x872]==reset[:0x872]==restore[:0x872]
assert (QA/game/'save/slot-test.bin').read_bytes()==b'untouched-slot-fixture'
meta=dict(title_xy=xy,real_buttons=4,default_cancel_preserves_file=u0==s0,unlock=value(u,MODE),cancel=value(can,MODE),reset=value(reset,PENDING),restore=value(restore,PENDING),catalog_marks=len(inds),flags_restore=True,preferences_preserved=True,route_and_slot_preserved=True)
(folder/'buttons.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8');print(meta,flush=True)

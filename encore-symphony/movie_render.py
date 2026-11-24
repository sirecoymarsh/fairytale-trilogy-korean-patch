from movie_design import *
from opening_gops import FF,PROBE,ES,table
import subprocess,hashlib
from pathlib import Path
rec=read('audit/op_track_final.json')
poses={int(k):np.array(v) for k,v in rec['matrices'].items()}
RADIUS=rec['source_radius']
LAST=max(poses)
def source_template():
    return cv2.imread(str(OUT/'samples/2160.jpg'))[T:B,L:R].copy()
def new_template():
    im=master('앙코르',4).resize((W,H),Image.Resampling.LANCZOS)
    white=Image.new('RGBA',(W,H),'white');white.alpha_composite(im)
    return np.ascontiguousarray(np.asarray(white.convert('RGB'))[:,:,::-1])
def pyramid(image):
    ink=255-image
    return [cv2.resize(ink,(max(4,round(W*s)),max(4,round(H*s))),interpolation=cv2.INTER_AREA) for s in (1.,.5,.25,.125,.0625)]
JAPAN=pyramid(source_template());KOREAN=pyramid(new_template())
def pose(f):
    at=max(min(int(np.floor(f)),LAST),2136);after=min(at+1,LAST)
    t=np.clip(f-at,0,1);return poses[at]*(1-t)+poses[after]*t
def project(f,images,shutter):
    if shutter<=.015 or f<2209:count=1
    else:
        probe=np.array([[0,0,1],[W,0,1],[0,H,1],[W,H,1]])
        travel=np.linalg.norm(probe@(pose(f+.5*shutter)-pose(f-.5*shutter)).T,axis=1).max()
        count=max(3,min(65,2*int(np.ceil(travel/2.3))+1))
    transforms=[pose(f+delta) for delta in (np.linspace(-.5,.5,count)*shutter if count>1 else [0])]
    corners=np.array([[0,0],[W,0],[0,H],[W,H]])
    bounds=np.concatenate([corners@a[:,:2].T+a[:,2] for a in transforms])
    l,t=np.maximum(0,np.floor(bounds.min(0)-2)).astype(int)
    r,b=np.minimum([1280,720],np.ceil(bounds.max(0)+2)).astype(int)
    if l>=r or t>=b:return (0,0,0,0),None
    out=np.zeros((b-t,r-l,3),'float32')
    for a in transforms:
        a=a.copy();sval=np.linalg.svd(a[:,:2],compute_uv=False)
        size=min(max(sval[0],.065),1);n=max(0,min(4,int(np.floor(-np.log2(size)))))
        tex=images[n];a[:,:2]=a[:,:2]@np.diag([W/tex.shape[1],H/tex.shape[0]])
        a[:,2]-=[l,t]
        view=cv2.warpAffine(tex,a,(r-l,b-t),flags=cv2.INTER_LINEAR)
        out+=view
    return (l,t,r,b),np.rint(out/count).clip(0,255).astype('uint8')
def ring(frame,i):
    a=poses[i]
    if i<2378:
        disk_center=a@np.r_[center-np.array(rec['radial_offset']),1]
        radius=RADIUS*np.sqrt(abs(np.linalg.det(a[:,:2])))
        GG=np.eye(2)*radius;spindle=disk_center
    else:
        el=scan[str(i)]['ellipse'];GG=ellipseH(el);disk_center=np.array(el[0])
        spindle=a@np.r_[center-np.array(rec['radial_offset']),1]
    # The press label is uniform white. Remove ink only from its unbroken interior;
    # the spindle, black vinyl and original scene remain available in the base.
    y,x=np.indices(frame.shape[:2],dtype='float32')
    inv=np.linalg.inv(GG);xx=x-disk_center[0];yy=y-disk_center[1]
    dx=inv[0,0]*xx+inv[0,1]*yy;dy=inv[1,0]*xx+inv[1,1]*yy
    geom=dx*dx+dy*dy
    dx=inv[0,0]*(x-spindle[0])+inv[0,1]*(y-spindle[1]);dy=inv[1,0]*(x-spindle[0])+inv[1,1]*(y-spindle[1])
    m=(geom<.933**2)&((dx*dx+dy*dy)>.161**2)
    if i>=2480:
        _,native,_,_=features(frame)
        if native is not None:m&=native!=0
    return m
def credits_prepare(n,groups):
    im=cv2.imread(str(OUT/f'samples/{n}.jpg'));ref=gray(im)
    x0,y0,x1,y1=(505,263,776,458) if n==3530 else (550,252,730,284)
    rr=ref[y0:y1,x0:x1]
    wipe=cv2.dilate((rr>5).astype('uint8'),np.ones((5,5),np.uint8))!=0
    c=Image.new('L',(1280,720),0);d=ImageDraw.Draw(c)
    for top,btm,phrase in groups:
        for size in range((btm-top)*2,8,-1):
            font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size);bbox=font.getbbox(phrase)
            if bbox[3]-bbox[1]<=btm-top+1:break
        d.text((640-(bbox[0]+bbox[2])/2,top-bbox[1]),phrase,font=font,fill=255)
    cc=np.array(c);yy,xx=np.where(cc);ll,tt,rs,bb=int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1
    return ((x0,y0,x1,y1),rr,wipe,(ll,tt,rs,bb),cc[tt:bb,ll:rs])
C1=credits_prepare(3530,[(271,290,'시나리오'),(303,334,'우미하라 노조무'),(386,405,'원화'),(418,449,'오이시 류코')])
C2=credits_prepare(3695,[(257,277,'제작·저작')])
def film_credit(frame,i):
    (x,y,r,b),ref,wipe,(l,t,rr,bb),letters=C1 if i<3656 else C2
    roi=frame[y:b,x:r]
    vals=gray(roi);bright=float(np.median(vals[ref>232]));baseline=float(np.median(vals[~wipe]))
    if bright-baseline<=1:return frame
    scale=np.clip((bright-baseline)/255,0,1)
    out=frame.copy();target=out[y:b,x:r];target[wipe]=np.rint(baseline).astype('uint8')
    region=out[t:bb,l:rr];alpha=(letters.astype('float32')/255)[:,:,None]
    region[:]=np.rint(region*(1-alpha)+(baseline+255*scale)*alpha).clip(0,255).astype('uint8')
    return out
def edit(frame,i,shutter,images=KOREAN):
    if i>=3499:return film_credit(frame,i)
    if i<2136 or i>LAST:return frame
    (l,t,r,b),ink=project(i,images,shutter)
    if i<=2313:
        out=np.full_like(frame,255);m=None
    else:
        out=frame.copy();m=ring(frame,i);out[m]=255
    if ink is not None:
        if m is None:out[t:b,l:r]=255-ink
        else:
            sel=m[t:b,l:r];dst=out[t:b,l:r];dst[sel]=(255-ink)[sel]
    return out
def loadframes(ids):
    wanted=set(ids);cap=cv2.VideoCapture(str(SRC));res={}
    for i in range(max(wanted)+1):
        if not cap.grab():raise ValueError(i)
        if i in wanted:ok,im=cap.retrieve();assert ok;res[i]=im
    cap.release();return res
def proof():
    ids=[2136,2160,2214,2225,2259,2261,2301,2328,2338,2341,2346,2350,2360,2374,2380,2391,2412,2436,2471,2492,3530,3695]
    frames=loadframes(ids);cal={}
    for shutter in [0,.25,.42,.58,.72,.88,1.]:
        errs=[]
        for i in [2214,2259,2261,2301]:
            a=edit(frames[i],i,shutter,JAPAN).astype('int16');b=frames[i].astype('int16')
            errs.append(round(float(np.abs(a-b).mean()),3))
        cal[str(shutter)]=errs
    best=float(min(cal,key=lambda k:sum(cal[k])));stats={}
    outdir=OUT/'design-check';outdir.mkdir(exist_ok=True)
    for i,src in frames.items():
        revised=edit(src,i,best)
        cv2.imwrite(str(outdir/f'{i}-ko.jpg'),revised,[cv2.IMWRITE_JPEG_QUALITY,93])
        if i<=LAST:
            test=edit(src,i,best,JAPAN);err=cv2.absdiff(test,src);stats[i]=round(float(err.mean()),3)
    save('audit/op_design_proof.json',dict(shutter=best,source_registration_mae=stats,calibration=cal));print('shutter',best,'registration',stats)
if __name__=='__main__':proof()


from assets import *
import cv2, numpy as np
from PIL import Image, ImageFont, ImageDraw
from functools import lru_cache
from pathlib import Path
import json,subprocess,os
W,H=1280,720
RATE=30000/1001
M=Path('P:/AI/Codex/projects/migrated-from-c/onedrive-chatgpt/페이러 테일 및 도화이담 시리즈')
QM=read(M/'opening_motion_v6_1/deliverables/manifest.json')
CUES=QM['lyrics']['segments']
OLD=M/'opening_motion_v6_1/deliverables/0001.mpg'
REF=Path(QM['source']['path'])
if not REF.exists():REF=RJ/'mov/0001.mpg'
TITLE=RBASE/'staging/opening_full_korean_v3/clean_clips/title_korean_v4.mkv'
QUESTION=RBASE/'staging/opening_full_korean_v3/clean_clips/question_korean.mkv'
OD=ROOT/'opening/자막'
BANDS=ROOT/'tmp/opening_clean_bands';Y0=624;Y1=704
FF=Path('F:/DOWN/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe')
# Source name and last original quote bands. Korean design ends above the legacy caption.
SCENES=[(1003,1176,[(58,590,344,675),(937,544,1275,704)]),
        (1176,1349,[(408,615,1058,704),(731,541,1280,716)]),
        (1349,1522,[(54,582,1178,674),(262,539,1273,704)]),
        (1522,1695,[(222,538,1198,639),(631,542,1280,719)]),
        (1695,1868,[(527,570,1098,661),(907,542,1280,716)])]
@lru_cache(maxsize=32)
def oldmask(s):
    font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',34);im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
    box=d.textbbox((0,0),s,font=font,stroke_width=2)
    d.text(((W-(box[2]-box[0]))/2-box[0],646-box[1]),s,font=font,fill=255,stroke_width=2,stroke_fill=255)
    return cv2.dilate((np.array(im)[Y0:Y1]>0).astype('uint8'),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))>0
def oldtext(i):
    for r in CUES:
        if r['start']<=i/RATE<r['end']:return r['ko']
    return ''
def grab(cap):
    ok,b=cap.read()
    if not ok:raise ValueError('video frame unavailable')
    return b
def bands():
    import cv2
    BANDS.mkdir(parents=True,exist_ok=True);cv2.setNumThreads(4)
    score=[];grid=np.stack(np.meshgrid(np.arange(W,dtype='float32'),np.arange(Y1-Y0,dtype='float32')),axis=2)
    for lo,hi,rects in SCENES:
        original=cv2.VideoCapture(str(REF)); prior=cv2.VideoCapture(str(OLD))
        for cap in (original,prior):cap.set(cv2.CAP_PROP_POS_FRAMES,lo)
        pos=np.zeros((Y1-Y0,W),bool)
        for x1,y1,x2,y2 in rects:pos[max(y1-Y0,0):max(0,min(Y1,y2)-Y0),x1:x2]=True
        source=[];masked=[];base=[];mono=[];seen=[]
        for i in range(lo,hi):
            a=grab(original)[Y0:Y1].copy();b=grab(prior)[Y0:Y1].copy();old=oldtext(i)
            mask=oldmask(old) if old else np.zeros_like(pos);uncertain=mask&pos
            b[mask&~pos]=a[mask&~pos]
            base.append(b);source.append(a);masked.append(mask);seen.append(~uncertain);mono.append(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY))
        prior.release();original.release()
        def sweep(direction):
            ids=list(range(len(base))) if direction==1 else list(reversed(range(len(base))))
            out=[None]*len(base);cost=[None]*len(base);last=None;flow=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)
            for j in ids:
                val=base[j].copy();dist=np.where(seen[j],0.,9999.).astype('float32')
                if last is not None:
                    mv=flow.calc(mono[j],mono[last],None);xy=grid+mv
                    predicted=cv2.remap(out[last],xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
                    # Require all contributing pixels to have a valid previous observation.
                    d=cv2.remap(cost[last],xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
                    srcprev=cv2.remap(mono[last],xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
                    mismatch=abs(srcprev.astype('float32')-mono[j])
                    d+=1+np.minimum(6,mismatch*.07)
                    use=(dist>0)&(d<300)
                    val[use]=predicted[use];dist[use]=d[use]
                out[j],cost[j]=val,dist;last=j
            return out,cost
        fw,fd=sweep(1);bw,bd=sweep(-1)
        path=BANDS/f'{lo}.mkv';pending=path.with_suffix('.tmp.mkv')
        proc=subprocess.Popen([str(FF),'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{Y1-Y0}','-r','30000/1001','-i','pipe:0','-an','-c:v','ffv1','-level','3','-threads','4',str(pending)],stdin=subprocess.PIPE)
        fallback=0;total=0
        for j,original_band in enumerate(source):
            lost=~seen[j];out=base[j].copy()
            use1=lost&(fd[j]<300);use2=lost&(bd[j]<300);both=use1&use2
            out[use1]=fw[j][use1];out[use2]=bw[j][use2]
            if both.any():
                f=1/(fd[j][both]+1)**2;b=1/(bd[j][both]+1)**2
                out[both]=np.rint((fw[j][both]*f[:,None]+bw[j][both]*b[:,None])/(f+b)[:,None]).astype('uint8')
            missing=lost&~(use1|use2)
            if missing.any():
                # Use the actual source where the neighboring source and localized pixels agree.
                delta=np.max(np.abs(original_band.astype('int16')-out.astype('int16')),axis=2).astype('float32')
                support=(~missing).astype('float32')
                kernel=(19,19)
                local=cv2.boxFilter(delta*support,-1,kernel)/np.maximum(.01,cv2.boxFilter(support,-1,kernel))
                srcok=missing&(local<9)
                out[srcok]=original_band[srcok];rest=missing&~srcok
                if rest.any():out=cv2.inpaint(out,rest.astype('uint8'),3,cv2.INPAINT_TELEA)
                fallback+=int(rest.sum())
            total+=int(masked[j].sum())
            assert np.array_equal(out[~masked[j]],base[j][~masked[j]])
            proc.stdin.write(out.tobytes())
        proc.stdin.close();assert proc.wait()==0;os.replace(pending,path)
        score.append(dict(first=lo,end=hi,masked_pixels=total,spatial_interpolation_pixels=fallback))
        print(lo,total,fallback,flush=True)
    save('audit/requiem_caption_band_recovery.json',score)
if __name__=='__main__':bands()

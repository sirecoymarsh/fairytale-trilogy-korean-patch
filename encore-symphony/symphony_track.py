from assets import *
import cv2,numpy as np
from PIL import Image
def frame(i):
    p=ROOT/f'audit/full/Symphony/grpo_ef/{i:04d}.png'
    a=np.asarray(Image.open(p).convert('RGBA'));alpha=a[:,:,3].astype('float32')/255
    ink=a[:,:,:3].mean(2);return (128*(1-alpha)+ink*alpha).astype('uint8')
def main():
    cv2.setNumThreads(2)
    first=frame(96);points=cv2.goodFeaturesToTrack(first,2400,.001,2.,blockSize=3).reshape(-1,2)
    pos=points.copy();valid=np.ones(len(pos),bool)
    tracked=np.full((96,len(pos),2),np.nan,dtype='float32')
    tracked[95]=pos;prev=first
    for i in range(95,0,-1):
        img=frame(i)
        nxt,ok,err=cv2.calcOpticalFlowPyrLK(prev,img,pos.reshape(-1,1,2),None,winSize=(11,11),maxLevel=2,criteria=(3,22,.005))
        back,okb,errb=cv2.calcOpticalFlowPyrLK(img,prev,nxt,None,winSize=(11,11),maxLevel=2,criteria=(3,22,.005))
        nxt=nxt.reshape(-1,2);back=back.reshape(-1,2)
        valid &= (ok.ravel()>0)&(okb.ravel()>0)&(np.linalg.norm(back-pos,axis=1)<1.7)&(err.ravel()<32)
        valid&=(nxt[:,0]>=1)&(nxt[:,0]<565)&(nxt[:,1]>=1)&(nxt[:,1]<281)
        tracked[i-1,valid]=nxt[valid]
        pos=nxt;prev=img
    np.savez_compressed(ROOT/'audit/symphony_tile_tracks.npz',base=points,series=tracked)
    for i in (1,16,32,48,64,72,80,84,90,95):
        ok=np.isfinite(tracked[i-1,:,0]);print(i,int(ok.sum()),np.round(np.nanmedian(tracked[i-1]-points,axis=0),1))
if __name__=='__main__':main()


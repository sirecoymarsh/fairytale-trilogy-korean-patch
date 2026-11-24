from focus import *
import cv2,numpy as np
from collections import defaultdict
def find():
    ref=[np.asarray(Image.open(fullpath('Encore',k+'.wcg') if '3022' in k else ROOT/'audit/full/Encore/grpe/9101-7.png').convert('RGB').resize((144,81)),dtype=int) for k in ('grpe/3022','title')]
    mask=np.zeros((81,144),bool);mask[12:59,23:110]=True;mask[16:61,55:89]=False
    out={}
    for p in sorted((source('Encore')/'mov').glob('*.mpg')):
        cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS) or 30; i=0; best=[(1e5,None),(1e5,None)]
        while cap.grab():
            if i%max(1,round(fps*.5))==0:
                valid,frame=cap.retrieve()
                if valid:
                    a=cv2.resize(frame,(144,81),interpolation=cv2.INTER_AREA)[:,:,::-1].astype(int)
                    for j,t in enumerate(ref):
                        e=float(np.abs(a[mask]-t[mask]).mean())
                        if e<best[j][0]:best[j]=(e,i)
            i+=1
        cap.release();out[p.name]=best
    print(out);save('audit/footage_donor_scores.json',out)
if __name__=='__main__':find()

from opening_scan import *
from functools import lru_cache
FSCAN=read('audit/op_frame_scan.json')['stats']
sift=cv2.SIFT_create(nfeatures=1000,contrastThreshold=.022)
matcher=cv2.BFMatcher()
def points(k):return np.asarray([i.pt for i in k],np.float32)
def learn(template):
    bag=[]
    for ratio in (1.,.53,.25,.13):
        small=cv2.resize(template,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA)
        k,d=sift.detectAndCompute(small,None)
        if len(k)>3:bag.append((points(k)/ratio,d))
    return bag
def fit(bag,img,mask):
    k,d=sift.detectAndCompute(img,mask)
    if d is None or len(k)<3:return None
    xy=points(k);best=None
    for src,desc in bag:
        matches=matcher.knnMatch(desc,d,k=2)
        pairs=[pair[0] for pair in matches if len(pair)>1 and pair[0].distance<.78*pair[1].distance]
        if len(pairs)<5:continue
        p=np.float32([src[m.queryIdx] for m in pairs]);q=np.float32([xy[m.trainIdx] for m in pairs])
        affine,inliers=cv2.estimateAffine2D(p,q,method=cv2.RANSAC,ransacReprojThreshold=3.,maxIters=1400)
        if affine is None:continue
        n=int(inliers.sum())
        good=inliers.ravel()>0
        if n<5 or np.linalg.det(affine[:,:2])<=0:continue
        extent=np.ptp(p[good],axis=0); ratio=np.linalg.svd(affine[:,:2],compute_uv=False)
        if extent[0]<130 or extent[1]<50 or ratio[0]>12 or ratio[1]<.01 or ratio[0]/ratio[1]>9:continue
        if best is None or n>best[0]:best=(n,affine)
    return best
def main():
    static=gray(cv2.imread(str(OUT/'samples/2160.jpg')))
    y,x=np.where(static<182);l,t,r,b=int(x.min())-23,int(y.min())-23,int(x.max())+24,int(y.max())+24
    ref=static[t:b,l:r];bag=learn(ref)
    cap=cv2.VideoCapture(str(SRC));result={};i=0;cv2.setNumThreads(4)
    while cap.grab():
        if i>2513:break
        if i>=2128:
            ok,im=cap.retrieve()
            val=FSCAN[str(i)]; area=val['area'];mask=None
            if area>75:
                if i>2326:
                    _,mask,_,_=features(im)
                    mask=cv2.dilate(mask,np.ones((5,5),np.uint8))
                found=fit(bag,gray(im),mask)
                if found:
                    n,m=found;result[i]=dict(count=n,matrix=m.tolist())
        i+=1
    cap.release()
    save('audit/op_motion.json',dict(ref=[l,t,r,b],direct=result))
    hits=np.asarray(list(result));g=np.split(hits,np.flatnonzero(np.diff(hits)!=1)+1);print('ref',l,t,r,b,'direct',[(int(v[0]),int(v[-1])) for v in g if len(v)])
if __name__=='__main__':main()


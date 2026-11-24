from opening_scan import SRC,OUT,features,gray
from assets import ROOT,read,save
import cv2,numpy as np
from functools import lru_cache
from PIL import Image,ImageFont,ImageDraw
from lettering import master
motion=read('audit/op_motion.json');refbox=motion['ref'];L,T,R,B=refbox;W,H=R-L,B-T
center=np.array([W*.5,H*.5]);direct={int(k):np.array(v['matrix']) for k,v in motion['direct'].items()}
scan=read('audit/op_frame_scan.json')['stats']
def rot(deg):
    t=np.radians(deg);a,b=np.cos(t),np.sin(t)
    return np.array([[a,-b],[b,a]])
def adiff(a,b):return (a-b+180)%360-180
def aff(origin,linear):
    return np.c_[linear,origin-linear@center]
def matrix_angle(a):return np.degrees(np.arctan2(a[1,0],a[0,0]))
def ellipseH(el):
    (_, _),(w,h),angle=el;q=rot(angle)
    return q@np.diag([w/2,h/2])@q.T
def robust_fit():
    rows=[];vals=[]
    for j in [*range(2209,2223),*range(2257,2265),*range(2297,2305)]:
        if j not in direct:continue
        a=direct[j];s=np.linalg.svd(a[:,:2],compute_uv=False)
        if np.max(np.abs(s-1))>.065:continue
        rows.extend(np.c_[np.eye(2),a[:,:2]]);vals.extend(a@np.r_[center,1])
    mat=np.asarray(rows);val=np.asarray(vals)
    res=np.linalg.lstsq(mat,val,rcond=None)[0]
    for j in range(3):
        good=np.repeat(np.linalg.norm((mat@res-val).reshape(-1,2),axis=1)<4.,2)
        res=np.linalg.lstsq(mat[good],val[good],rcond=None)[0]
    return res[:2],res[2:]
pivot,rad=robust_fit()
# Register the resting print to its measured original pixel window.
pivot=np.array([L,T])+center-rad
def angle(f):
    if f<=2208:return 0.
    if f<=2222:
        key=[2208]+list(range(2209,2223))
        values=[0.]+[matrix_angle(direct[j]) for j in key[1:]]
        return np.interp(f,key,values)
    if f<2239:
        u=(f-2222)/17
        return (2*u**3-3*u**2+1)*angle(2222)+(u**3-2*u**2+u)*17*5.6+(-2*u**3+3*u**2)*161.7+(u**3-u**2)*17*9.
    return (f-2301)*9-.3
def hole_fit(frame,px):
    g=gray(frame);crop=g[225:495,:]
    contours=cv2.findContours((crop<173).astype('uint8'),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)[0]
    found=[]
    for c in contours:
        pts=c[:,0,:].astype('float32');pts[:,1]+=225
        pts=pts[(pts[:,0]>1)&(pts[:,0]<1278)&(pts[:,1]>226)&(pts[:,1]<493)]
        if len(pts)<18:continue
        el=cv2.fitEllipse(pts.reshape(-1,1,2));(x,y),(w,h),_ =el
        if not(30<w<260 and 30<h<260 and .76<w/h<1.24 and abs(y-360)<28 and abs(x-px)<95):continue
        found.append((abs(y-360)+abs(x-px)*.2+abs(w/h-1)*85,np.array([x,y,(w+h)*.25])))
    return min(found,key=lambda v:v[0])[1] if found else None
def smooth_samples(d,at,width):
    keys=np.array(sorted(d));vals=np.array([d[k] for k in keys]);delta=keys-at
    pick=np.argsort(abs(delta))[:max(5,int(width))]
    dx=delta[pick];scale=max(np.median(abs(dx)),2.);w=np.exp(-.5*(dx/(scale*1.7))**2)
    p=np.c_[np.ones(len(dx)),dx,dx*dx];th=np.linalg.lstsq(p*w[:,None],vals[pick]*w[:,None],rcond=None)[0]
    return th[0]
def grayink():
    frame=cv2.imread(str(OUT/'samples/2160.jpg'));return (255-gray(frame[T:B,L:R]).astype('float32'))/255
def measure():
    cap=cv2.VideoCapture(str(SRC));i=0;holes={};cent={};ell={};ratios=[];samps={}
    a=grayink();ii,jj=np.indices(a.shape);inkcent=np.array([(a*jj).sum(),(a*ii).sum()])/a.sum()
    while cap.grab():
        if i>2508:break
        if 2314<=i<=2508:
            ok,frame=cap.retrieve()
            if i<=2384:
                predicted=np.interp(i,[2314,2321,2330,2340,2350,2360,2375,2384],[-150,-85,-6,172,292,390,478,512])
                hole=hole_fit(frame,predicted)
                if hole is not None:holes[i]=hole
            raw=scan[str(i)]['ellipse']
            if i>=2378 and raw and min(raw[1])>3 and abs(raw[0][0]-635)<190 and abs(raw[0][1]-360)<36:
                G=ellipseH(raw);ec=np.array(raw[0]);xx,yy=ec
                l=max(0,int(xx-max(raw[1])*.57));r=min(1280,int(xx+max(raw[1])*.57+2))
                t=max(0,int(yy-max(raw[1])*.52));b=min(720,int(yy+max(raw[1])*.52+2))
                y,x=np.indices((b-t,r-l),dtype=np.float32);xy=np.stack((x+l,y+t),axis=-1)
                coords=(xy-ec)@np.linalg.inv(G).T;rr=(coords*coords).sum(2)
                dark=(255-gray(frame[t:b,l:r]).astype('float32'))/255
                hmask=(rr<.16**2)*dark**2
                hc=(xy*hmask[:,:,None]).sum((0,1))/max(hmask.sum(),.00001)
                if hmask.sum()<3 or np.linalg.norm(hc-ec)>max(raw[1])*.14:hc=ec
                ink=(rr>.2**2)&(rr<.91**2);wt=dark*ink
                if wt.sum()>1.6:
                    ic=(xy*wt[:,:,None]).sum((0,1))/wt.sum()
                    direction=np.linalg.solve(G,ic-hc)
                    if .20<np.linalg.norm(direction)<.86:
                        phi=np.degrees(np.arctan2(direction[1],direction[0]))-np.degrees(np.arctan2(*(rad+inkcent-center)[::-1]))
                        cent[i]=[hc.tolist(),ic.tolist(),phi]
                        ell[i]=G.tolist()
                        if i in direct and i<2441:
                            K=np.linalg.solve(G,direct[i][:,:2]);v=np.linalg.svd(K,compute_uv=False)
                            if v.max()/v.min()<1.31:ratios.append(float(v.mean()))
            if i in direct and i<2388:
                A=direct[i];k=np.linalg.svd(A[:,:2],compute_uv=False)
                if k[0]/k[1]<1.16 and abs(adiff(matrix_angle(A),angle(i)))<9 and .16<k.mean()<1.05:
                    samps[i]=[*(A@np.r_[center,1]-A[:,:2]@rad),k.mean()]
        i+=1
    cap.release();rratio=float(np.median(ratios))
    ratio=np.median([holes[j][2]/samps[j][2] for j in holes if j in samps and j>2338])
    rigid={}
    for j in range(2285,2314,2):rigid[j]=[*pivot,1.]
    for j,src in samps.items():rigid[j]=src
    for j,src in holes.items():
        v=[src[0],src[1],src[2]/ratio]
        if v[2]<1.06 and (j not in samps or abs(samps[j][2]-v[2])<.065):rigid[j]=v
    rsave={}
    for j in range(2136,2511):
        if j<=2313:
            G=rot(angle(j));origin=pivot+G@rad;A=aff(origin,G)
        elif j<2378 or j not in cent or j not in ell:
            if j>=2378:continue
            px,py,s=smooth_samples(rigid,j,10);G=rot(angle(j))*s;A=aff(np.array([px,py])+G@rad,G)
        else:
            hc,ic,phi=cent[j];G=np.array(ell[j])@rot(phi)*rratio
            A=np.c_[G,np.array(ic)-G@inkcent]
        rsave[j]=A.tolist()
    # Near edge-on, subpixel ink can momentarily disappear between samples.
    for j in range(2378,2508):
        if j in rsave:continue
        ks=sorted(rsave);left=max([k for k in ks if k<j],default=ks[0]);right=min([k for k in ks if k>j],default=ks[-1])
        if left==right:continue
        frac=(j-left)/(right-left);rsave[j]=(np.array(rsave[left])*(1-frac)+np.array(rsave[right])*frac).tolist()
    save('audit/op_track_final.json',dict(ref=refbox,matrices=rsave,ink_center=inkcent.tolist(),pivot=pivot.tolist(),radial_offset=rad.tolist(),source_radius=1/rratio,spindle_radius=float(ratio),holes_measured=len(holes),measured_ink_centroids=len(cent)))
    print('Spindle',np.round(pivot,2),'label/native ratio',1/rratio,'hole radius',ratio,'late centroids',len(cent),'frames',len(rsave))
if __name__=='__main__':measure()


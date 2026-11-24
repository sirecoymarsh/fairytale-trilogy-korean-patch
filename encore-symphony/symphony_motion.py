from assets import *
from labels import raw,emit,INFO,ART,artkey
from lettering import logo_layer
import numpy as np, cv2
from PIL import Image
def track():
    z=np.load(ROOT/'audit/symphony_tile_tracks.npz');base=z['base'];series=z['series']
    xs=np.rint(101.8+np.arange(-1,14)*30.2).astype(int);ys=np.rint(52+np.arange(-1,8)*30.1).astype(int)
    grids={}; paths={}
    for ix,(x,r) in enumerate(zip(xs,xs[1:])):
        for iy,(y,b) in enumerate(zip(ys,ys[1:])):
            key=ix,iy;center=np.array([(x+r)/2,(y+b)/2])
            tile=(base[:,0]>x+1)&(base[:,0]<r-1)&(base[:,1]>y+1)&(base[:,1]<b-1)
            grids[key]=(x,y,r,b);stats=[]
            for f in range(96):
                mask=tile&np.isfinite(series[f,:,0]);p=base[mask]-center;q=series[f,mask]-center
                if len(p)<4 or min(np.ptp(p,axis=0))<5:continue
                aff,keep=cv2.estimateAffine2D(p,q,method=cv2.RANSAC,ransacReprojThreshold=1.7,maxIters=400)
                if aff is None or keep.sum()<4:continue
                sv=np.linalg.svd(aff[:,:2],compute_uv=False)
                if sv.min()<.25 or sv.max()>1.75 or np.linalg.det(aff[:,:2])<.22:continue
                stats.append((f,aff.flatten()))
            if len(stats)>15:
                # Local interpolation follows the actual perspective and spin. Off-canvas
                # endpoints use the observed acceleration of that same piece.
                fi=np.array([q[0] for q in stats]);v=np.array([q[1] for q in stats])
                ident=np.array([1,0,0,0,1,0]);v[-1]=ident
                window=np.abs(fi[:,None]-fi[None,:])<=3
                smooth=np.stack([np.median(v[window[j]],axis=0) for j in range(len(v))]);smooth[-1]=ident
                path=[]
                for f in range(96):
                    if f>=fi[0]:
                        row=np.array([np.interp(f,fi,smooth[:,j]) for j in range(6)])
                    else:
                        # Extrapolate local motion of the first visible portion conservatively.
                        mask=fi<=fi[0]+17;tt=fi[mask]-fi[0]
                        speed=np.linalg.lstsq(np.c_[np.ones(len(tt)),tt],smooth[mask],rcond=None)[0][1]
                        row=smooth[0]+speed*(f-fi[0])
                        row[[0,1,3,4]]=np.clip(row[[0,1,3,4]],-1.25,1.5)
                    path.append(row.reshape(2,3))
                paths[key]=np.array(path)
    new=logo_layer((566,282),(101,53,467,229),'심포니')
    alpha=np.array(new,dtype='float32')/255;alpha[:,:,:3]*=alpha[:,:,3,None]
    cells=[];direct=borrow=0
    for key,(x,y,r,b) in grids.items():
        part=alpha[y:b,x:r]
        if not part.size or not part[:,:,3].max():continue
        donor=key if key in paths else min(paths,key=lambda k:(1.0*(k[0]-key[0]))**2+(k[1]-key[1])**2)
        direct+=key==donor;borrow+=key!=donor
        # For a piece with no Japanese ink, use the motion of the closest observed piece,
        # expressed in its true canvas coordinates.
        ref=grids[donor];origin=np.array([(ref[0]+ref[2])*.5,(ref[1]+ref[3])*.5])
        cells.append((x,y,part,origin,paths[donor]))
    original=read('audit/index.json')['Symphony'];last=original['grpo_ef/0096.wcg']['sha']
    for f in range(96):
        k=f'grpo_ef/{f+1:04d}.wcg';clean=Image.new('RGBA',(566,282));src=raw('Symphony',k)
        if original[k]['sha']==last:out=new.copy()
        else:
            acc=np.zeros((282,566,4),'float32')
            for x,y,part,origin,seq in cells:
                m=seq[f].copy();m[:,2]+=origin+m[:,:2]@(np.array([x,y])-origin)
                h,w=part.shape[:2];corners=np.array([[0,0],[w,0],[0,h],[w,h]])@m[:,:2].T+m[:,2]
                x0,y0=np.maximum(0,np.floor(corners.min(0)-2)).astype(int)
                x1,y1=np.minimum([566,282],np.ceil(corners.max(0)+2)).astype(int)
                if x1<=x0 or y1<=y0:continue
                m[:,2]-=[x0,y0]
                add=cv2.warpAffine(part,m,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR)
                region=acc[y0:y1,x0:x1];region[:]=add+region*(1-add[:,:,3,None])
            acc[:,:,:3]=np.divide(acc[:,:,:3],acc[:,:,3,None],out=np.zeros_like(acc[:,:,:3]),where=acc[:,:,3,None]>.00001)
            out=Image.fromarray(np.rint(acc.clip(0,1)*255).astype('uint8'))
        emit('Symphony',k,src,clean,out,'フェアリーテイル・シンフォニー','페어리테일 심포니','Localized wordmark split on measured original puzzle boundaries. Motion and tilt recovered from reverse-tracked corners in the original 96 frames.')
    m=read('audit/logos.json');m['Symphony'].update(INFO['Symphony']);save('audit/logos.json',m)
    save('audit/symphony_motion.json',dict(frames=96,recovered_tiles=direct,nearest_measured_motion=borrow,grid_x=xs.tolist(),grid_y=ys.tolist()))
    print('tiles with recovered transforms',direct,'neighbour registered',borrow)
if __name__=='__main__':track()


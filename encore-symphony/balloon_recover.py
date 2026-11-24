"""Fit the original painted balloon cutout to visible portions of the three balloons."""
from logos import *
from scipy import ndimage,optimize
def get_rgb():return original_title('Encore',0)[:,:,:3]
def native_shape():
    a=get_rgb();x0,y0,x1,y1=401,441,483,504
    patch=a[y0:y1,x0:x1];p=patch.astype('float32');r,g,b=cv2.split(p)
    hsv=cv2.cvtColor(patch,cv2.COLOR_RGB2HSV)
    sat=np.minimum(g-r,g-b)
    preliminary=((sat>53)&(g>100)&(hsv[:,:,0]>=44)&(hsv[:,:,0]<=77)).astype('uint8')
    _,labs,stats,_=cv2.connectedComponentsWithStats(preliminary)
    mask=(labs==1+stats[1:,4].argmax()).astype('uint8')
    # Keep the separate string pixels only where the measured string runs from the neck.
    y,x=np.indices(mask.shape);string=preliminary&(y>=28)&(x>42)&(x<73)&(y<52)
    mask=np.maximum(mask,string)
    # Subpixel matte at the antialiased painted rim.
    weak=np.clip((sat-6)/130,0,1)*np.clip((g-68)/104,0,1)
    alpha=np.where(cv2.erode(mask,np.ones((3,3),np.uint8))!=0,1.,weak)*cv2.dilate(mask,np.ones((3,3),np.uint8))
    # The highlight in the source is a lighter circular sweep on the left of the balloon.
    highlight=np.clip(np.maximum(r,b)/218,0,.85)*alpha
    # The cast shadow is offset below/right in the native art.
    base=arr(Image.open(ROOT/'art/Encore/grpe/3022/clean.png'))[:,:,:3].astype('float32')
    ysl=slice(y0-9,y1+8);xsl=slice(x0-12,x1+10);src=a[ysl,xsl].astype('float32');bg=base[ysl,xsl]
    ratio=(src+9)/(bg+9); border=np.ones(ratio.shape[:2],bool);border[11:-11,11:-11]=False
    coeff=np.median(ratio[border],axis=0);estimate=(base[y0:y1,x0:x1]+9)*coeff-9
    attenuation=np.clip(1-((p*np.array([.30,.59,.11])).sum(2)+1)/((estimate*np.array([.30,.59,.11])).sum(2)+1),0,.86)
    nearby=(cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))>0)
    shifted=np.roll(np.roll(mask,4,axis=1),6,axis=0);shadow_near=cv2.dilate(shifted,np.ones((5,5),np.uint8))!=0
    sm=np.where(shadow_near&nearby,attenuation,0.)
    yy,xx=np.indices(mask.shape);body=(mask>0)&(xx<53)
    c=np.array([xx[body].mean(),yy[body].mean()])
    dist=ndimage.distance_transform_edt(body)-ndimage.distance_transform_edt(~body)
    return c,alpha.astype('float32'),highlight.astype('float32'),sm.astype('float32'),dist.astype('float32')
BASE_C,ALPHA,HIGHLIGHT,SHADOW,DIST=native_shape()
def region(kind):
    return {'blue':(352,296,442,372),'red':(439,273,527,352),'yellow':(519,193,585,276)}[kind]
NAMES=['blue','red','yellow']
def evidence(kind):
    x0,y0,x1,y1=region(kind);yy,xx=np.indices((y1-y0,x1-x0));xx+=x0;yy+=y0
    pos=np.zeros(xx.shape,bool);neg=pos.copy();v=[]
    refs=[original_title(g,0)[:,:,:3] for g in GAMES]+[arr(Image.open(REF/'00/source.png'))[:,:,:3]]
    for ii,src in enumerate(refs):
        p=src[y0:y1,x0:x1];hsv=cv2.cvtColor(p,cv2.COLOR_RGB2HSV);h,s,b=cv2.split(hsv)
        if kind=='blue': good=(h>=95)&(h<=109)&(s>185)&(b>68);valid=np.ones(xx.shape,bool) if ii<2 else yy>324
        elif kind=='red':good=((h<=3)|(h>=176))&(s>220)&(b>80);valid=np.ones(xx.shape,bool) if ii<2 else ((yy>326)&(xx<508))
        else:good=(h>=25)&(h<=34)&(s>194)&(b>86);valid=(yy<264) if ii<2 else np.zeros(xx.shape,bool)
        # The lettering and its black shadow conceal evidence. Other saturated native
        # pigment remains a reliable observation of where the painted balloon ends.
        p0=good&valid
        if kind=='blue':p0&=(xx<420)&(yy<364)
        if kind=='red':p0&=(xx<502)&(yy<333)
        if kind=='yellow':p0&=(xx>530)&(xx<574)
        negative=valid&(s>130)&(b>110)&~cv2.dilate(good.astype('uint8'),np.ones((5,5),np.uint8)).astype(bool)
        pos|=p0;neg|=negative
        if np.any(p0):v.extend(p[p0].tolist())
    neg&=~pos
    if kind=='red':neg&=~((yy<328)&(yy>283)&(xx>451)&(xx<506)&((xx+yy)%2==1))
    # Paper lettering from the independent Requiem card is never inserted as colour.
    return xx,yy,pos,neg,np.array(v)
def transform(vals):
    x,y,sx,sy,ang=vals;theta=np.deg2rad(ang);cr,sn=np.cos(theta),np.sin(theta)
    lin=np.array([[cr,-sn],[sn,cr]])@np.diag([sx,sy]);return np.c_[lin,np.array([x,y])-lin@BASE_C]
def fit(kind):
    x,y,pos,neg,values=evidence(kind)
    ini={'blue':[394.,333.,1.28,1.26,12.],'red':[480.,310.,1.13,1.17,10.],'yellow':[552.,237.,.98,1.15,23.]}[kind]
    lo=np.array(ini)-[7,8,.32,.33,20];hi=np.array(ini)+[7,8,.32,.34,21]
    a=np.c_[x[pos],y[pos]];b=np.c_[x[neg],y[neg]]
    def loss(v):
        m=transform(v);iv=np.linalg.inv(m[:,:2]);ap=(a-m[:,2])@iv.T;bp=(b-m[:,2])@iv.T
        pa=ndimage.map_coordinates(DIST,ap.T[::-1],order=1,mode='constant',cval=-14)
        pb=ndimage.map_coordinates(DIST,bp.T[::-1],order=1,mode='constant',cval=-14)
        return (np.maximum(-pa-.2,0)**1.2).sum()/max(len(a),1)+(np.maximum(pb-.45,0)**1.2).sum()*1.5/max(len(a),1)+.012*np.linalg.norm((v-np.array(ini))/[4,4,.23,.22,14])
    result=optimize.differential_evolution(loss,list(zip(lo,hi)),seed=16,maxiter=30,popsize=7,tol=.004,polish=True)
    v=result.x;strong=values[np.max(values,axis=1)>=np.quantile(np.max(values,axis=1),.88)];color=np.median(strong,axis=0).clip(0,255)
    return dict(geometry=v.tolist(),color=color.tolist(),loss=float(result.fun),positive=int(pos.sum()))
def overlay(sky,settings):
    scene=sky.astype('float32').copy()
    for name,rec0 in settings.items():
        mat=transform(rec0['geometry']);dsize=sky.shape[1::-1]
        alpha=cv2.warpAffine(ALPHA,mat,dsize,flags=cv2.INTER_CUBIC).clip(0,1)
        hi=cv2.warpAffine(HIGHLIGHT,mat,dsize,flags=cv2.INTER_LINEAR).clip(0,.82)
        shadow=cv2.warpAffine(SHADOW,mat,dsize,flags=cv2.INTER_CUBIC).clip(0,.84)
        color=np.asarray(rec0['color']).astype('float32')
        body=color+(255-color)*hi[:,:,None]
        scene=scene*(1-shadow[:,:,None]);scene=scene*(1-alpha[:,:,None])+body*alpha[:,:,None]
    return scene.clip(0,255).round().astype('uint8')
def assemble(game,i,settings):
    src=original_title(game,i);path=ART/game/'grpe'/f'9101-{i}';prior=arr(Image.open(path/'clean.png'))
    sky_ref=arr(Image.open(ART/'Encore/grpe/3022/clean.png'));m=registered_ink(game)
    sky=sky_colours(sky_ref,prior,~m);paint=overlay(sky,settings)
    yy,xx=np.indices(m.shape);z=np.zeros_like(m,'float32')
    for name,(x,y,wx,hy) in {'blue':(397,334,44,43),'red':(478,309,42,37),'yellow':(553,236,32,43)}.items():
        radius=((xx-x)/wx)**2+((yy-y)/hy)**2;z=np.maximum(z,np.clip((1.52-radius)*2.4,0,1))
    # Use the registered original cloud pattern up to the unprinted lower border. Do
    # not import the separate parchment edge or the film's different castle silhouette.
    band=np.clip((yy-303)/12,0,1)*np.clip((358-yy)/10,0,1)*np.clip((xx-267)/17,0,1)*np.clip((543-xx)/17,0,1)
    z=np.maximum(z,band)
    # Apply only on the original Japanese mark and its shadow. Unprinted portions of
    # the native balloons (including the ends of their strings) are original pixels.
    support=cv2.GaussianBlur(dil(m,23).astype('float32'),(0,0),3.5)
    z*=support
    out=prior.copy();out[:,:,:3]=np.rint(prior[:,:,:3]*(1-z[:,:,None])+paint*z[:,:,None]).astype('uint8')
    return out
def main(mode):
    fp=ROOT/'audit/balloon_fits.json'
    if not fp.exists():save(fp,{k:fit(k) for k in NAMES})
    settings=read(fp)
    if mode=='sample':
        a=Image.fromarray(assemble('Encore',0,settings));a.crop((245,125,710,365)).save(ROOT/'audit/balloon-sample.png')
        print(settings);return
    index=read('audit/index.json');manifest=read('audit/logos.json')
    for game,name in zip(GAMES,['앙코르','심포니']):
        ink=logo_layer((1280,720),(249,127,720,344),name)
        for i in range(8):
            k=next(k for k in index[game] if k.startswith(f'grpe/9101.lwg/{i}:'))
            org=Image.fromarray(original_title(game,i));cl=Image.fromarray(assemble(game,i,settings));out=cl.copy();out.alpha_composite(ink)
            row=manifest[game][k];emit(game,k,org,cl,out,row['source_ja'],row['target_ko'],'Verified adjacent title frames and registered native cloud print. Occluded balloon outlines fitted to the visible source edges with the native unlettered balloon cutout and pigment.')
        manifest[game].update(INFO[game])
    save('audit/logos.json',manifest)
if __name__=='__main__':main(sys.argv[1])



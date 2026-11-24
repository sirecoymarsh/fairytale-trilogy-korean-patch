from plates import *

import re
from restoration import restore
REF=Path('P:/AI/Codex/projects/migrated-from-c/onedrive-chatgpt/페이러 테일 및 도화이담 시리즈/asset_cleanup_20260908/layers/title_logo_frames')
def dil(m,k):
    return cv2.dilate(m.astype('uint8'),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))).astype(bool)
def registered_ink(g):
    if g=='Encore':
        p=Image.open(ROOT/'research/fairy_encore-frt_encore_logo.png').convert('RGBA').crop((0,0,256,144));w,h,x,y=466,211,252,132
    else:
        p=raw(g,'grpo_ef/0096.wcg');w,h,x,y=470,224,246,127
    p=p.crop(p.getchannel('A').getbbox()).resize((w,h),Image.Resampling.LANCZOS)
    out=np.zeros((720,1280),np.uint8);out[y:y+h,x:x+w]=arr(p)[:,:,3]
    # Include the soft title shadow beyond the antialiasing in the publisher's transparent mark.
    return dil(out>0,13)
def original_title(g,i):return arr(Image.open(ROOT/f'audit/full/{g}/grpe/9101-{i}.png'))
def encore_credit():
    g,k='Encore','grpe/3022.wcg';s=raw(g,k);a=arr(s);q=a[:,:,:3].copy()
    mask=np.zeros(q.shape[:2],bool)
    bands=[(537,135,699,154),(588,158,649,176),(511,202,728,222),(575,225,659,243),(597,275,641,287),(548,294,690,311),(542,339,695,355),(528,358,711,380),(564,383,671,401),(502,406,736,424),(564,429,671,446),(602,477,635,491),(484,495,751,514),(579,545,657,559),(544,564,691,581)]
    for x,y,r,b in bands:
        x-=3;y-=3;r+=4;b+=4;p=q[y:b,x:r].astype(int);mask[y:b,x:r]|=(p.max(2)<64)&(p.max(2)-p.min(2)<27)
    mask=dil(mask,11)
    result=restore(a,mask,(358,65,576,576))
    # Use native paper texture to replace the fine grain lost inside the hidden ink.
    donor=q[:,np.minimum(np.arange(q.shape[1])+325,q.shape[1]-1),:].astype('float32')
    grain=donor-cv2.GaussianBlur(donor,(0,0),.9)
    result[:,:,:3][mask]=np.clip(np.rint(result[:,:,:3].astype('float32')+.34*grain),0,255).astype('uint8')[mask]
    clean=Image.fromarray(result);out=clean.copy()
    lines=[('기획·원안·시나리오',22),('우미하라 노조무',25),('',4),('캐릭터 디자인·원화',22),('오이시 류코',25),('',4),('BGM',20),('삿포로 모모코',25),('',4),('오프닝 테마 『페어리테일』',23),('작사·노래  Rita',22),('작곡·편곡  Blueberry & Yogurt',22),('',4),('판매',21),('주식회사 비즈니스 파트너',23),('',4),('제작·저작',21),('Liar-Soft',26)]
    y=(720-sum(p+4 for st,p in lines))//2
    for st,p in lines:
        if st:fittext(out,(385,y,858,y+p+4),st,p,(20,10,12,255),FONT,'center',2,'#f4e7cf')
        y+=p+4
    for game in GAMES:
        if game != g and blob(source(game),k) != blob(source(g),k):
            raise ValueError('Shared staff card originals differ')
        emit(game,k,s,clean,out,'スタッフクレジット','\n'.join(t for t,p in lines if t),'Source ink/shadow mask, locally restored colour and boundaries with donor grain from the same printed end card.')
    return result
def sky_colours(credit,observed,valid):
    # The original cloud/sky texture registers at native coordinates. Match the end card vignette to the title state through unprinted corresponding sky pixels.
    src=credit[:,:,:3].astype('float32');dst=observed[:,:,:3].astype('float32')
    yy,xx=np.indices(valid.shape)
    valid=valid&(xx>175)&(xx<781)&(yy>109)&(yy<485)
    ratios=(dst+8)/(src+8)
    near=np.max(np.abs(np.log(ratios+.0001)),2)<.68
    good=valid&near
    field=[]
    for c in range(3):
        ratio=np.clip(ratios[:,:,c],.75,1.8);m=(good&(src[:,:,c]>24)&(src[:,:,c]<212)&(dst[:,:,c]<249)).astype('float32')
        def smooth(x):return cv2.GaussianBlur(x,(0,0),39)
        v=smooth(ratio*m)/np.maximum(smooth(m),.0001)
        robust=m*(np.abs(ratio-v)<.19)
        num=smooth(ratio*robust);den=smooth(robust)
        fused=np.where(den>.002,num/np.maximum(den,.0001),v);fused=np.where(fused>.5,fused,1.23)
        field.append(np.clip((src[:,:,c]+8)*fused-8,0,255))
    return np.stack(field,2).astype('uint8')
def recover_title(g,i,frames,masks,req,credit):
    other='Symphony' if g=='Encore' else 'Encore'
    a=frames[g][i];my=masks[g];their=masks[other]
    # Register the companion animation using unprinted background, lights, and moving foliage.
    px=np.zeros(my.shape,bool);px[100:375,200:755]=True;seen=px&~(my|their)
    def score(v):return np.mean(np.abs(a[seen,:3].astype(int)-v[seen,:3].astype(int)))
    o=min(frames[other],key=score)
    base=a.copy();unknown=my.copy()
    can=my&~their;base[can]=o[can];unknown[can]=False
    # Requiem contains the same moving castle outside its separate parchment. Include its authored shadow in the exclusion.
    rp=np.zeros(my.shape,bool);rp[113:350,199:622]=True
    free=my&~rp
    if free.any():
        ring=dil(free,23)&~my&~rp
        if ring.any(): r=min(req,key=lambda z:np.abs(z[ring,:3].astype(int)-a[ring,:3].astype(int)).mean())
        else:r=req[i]
        can=unknown&~rp;base[can]=r[can];unknown[can]=False
    # In the remaining intersections the registered original end-card sky supplies the actual printed texture and its colour boundaries.
    sky=sky_colours(credit,base,~unknown)
    # The sky grain is a known native sample. Recover the contours hidden in both
    # title sources from the unprinted foreground on all sides of each mask.
    inferred=restore(base,unknown,(189,29,576,448))[:,:,:3].astype('float32')
    texture=sky.astype('float32')-cv2.GaussianBlur(sky.astype('float32'),(0,0),1.05)
    close=(np.max(np.abs(cv2.GaussianBlur(inferred,(0,0),2)-cv2.GaussianBlur(sky.astype('float32'),(0,0),2)),axis=2)<35)
    yy,xx=np.indices(unknown.shape)
    foreground=np.zeros_like(unknown,dtype='float32')
    # Three balloons and the castle turret cross the native sky. Keep the actual
    # registered sky elsewhere, including its paper edges, seams and cloud ink.
    for x,y,rx,ry in [(393,333,30,32),(477,312,29,29),(551,235,23,32)]:
        radius=((xx-x)/rx)**2+((yy-y)/ry)**2
        foreground=np.maximum(foreground,np.clip((1.30-radius)*3.3,0,1))
    roof=np.asarray([[532,306],[549,281],[563,276],[571,245],[591,256],[599,225],[629,210],[684,211],[718,323],[590,350],[545,333]],'int32')
    castle=np.zeros_like(unknown,dtype='uint8');cv2.fillPoly(castle,[roof],255)
    foreground=np.maximum(foreground,cv2.GaussianBlur(castle.astype('float32')/255,(0,0),1.4))
    inferred=np.clip(inferred+texture*np.where(close,.63,.22)[:,:,None],0,255)
    rec=np.rint(sky*(1-foreground[:,:,None])+inferred*foreground[:,:,None]).astype('uint8')
    # The parchment ends above the hanging blue and red balloons. Its independently
    # unobstructed lower contours are native pixels and take priority over prediction.
    native=req[i][:,:,:3];hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
    exposed=(yy>=325)&(yy<371)&(xx>=369)&(xx<=524)&(hsv[:,:,1]>180)&(hsv[:,:,2]>101)
    native_close=np.abs(native.astype('int16')-rec.astype('int16')).max(2)<55
    rec[exposed&native_close]=native[exposed&native_close]
    base[:,:,:3][unknown]=rec[unknown]
    return base,dict(companion_pixels=int((my&~their).sum()),series_backdrop_pixels=int((my&their&~rp).sum()),registered_sky_and_boundary_reconstruction=int(unknown.sum()))
def titles(credit):
    data=read('audit/index.json');masks={g:registered_ink(g) for g in GAMES}
    frames={g:[original_title(g,i) for i in range(8)] for g in GAMES}
    req=[arr(Image.open(REF/f'{i:02d}/source.png')) for i in range(8)]
    evidence={}
    for g,name in [('Encore','앙코르'),('Symphony','심포니')]:
        ink=logo_layer((1280,720),(249,127,720,344),name,False)
        for i in range(8):
            key=next(k for k in data[g] if k.startswith(f'grpe/9101.lwg/{i}:'));a=frames[g][i]
            base,stats=recover_title(g,i,frames,masks,req,credit);cl=Image.fromarray(base);out=cl.copy();out.alpha_composite(ink)
            emit(g,key,Image.fromarray(a),cl,out,'フェアリーテイル・'+('アンコール' if g=='Encore' else 'シンフォニー'),'페어리테일 '+name,'Registered companion title frames and Requiem castle; jointly occluded contours inferred locally with grain from the registered original sky. Korean-only logo on separate layer.')
            evidence[g+'/'+str(i)]=stats
    save('audit/title_background_recovery.json',evidence)
def animation():
    from symphony_motion import track
    track()
if __name__=='__main__':
    credit=encore_credit();titles(credit);animation();save('audit/logos.json',INFO)


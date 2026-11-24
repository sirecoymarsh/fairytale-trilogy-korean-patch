from focus import *
from wording import *
import numpy as np, cv2
from PIL import ImageFont, ImageFilter
FONT=Path('C:/Windows/Fonts/malgunbd.ttf')
HAND=RBASE/'tools/fonts/Gaegu-Bold.ttf'
SERIF=Path('C:/Windows/Fonts/NotoSerifKR-VF.ttf')
MENU=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
ART=ROOT/'art'
INFO={}
def raw(g,key): return Image.open(fullpath(g,key)).convert('RGBA')
def arr(im):return np.array(im.convert('RGBA'))
def fittext(im,box,s,size=26,fill=(255,255,255,255),font=HAND,align='center',stroke=0,stroke_fill=None):
    x0,y0,x1,y1=box
    if not s:return
    for points in range(size,7,-1):
        face=ImageFont.truetype(str(font),points)
        b=face.getbbox(s,stroke_width=stroke)
        if b[2]-b[0]<=x1-x0 and b[3]-b[1]<=y1-y0:break
    if b[2]-b[0]>x1-x0 or b[3]-b[1]>y1-y0:raise ValueError((s,box,b))
    w,h=b[2]-b[0],b[3]-b[1];x=x0 if align=='left' else x1-w if align=='right' else round((x0+x1-w)/2)
    y=round((y0+y1-h)/2);ImageDraw.Draw(im).text((x-b[0],y-b[1]),s,font=face,fill=fill,stroke_width=stroke,stroke_fill=stroke_fill or fill)
def artkey(g,key):
    b,n,*sub=key.split('/');return g+'/'+b+'/'+n.split('.')[0]+('-'+sub[0].split(':')[0] if sub else '')
def emit(g,key,original,clean,final,jp,ko,method):
    src,cln,dst=map(arr,(original,clean,final));assert src.shape==cln.shape==dst.shape
    path=ART/artkey(g,key);path.mkdir(parents=True,exist_ok=True)
    erased=(src!=cln).any(2); drawn=(dst!=cln).any(2);owned=erased|drawn
    for label,im in [('clean',clean),('final',final),('ownership',Image.fromarray((owned*255).astype('uint8')))]:
        im.save(path/(label+'.png'))
    if not owned.any(): raise ValueError(('empty',g,key))
    rec=dict(source_ja=jp,target_ko=ko,method=method,geometry=list(original.size),outside_owned_changes=int(((src!=dst).any(2)&~owned).sum()),pixels_erased=int(erased.sum()),pixels_drawn=int(drawn.sum()))
    INFO.setdefault(g,{})[key]=rec
def recolor_blank(blank,target):
    b=arr(blank);t=arr(target)
    # The five save colours share exactly the same paper grain. Recover the per-colour lookup at the same coordinates in a blank part of this plate.
    base=b[9:70,459:510,:3];compare=t[9:70,459:510,:3]
    good=compare.max(2)<125
    src=base[...,2][good]; dest=compare[good]
    levels=np.unique(src);median=np.array([np.median(dest[src==n],axis=0) for n in levels])
    out=b.copy()
    for c in range(3):out[:,:,c]=np.rint(np.interp(b[:,:,2],levels,median[:,c])).astype('uint8')
    return out
def slot_clean(original,template,box,threshold=6):
    a=arr(original);t=np.asarray(template);x,y,r,b=box
    part=a[y:b,x:r];ref=t[y:b,x:r]
    delta=np.abs(part[:,:,:3].astype(int)-ref[:,:,:3].astype(int)).max(2)
    m=delta>threshold
    if threshold:m=cv2.dilate(m.astype('uint8'),np.ones((3,3),np.uint8)).astype(bool)
    part[m]=ref[m];return Image.fromarray(a)
def clear_white(original,box,color=(19,1,1),red=False):
    a=arr(original);l,t,r,b=box;q=a[t:b,l:r]
    # Glyphs lie on the solid, opaque interior of the ink stroke.
    if red:m=(q[:,:,0]>color[0]+2)&(q[:,:,0].astype(int)-q[:,:,1]>20)
    else:m=(q[:,:,1]>color[1]+2)&(q[:,:,2]>color[2]+2)
    q[m]=(*color,255)
    return Image.fromarray(a)
def localized(g,key,clean,fields,jp,ko,method):
    src=raw(g,key); out=clean.copy()
    for args in fields:fittext(out,*args)
    emit(g,key,src,clean,out,jp,ko,method)
def text_only(g,key,jp,ko,fill,font=HAND,points=32,stroke=0,stroke_fill=None):
    src=raw(g,key); c=Image.new('RGBA',src.size);bbox=src.getchannel('A').getbbox()
    localized(g,key,c,[(bbox,ko,points,fill,font,'center',stroke,stroke_fill)],jp,ko,'Isolated type layer; use original alpha bounds.')
def rows():
    d=RBASE/'staging/grpo_ex_title_translation_v1'
    tmps=[arr(Image.open(d/name)) for name in ('exact_observed_template_48_64_80.png','clean_template_160_0_64.png','clean_template_80_96_16.png')]
    blank=Image.open(RBASE/'staging/grps_save_metadata_korean_v1_source/dt1_clean_title_slab.png')
    for g,words in [('Encore',EN),('Symphony',SY)]:
        for code,(jp,ko) in words.items():
            for shift in (1000,2000):
                key='grpo_ex/'+str(code+shift)+'.wcg';p=fullpath(g,key)
                if not p.exists():continue
                s=raw(g,key);a=arr(s);b=min(tmps,key=lambda t:np.abs(t[20,42,:3].astype(int)-a[20,42,:3].astype(int)).sum())
                c=slot_clean(s,b,(38,3,384,37),1)
                color=(255,255,255,255) if shift==1000 else (255,66,76,255)
                localized(g,key,c,[((39,4,350,36),ko,33,color)],jp,ko,'Registered blank 390×40 gallery plate, original normal/hover foreground.')
            key=f'grps/dt1_{code}.wcg'
            if not fullpath(g,key).exists():continue
            s=raw(g,key);template=recolor_blank(blank,s);c=slot_clean(s,template,(157,9,512,47),5); c=slot_clean(c,template,(121,48,512,73),5)
            if g=='Encore' and code not in (1121,1501):
                title=ROUTES[code//100-11]
                fields=[((159,10,509,44),title[1],32,(255,255,255,255),HAND,'left'),((123,47,508,73),ko,23,(255,255,255,255),HAND,'left')]
                src_text=title[0]+' / '+jp;tgt_text=title[1]+' / '+ko
            else:
                fields=[((159,10,509,46),ko,32,(255,255,255,255),HAND,'left')];src_text=jp;tgt_text=ko
            localized(g,key,c,fields,src_text,tgt_text,'Registered 520×80 blank save plate, calibrated against the original chapter colour.')
    plates=[arr(raw('Encore',f'grpo/0{i:03d}.wcg')) for i in range(201,207)]
    shared=np.min(plates,axis=0);scaled=np.asarray(Image.fromarray(tmps[0]).resize((780,80),Image.Resampling.BICUBIC))
    residue=shared[:,:,1].astype(int)>scaled[:,:,1].astype(int)+8;shared[residue]=scaled[residue]
    for i,(jp,ko) in enumerate(ROUTES,201):
        key=f'grpo/{i:04d}.wcg';s=raw('Encore',key);c=slot_clean(s,shared,(90,4,766,77),3)
        localized('Encore',key,c,[((94,6,683,73),ko,57)],jp,ko,'Six registered full-size companion plates and the matching blank gallery template.')
def render_movie_popup(src, master):
    with Image.open(master) as image:
        ink=image.convert('RGBA')
    ink=ink.crop(ink.getchannel('A').point(lambda a: 255 if a>5 else 0).getbbox())
    left,top,right,bottom=src.getchannel('A').getbbox()
    # The companion '환경 설정' hover lettering is 85 native pixels tall.
    height=min(85,bottom-top-2)
    width=round(ink.width*height/ink.height)
    if width>=right-left:
        raise ValueError('Movie hover lettering exceeds its original slot')
    plate=Image.new('RGBA',src.size)
    plate.alpha_composite(ink.resize((width,height),Image.Resampling.LANCZOS),(right-width-1,round((top+bottom-height)/2)))
    return plate

def music():
    for g in GAMES:
        for n,(jp,ko) in enumerate(TRACKS,1):
            for prefix in (9700,9800):
                key=f'grpo_ex/{prefix+n}.wcg';s=raw(g,key);a=arr(s);red=prefix==9800
                c=clear_white(s,(8,4,466,46),red=red)
                color=(228,29,29,255) if red else (255,255,255,255)
                localized(g,key,c,[((15,6,460,44),f'{n:02d}. '+ko,38,color,HAND,'left')],jp,ko,'White/red lettering isolated on original opaque ink strip.')
        for n in (9518,9618):
            text_only(g,f'grpo_ex/{n}.wcg','歌詞','가사',(247,74,79,255) if n==9618 else (19,10,12,255),HAND,90,4,'white')
        key='grpo_ex/9502.wcg';s=raw(g,key);a=arr(s);c=a.copy();c[0:33,:,:]=[0,0,0,0]
        localized(g,key,Image.fromarray(c),[((8,2,1010,31),'작곡·편곡  Blueberry & Yogurt (01·11)   /   삿포로 모모코 (02·03·04·05·06·07·08·09·10)',25,'white',SERIF)],'作・編曲：Blueberry＆Yogurt ／ 作・編曲：さっぽろももこ','작곡·편곡, 트랙 번호','Isolated text above the original underline.')
    import build_fairytale_grpo_ui_master as title
    for key,small in [('grpo/0006.wcg',True),('grpo/0106.wcg',False)]:
        src=raw('Encore',key)
        if small:
            a=arr(src); c,_,_=title.restore_small_plate(a,title.neutral_bright_mask(a));clean=Image.fromarray(c);out,_,_=title.render_small_label(src,'영상',MENU)
        else:
            clean=Image.new('RGBA',src.size)
            master=ART/artkey('Encore',key)/'ink_master.png'
            out=render_movie_popup(src,master)
        method='Requiem oblique miniature.' if small else '환경 설정과 같은 높이와 오른쪽 정렬을 적용한 영상 손글씨 도안.'
        emit('Encore',key,src,clean,out,'Movie' if small else 'ムービー','영상',method)
    for g in GAMES:
        src=raw(g,'grps/dat_new.wcg');s=src.getchannel('A').getbbox();text_only(g,'grps/dat_new.wcg','NEW!','신규!',(238,13,20,255),HAND,32)
        key='grpe/9003.wcg';s=raw(g,key);r=RBASE/'staging/grpe_gallery_headers_korean_v1_assets'
        j=arr(Image.open(r/'source_png/9003.png'));k=arr(Image.open(r/'candidate_png/9003.png'));a=arr(s)
        region=np.s_[0:124,0:349,:];assert np.array_equal(a[region],j[region]),'Header placement mismatch'
        ch=(j!=k).any(2);ch[124:]=False;ch[:,349:]=False
        out=a.copy();out[ch]=k[ch];clean=clear_white(s,(202,28,321,100))
        emit(g,key,s,clean,Image.fromarray(out),'BGM鑑賞','BGM 감상','Verified matching header crop from Requiem; preserve the game-specific BGM slots.')
        key='grpe/9905.wcg';s=raw(g,key);a=arr(s)
        # Entire source label is on a near-black wax stroke. Use the ink colour measured underneath its glyphs.
        c=clear_white(s,(43,34,367,86),color=(19,1,1))
        localized(g,key,c,[((48,25,363,90),'시나리오 선택',64,'white',HAND)],'シナリオ選択','시나리오 선택','Printed white label on dark ink.')
def main():
    rows(); music();save('audit/labels.json',INFO)
if __name__=='__main__':main()

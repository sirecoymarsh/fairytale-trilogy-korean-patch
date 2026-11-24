from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2, hashlib, json, numpy as np, re

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'review_input'/'0011_original.png'
DONOR=ROOT/'review_input'/'0011_clean.png'
OUT=ROOT/'work'/'library_book_0011_alice_round_v4'
FONT=Path(r'C:\Windows\Fonts\gulim.ttc')
S=4

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def main():
    for d in ['source','clean','candidate','owned_mask','removed_text_mask','evidence']:
        (OUT/d).mkdir(parents=True,exist_ok=True)
    src_im=Image.open(SRC).convert('RGBA')
    src=np.array(src_im)
    h,w=src.shape[:2]
    if (w,h)!=(150,568): raise SystemExit(src_im.size)

    # Title-only ownership. The red cloth caps and blue rules stay byte-identical.
    roi=np.zeros((h,w),np.uint8)
    roi[86:433,54:98]=255
    gray=cv2.cvtColor(src[...,:3],cv2.COLOR_RGB2GRAY)
    chroma=src[...,:3].max(2).astype(np.int16)-src[...,:3].min(2).astype(np.int16)
    ink=((gray<138) & (roi>0) & (src[...,3]>0)).astype(np.uint8)*255
    ink=cv2.dilate(ink,np.ones((5,5),np.uint8),iterations=1)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))

    # Reconstruct the woven paper face from its untouched left/right fibres.
    # This removes the full Japanese title without placing a flat rectangular label.
    clean_region=np.zeros((h,w),np.uint8)
    clean_region[82:433,53:99]=255
    y0,y1=82,433; x0,x1=53,99
    left=np.median(src[y0:y1,50:56,:3].astype(np.float32),axis=1)
    right=np.median(src[y0:y1,96:102,:3].astype(np.float32),axis=1)
    left=cv2.GaussianBlur(left[:,None,:],(1,0),sigmaX=0,sigmaY=3.2)[:,0,:]
    right=cv2.GaussianBlur(right[:,None,:],(1,0),sigmaX=0,sigmaY=3.2)[:,0,:]
    t=np.linspace(0,1,x1-x0,dtype=np.float32)[None,:,None]
    paper=left[:,None,:]*(1-t)+right[:,None,:]*t
    rng=np.random.default_rng(1101)
    mono=rng.normal(0,2.4,paper.shape[:2]).astype(np.float32)
    coarse=cv2.GaussianBlur(rng.normal(0,1.0,paper.shape[:2]).astype(np.float32),(0,0),2.2)*2.0
    paper += (mono+coarse)[:,:,None]
    clean=src.copy()
    clean[y0:y1,x0:x1,:3]=np.clip(paper,0,255).astype(np.uint8)
    clean_im=Image.fromarray(clean,'RGBA')

    # Heavy square Korean glyphs with the source's dark-brown core,
    # red underprint, slight offset, and uneven old-print edge.
    glyph_hi=Image.new('L',(w*S,h*S),0)
    draw=ImageDraw.Draw(glyph_hi)
    font=ImageFont.truetype(str(FONT),35*S,index=0)
    try: font.set_variation_by_name('Black')
    except Exception: pass
    text='이상한나라의앨리스'
    top=94
    bottom=423
    advance=(bottom-top)/len(text)
    cx=76*S
    for i,ch in enumerate(text):
        y=(top+i*advance)*S
        box=draw.textbbox((0,0),ch,font=font,stroke_width=1*S)
        tw,th=box[2]-box[0],box[3]-box[1]
        px=cx-tw/2-box[0]
        py=y+(advance*S-th)/2-box[1]
        draw.text((px,py),ch,font=font,fill=255,stroke_width=1*S,stroke_fill=255)
    glyph=glyph_hi.resize((w,h),Image.Resampling.LANCZOS)
    ga=np.array(glyph.filter(ImageFilter.GaussianBlur(0.62))).astype(np.float32)
    ga=np.clip((ga-35.0)*1.30,0,255)
    print_rng=np.random.default_rng(1011)
    ga=np.clip(ga+print_rng.normal(0,4.0,ga.shape)*(ga>12),0,255).astype(np.uint8)
    glyph=Image.fromarray(ga,'L')
    shadow_alpha=glyph.filter(ImageFilter.GaussianBlur(0.62)).transform(
        (w,h),Image.Transform.AFFINE,(1,0,-1.1,0,1,-1.0),resample=Image.Resampling.BICUBIC
    ).point(lambda v:int(v*0.82))
    shadow=Image.new('RGBA',(w,h),(111,57,60,0)); shadow.putalpha(shadow_alpha)
    core=Image.new('RGBA',(w,h),(45,22,25,0)); core.putalpha(glyph)
    layer=Image.new('RGBA',(w,h),(0,0,0,0)); layer.alpha_composite(shadow); layer.alpha_composite(core)
    cand=clean_im.copy(); cand.alpha_composite(layer)
    cand_arr=np.array(cand)
    owned=clean_region.copy()
    # Korean title may extend slightly beyond the removed Japanese glyph mask.
    text_alpha=np.array(layer.getchannel('A'))
    owned=np.maximum(owned,cv2.dilate((text_alpha>0).astype(np.uint8)*255,np.ones((5,5),np.uint8)))
    cand_arr[owned==0]=src[owned==0]
    cand=Image.fromarray(cand_arr,'RGBA')

    paths={
      'source':OUT/'source'/'0011.png','clean':OUT/'clean'/'0011.png','candidate':OUT/'candidate'/'0011.png',
      'owned_mask':OUT/'owned_mask'/'0011.png','removed_text_mask':OUT/'removed_text_mask'/'0011.png'}
    src_im.save(paths['source']); clean_im.save(paths['clean']); cand.save(paths['candidate'])
    Image.fromarray(owned,'L').save(paths['owned_mask']); Image.fromarray(ink,'L').save(paths['removed_text_mask'])
    ev=Image.new('RGB',(w*3,h),'white')
    for i,im in enumerate([src_im,clean_im,cand]): ev.paste(im.convert('RGB'),(i*w,0))
    ev=ev.resize((w*6,h*2),Image.Resampling.NEAREST)
    ev.save(OUT/'evidence'/'0011_source_clean_candidate_2x.png')

    outside=owned==0
    val={
      'outside_owned_mask_byte_exact':bool(np.array_equal(src[outside],np.array(cand)[outside])),
      'top_red_cap_byte_exact':bool(np.array_equal(src[:80],np.array(cand)[:80])),
      'bottom_red_cap_byte_exact':bool(np.array_equal(src[454:],np.array(cand)[454:])),
      'blue_rules_byte_exact':bool(np.array_equal(src[55:82],np.array(cand)[55:82]) and np.array_equal(src[434:455],np.array(cand)[434:455])),
      'removed_source_ink_pixels':int((ink>0).sum()),
      'old_title_exact_ratio_after_clean':float(np.mean(np.all(src[ink>0]==clean[ink>0],axis=1))),
    }
    manifest={
      'schema':'fairytale-requiem-library-book-spine-alice-round-v4','status':'USER_REVIEW_REQUIRED_NOT_INSTALLED',
      'surface':'grpo_lib/0011','target':'이상한 나라의 앨리스','contract':{
        'old_title_removed_before_typesetting':True,'no_rectangular_label_overpaint':True,
        'original_red_caps_preserved':True,'original_blue_rules_preserved':True,'original_spine_silhouette_preserved':True,'heavy_japanese_print_character_matched':True,'per_book_typeface_profile':'alice_round_gulim_burgundy','installed':False},
      'validation':val,'files':{k:str(v) for k,v in paths.items()},'sha256':{k:sha(v) for k,v in paths.items()}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(val|{'output':str(OUT)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

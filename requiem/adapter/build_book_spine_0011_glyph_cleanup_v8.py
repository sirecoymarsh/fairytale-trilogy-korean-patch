from __future__ import annotations
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import cv2,hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'review_input'/'0011_original.png'
OUT=ROOT/'work'/'library_book_0011_glyph_cleanup_v8'
FONT=Path(r'C:\Windows\Fonts\gulim.ttc')
S=4

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def main():
 for d in ['source','clean','candidate','owned_mask','removed_text_mask','evidence']:(OUT/d).mkdir(parents=True,exist_ok=True)
 src_im=Image.open(SRC).convert('RGBA');src=np.array(src_im);h,w=src.shape[:2]
 if (w,h)!=(150,568):raise SystemExit(src_im.size)
 # Detect only the dark/red Japanese ink inside the authored paper face.
 roi=np.zeros((h,w),np.uint8);roi[86:433,56:97]=255
 rgb=src[...,:3].astype(np.float32);gray=cv2.cvtColor(src[...,:3],cv2.COLOR_RGB2GRAY)
 ink=((gray<172)&(roi>0)&(src[...,3]>0)).astype(np.uint8)*255
 ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 ink=cv2.dilate(ink,np.ones((5,5),np.uint8),iterations=1)
 # Estimate the hidden paper with normalized convolution from nearby untouched source pixels.
 # This preserves the original face and changes only the full Japanese-ink silhouette.
 valid=np.zeros((h,w),np.float32);valid[80:435,50:103]=1.0;valid[ink>0]=0.0;valid[src[...,3]==0]=0.0
 rgbf=src[...,:3].astype(np.float32)
 sigma=7.0
 den=cv2.GaussianBlur(valid,(0,0),sigma)+1e-4
 background=np.zeros_like(rgbf)
 for c in range(3):background[...,c]=cv2.GaussianBlur(rgbf[...,c]*valid,(0,0),sigma)/den
 paper_rng=np.random.default_rng(8011)
 grain=cv2.GaussianBlur(paper_rng.normal(0,2.2,(h,w)).astype(np.float32),(0,0),0.35)
 fill=np.clip(background+grain[...,None],0,255)
 core_mask=ink.astype(np.float32)/255.0
 soft=cv2.GaussianBlur(core_mask,(0,0),0.55)
 alpha=np.maximum(core_mask,soft*0.70)[...,None]
 alpha[:84]=0.0;alpha[433:]=0.0
 clean=src.copy().astype(np.float32)
 clean[...,:3]=rgbf*(1-alpha)+fill*alpha
 clean[...,3]=src[...,3]
 clean=np.clip(clean,0,255).astype(np.uint8)
 owned_clean=(alpha[...,0]>0.002)
 clean[~owned_clean]=src[~owned_clean]
 clean_im=Image.fromarray(clean,'RGBA')
 # Alice-specific round Korean lettering with burgundy double-print.
 hi=Image.new('L',(w*S,h*S),0);d=ImageDraw.Draw(hi);font=ImageFont.truetype(str(FONT),35*S,index=0)
 text='이상한나라의앨리스';top,bottom=94,423;adv=(bottom-top)/len(text);cx=76*S
 for i,ch in enumerate(text):
  y=(top+i*adv)*S;bb=d.textbbox((0,0),ch,font=font,stroke_width=1*S);tw,th=bb[2]-bb[0],bb[3]-bb[1]
  d.text((cx-tw/2-bb[0],y+(adv*S-th)/2-bb[1]),ch,font=font,fill=255,stroke_width=1*S,stroke_fill=255)
 glyph=hi.resize((w,h),Image.Resampling.LANCZOS)
 ga=np.array(glyph.filter(ImageFilter.GaussianBlur(.62))).astype(np.float32);ga=np.clip((ga-35)*1.30,0,255)
 ga=np.clip(ga+paper_rng.normal(0,4.0,ga.shape)*(ga>12),0,255).astype(np.uint8);glyph=Image.fromarray(ga,'L')
 sh=glyph.filter(ImageFilter.GaussianBlur(.72)).transform((w,h),Image.Transform.AFFINE,(1,0,-1.15,0,1,-1.05),resample=Image.Resampling.BICUBIC).point(lambda v:int(v*.84))
 shadow=Image.new('RGBA',(w,h),(112,57,60,0));shadow.putalpha(sh);core=Image.new('RGBA',(w,h),(48,24,27,0));core.putalpha(glyph)
 layer=Image.new('RGBA',(w,h),(0,0,0,0));layer.alpha_composite(shadow);layer.alpha_composite(core)
 cand=clean_im.copy();cand.alpha_composite(layer);cand_arr=np.array(cand)
 text_owned=cv2.dilate((np.array(layer.getchannel('A'))>0).astype(np.uint8)*255,np.ones((5,5),np.uint8))>0
 owned=owned_clean|text_owned
 cand_arr[~owned]=src[~owned];cand=Image.fromarray(cand_arr,'RGBA')
 paths={'source':OUT/'source'/'0011.png','clean':OUT/'clean'/'0011.png','candidate':OUT/'candidate'/'0011.png','owned_mask':OUT/'owned_mask'/'0011.png','removed_text_mask':OUT/'removed_text_mask'/'0011.png'}
 src_im.save(paths['source']);clean_im.save(paths['clean']);cand.save(paths['candidate']);Image.fromarray(owned.astype(np.uint8)*255,'L').save(paths['owned_mask']);Image.fromarray(ink,'L').save(paths['removed_text_mask'])
 ev=Image.new('RGB',(w*3,h),'black');[ev.paste(im.convert('RGB'),(i*w,0)) for i,im in enumerate([src_im,clean_im,cand])];ev.save(OUT/'evidence'/'0011_source_clean_candidate.jpg',quality=94,optimize=True)
 ca=np.array(cand);outside=~owned
 # A rectangular patch would change most pixels of the paper face; this clean changes only ink-shaped pixels.
 paper_face=np.zeros((h,w),bool);paper_face[82:433,50:103]=True
 changed_clean=np.any(src!=clean,axis=2)
 val={'outside_owned_mask_byte_exact':bool(np.array_equal(src[outside],ca[outside])),'top_red_cap_byte_exact':bool(np.array_equal(src[:80],ca[:80])),'bottom_red_cap_byte_exact':bool(np.array_equal(src[454:],ca[454:])),'blue_rules_byte_exact':bool(np.array_equal(src[55:82],ca[55:82]) and np.array_equal(src[434:455],ca[434:455])),'clean_changed_paper_face_ratio':float(changed_clean[paper_face].mean()),'clean_change_is_glyph_shaped':bool(np.all(~changed_clean | (alpha[...,0]>0.002))),'old_ink_exact_ratio_after_clean':float(np.mean(np.all(src[ink>0]==clean[ink>0],axis=1)))}
 manifest={'schema':'fairytale-requiem-library-book-alice-glyph-cleanup-v8','status':'USER_REVIEW_REQUIRED_NOT_INSTALLED','surface':'grpo_lib/0011','target':'이상한 나라의 앨리스','contract':{'old_title_removed_before_typesetting':True,'no_rectangular_paper_face_replacement':True,'glyph_shaped_cleanup_only':True,'source_paper_fibres_reused':True,'per_book_typeface_profile':'alice_round_gulim_burgundy','installed':False},'validation':val,'files':{k:str(v) for k,v in paths.items()},'sha256':{k:sha(v) for k,v in paths.items()}}
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(val|{'output':str(OUT)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()




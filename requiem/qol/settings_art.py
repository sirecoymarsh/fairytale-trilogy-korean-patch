"""Use the exact blank option plates produced for the original Korean settings screen."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import struct, subprocess, sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assets import ROOT, RBASE, lwg, sha
OUT=ROOT/'qol'/'built'/'art'
PLATES=RBASE/'staging/ui_master_lwg/confscrn_ko_candidate/clean_plate_png'
FACE=RBASE/'tools/fonts/Gaegu-Bold.ttf'
WORDS=('모든 콘텐츠 해방','해방 취소','초기화','초기화 되돌리기')
# Left edge of the original row labels is 138. Original buttons use 40 native pixels.
SLOTS=((332,220),(566,154),(734,140),(888,226))
Y=586
def run(*args):
    subprocess.run([str(ROOT/'tools/UiAssetTool.exe'),*map(str,args)],check=True,capture_output=True)
def letter(im,text,box,size,color):
    x,y,w,h=box
    font=ImageFont.truetype(str(FACE),size)
    d=ImageDraw.Draw(im)
    left,top,right,bottom=d.textbbox((0,0),text,font=font)
    if right-left>w-4: raise ValueError((text,w,right-left))
    d.text((x+(w-right+left)//2-left,y+(h-bottom+top)//2-top),text,font=font,fill=color)
def resized_plate(source,width):
    # Keep the hand-painted ends intact. Only the central painted surface stretches.
    src=Image.open(PLATES/source).convert('RGBA')
    cap=18
    out=Image.new('RGBA',(width,src.height))
    out.paste(src.crop((0,0,cap,src.height)),(0,0))
    out.paste(src.crop((cap,0,src.width-cap,src.height)).resize((width-2*cap,src.height),Image.Resampling.LANCZOS),(cap,0))
    out.paste(src.crop((src.width-cap,0,src.width,src.height)),(width-cap,0))
    return out
def options_lwg(live_data):
    OUT.mkdir(parents=True,exist_ok=True)
    old=lwg(live_data)
    if any(n.startswith('ex09_') for n,*_ in old): raise ValueError('already built')
    originals={n:live_data[p:p+s] for n,_,p,s,*_ in old}
    bgwcg=OUT/'source-bg.wcg'; bgwcg.write_bytes(originals['bg'])
    run('wcg2png',bgwcg,OUT/'source-bg.png')
    bg=Image.open(OUT/'source-bg.png').convert('RGBA')
    letter(bg,'감상 기록',(130,Y,154,40),35,(73,32,5,255))
    bg.save(OUT/'bg.png')
    run('png2wcg',OUT/'bg.png',OUT/'bg.wcg')
    # Slot zero is the neutral native radio choice. The other four stay clickable.
    neutral=Image.new('RGBA',(2,2),(0,0,0,0));neutral.save(OUT/'ex09_0.png')
    run('png2wcg',OUT/'ex09_0.png',OUT/'ex09_0.wcg')
    extras=[('ex09_0',-8,-8,8,(OUT/'ex09_0.wcg').read_bytes())]
    for i,(word,(x,width)) in enumerate(zip(WORDS,SLOTS)):
        for focus in (True,False):
            suffix='_f' if focus else ''
            name=f'ex09_{i+1}'+suffix
            plate=resized_plate('scm_wnd'+suffix+'.png',width)
            letter(plate,word,(4,0,width-8,40),31,(255,255,255,255) if focus else (75,34,4,255))
            plate.save(OUT/(name+'.png'))
            run('png2wcg',OUT/(name+'.png'),OUT/(name+'.wcg'))
            extras.append((name,x,Y,8,(OUT/(name+'.wcg')).read_bytes()))
    h=bytearray(live_data[:24]); rows=bytearray(); blob=bytearray()
    for n,x,y,flag,content in [(n,x,y,flag,(OUT/'bg.wcg').read_bytes() if n=='bg' else originals[n]) for n,_,_,_,x,y,flag in old]+extras:
        name=n.encode('cp932')
        rows.extend(struct.pack('<iiBIIB',x,y,flag,len(blob),len(content),len(name))+name)
        blob.extend(content)
    struct.pack_into('<I',h,12,len(old)+len(extras));struct.pack_into('<I',h,20,len(rows))
    size_field=struct.unpack_from('<I',live_data,24+struct.unpack_from('<I',live_data,20)[0])[0]
    packed=bytes(h+rows+struct.pack('<I',len(blob) if size_field else 0)+blob)
    check=lwg(packed)
    assert [(r[0],*r[4:]) for r in check[:len(old)]]==[(r[0],*r[4:]) for r in old]
    assert all(n=='bg' or packed[pos:pos+size]==originals[n] for n,_,pos,size,*_ in check[:len(old)])
    for (n,x,y,_,b),r in zip(extras,check[len(old):]):
        assert (n,x,y,b)==(r[0],r[4],r[5],packed[r[2]:r[2]+r[3]])
    return packed

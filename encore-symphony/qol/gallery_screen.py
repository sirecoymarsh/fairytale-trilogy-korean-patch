from assets import ROOT,live,read_entry
import subprocess
tag=os.environ['FAIRY_QA_SCREEN'];gallery,overlay=map(int,tag.split('-'))
bgcode=9001 if gallery==201 else 9002
wcg=folder/('gallery-background-'+str(bgcode)+'.wcg');png=wcg.with_suffix('.png')
if not png.exists():
    wcg.write_bytes(read_entry(live(game)/'grpe.xfl',str(bgcode)+'.wcg'))
    subprocess.run([str(ROOT/'tools/UiAssetTool.exe'),'wcg2png',str(wcg),str(png)],check=True,capture_output=True)
expect=np.array(Image.open(png).convert('RGB'),dtype='int16')
win32gui.PostMessage(h,0x1c,1,0);win32gui.PostMessage(h,6,1,0)
start=time.monotonic();last=0
while time.monotonic()-start<48:
    img=capture(h);actual=np.array(img,dtype='int16')
    diff=np.abs(actual[::8,::8]-expect[::8,::8]).max(2);match=(diff<7).mean()
    if match>.20 and time.monotonic()-start>1.8:
        time.sleep(.9);img=capture(h);break
    if time.monotonic()-last>2:
        key(h,13);last=time.monotonic()
    time.sleep(.25)
else:
    img.save(folder/('undetected-'+tag+'.png'));raise RuntimeError(f'gallery screen not found: {tag} {match}')
img.save(folder/('gallery-'+tag+'.png'));print('real gallery',game,tag,round(float(match),2),flush=True)

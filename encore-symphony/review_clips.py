from opening_build import FF,ROOT,OUT,SRC
from assets import live
from PIL import Image
import numpy as np,subprocess,cv2
MEDIA=ROOT/'review';MEDIA.mkdir(exist_ok=True)
def clips():
    args=['-v','error','-y','-hide_banner']
    ext=['-an','-c:v','libx264','-preset','fast','-crf','17','-threads','6','-pix_fmt','yuv420p','-movflags','+faststart']
    target=MEDIA/'앙코르-오프닝-비교.mp4'
    trim='trim=start_frame=2128:end_frame=2514,setpts=PTS-STARTPTS'
    graph=f'[0:v]{trim}[l];[1:v]{trim}[r];[l][r]hstack=inputs=2[v]'
    subprocess.run([str(FF),*args,'-threads','4','-i',str(SRC),'-threads','4','-i',str(live('Encore')/'mov/0001.mpg'),'-filter_complex',graph,'-map','[v]','-frames:v','386',*ext,str(target)],check=True)
    cmd=[str(FF),*args,'-f','rawvideo','-pixel_format','rgb24','-framerate','30','-video_size','1132x282','-i','pipe:0',*ext,str(MEDIA/'심포니-조각-비교.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=0x08000000)
    for i in range(1,97):
        frame=Image.new('RGB',(1132,282),(174,159,170))
        for j,f in enumerate([ROOT/f'audit/full/Symphony/grpo_ef/{i:04d}.png',ROOT/f'art/Symphony/grpo_ef/{i:04d}/final.png']):
            a=Image.open(f).convert('RGBA');frame.paste(a,(566*j,0),a)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close();rc=proc.wait();assert not rc
    print('Two synchronized original/Korean comparison clips built.')
if __name__=='__main__':clips()


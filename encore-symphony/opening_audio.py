from assets import *
import subprocess
import numpy as np
from scipy import signal
from concurrent.futures import ThreadPoolExecutor
FF=Path('F:/DOWN/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe')
def wav(p=None,b=None):
    args=[str(FF),'-v','error','-i',str(p) if p else 'pipe:0','-map','0:a:0','-ac','1','-ar','4000','-f','f32le','pipe:1']
    return np.frombuffer(subprocess.check_output(args,input=b),np.float32)
def scores(ref,queries):
    x=ref-ref.mean()
    results=[]
    for q in queries:
        q=q-q.mean();d=(np.sum(q*q)*np.convolve([1],[1]))[0]
        if d<.001 or len(x)<len(q):results.append([0.,None]);continue
        cs=np.r_[0.,np.cumsum(x*x,dtype=np.float64)];power=cs[len(q):]-cs[:-len(q)]
        cc=signal.correlate(x,q,'valid',method='fft')/np.sqrt(np.maximum(power*d,.00001))
        idx=np.argmax(np.abs(cc));results.append([round(float(abs(cc[idx])),3),round(idx/4000,2)])
    return results
def run():
    op=wav(source('Encore')/'mov/0001.mpg')
    sec=[3,13,22,37,49,62,74,84,97,110,120];queries=[op[s*4000:(s+3)*4000] for s in sec]
    bank=source('Encore')/'bgm.xfl'; out={}
    def check(n):
        b=read_entry(bank,n);at=b.find(b'OggS',0,88)
        return n,scores(wav(b=b[at:] if at>=0 else b),queries)
    with ThreadPoolExecutor(max_workers=4) as pool:
        out=dict(pool.map(check,entry_map(bank)))
    for f in [RJ/'mov/0001.mpg',source('Encore')/'mov/0011.mpg',source('Encore')/'mov/0012.mpg']:
        out[str(f)]=scores(wav(f),queries)
    save('audit/opening_audio_match.json',dict(times=sec,scores=out))
    for j,s in enumerate(sec):
        name,v=max(out.items(),key=lambda kv:kv[1][j][0]);print(s,name.split('\\')[-1],v[j])
if __name__=='__main__':run()


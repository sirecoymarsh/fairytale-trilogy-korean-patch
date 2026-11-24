from assets import ROOT,RBASE,RJ,source,entry_map,read_entry,read,save
from gsc_codec import parse_gsc
from build_scenario_catalog import parse_commands
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from io import BytesIO
import struct,subprocess,re,json,os
import numpy as np
import soundfile as sf
from scipy import signal,fft
FF=Path('F:/DOWN/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe')
BANKS={'R':RJ,'E':source('Encore')}
def inventory():
    index={}
    for g,root in BANKS.items():
        arc=root/'voice.xfl'
        with arc.open('rb') as f:
            for n,e in entry_map(arc).items():
                if n.endswith('.wav') and n[:-4].isdigit():
                    index[g,int(n[:-4])]=(arc,e.absolute_offset,e.size)
                elif n.endswith('.xfl'):
                    f.seek(e.absolute_offset);head=f.read(12);sz,count=struct.unpack_from('<II',head,4);table=f.read(sz)
                    for j in range(count):
                        name,off,size=struct.unpack_from('<32sII',table,j*40)
                        filename=name.split(b'\0')[0].decode('cp932')
                        if filename.endswith('.wav') and filename[:-4].isdigit():
                            index[g,int(n[:-4])*10000+int(filename[:-4])]=(arc,e.absolute_offset+12+sz+off,size)
    return index
def scriptmap():
    fmt={r['opcode']:(r['format'],r['name']) for r in read(RBASE/'adapter/command_formats.json')['commands']};result={}
    for g,root in BANKS.items():
        p=root/'scr.xfl'
        for n in entry_map(p):
            if not 1001<int(n[:4])<1999:continue
            parts=parse_gsc(read_entry(p,n))
            for c in parse_commands(parts.command,fmt):
                if c.opcode==81 and c.args[1]:
                    result[g,c.args[1]]=(n,c.args[5],parts.strings[c.args[4]].decode('cp932'),parts.strings[c.args[5]].decode('cp932'))
    return result
def voice(key):
    p,off,size=entries[key]
    with p.open('rb') as f:f.seek(off);b=f.read(size)
    at=b.find(b'OggS',0,150)
    y,sr=sf.read(BytesIO(b[at:] if at>=0 else b),dtype='float32');assert sr==44100
    if y.ndim>1:y=y.mean(1)
    return y
def movie():
    y=subprocess.check_output([str(FF),'-v','error','-i',str(source('Encore')/'mov/0001.mpg'),'-map','0:a:0','-ac','1','-ar','44100','-f','f32le','pipe:1'])
    return np.frombuffer(y,np.float32)
def transform(y,div):
    a=signal.resample_poly(y,1,div);return np.diff(a,prepend=np.float32(0))
def xcorr(sub,template):
    return signal.correlate(sub,template,mode='valid',method='fft')
def main():
    global entries
    entries=inventory();text=scriptmap()
    mix=movie(); step=30; sr=44100//step; win=int(sr*.85)
    mixslow=transform(mix[:44100*69],step)
    nfft=fft.next_fast_len(len(mixslow)+win)
    ref=fft.rfft(mixslow,nfft)
    energy=np.r_[0.,np.cumsum(mixslow**2,dtype='float64')]
    windowpow=np.sqrt(np.maximum(1e-9,energy[win:]-energy[:-win])).astype('float32')
    fastmix=transform(mix,6); sr1=7350
    def one(key):
        full=voice(key);x=transform(full,step)
        if len(x)<win:return []
        # The opening sometimes uses only the last clause of a long line.
        offsets=np.arange(0,len(x)-win+1,max(1,win//3))
        if not len(offsets):return []
        power=np.r_[0.,np.cumsum(x**2,dtype='float64')];rank=power[offsets+win]-power[offsets]
        choices=[]
        for group in np.array_split(np.arange(len(offsets)),min(3,len(offsets))):
            choices.append(int(offsets[group[rank[group].argmax()]]))
        coarse=[]
        for pos in choices:
            t=x[pos:pos+win].copy();t-=t.mean()
            v=fft.irfft(ref*fft.rfft(t[::-1],nfft),nfft)[win-1:len(mixslow)]
            v=np.abs(v)/(windowpow*max(.00001,np.linalg.norm(t)))
            j=int(v.argmax())
            if v[j]>.17:coarse.append(((j-pos)/sr,float(v[j])))
        if not coarse:return []
        high=transform(full,6);result=[]
        for shift,cc in sorted(coarse,key=lambda a:-a[1]):
            if any(abs(shift-r['offset'])<.09 for r in result):continue
            # High-frequency normalized correlation distinguishes voices with similar vowel pitch.
            hits=[];w=int(.27*sr1)
            for pos in range(0,len(high)-w,max(1,w//2)):
                y=high[pos:pos+w];power_y=np.linalg.norm(y)
                if power_y<.015:continue
                expect=int(shift*sr1)+pos;a=max(0,expect-70);b=min(len(fastmix),expect+70+w)
                if b-a<w:continue
                xs=fastmix[a:b];cum=np.r_[0.,np.cumsum(xs**2,dtype='float64')]
                v=abs(np.correlate(xs,y,'valid'))/np.maximum(.0001,power_y*np.sqrt(cum[w:]-cum[:-w]));j=int(v.argmax())
                if v[j]>.18:hits.append((round(pos/sr1,3),round(float(v[j]),3),round((a+j-pos)/sr1,5)))
            if len(hits)>=2 and max(h[1] for h in hits)>=.23:
                consensus=float(np.median([h[2] for h in hits if h[1]>=max(a[1] for a in hits)*.70]))
                valid=[h for h in hits if abs(h[2]-consensus)<=.0025]
                if len(valid)<2:continue
                result.append(dict(game=key[0],voice=key[1],offset=round(consensus,4),duration=round(len(full)/44100,3),hits=valid,text=text.get(key)))
        return result
    keys=list(entries)
    priority={'1221.gsc','1310.gsc','1416.gsc','1420.gsc','1504.gsc'}
    keys.sort(key=lambda k:0 if text.get(k,('none',))[0] in priority else 1)
    out=[]
    with ThreadPoolExecutor(max_workers=9) as pool:
        for i,rs in enumerate(pool.map(one,keys)):
            out.extend(rs)
            if i in (400,2000):print('scanned',i,'matched',len(out),flush=True)
    out.sort(key=lambda r:r['offset']);save('audit/encore_opening_spoken_matches.json',out)
    for r in out:print(r['game'],r['voice'],r['offset'],min(x[0] for x in r['hits']),max(x[0] for x in r['hits']),max(x[1] for x in r['hits']),str(r['text'])[:116],flush=True)
if __name__=='__main__':main()

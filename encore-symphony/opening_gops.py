from opening_scan import *
from pathlib import Path
import subprocess,re
FF=Path('F:/DOWN/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe')
PROBE=FF.with_name('ffprobe.exe')
ES=OUT/'original.m1v'
def table(data):
    starts=[m.start() for m in re.finditer(b'\x00\x00\x01\xb3',data)]
    ps=[m.start() for m in re.finditer(b'\x00\x00\x01\x00',data)]
    gs=[m.start() for m in re.finditer(b'\x00\x00\x01\xb8',data)]
    import bisect
    result=[]
    for i,g in enumerate(gs):
        j=bisect.bisect_right(starts,g)-1
        start=starts[j] if j>=0 and (i==0 or starts[j]>gs[i-1]) else g
        end=gs[i+1] if i+1<len(gs) else len(data)
        k=bisect.bisect_right(ps,g);z=bisect.bisect_left(ps,end)
        ptypes=[(int.from_bytes(data[a+4:a+6],'big')>>3&7,int.from_bytes(data[a+4:a+6],'big')>>6) for a in ps[k:z]]
        result.append(dict(frame=k,n=z-k,offset=start,closed=bool(data[g+7]&64),broken=bool(data[g+7]&32),seq=(start!=g),first=ptypes[:4]))
    return result
if __name__=='__main__':
    if not ES.exists():
        subprocess.run([str(FF),'-hide_banner','-v','error','-i',str(SRC),'-map','0:v:0','-c:v','copy','-f','mpeg1video',str(ES)],check=True)
    tab=table(ES.read_bytes());save('audit/op_gops.json',tab)
    print('groups',len(tab),'isolated',sum(d['closed'] for d in tab),'repeated sequence headers',sum(d['seq'] for d in tab),'picture count',sum(d['n'] for d in tab))
    for d in tab:
        if d['frame'] in range(2090,2170) or d['frame'] in range(2490,2555) or d['frame'] in range(3470,3540):print(d)


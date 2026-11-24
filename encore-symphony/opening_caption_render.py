from opening_lyric_base import *
from PIL import Image,ImageFont
from functools import lru_cache
from fractions import Fraction
from collections import Counter
import shutil,hashlib,re,sys
D=read('audit/opening_caption_timeline.json')
KFONT=OD/'fonts/Jua-Regular.ttf';JFONT=OD/'fonts/MPLUSRounded1c-Bold.ttf'
KF=ImageFont.truetype(str(KFONT),40).getname()[0]
JF=ImageFont.truetype(str(JFONT),30).getname()[0]
WORK={'Encore':'앙코르','Requiem':'레퀴엠'}
PROBE=FF.with_name('ffprobe.exe')
def hs(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ats(t):
    cent=round(t*100);ss,cc=divmod(cent,100);mm,ss=divmod(ss,60);hh,mm=divmod(mm,60)
    return f'{hh}:{mm:02}:{ss:02}.{cc:02}'
def strs(t):
    ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode('utf-8-sig'))
@lru_cache(None)
def font(sz):
    return ImageFont.truetype(str(KFONT),sz)
def wrap(s,sz,limit):
    res=[];line=''
    for word in s.split(' '):
        trial=(line+' '+word).strip()
        if line and font(sz).getlength(trial)>limit:
            res.append(line);line=word
        else:line=trial
    if line:res.append(line)
    assert len(res)<=2 and all(font(sz).getlength(v)<=limit for v in res),(s,res)
    return res
def render_ass(game):
    root=OD/WORK[game]; root.mkdir(exist_ok=True,parents=True)
    head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.601
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
'''
    def style(name,face,sz,alignment,edge,outline,shade):
        return f'Style: {name},{face},{sz},&H00160F13,&H00160F13,{edge},&H00160D19,0,0,0,0,100,100,0,0,1,{outline},{shade},{alignment},0,0,0,1'
    for n,f,sz,al in [('Dialogue',KF,36,7),('Speaker',KF,25,7),('Japanese',JF,32,2),('Korean',KF,46,2)]:
        head+=style(n+'Rim',f,sz,al,'&H00201521',5 if n!='Speaker' else 3.3,2.3)+'\n'
        head+=style(n,f,sz,al,'&H00F5FAFF',3.3 if n!='Speaker' else 2.1,0)+'\n'
    head+='[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    events=[];simple=[];boxes=[]
    def add(st,en,sty,x,y,s,name='',color=None):
        assert 0<=st<en and not any(ch in s for ch in '{}')
        point=r'{\pos('+str(x)+','+str(y)+')}'
        pos=point+(('{'+r'\1c&H'+color+'&}') if color else '')+s
        for layer,key in ((0,sty+'Rim'),(1,sty)):
            events.append(f'Dialogue: {layer},{ats(st)},{ats(en)},{key},{name},0,0,0,,{pos}')
    if game=='Encore':
        colors={'앨리스':'4B194F','라푼젤':'333D20','눈의 여왕':'52361C','게르다':'494624','그레텔':'30294E','오데트':'423925','오딜':'3B1F4B'}
        for take in D['Encore']:
            lane=take['lane'];x=(56,663)[lane%2];top=586-126*(lane//2)
            add(take['start'],take['end'],'Speaker',x,top,take['speaker'],take['speaker'],colors[take['speaker']])
            for c in take['cues']:
                lines=wrap(c['ko'],36,535);add(c['start'],c['end'],'Dialogue',x,top+28,r'\N'.join(lines),take['speaker'])
                boxes.append((c['start'],c['end'],(x-6,top-6,x+550,top+30+len(lines)*41+5)))
                simple.append(dict(start=c['start'],end=c['end'],text=take['speaker']+'  '+c['ko'],lane=lane))
        slices=[]
        cuts=sorted(set([q['start'] for q in simple]+[q['end'] for q in simple]))
        for a,b in zip(cuts,cuts[1:]):
            val='\n'.join(q['text'] for q in sorted(simple,key=lambda r:r['lane']) if q['start']<=a<q['end'])
            if val:slices.append((a,b,val))
    else:
        slices=[]
        for cue in D['Requiem']:
            a,b,s,ko=cue['start'],cue['end'],cue['source'],cue['ko']
            if s:add(a,b,'Japanese',640,655,s)
            add(a,b,'Korean',640,701,ko)
            assert font(46).getlength(ko)<1160
            slices.append((a,b,((s+'\n') if s else '')+ko))
    write(root/'captions.ass',head+'\n'.join(events)+'\n')
    write(root/'captions.srt','\n\n'.join(f'{i+1}\n{strs(a)} --> {strs(b)}\n{v}' for i,(a,b,v) in enumerate(slices))+'\n')
    if game=='Encore':
        for i,(a,b,rect) in enumerate(boxes):
            assert rect[0]>=0 and rect[2]<=1280 and rect[1]>=0 and rect[3]<=716,rect
            for c,d,r in boxes[i+1:]:
                if max(a,c)>=min(b,d):continue
                assert max(rect[0],r[0])>=min(rect[2],r[2]) or max(rect[1],r[1])>=min(rect[3],r[3]),(a,c,rect,r)
    return root
def cleaned_normal(frame,raw,i,band):
    text=oldtext(i)
    if not text:return frame
    mask=oldmask(text)
    dest=frame[Y0:Y1];donor=band if band is not None else raw[Y0:Y1]
    dest[mask]=donor[mask]
    return frame
def recover_sources():
    paths=[(a,b,BANDS/f'{a}.mkv',True) for a,b,_ in SCENES]+[(863,1003,TITLE,False),(1898,1932,QUESTION,False)]
    return paths
def baseframe(game,i):
    def get(path,idx):
        c=cv2.VideoCapture(str(path));c.set(cv2.CAP_PROP_POS_FRAMES,idx);im=grab(c);c.release();return im
    if game=='Encore':return get(ROOT/'opening/0001-ko.mpg',i)
    b=get(OLD,i);raw=get(REF,i);band=None
    for a,z,p,crop in recover_sources():
        if a<=i<z:
            im=get(p,i-a)
            if crop:band=im
            else:raw=im
            break
    return cleaned_normal(b,raw,i,band)
def sample(game,t):
    d=render_ass(game);i=round(t*RATE);b=baseframe(game,i)
    with subprocess.Popen([str(FF),'-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','30000/1001','-i','pipe:0','-vf',f'setpts=PTS+{i},ass=captions.ass:fontsdir=../fonts','-frames:v','1','-c:v','png','-f','image2pipe','pipe:1'],cwd=d,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as f:
        out,err=f.communicate(b.tobytes());assert f.returncode==0,err
    p=BANDS/f'sample_{game}_{i}.png';p.write_bytes(out);return p
def encargs():
    return ['-an','-pix_fmt','yuv420p','-c:v','mpeg1video','-q:v','2','-b:v','12000k','-maxrate','18000k','-bufsize','1835008','-g','18','-bf','2','-flags','+cgop','-sc_threshold','1000000000','-threads','7']
def app(args,**kw):
    subprocess.run([str(x) for x in args],check=True,**kw)
def frames(file):
    from json import loads
    return loads(subprocess.check_output([str(PROBE),'-v','error','-count_frames','-show_entries','stream=codec_name,width,height,sample_rate,channels,nb_read_frames,avg_frame_rate,start_time,duration','-of','json',str(file)]))['streams']
def audiohash(path):
    return subprocess.check_output([str(FF),'-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','pipe:1']).decode().strip().split('=')[-1]
def build(game):
    from opening_gops import table
    d=render_ass(game);base=ROOT/'opening/0001-ko.mpg' if game=='Encore' else OLD
    n=3818 if game=='Encore' else 3540;work=BANDS;intro=work/(game+'-subtitle.m1v')
    if game=='Encore':
        old=ROOT/'opening/앙코르-한국어.m1v'
        g=next(g for g in read('audit/op_gops.json') if g['closed'] and g['seq'] and g['frame']>=mathceil(max(t['end'] for t in D['Encore'])*RATE))
        stop=g['frame']
        assert stop<2130
        app([FF,'-y','-v','error','-i',base,'-map','0:v:0','-frames:v',str(stop),'-vf','ass=captions.ass:fontsdir=../fonts',*encargs(),'-f','mpeg1video',intro],cwd=d)
        head=intro.read_bytes();newrows=table(head);assert sum(g['n'] for g in newrows)==stop and newrows[0]['closed']
        with intro.open('ab') as out,old.open('rb') as src:
            src.seek(g['offset']);shutil.copyfileobj(src,out)
        with old.open('rb') as f,intro.open('rb') as q:
            f.seek(g['offset']);q.seek(len(head));assert hashlib.file_digest(f,'sha256').digest()==hashlib.file_digest(q,'sha256').digest()
    else:
        cap=cv2.VideoCapture(str(OLD));orig=cv2.VideoCapture(str(REF));paths=recover_sources();streams={};active={}
        args=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','30000/1001','-i','pipe:0','-vf','ass=captions.ass:fontsdir=../fonts',*encargs(),'-f','mpeg1video',intro]
        p=subprocess.Popen([str(x) for x in args],cwd=d,stdin=subprocess.PIPE)
        try:
            for i in range(n):
                b=grab(cap);org=grab(orig);band=None
                for a,z,path,isband in paths:
                    if a<=i<z:
                        if a not in streams:streams[a]=cv2.VideoCapture(str(path))
                        patch=grab(streams[a])
                        if isband:band=patch
                        else:org=patch
                        if i+1==z:streams[a].release()
                        break
                b=cleaned_normal(b,org,i,band);p.stdin.write(b.tobytes())
        finally:
            p.stdin.close();ret=p.wait();cap.release();orig.release()
            for obj in streams.values():obj.release()
        assert ret==0
    assert sum(g['n'] for g in table(intro.read_bytes()))==n
    pending=d/'0001.pending.mpg'
    app([FF,'-y','-v','error','-fflags','+genpts','-r','30000/1001','-i',intro,'-i',base,'-map','0:v','-map','1:a','-c','copy','-muxpreload','.5','-muxdelay','.7','-f','mpeg',pending],cwd=d)
    ss=frames(pending);assert int(ss[0]['nb_read_frames'])==n and ss[0]['codec_name']=='mpeg1video'
    assert (ss[0]['width'],ss[0]['height'],ss[0]['avg_frame_rate'])==(1280,720,'30000/1001')
    assert ss[1]['codec_name']=='mp2' and ss[1]['channels']==2 and ss[1]['sample_rate']=='48000'
    assert abs(float(ss[0]['start_time'])-float(ss[1]['start_time']))<.038
    ah=audiohash(base);assert ah==audiohash(pending)
    res=subprocess.run([str(FF),'-v','error','-xerror','-i',str(pending),'-map','0:v','-map','0:a','-f','null','-'],capture_output=True);assert res.returncode==0 and not res.stderr,res.stderr
    target=d/'0001.mpg';os.replace(pending,target)
    proof=dict(game=game,file=str(target),source=str(base),old_sha256=hs(base),sha256=hs(target),streams=ss,audio_sha256=ah,decode='OK',restored_earlier_caption=(game=='Requiem'),ass_sha256=hs(d/'captions.ass'))
    if game=='Encore':proof['unchanged_compressed_tail_frames']=[stop,n]
    save('audit/opening_caption_'+game+'.json',proof)
    print(game,n,hs(target),ah,flush=True)
def mathceil(z):
    import math
    return math.ceil(z)
if __name__=='__main__':
    for game in sys.argv[2:]:
        if sys.argv[1]=='sample':
            for t in ([3.8,46.2] if game=='Encore' else [12,40.5,54.5,63.5]):print(sample(game,t))
        else:build(game)

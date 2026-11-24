"""Smart-render two edit intervals and keep the native MPEG video bytes elsewhere."""
from movie_render import *
import json,os,shutil
BOUND=[(2130,3015),(3499,3818)]
ORIGINAL='76d24ef0b54a6835bc4bfff4f5201423c2d8bb6d33689341854b18d332519b4e'
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def encode():
    key=hashlib.sha256()
    for p in [ROOT/'design/앙코르.png',ROOT/'movie_render.py',ROOT/'audit/op_track_final.json',ROOT/'audit/op_design_proof.json']:
        key.update(bytes.fromhex(digest(p)))
    sig=key.hexdigest()
    code=OUT/'encoded';code.mkdir(exist_ok=True);names=[code/f'{s}-{e}.{sig[:12]}.m1v' for s,e in BOUND]
    absent=[not n.exists() for n in names]
    if any(absent):
        cap=cv2.VideoCapture(str(SRC));proc=None;log=None;count=0;shutter=read('audit/op_design_proof.json')['shutter'];cv2.setNumThreads(6)
        for i in range(3818):
            if not cap.grab():raise RuntimeError(f'source stopped on frame {i}')
            for j,(s,e) in enumerate(BOUND):
                if not absent[j] or not s<=i<e:continue
                nm=names[j];temp=Path(str(nm)+'.pending')
                if i==s:
                    log=(code/f'{s}.log').open('wb')
                    cmd=[str(FF),'-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pixel_format','bgr24','-video_size','1280x720','-framerate','30000/1001','-i','pipe:0','-an','-pix_fmt','yuv420p','-c:v','mpeg1video','-q:v','2','-b:v','12000k','-maxrate','18000k','-bufsize','1835008','-g','18','-bf','2','-flags','+cgop','-sc_threshold','1000000000','-threads','6','-f','mpeg1video',str(temp)]
                    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,stdout=subprocess.DEVNULL,creationflags=0x08000000)
                    count=0
                ok,im=cap.retrieve();assert ok
                edited=edit(im,i,shutter);proc.stdin.write(edited.tobytes());count+=1
                if i==e-1:
                    proc.stdin.close();ret=proc.wait();log.close()
                    if ret:raise RuntimeError('ffmpeg encode '+str(ret))
                    raw=temp.read_bytes();gops=table(raw)
                    assert count==e-s==sum(v['n'] for v in gops) and gops[0]['closed']
                    os.replace(temp,nm);print('Rendered',s,e,count,flush=True)
        cap.release()
    return names
def retime(data,offset):
    patch=bytearray(data)
    for g in table(data):
        p=data.index(b'\x00\x00\x01\xb8',g['offset'])+4
        tc=g['frame']+offset;hour,tc=divmod(tc,30*3600);minute,tc=divmod(tc,30*60);sec,num=divmod(tc,30)
        original=int.from_bytes(data[p:p+4],'big')
        code=((hour&31)<<26)|((minute&63)<<20)|(1<<19)|((sec&63)<<13)|(num<<7)|(original&0x7f)
        patch[p:p+4]=code.to_bytes(4,'big')
    return patch
def probe(path,count=False):
    args=[str(PROBE),'-v','error']
    if count:args+=['-count_frames']
    args+=['-show_entries','stream=codec_name,width,height,sample_rate,channels,sample_aspect_ratio,avg_frame_rate,start_time,duration,nb_read_frames','-of','json',str(path)]
    return json.loads(subprocess.check_output(args))['streams']
def audio_sha(path):
    result=subprocess.check_output([str(FF),'-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','pipe:1'])
    return result.decode().strip().split('=')[-1]
def build():
    assert digest(SRC)==ORIGINAL
    ns=encode()
    raw=ES.read_bytes();old=read('audit/op_gops.json');groups={v['frame']:v for v in old};groups[3818]=dict(offset=len(raw))
    assert groups[3015]['closed'] and groups[3015]['seq']
    combined=OUT/'앙코르-한국어.m1v';refs=[];pos=0;last=0
    with combined.open('wb') as f:
        for (s,e),file in zip(BOUND,ns):
            h=groups[s]['offset'];q=groups[e]['offset'];copy=raw[pos:h]
            if copy:
                refs.append(dict(frames=[last,s],bytes=len(copy),sha256=hashlib.sha256(copy).hexdigest(),output_offset=f.tell()))
                f.write(copy)
            f.write(retime(file.read_bytes(),s));pos=q;last=e
        if pos<len(raw):f.write(raw[pos:])
    with combined.open('rb') as f:
        for rec0 in refs:
            f.seek(rec0['output_offset']);assert hashlib.sha256(f.read(rec0['bytes'])).hexdigest()==rec0['sha256']
    full=combined.read_bytes();groups_new=table(full);assert sum(g['n'] for g in groups_new)==3818
    del raw,full
    target=OUT/'0001-ko.mpg';pending=OUT/'0001-ko.pending.mpg'
    spec=[str(FF),'-y','-hide_banner','-loglevel','warning','-fflags','+genpts','-r','30000/1001','-i',str(combined),'-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c','copy','-muxpreload','.5','-muxdelay','.7','-f','mpeg',str(pending)]
    with (OUT/'mux.log').open('wb') as log:subprocess.run(spec,stderr=log,check=True)
    streams=probe(pending,True);original=probe(SRC)
    assert streams[0]['codec_name']=='mpeg1video' and streams[0]['width']==1280 and streams[0]['height']==720
    assert int(streams[0]['nb_read_frames'])==3818,streams
    a0=audio_sha(SRC);a1=audio_sha(pending);assert a0==a1
    assert abs(float(streams[0]['duration'])-float(original[0]['duration']))<.16,streams
    assert abs(float(streams[1]['duration'])-float(original[1]['duration']))<.07,streams
    assert abs(float(streams[1]['start_time'])-float(streams[0]['start_time']))<=.05,streams
    decode=subprocess.run([str(FF),'-v','error','-xerror','-i',str(pending),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True)
    if decode.returncode or decode.stderr:raise RuntimeError(decode.stderr.decode(errors='replace')[:800])
    os.replace(pending,target)
    save('audit/opening_build.json',dict(source=str(SRC),source_sha256=ORIGINAL,replacement=str(target),sha256=digest(target),original_streams=original,streams=streams,original_video_runs=refs,original_picture_count=sum(v['frames'][1]-v['frames'][0] for v in refs),edited_gop_intervals=BOUND,original_audio_elementary_sha256=a0,output_audio_elementary_sha256=a1,full_decode='OK',translator_model='Codex internal',title_frames=[2136,LAST],engine_viewport=[1280,720]))
    print('Ready',target,streams,a1,flush=True)
if __name__=='__main__':build()


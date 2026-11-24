from assets import *
from focus import fullpath
from labels import artkey,ART
import numpy as np, shutil, subprocess
from PIL import Image
def encode(maps,previous):
    verified={r['file']:r for group in previous.values() for r in group.values()}
    rows=[];meta={};dest=ROOT/'encoded';dest.mkdir(exist_ok=True)
    ix=read('audit/index.json')
    for g,records in maps.items():
        for k,r in records.items():
            folder=ART/artkey(g,k);final=folder/'final.png'; mask=folder/'ownership.png'; hs=ix[g][k]['sha']
            variant=sha((hs+sha(final.read_bytes())+sha(mask.read_bytes())).encode())
            wcg=dest/(variant+'.wcg');decoded=dest/(variant+'.png')
            if not(wcg.exists() and decoded.exists()) and variant not in meta:
                raw=dest/(hs+'.src');data=blob(source(g),k);assert sha(data)==hs
                if not raw.exists():raw.write_bytes(data)
                rows.append('\t'.join(str(p) for p in [raw,final,mask,wcg,decoded]))
            meta.setdefault(variant,[]).append((g,k,folder,wcg,decoded))
    if rows:
        f=ROOT/'audit/patch-jobs.tsv';f.write_text('\n'.join(rows),encoding='utf-8-sig')
        subprocess.run([str(ROOT/'tools/RasterPatch.exe'),str(f)],check=True)
    mapping={g:{} for g in maps}
    for v,group in meta.items():
        g,k,folder,wcg,decoded=group[0]
        digest=sha(wcg.read_bytes()); file=str(wcg.relative_to(ROOT))
        cached=verified.get(file)
        if not (cached and cached['sha256']==digest and cached.get('outside_changed')==0):
            a=np.asarray(Image.open(fullpath(g,k)).convert('RGBA'),dtype=int)
            c=np.asarray(Image.open(folder/'final.png').convert('RGBA'),dtype=int)
            m=np.asarray(Image.open(folder/'ownership.png').convert('L'))>0
            b=np.asarray(Image.open(decoded).convert('RGBA'),dtype=int)
            if b.shape!=a.shape or np.any((b!=a)[~m]):raise ValueError(('Protected pixel mismatch',g,k))
            alpha_err=np.abs(c[:,:,3]-b[:,:,3]); opaque=np.logical_and(m,c[:,:,3]==255)
            if alpha_err[m].max(initial=0)>0 or np.max(np.abs(c[opaque]-b[opaque]),initial=0)>1:raise ValueError(('WCG visible mismatch',g,k,np.max(alpha_err),np.max(np.abs(c[opaque]-b[opaque]),initial=0)))
        for g,k,*_ in group:mapping[g][k]={'file':str(wcg.relative_to(ROOT)),'sha256':digest,'outside_changed':0}
    return mapping
def packed_lwg(src,changes):
    layers=lwg(src);header_size=24+struct.unpack_from('<I',src,20)[0];h=bytearray(src[:header_size+4]);payload=bytearray()
    for i,(label,p,off,size,_,_,_) in enumerate(layers):
        item=changes.get(str(i)+':'+label,src[off:off+size]); struct.pack_into('<II',h,p+9,len(payload),len(item));payload.extend(item)
    if struct.unpack_from('<I',h,header_size)[0]:struct.pack_into('<I',h,header_size,len(payload))
    result=bytes(h+payload);after=lwg(result)
    if [(i[0],*i[4:]) for i in layers]!=[(i[0],*i[4:]) for i in after]:raise ValueError('LWG geometry')
    return result
def current_hash(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def patch():
    merged=defaultdict(dict)
    for fn in ('labels','plates','logos','props'):
        path=ROOT/'audit'/(fn+'.json')
        if path.exists():
            for g,m in read(path).items():merged[g].update(m)
    old_enc=read('audit/encoded.json') if (ROOT/'audit/encoded.json').is_file() else {}
    enc=encode(merged,old_enc);index=read('audit/index.json');report={}
    previous=read('audit/install.json') if (ROOT/'audit/install.json').is_file() else {}
    for g,rec in index.items():
        allchanges=defaultdict(lambda:defaultdict(dict));counts=Counter()
        for k,r in rec.items():
            b,n,*layer=k.split('/')
            if k in enc[g]:
                z=enc[g][k];data=(ROOT/z['file']).read_bytes();kind='new'
            elif 'donor' in r:
                data=blob(RK,r['donor'],True);assert sha(data)==r['ko'];kind='reuse'
            else: continue
            assert struct.unpack_from('<II',data,8)==tuple(r['size'])
            allchanges[b][n][layer[0] if layer else '']=data;counts[kind]+=1
        banks={}
        for b,changes in allchanges.items():
            org=source(g)/(b+'.xfl');installed=live(g)/org.name
            priorbank=previous.get(g,{}).get('banks',{}).get(b,{})
            old_subset={k:v['sha256'] for k,v in old_enc.get(g,{}).items() if k.startswith(b+'/')}
            new_subset={k:v['sha256'] for k,v in enc[g].items() if k.startswith(b+'/')}
            live_hash=current_hash(installed)
            source_set=sha(repr(sorted(new_subset.items())).encode())
            if priorbank.get('installed_sha256')==live_hash and (priorbank.get('asset_set_sha256')==source_set or ('asset_set_sha256' not in priorbank and old_subset==new_subset)):
                banks[b]=dict(priorbank,asset_set_sha256=source_set);continue
            original_hash=current_hash(org)
            if live_hash not in (original_hash,previous.get(g,{}).get('banks',{}).get(b,{}).get('installed_sha256')):raise ValueError(('Unexpected live archive',installed))
            arc=parse_archive(org);stage=ROOT/'staging'/g/org.name;stage.parent.mkdir(parents=True,exist_ok=True)
            payload={};expected={}
            with org.open('rb') as f:
                for e in arc.entries:
                    f.seek(e.absolute_offset);j=f.read(e.size);k=changes.get(e.name)
                    if k:payload[e.name]=k[''] if '' in k else packed_lwg(j,k)
                    if k and '' not in k:
                        old=dict(flatten(b,e.name,j));new=dict(flatten(b,e.name,payload[e.name]))
                        if old.keys()!=new.keys():raise ValueError('layer set')
                        for uid in old:
                            targets=k.get(uid.split('/',2)[-1],old[uid])
                            if new[uid]!=targets:raise ValueError(('Unexpected layer',uid))
                    expected[e.name]=sha(payload.get(e.name,j))
            with org.open('rb') as f,stage.open('wb') as o:
                o.write(f.read(12));pos=0
                for e in arc.entries:
                    size=len(payload[e.name]) if e.name in payload else e.size
                    o.write(e.raw_name+struct.pack('<II',pos,size));pos+=size
                for e in arc.entries:
                    if e.name in payload:o.write(payload[e.name])
                    else:f.seek(e.absolute_offset);o.write(f.read(e.size))
            result=parse_archive(stage)
            assert [e.raw_name for e in result.entries]==[e.raw_name for e in arc.entries]
            with stage.open('rb') as f:
                for e in result.entries:f.seek(e.absolute_offset);assert sha(f.read(e.size))==expected[e.name]
            output_hash=current_hash(stage);banks[b]=dict(original_sha256=original_hash,installed_sha256=output_hash,asset_set_sha256=source_set,changed_entries=len(changes),total_entries=len(arc.entries))
        running=subprocess.run(['powershell','-NoProfile','-Command',"$p=Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq '"+str(next(live(g).glob('*.exe')))+"' }; if($p){exit 1}"],capture_output=True)
        if running.returncode:raise RuntimeError('Game is running: '+g)
        prior=[]
        try:
            for b,recb in banks.items():
                name=b+'.xfl';installed=live(g)/name
                if current_hash(installed)==recb['installed_sha256']:continue
                keep=ROOT/'rollback'/g/name;keep.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(installed,keep)
                incoming=installed.with_suffix('.ko-pending');shutil.copyfile(ROOT/'staging'/g/name,incoming);assert current_hash(incoming)==recb['installed_sha256']
                os.replace(incoming,installed);prior.append((installed,keep))
            for b,recb in banks.items():assert current_hash(live(g)/(b+'.xfl'))==recb['installed_sha256']
        except BaseException:
            for path,backup in reversed(prior):shutil.copyfile(backup,path)
            raise
        assert current_hash(live(g)/'scr.xfl')==current_hash(source(g)/'scr.xfl')
        report[g]=dict(translator_model='Codex internal',changed_image_states=dict(counts),banks=banks,original_scenario_sha256=current_hash(source(g)/'scr.xfl'));print(g,dict(counts),len(banks),'archives',flush=True)
        save('audit/install.json',dict(previous,**report))
    save('audit/encoded.json',enc)
    save('progress.json',dict(phase='Korean raster assets installed',status=report,original=str(ROOT/'original'),scenario_translation='Awaiting user-provided Gemini result'))
if __name__=='__main__':patch()

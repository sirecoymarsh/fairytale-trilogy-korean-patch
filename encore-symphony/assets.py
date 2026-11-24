from __future__ import annotations
import hashlib, json, struct, sys
from pathlib import Path
from collections import defaultdict, Counter
from functools import lru_cache
import os
ROOT=Path(__file__).resolve().parent
RBASE=Path('P:/AI/Codex/projects/fairytale-requiem-ko')
RJ=Path('Y:/GAME/H Games/FairyTale Requiem/フェアリーテイル・レクイエム')
RK=RBASE/'runtime/trial_ko'
GAMES=('Encore','Symphony')
sys.path.insert(0,str(RBASE/'adapter'))
from xfl_tool import parse_archive
def sha(b): return hashlib.sha256(b).hexdigest()
def save(path,data):
    path=ROOT/path
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf-8')
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def source(g): return ROOT/'original'/g/'Files'
def live(g): return Path('Y:/GAME')/('Fairytale '+g)
@lru_cache(maxsize=64)
def entry_map(path): return {e.name:e for e in parse_archive(path).entries}
def read_entry(path,name):
    e=entry_map(path)[name]
    with path.open('rb') as f:
        f.seek(e.absolute_offset); b=f.read(e.size)
    if len(b)!=e.size: raise ValueError((path,name))
    return b
def lwg(data):
    count=struct.unpack_from('<I',data,12)[0]
    end=24+struct.unpack_from('<I',data,20)[0]
    base=end+4; total=struct.unpack_from('<I',data,end)[0]; p=24
    layers=[]
    for i in range(count):
        x,y,flags,off,size,n=struct.unpack_from('<iiBIIB',data,p)
        name=data[p+18:p+18+n].decode('cp932')
        if base+off+size>len(data): raise ValueError(('layer',name,size))
        layers.append((name,p,base+off,size,x,y,flags));p+=18+n
    if p!=end or total not in (0,len(data)-base): raise ValueError(('lwg table',p,end,base,total,len(data)))
    return layers
def flatten(bank,name,data):
    key=bank+'/'+name
    if data.startswith(b'LG\x01\x00'):
        for i,(label,_,off,size,x,y,flags) in enumerate(lwg(data)):
            if size: yield key+'/'+str(i)+':'+label,data[off:off+size]
    else: yield key,data
def blob(root,key,loose=False):
    bank,name,*sub=key.split('/')
    loosefile=root/bank/name
    data=loosefile.read_bytes() if loose and loosefile.is_file() else read_entry(root/(bank+'.xfl'),name)
    if sub:
        i=int(sub[0].split(':')[0]); layer=lwg(data)[i]
        if layer[0]!=sub[0].split(':',1)[1]: raise ValueError(key)
        return data[layer[2]:layer[2]+layer[3]]
    return data
def index():
    original={}; changed=defaultdict(list); verified_source={}
    trusted={x['path'].lower():x['sha256'].lower() for x in read(RBASE/'audit/original_inventory.json')['entries'] if 'sha256' in x}
    for jp in sorted(RJ.glob('grp*.xfl')):
        ko=RK/jp.name
        if not ko.exists(): continue
        with jp.open('rb') as f: jp_hash=hashlib.file_digest(f,'sha256').hexdigest()
        if jp_hash!=trusted[jp.name.lower()]: raise ValueError('Requiem donor source differs: '+jp.name)
        verified_source[jp.name]=jp_hash
        kmap=entry_map(ko)
        with jp.open('rb') as jf,ko.open('rb') as kf:
            for name,j in entry_map(jp).items():
                if name not in kmap: continue
                k=kmap[name];jf.seek(j.absolute_offset); jd=jf.read(j.size)
                loose=RK/jp.stem/name
                if loose.is_file():kd=loose.read_bytes()
                else: kf.seek(k.absolute_offset);kd=kf.read(k.size)
                kl=dict(flatten(jp.stem,name,kd)) if jd!=kd else {}
                for key,jb in flatten(jp.stem,name,jd):
                    hj=sha(jb); original[hj]=key
                    if not kl or key not in kl or kl[key]==jb: continue
                    kb=kl[key]
                    if not (jb[:2]==b'WG' and kb[:2]==b'WG' and jb[8:16]==kb[8:16]):continue
                    changed[hj].append([key,sha(kb)])
    out={}
    for g in GAMES:
        records={}
        for a in sorted(source(g).glob('grp*.xfl')):
            with a.open('rb') as f:
                for name,e in entry_map(a).items():
                    f.seek(e.absolute_offset);d=f.read(e.size)
                    for key,b in flatten(a.stem,name,d):
                        if not b: continue
                        h=sha(b); row={'sha':h}
                        if h in changed:
                            choices=changed[h]; options=[v for v in choices if v[0]==key] or choices
                            if len(set(v[1] for v in options))==1: row.update(donor=options[0][0],ko=options[0][1])
                            else:row['ambiguous']=options
                        if h in original: row['jp_donor']=original[h]
                        if b[:2]==b'WG':row['size']=list(struct.unpack_from('<II',b,8))
                        records[key]=row
        out[g]=records
        print(g)
        for bank in sorted(set(k.split('/')[0] for k in records)):
            rows=[v for k,v in records.items() if k.startswith(bank+'/')]
            print(bank,len(rows),'ko',sum('donor'in v for v in rows),'uniqueJP',sum('jp_donor' not in v for v in rows))
    save('audit/index.json',out);save('audit/requiem_source_hashes.json',verified_source)
    save('progress.json',dict(installed={g:str(live(g)) for g in GAMES},phase='Indexed both installed games and original-to-Korean donor identity',translator_model='Codex internal',scenario='User commissions Gemini separately; verification on receipt',sources=['https://www.liar.co.jp/fairy_symphony/','https://www.liar.co.jp/fairy_encore/','https://github.com/Love-in-idleness/LiarsoftTool (GPL-3.0; reference)','https://github.com/morkt/GARbro/blob/master/ArcFormats/Liar/ArcXFL.cs (MIT; reference)',str(RBASE/'adapter/UiAssetTool.exe'),str(RBASE/'adapter/xfl_tool.py')]))
if __name__=='__main__':index()


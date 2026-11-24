import json,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
from gsc_codec import parse_gsc, rebuild_gsc
sys.stdout.reconfigure(encoding='utf-8')
W=Path(r"Y:\AI\claude-work\fairytale-review")
SRC={"Requiem":(r"Y:\GAME\Fairytale Collection\Games\Requiem\scr.xfl","6D25F45A83AA"),
     "Encore":(r"Y:\GAME\Fairytale Collection\Games\Encore\scr.xfl","CB585DF31160"),
     "Symphony":(r"Y:\GAME\Fairytale Collection\Games\Symphony\scr.xfl","8D0925837DDC")}
edits=json.load(open(W/"terms_edits_auto.json",encoding='utf-8'))
# manual additions/adjustments
for e in edits["Requiem"]:
    if (e["scene"],e["slot"])==("1704.gsc",236):
        assert "할머님의질책도" in e["new"]; e["new"]=e["new"].replace("할머님의질책도","할머님의 질책도"); e["why"].append("띄어쓰기")
edits["Encore"].append(dict(scene="1201.gsc",slot=82,ja="せいしょ……。",old="성경…….",new="성서…….",why=["聖書=성서(せいしょ)"]))
json.dump(edits,open(W/"terms_edits_final.json","w",encoding='utf-8'),ensure_ascii=False,indent=1)
def sha(b): return hashlib.sha256(b).hexdigest().upper()
def read(path):
    data=Path(path).read_bytes(); assert data[:4]==b"LB\x01\x00"
    ts,n=struct.unpack_from("<II",data,4); start=12+ts; ents=[]
    for i in range(n):
        row=data[12+i*0x28:12+(i+1)*0x28]; off,size=struct.unpack_from("<II",row,0x20)
        ents.append([row[:0x20],data[start+off:start+off+size]])
    return data,ents
def pack(ents):
    out=bytearray(b"LB\x01\x00"+struct.pack("<II",len(ents)*0x28,len(ents))); off=0
    for raw,p in ents: out+=raw+struct.pack("<II",off,len(p)); off+=len(p)
    for raw,p in ents: out+=p
    return bytes(out)
report={}
for g,(path,h) in SRC.items():
    data,ents=read(path)
    assert sha(data).startswith(h), (g,"source hash drift")
    assert pack(ents)==data, (g,"round-trip not identical")
    idx={raw.split(b"\0",1)[0].decode("cp932"):i for i,(raw,p) in enumerate(ents)}
    by=__import__('collections').defaultdict(list)
    for e in edits[g]: by[e["scene"]].append(e)
    changed_slots=0
    for scene,es in by.items():
        i=idx[scene]; parts=parse_gsc(ents[i][1]); strs=list(parts.strings)
        for e in es:
            cur=strs[e["slot"]].decode("cp949")
            assert cur==e["old"], (g,scene,e["slot"],"old mismatch")
            strs[e["slot"]]=e["new"].encode("cp949")   # strict
            changed_slots+=1
        newb=rebuild_gsc(parts,tuple(strs)); p2=parse_gsc(newb)
        assert p2.command==parts.command and len(p2.strings)==len(parts.strings)
        diff=[k for k,(a,b) in enumerate(zip(parts.strings,p2.strings)) if a!=b]
        assert sorted(diff)==sorted(e["slot"] for e in es), (g,scene,diff)
        ents[i][1]=newb
    out=pack(ents)
    _,ents2=read_bytes=None,None
    od=W/"build"/g; od.mkdir(parents=True,exist_ok=True); (od/"scr.xfl").write_bytes(out)
    d2,e2=read(od/"scr.xfl")
    _,e0=read(path)
    changed_files=[e2[k][0].split(b"\0",1)[0].decode() for k in range(len(e2)) if e2[k][1]!=e0[k][1]]
    assert len(e2)==len(e0) and all(e2[k][0]==e0[k][0] for k in range(len(e0)))
    report[g]=dict(source=path,source_sha256=sha(data),built=str(od/"scr.xfl"),built_sha256=sha(out),edits=len(edits[g]),changed_slots=changed_slots,changed_gsc=sorted(changed_files),size=(len(data),len(out)))
    print(g, report[g]["edits"],"edits;",len(changed_files),"gsc changed; size",len(data),"->",len(out),"; sha",sha(out)[:12])
json.dump(report,open(W/"build_report.json","w",encoding='utf-8'),ensure_ascii=False,indent=1)

"""Build the feature for the two exact localized codeX editions, always from a known base."""
from pathlib import Path
import sys, os, struct, shutil, json, subprocess, hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assets import ROOT,RBASE,live,read,read_entry,entry_map,sha,parse_archive,GAMES,lwg
from menu_scripts import catalog,script
import pefile
HERE=Path(__file__).resolve().parent
BUILT=HERE/'built'; BASE=HERE/'baseline'; QA=HERE/'trial'
DLL='FairytaleContent.dll'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def backup(src,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        # Copies are independent of future outside installers.
        stage=p.with_suffix(p.suffix+'.new');shutil.copyfile(src,stage);stage.replace(p)
def archive(src,dest,changes):
    obj=parse_archive(src);dest.parent.mkdir(parents=True,exist_ok=True)
    names={e.name for e in obj.entries}
    assert changes.keys()<=names
    stage=dest.with_suffix('.new')
    with src.open('rb') as inp,stage.open('wb') as out:
        out.write(inp.read(12));offset=0
        for e in obj.entries:
            size=len(changes[e.name]) if e.name in changes else e.size
            out.write(e.raw_name+struct.pack('<II',offset,size));offset+=size
        for e in obj.entries:
            if e.name in changes:out.write(changes[e.name]);continue
            inp.seek(e.absolute_offset);remaining=e.size
            while remaining:
                chunk=inp.read(min(4194304,remaining));assert chunk
                out.write(chunk);remaining-=len(chunk)
    stage.replace(dest)
    check=parse_archive(dest)
    assert [e.name for e in check.entries]==[e.name for e in obj.entries]
    for name,b in changes.items():
        assert read_entry(dest,name)==b
def link_feature(src,dest,game_name,expected_sha=None):
    data=bytearray(src.read_bytes())
    assert sha(data).lower()==(expected_sha or read('audit/native_ui.json')[game_name]['sha256']).lower()
    pe=pefile.PE(data=bytes(data));opt=pe.OPTIONAL_HEADER;base=opt.ImageBase;assert base==0x400000
    orig=opt.DATA_DIRECTORY[1];i=pe.get_offset_from_rva(orig.VirtualAddress)
    old=b''
    while any(data[i:i+20]):old+=bytes(data[i:i+20]);i+=20
    assert len(old)==7*20
    section_rva=opt.SizeOfImage
    descriptors=len(old)+40
    dllname=descriptors
    name=dllname+len(DLL)+1
    thunk=(name+2+len('ContentAction')+1+3)&~3
    iat=thunk+8
    payload=bytearray(iat+8)
    payload[:len(old)]=old
    struct.pack_into('<IIIII',payload,len(old),section_rva+thunk,0,0,section_rva+dllname,section_rva+iat)
    payload[dllname:name]=DLL.encode('ascii')+b'\0'
    exp=b'\0\0ContentAction\0';payload[name:name+len(exp)]=exp
    for off in (thunk,iat):struct.pack_into('<I',payload,off,section_rva+name)
    def put(rva,old,new):
        i=pe.get_offset_from_rva(rva)
        assert len(new)==len(old) and data[i:i+len(old)]==old
        data[i:i+len(old)]=new
    # Retain normal codeX behavior for every reserved group other than ex09.
    # Its registration now references a regular, statically imported callback.
    put(0xe410,b'\x68'+struct.pack('<I',base+0x102f0),b'\x68'+struct.pack('<I',base+0x102e8))
    put(0x102e8,b'\x90'*6,b'\xff\x25'+struct.pack('<I',base+section_rva+iat))
    h=pe.sections[-1].get_file_offset()+40
    assert not any(data[h:h+40])
    align=opt.FileAlignment;raw=(len(payload)+align-1)//align*align
    assert len(data)%align==0
    data[h:h+40]=struct.pack('<8sIIIIIIHHI',b'.ftopts\0',len(payload),section_rva,raw,len(data),0,0,0,0,0xc0000040)
    struct.pack_into('<H',data,pe.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(pe.sections)+1)
    struct.pack_into('<I',data,opt.get_field_absolute_offset('SizeOfImage'),section_rva+opt.SectionAlignment)
    struct.pack_into('<I',data,opt.get_field_absolute_offset('SizeOfInitializedData'),opt.SizeOfInitializedData+raw)
    struct.pack_into('<II',data,orig.get_file_offset(),section_rva,descriptors)
    data+=payload.ljust(raw,b'\0')
    linked=pefile.PE(data=bytes(data))
    assert [(e.dll,[i.name for i in e.imports]) for e in linked.DIRECTORY_ENTRY_IMPORT[:-1]]==[(e.dll,[i.name for i in e.imports]) for e in pe.DIRECTORY_ENTRY_IMPORT]
    e=linked.DIRECTORY_ENTRY_IMPORT[-1];assert e.dll==DLL.encode() and e.imports[0].name==b'ContentAction'
    struct.pack_into('<I',data,opt.get_field_absolute_offset('CheckSum'),linked.generate_checksum())
    dest.write_bytes(data)
def fixture(g,out):
    home=live(g);d=QA/g;d.mkdir(parents=True,exist_ok=True)
    for f in home.rglob('*'):
        rel=f.relative_to(home)
        if 'save' in rel.parts or f.name==DLL:continue
        to=d/rel
        if f.is_dir():to.mkdir(parents=True,exist_ok=True);continue
        if rel.parent==Path('.') and (out/f.name).is_file():continue
        if not to.exists():os.link(f,to)
    for p in out.iterdir():
        if p.is_file() and (p.suffix.lower() in ('.exe','.dll','.xfl')):
            to=d/p.name
            if to.exists():to.unlink()
            os.link(p,to)
    (d/'save').mkdir(exist_ok=True)
def main():
    BUILT.mkdir(parents=True,exist_ok=True);report={}
    for g in GAMES:
        home=live(g);out=BUILT/g;out.mkdir(exist_ok=True)
        exe=next(home.glob('*.exe'));base=BASE/g
        for n in (exe.name,'scr.xfl','grps.xfl'):backup(home/n,base/n)
        assert digest(base/exe.name)==read('audit/native_ui.json')[g]['sha256'].lower()
        cat=catalog(g,base/'scr.xfl'); changes={}; stats={}
        for name in entry_map(base/'scr.xfl'):
            if not name.endswith('.gsc'):continue
            src=read_entry(base/'scr.xfl',name);new,counts=script(g,int(name[:4]),src,cat)
            if counts:changes[name]=new;stats[name]=counts
        archive(base/'scr.xfl',out/'scr.xfl',changes)
        new=(BUILT/'art/confscrn.lwg').read_bytes()
        if not (out/'grps.xfl').exists():
            assert sha(read_entry(base/'grps.xfl','confscrn.lwg'))=='ff7b633ba82503f6a054f0829ef66bc3981688082a6e5c1b8dfc3c188ca30c09'
            archive(base/'grps.xfl',out/'grps.xfl',{'confscrn.lwg':new})
        elif read_entry(out/'grps.xfl','confscrn.lwg')!=new:archive(base/'grps.xfl',out/'grps.xfl',{'confscrn.lwg':new})
        link_feature(base/exe.name,out/exe.name,g)
        report[g]={'catalog':cat,'script_edits':stats}
    h=['// Generated from the installed game gallery tables.','#include <utility>']
    for g,rec in report.items():
        c=rec['catalog']
        for label,k in [('CG','cg'),('Pictures','images')]:
            h.append('const std::vector<int> '+g+label+'={'+','.join(map(str,c[k]))+'};')
        h.append('const std::vector<std::pair<int,int>> '+g+'Shadow={'+','.join('{%d,%d}'%v for v in c['shadow'].items())+'};')
    (BUILT/'catalog.h').write_text('\n'.join(h)+'\n',encoding='utf-8')
    shell=Path(os.environ['SystemRoot'])/'System32/cmd.exe'
    vc=Path('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvarsall.bat')
    cmd=BUILT/'compile.cmd'
    cmd.write_text('@echo off\ncall "'+str(vc)+'" x86 >nul\nif errorlevel 1 exit /b 1\ncl /nologo /O2 /EHsc /MT /std:c++17 /utf-8 /I. /LD "..\\content_options.cpp" /link /OUT:FairytaleContent.dll /EXPORT:ContentAction=_ContentAction@8 user32.lib\n',encoding='ascii')
    subprocess.run([str(shell),'/d','/c','compile.cmd'],cwd=BUILT,check=True)
    dll=pefile.PE(str(BUILT/DLL));assert [s.name for s in dll.DIRECTORY_ENTRY_EXPORT.symbols]==[b'ContentAction']
    for g in GAMES:
        out=BUILT/g;shutil.copyfile(BUILT/DLL,out/DLL);fixture(g,out)
        report[g]['files']={p.name:digest(p) for p in out.iterdir() if p.is_file()}
    (HERE/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print({g:(r['catalog']['groups'],r['catalog']['scenes'],len(r['script_edits'])) for g,r in report.items()})
if __name__=='__main__':main()

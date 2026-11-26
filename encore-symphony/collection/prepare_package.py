"""Create a source-visible, portable builder from explicit private input paths.

Reuses Claude's delta-kit xdelta format and the existing collection runtime.
The private spec/cache are outside the package; no original assets or saves are
copied wholesale into the distribution. Only same-file deltas and new files.
"""
from pathlib import Path
import argparse, ast, hashlib, json, os, shutil, subprocess, sys, tempfile, urllib.request, zipfile
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from assemble import EXES
DIRECTORIES={'mov','grpe','grpo','grps','scr','grpo_ex','grpo_map','bgm','wav','voice'}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=1),'utf-8');tmp.replace(path)
def run(args):
    r=subprocess.run([str(a) for a in args],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf-8','replace')[-2500:]+'\n'+r.stdout.decode('utf-8','replace')[-2500:])
def encode(tool,source,target,payload,window,cache):
    # This xdelta CLI uses ANSI filenames. Unicode cwd plus an ASCII source alias
    # and Python-opened stdin/stdout work even when 8.3 filenames are disabled.
    with tempfile.TemporaryDirectory(prefix='delta-',dir=cache) as folder:
        alias=Path(folder)/'source.bin'
        try:os.link(source,alias)
        except OSError:shutil.copyfile(source,alias)
        with target.open('rb') as inp,payload.open('wb') as out:
            r=subprocess.run([str(tool),'-e','-6','-c','-B',str(window),'-s','source.bin','-A'],stdin=inp,stdout=out,stderr=subprocess.PIPE,cwd=folder,creationflags=subprocess.CREATE_NO_WINDOW)
        if r.returncode:payload.unlink(missing_ok=True);raise RuntimeError(r.stderr.decode('utf-8','replace')[-2500:])
def files(root,w):
    for p in sorted(root.iterdir()):
        if p.is_file() and (p.suffix.lower() in {'.acm','.xfl','.dll'} or p.name==EXES[w]):yield p
        elif p.is_dir() and p.name in DIRECTORIES:
            for q in sorted(p.rglob('*')):
                if q.is_file() and not (p.name=='mov' and q.name=='0002.mpg'):yield q
def main():
    a=argparse.ArgumentParser();a.add_argument('spec',type=Path);a.add_argument('--stage-only',action='store_true');args=a.parse_args()
    spec=json.loads(args.spec.read_text('utf-8-sig'));out=Path(spec['output']);out.mkdir(parents=True,exist_ok=True)
    cache=Path(spec['cache']);cache.mkdir(parents=True,exist_ok=True)
    os.environ['TEMP']=os.environ['TMP']=str(cache)
    runtime=out/'Runtime';runtime.mkdir(exist_ok=True)
    embedded=cache/'python-3.11.9-embed-amd64.zip'
    if not embedded.exists():urllib.request.urlretrieve('https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip',embedded)
    if not (runtime/'python.exe').is_file():
        with zipfile.ZipFile(embedded) as z:z.extractall(runtime)
    (runtime/'python311._pth').write_text('python311.zip\n.\n../Scripts\n','ascii')
    import PIL
    shutil.copytree(Path(PIL.__file__).parent,runtime/'PIL',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for item in Path(PIL.__file__).parent.parent.glob('pillow-*.dist-info/licenses'):
        shutil.copytree(item,out/'Licenses'/'Pillow',dirs_exist_ok=True)
    scripts=out/'Scripts';scripts.mkdir(exist_ok=True)
    for n in ['build_collection.py','collection_core.py','assemble.py','album.py','entries.py']:put(HERE/n,scripts/n)
    # Only the gallery vocabulary is needed; reuse its exact existing assignments.
    wording=HERE.parent/'wording.py';source=wording.read_text('utf-8');tree=ast.parse(source)
    selected=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='pairs':selected.append(ast.get_source_segment(source,node))
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'ROUTES','TRACKS'} for t in node.targets):selected.append(ast.get_source_segment(source,node))
    (scripts/'wording.py').write_text('\n\n'.join(selected)+'\n','utf-8')
    adapter=HERE.parents[1]/'requiem'/'adapter'
    for n in ['xfl_tool.py','gsc_codec.py','build_scenario_catalog.py','command_formats.json']:put(adapter/n,scripts/'adapter'/n)
    formats=json.loads((adapter/'command_formats.json').read_text('utf-8'))
    dump(scripts/'adapter'/'command_formats.json',{'commands':formats['commands']})
    for n,src in spec['tools'].items():put(Path(src),out/'Tools'/n)
    fixture=Path(spec['fixture']);common=[]
    common_names=['페어리테일 통합판.exe.config']
    common_names += ['Support/'+p.name for p in (fixture/'Support').glob('*') if p.is_file()]
    common_names += ['Library/'+n for n in ['title.png','doors.png','Jua-Regular.ttf','Jua-OFL.txt']]
    for rel in common_names:put(fixture/rel,out/'Common'/rel)
    if (out/'WebView2_설치.exe').exists():put(out/'WebView2_설치.exe',out/'Common'/'Support'/'WebView2_설치.exe')
    for n in ['castle.js','castle.css','index.html']:put(HERE/n,out/'Common'/'Library'/n)
    net=Path(os.environ['WINDIR'])/'Microsoft.NET'/'Framework64'/'v4.0.30319'
    refs=[]
    for n in ['System.dll','System.Core.dll','System.Drawing.dll','System.Web.Extensions.dll','System.Xaml.dll','WindowsBase.dll','PresentationCore.dll','PresentationFramework.dll']:
        p=net/n
        if not p.exists():p=net/'WPF'/n
        refs.append('/reference:'+str(p))
    refs += ['/reference:'+str(out/'Common'/'Support'/n) for n in ['Microsoft.Web.WebView2.Core.dll','Microsoft.Web.WebView2.Wpf.dll']]
    run([net/'csc.exe','/nologo','/target:winexe','/platform:x64','/optimize+','/codepage:65001','/out:'+str(out/'Common'/'페어리테일 통합판.exe'),*refs,HERE/'Castle.cs',HERE/'EntryArchive.cs'])
    run([net/'csc.exe','/nologo','/target:winexe','/platform:x64','/optimize+','/codepage:65001','/out:'+str(out/'페어리테일 통합판 만들기.exe'),'/reference:'+str(net/'System.dll'),'/reference:'+str(net/'System.Core.dll'),'/reference:'+str(net/'System.Drawing.dll'),'/reference:'+str(net/'System.Windows.Forms.dll'),'/reference:'+str(net/'System.Web.Extensions.dll'),HERE/'Builder.cs'])
    for p in sorted((out/'Common').rglob('*')):
        if p.is_file():common.append({'path':p.relative_to(out/'Common').as_posix(),'payload':p.relative_to(out).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
    man={'schema':1,'version':'2026.11.26','common':common,'games':{},'tools':[]}
    for p in sorted((out/'Tools').glob('*')):man['tools'].append({'payload':p.relative_to(out).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
    if args.stage_only:
        old=out/'manifest.json'
        if old.exists():man['games']=json.loads(old.read_text('utf-8'))['games']
        dump(out/'manifest.json',man);return
    for w,paths in spec['games'].items():
        original,patched=Path(paths['original']),Path(paths['korean']);rows=[]
        known=cache/(w+'-files.json');previous=json.loads(known.read_text('utf-8')) if known.exists() else {}
        current={}
        for i,p in enumerate(files(patched,w)):
            rel=p.relative_to(patched).as_posix();src=original/rel
            stamp=[p.stat().st_size,p.stat().st_mtime_ns,src.stat().st_size if src.exists() else None,src.stat().st_mtime_ns if src.exists() else None]
            old=previous.get(rel)
            payload_ok=old and ('payload' not in old['row'] or
                ((out/old['row']['payload']).is_file() and (out/old['row']['payload']).stat().st_size==old['row']['payload_size']
                 and sha(out/old['row']['payload'])==old['row']['payload_sha256']))
            if old and old['stamp']==stamp and payload_ok:
                row=old['row'];rows.append(row);current[rel]=old;continue
            row={'path':rel,'size':p.stat().st_size,'sha256':sha(p)}
            if src.exists():row.update(source_size=src.stat().st_size,source_sha256=sha(src))
            if row.get('source_sha256')==row['sha256']:row['kind']='same'
            else:
                name=hashlib.sha256(rel.encode()).hexdigest()[:20]
                payload=out/'Patch'/w/(name+('.vcdiff' if src.exists() else '.data'));payload.parent.mkdir(parents=True,exist_ok=True)
                if src.exists():
                    # Claude delta-kit uses an explicit source window bound and VCDIFF.
                    window=min(1<<max(20,(max(src.stat().st_size,p.stat().st_size)-1).bit_length()),(1<<31)-1)
                    encode(out/'Tools'/'xdelta3.exe',src,p,payload,window,cache)
                    row.update(kind='delta',window=window)
                else:put(p,payload);row['kind']='new'
                row.update(payload=payload.relative_to(out).as_posix(),payload_size=payload.stat().st_size,payload_sha256=sha(payload))
            rows.append(row);current[rel]={'stamp':stamp,'row':row};dump(known,{**previous,**current})
            print(w,rel,row['kind'],row.get('payload_size',0),flush=True)
        dump(known,current);man['games'][w]={'exe':EXES[w],'files':rows};dump(out/'manifest.json',man)
    print('PACKAGE READY',str(out),flush=True)
if __name__=='__main__':main()

"""Assemble independent game folders from explicitly selected installations."""
from pathlib import Path
import sys, json, hashlib, os, shutil
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OUT=None
sys.path[:0]=[str(BASE),str(BASE/'qol')]
from collection_core import entry_map,read_entry,parse_gsc,parse_commands,FMT,op,const,archive
GAMES={}
EXES={w:'フェアリーテイル・'+jp+'.exe' for w,jp in [('Requiem','レクイエム'),('Encore','アンコール'),('Symphony','シンフォニー')]}
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def once(src,dest,private=False):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():return
 src=src.resolve()
 # Independent copies prevent later changes from altering the selected source.
 tmp=dest.with_name(dest.name+'.collecting')
 shutil.copyfile(src,tmp);os.replace(tmp,dest)
def jsonout(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.new');t.write_text(json.dumps(o,ensure_ascii=False,indent=1),encoding='utf-8');os.replace(t,p)
def main():
 if OUT is None or not GAMES:raise SystemExit('Use build_collection.py with a configuration.')
 sizes={}
 for work,root in GAMES.items():
  dest=OUT/'Games'/work;size=0
  for p in root.iterdir():
   if p.is_file() and (p.suffix.lower() in {'.acm','.xfl','.dll'} or p.name==EXES[work]) and p.name!='scr.xfl':
    once(p,dest/p.name,private=p.suffix.lower() in ('.exe','.dll'));size+=p.stat().st_size
   if p.is_dir() and p.name in ('save','mov','grpe','grpo','grps','scr','grpo_ex','grpo_map','bgm','wav','voice'):
    for child in p.rglob('*'):
     if child.is_file():
      if p.name=='mov' and child.suffix.lower()=='.mpg':
       once(child,OUT/'Cinema'/work/child.name)
       if child.name in ('0001.mpg','0002.mpg'):continue
      once(child,dest/child.relative_to(root),private=p.name=='save');size+=child.stat().st_size
  # Each work owns its current archive. The hub selects a verified entry archive before launch.
  once(root/'scr.xfl',dest/'scr.xfl',private=True)
  assert digest(root/EXES[work])==digest(dest/EXES[work])
  sizes[work]=size
  print(work,'ready',size,flush=True)
 pub=OUT/'Library';pub.mkdir(exist_ok=True)
 for src,dst in [('common-title-v1.png','title.png'),('work-selection-v2.png','doors.png')]:
  once(BASE/'design'/'collection-main-menu'/src,pub/dst,private=True)
 for name in ['Jua-Regular.ttf','Jua-OFL.txt']:once(BASE/'opening'/'자막'/'fonts'/name,pub/name,private=True)
 jsonout(HERE/'assembly.json',{'installation':str(OUT),'korean_sources':{g:str(v) for g,v in GAMES.items()},'payload_bytes_before_link_savings':sizes})
if __name__=='__main__':main()


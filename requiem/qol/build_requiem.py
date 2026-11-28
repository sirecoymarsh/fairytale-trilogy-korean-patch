"""Rebuild Requiem's viewing-record controls from the supported preview.3 input."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,os

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['input','output','plates','font','ui-tool']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();here=Path(__file__).resolve().parent;repo=here.parents[1]
 source=a.input.resolve();out=a.output.resolve()
 if source==out or source in out.parents or out in source.parents:p.error('input and output must not overlap')
 if out.exists() and any(out.iterdir()):p.error('output must be empty')
 out.mkdir(parents=True,exist_ok=True)
 def sha(path):
  with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
 baseline=json.loads((here/'baseline.json').read_text('utf-8'))
 for name,digest in baseline.items():
  if sha(source/name)!=digest:raise ValueError('Unsupported baseline: '+name)
 shared=repo/'encore-symphony'
 sys.path[:0]=[str(here),str(shared),str(repo/'requiem/adapter'),str(shared/'qol')]
 import assets
 assets.RBASE=repo/'requiem'
 from menu_scripts import catalog,script,parse_gsc,parse_commands,FMT
 from build_options import archive,link_feature
 import settings_art
 c=catalog('Requiem',source/'scr.xfl')
 assert json.loads(json.dumps(c))==json.loads((here/'catalog.json').read_text('utf-8'))
 reserved=set(c['shadow'].values())|{7985,7986,7987,7988}
 changes={};stats={}
 for name in assets.entry_map(source/'scr.xfl'):
  if not name.endswith('.gsc'):continue
  data=assets.read_entry(source/'scr.xfl',name)
  for cmd in parse_commands(parse_gsc(data).command,FMT):
   if cmd.opcode>=0x1000:assert not reserved.intersection(cmd.args),(name,cmd)
  result,edits=script('Requiem',int(name[:4]),data,c)
  if edits:changes[name]=result;stats[name]=edits
 assert not any(1300<=int(n[:4])<1531 for n in assets.entry_map(source/'grpe.xfl') if n[:4].isdigit())
 archive(source/'scr.xfl',out/'scr.xfl',changes)
 settings_art.OUT=out/'art';settings_art.PLATES=a.plates.resolve();settings_art.FACE=a.font.resolve()
 settings_art.run=lambda *args:subprocess.run([str(a.ui_tool.resolve()),*map(str,args)],check=True,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 art=settings_art.options_lwg(assets.read_entry(source/'grps.xfl','confscrn.lwg'))
 archive(source/'grps.xfl',out/'grps.xfl',{'confscrn.lwg':art})
 name=next(n for n in baseline if n.endswith('.exe'))
 link_feature(source/name,out/name,'Requiem',expected_sha=baseline[name])
 for name in ['catalog.h','content_options.cpp']:shutil.copyfile(here/name,out/name)
 report={'translator_model':'Codex internal','catalog':c,'script_edits':stats,'files':{f.name:sha(f) for f in out.iterdir() if f.suffix in ['.exe','.xfl']}}
 (out/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'cg_variants':len(c['images']),'scenes':c['scenes'],'changed_scripts':len(stats),'output':str(out)},ensure_ascii=False))
if __name__=='__main__':main()

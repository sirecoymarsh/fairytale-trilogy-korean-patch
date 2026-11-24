import json,sys,os,shutil,hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
W=Path(r"Y:\AI\claude-work\fairytale-review")
rep=json.load(open(W/"build_report.json",encoding='utf-8'))
T={"Requiem":[r"P:\AI\Codex\projects\fairytale-requiem-ko\runtime\trial_ko\scr.xfl",r"Y:\GAME\Fairytale Collection\Games\Requiem\scr.xfl"],
   "Encore":[r"Y:\GAME\Fairytale Encore\scr.xfl",r"Y:\GAME\Fairytale Collection\Games\Encore\scr.xfl"],
   "Symphony":[r"Y:\GAME\Fairytale Symphony\scr.xfl",r"Y:\GAME\Fairytale Collection\Games\Symphony\scr.xfl"]}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
log={}
for g,paths in T.items():
    built=Path(rep[g]["built"]); bh=rep[g]["built_sha256"]; assert sha(built)==bh
    for i,p in enumerate(paths):
        p=Path(p); before=sha(p); assert before==rep[g]["source_sha256"],(g,p,"target changed since build")
        bdir=W/"backup"/g/("standalone" if i==0 else "collection"); bdir.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,bdir/"scr.xfl"); assert sha(bdir/"scr.xfl")==before
        tmp=p.with_name("scr.xfl.terms-new"); shutil.copyfile(built,tmp); assert sha(tmp)==bh
        os.replace(tmp,p); after=sha(p); assert after==bh
        log[str(p)]=dict(before=before,after=after,backup=str(bdir/"scr.xfl"))
        print(g,p,before[:12],"->",after[:12])
json.dump(log,open(W/"install_log.json","w",encoding='utf-8'),ensure_ascii=False,indent=1)

"""Deploy exactly the tested files. Keep progress, saves and translation handoff independent."""
from build_options import *
from datetime import datetime,timezone
def writejson(dst,obj):
    tmp=dst.with_suffix(dst.suffix+'.content-new')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(dst)
def install():
    report=json.loads((HERE/'build.json').read_text(encoding='utf-8'))
    checks={}
    staged=[];swapped=[]
    for g in GAMES:
        home=live(g);checks[g]={}
        evidence=json.loads((HERE/'evidence'/g/'buttons.json').read_text(encoding='utf-8'))
        assert evidence['real_buttons']==4 and evidence['flags_restore'] and evidence['preferences_preserved']
        for n,after in report[g]['files'].items():
            assert Path(n).name==n and (n in ('scr.xfl','grps.xfl',DLL) or n==next(home.glob('*.exe')).name)
            dest=home/n;base=BASE/g/n;built=BUILT/g/n
            assert digest(built)==after
            prior=digest(dest) if dest.exists() else None
            baseline=digest(base) if base.is_file() else None
            if prior not in (baseline,after):raise ValueError(f'installed file changed: {dest}')
            checks[g][n]={'before':baseline,'after':after}
            if prior==after:continue
            staged.append((dest,built,base if baseline else None))
    # Stage siblings with full hashes before touching either game.
    for dst,bld,_ in staged:
        tmp=dst.with_suffix(dst.suffix+'.ft-new');shutil.copyfile(bld,tmp)
        assert digest(tmp)==digest(bld)
    try:
        for dst,bld,base in sorted(staged,key=lambda row:row[0].suffix.lower()=='.exe'):
            dst.with_suffix(dst.suffix+'.ft-new').replace(dst);swapped.append((dst,base))
        for g in GAMES:
            for n,item in checks[g].items():assert digest(live(g)/n)==item['after']
    except BaseException:
        for dst,base in reversed(swapped):
            if base:
                tmp=dst.with_suffix(dst.suffix+'.ft-restore');shutil.copyfile(base,tmp);tmp.replace(dst)
            elif dst.exists():dst.unlink()
        raise
    for g in GAMES:
        art=read_entry(live(g)/'grps.xfl','confscrn.lwg')
        assert len([v for v in lwg(art) if v[0].startswith('ex09_')])==9
    now=datetime.now(timezone.utc).isoformat()
    result={'date_utc':now,'translator_model':'Codex internal','files':checks,'install':{g:str(live(g)) for g in GAMES},'rollback':str(BASE),'evidence':{g:str(HERE/'evidence'/g) for g in GAMES},'text_preservation':'All original scenario strings, IDs and original command addresses kept. Translation packets still apply to the clean originals. Apply menu_scripts.script to translated GSCs before replacing the complete bank.','source':str(HERE)}
    writejson(ROOT/'audit/content_options.json',result)
    pr=read('progress.json');pr['content_options']={'phase':'설치 및 두 작품의 실제 환경 설정 검증 완료','report':str(ROOT/'audit/content_options.json'),'native_buttons':4,'groups':{g:report[g]['catalog']['groups'] for g in GAMES},'replays':{g:report[g]['catalog']['scenes'] for g in GAMES},'user_saves':'설치에서 읽거나 변경하지 않음','translation_handoff':'원본 대사와 행 ID 유지','default_font_display':'ＭＳ ゴシック 원래 시스템 글꼴명','translator_model':'Codex internal'}
    writejson(ROOT/'progress.json',pr);print('installed',list(checks))
if __name__=='__main__':install()

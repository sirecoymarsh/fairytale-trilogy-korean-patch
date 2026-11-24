from assets import *
from labels import raw,emit,INFO,ART,artkey
from install import encode,current_hash
from PIL import Image
import shutil
KEY='grpo/0106.wcg'
master=Path('P:/AI/Codex/generated_images/01a1e81c-6c8c-72a0-9646-fde8208b47a2/exec-18df8cb7-0a40-49c5-b39a-49a50c8e115b.png')
if __name__=='__main__':
    g='Encore'; dest=live(g)/'grpo.xfl'; local=ROOT/'staging'/g/'grpo.xfl'; arc=parse_archive(dest)
    reports=read('audit/install.json'); bank=reports[g]['banks']['grpo']; old=read('audit/encoded.json')
    assert current_hash(dest)==bank['installed_sha256'] and not (live(g)/KEY).exists()
    assert sha(read_entry(dest,'0106.wcg'))==old[g][KEY]['sha256']
    setting=RBASE/'work/asset_polish_20260929/handwriting/hover/0104'
    assert current_hash(setting/'candidate.wcg')==sha(read_entry(dest,'0104.wcg'))
    src=raw(g,KEY); m=Image.open(master).convert('RGBA')
    m=m.crop(m.getchannel('A').point(lambda a:255 if a>5 else 0).getbbox())
    x,y,r,b=src.getchannel('A').getbbox(); ref=Image.open(setting/'candidate.png').getchannel('A').point(lambda z:255 if z>5 else 0).getbbox()
    h=min(ref[3]-ref[1],b-y-2); w=round(m.width*h/m.height)
    assert w<r-x and h>=60
    clean=Image.new('RGBA',src.size); out=clean.copy();out.alpha_composite(m.resize((w,h),Image.Resampling.LANCZOS),(r-w-1,round((y+b-h)/2)))
    emit(g,KEY,src,clean,out,'ムービー','영상','환경 설정 손글씨 마스터를 기준으로 제작한 영상 전용 잉크 도안. 같은 높이, 오른쪽 기준, 투명 바탕.')
    work=ART/artkey(g,KEY);shutil.copyfile(master,work/'ink_master.png')
    new=encode(INFO,old)[g][KEY];newdata=(ROOT/new['file']).read_bytes()
    baseline=ROOT/'rollback'/g/'grpo.before-movie-popup.xfl'
    if not baseline.exists():shutil.copy2(dest,baseline)
    assert current_hash(baseline)==current_hash(dest)
    pending=dest.with_name('grpo.popup-incoming');expected={}
    with dest.open('rb') as a,pending.open('wb') as f:
        f.write(a.read(12));pos=0
        for e in arc.entries:
            ns=len(newdata) if e.name=='0106.wcg' else e.size
            f.write(e.raw_name+struct.pack('<II',pos,ns));pos+=ns
        for e in arc.entries:
            a.seek(e.absolute_offset);d=newdata if e.name=='0106.wcg' else a.read(e.size)
            expected[e.name]=sha(d);f.write(d)
    rebuilt=parse_archive(pending);assert [e.raw_name for e in rebuilt.entries]==[e.raw_name for e in arc.entries]
    for f,hsh in expected.items():assert sha(read_entry(pending,f))==hsh
    after=current_hash(pending);shutil.copyfile(pending,local);os.replace(pending,dest);entry_map.cache_clear()
    assert current_hash(dest)==after and sha(read_entry(dest,'0106.wcg'))==new['sha256']
    old[g][KEY]=new;save('audit/encoded.json',old);labels=read('audit/labels.json');labels[g][KEY]=INFO[g][KEY];save('audit/labels.json',labels)
    bank['installed_sha256']=after;bank['asset_set_sha256']=sha(repr(sorted((k,v['sha256']) for k,v in old[g].items() if k.startswith('grpo/'))).encode());save('audit/install.json',reports)
    progress=read('progress.json');progress['status'][g]['banks']['grpo']=bank;progress['movie_hover_lettering']={'game':g,'entry':KEY,'sha256':new['sha256'],'reference':'grpo/0104.wcg','verified_unchanged_other_entries':len(expected)-1};save('progress.json',progress)
    print('popup verified',w,h,len(expected)-1,after)

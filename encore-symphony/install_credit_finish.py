"""Install only the four reviewed Symphony credit cards and refresh their existing audit."""
from pathlib import Path
import base64
import io
import json
import os
import re
import shutil
import struct
import subprocess

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from assets import ROOT, live, read, source, read_entry, parse_archive, sha, entry_map
from focus import fullpath
from labels import FONT
from install import encode, current_hash
from install_hospital_sign import write_json, write_bytes

GAME = 'Symphony'
ORG = source(GAME)/'grpe.xfl'
LIVE = live(GAME)/'grpe.xfl'
STAGE = ROOT/'staging/Symphony/grpe.xfl'
BACKUP = ROOT/'rollback/Symphony/grpe.before-credit-finish.xfl'
ART = ROOT/'art/Symphony/grpe'
AUDIT = ROOT/'audit'
TMP = ROOT/'tmp/credit-finish'
PRIOR = '653b0c5aad4c4758738541efffae14fd88be87bf52dcdf3f9b582d3acfa04ad6'
OLD = {'3022':'ad119e9ad2e81fee5df9133967eaa6e342e1daef1287a582a117130b4a765fd0',
       '4003':'8ad7288c10e8e92a9b534a44401836d4bbd1c6cb5c101c35ede8e952d73c5152',
       '4004':'f4573cec1c55abd2cc79d10af0e8131e4bdcc8fe1023d23b26291ca22728e5f7',
       '4010':'f6595ca3b9ee2ae9b164250dc15c4dfca5994f70dbdfcea012e6b13dbea8090d'}
CREDITS = {
    '3022':('공통 제작진 카드','기획·시나리오, 원화, 음악, 오프닝 테마, 판매와 제작 크레딧을 앙코르와 같은 한국어 카드로 표시한다.'),
    '4003':('CG 작업진','CG 담당자 ‘오키 이누타로’를 다른 담당자와 같은 흰색 글씨로 표기했다.'),
    '4004':('프로그램·스크립트 작업진','프로그램·스크립트 담당자 이름을 ‘노기 후나사토 (codeX)’로 표기했다.'),
    '4010':('제작·저작과 회사 로고','원래 위치에 ‘제작·저작’을 한 줄로 배치했다. 아래에는 원작의 Liar-soft 로고가 보인다.')
}
BANDS = {'4003':(545,442,735,480), '4004':(475,440,805,485), '4010':(570,273,710,344)}
NAME_SOURCES = ['https://www.liar.co.jp/fairy_symphony/',
    'https://vndb.org/s10273', 'https://vndb.org/s7796',
    'https://www.mobygames.com/game/213558/sona-nyl-of-the-violet-shadows-refrain/credits/xbox360/']


def uid(n):
    return 'grpe/'+n+'.wcg'


def pixels(path):
    with Image.open(path) as im:
        return np.array(im.convert('RGBA'))


def make_bank(baseline, path, new):
    entries = parse_archive(baseline).entries
    assert len(entries)==149 and {n+'.wcg' for n in OLD} <= {e.name for e in entries}
    hashes = {}
    replacements = {n+'.wcg': (ROOT/r['file']).read_bytes() for n,r in new.items()}
    with baseline.open('rb') as src, path.open('wb') as dst:
        dst.write(src.read(12))
        offset = 0
        for e in entries:
            size = len(replacements[e.name]) if e.name in replacements else e.size
            dst.write(e.raw_name + struct.pack('<II',offset,size))
            offset += size
        for e in entries:
            src.seek(e.absolute_offset)
            before = src.read(e.size)
            assert len(before)==e.size
            if e.name in replacements:
                assert sha(before)==OLD[Path(e.name).stem]
            after = replacements.get(e.name,before)
            hashes[e.name] = sha(after)
            dst.write(after)
    out = parse_archive(path).entries
    assert [e.raw_name for e in out]==[e.raw_name for e in entries]
    with path.open('rb') as dst:
        for e in out:
            dst.seek(e.absolute_offset)
            assert sha(dst.read(e.size))==hashes[e.name]
    return len(entries)-len(new)


def check_idle():
    command = "$ErrorActionPreference='Stop'; $root='Y:\\GAME\\Fairytale Symphony\\'; Get-Process | Where-Object { $_.Path -and $_.Path.StartsWith($root,[StringComparison]::OrdinalIgnoreCase) } | Select-Object -ExpandProperty Id"
    procs = subprocess.run(['powershell','-NoProfile','-Command',command],check=True,capture_output=True)
    if procs.stdout.strip():
        raise RuntimeError('Symphony is currently running')


def checked_install(baseline, pending, after):
    if not BACKUP.exists():
        try:
            os.link(baseline,BACKUP)
        except OSError:
            shutil.copyfile(baseline,BACKUP)
    assert current_hash(BACKUP)==PRIOR
    assert current_hash(STAGE) in (PRIOR,after)
    check_idle()
    if current_hash(LIVE)==after:
        return False
    assert current_hash(LIVE)==PRIOR
    incoming = LIVE.with_name('grpe.credit-incoming')
    shutil.copyfile(pending,incoming)
    assert current_hash(incoming)==after
    check_idle()
    assert current_hash(LIVE)==PRIOR
    os.replace(incoming,LIVE)
    return True


def verify_persisted(new, previous_by_id, words):
    bank = parse_archive(LIVE).entries
    files = {}
    jobs = []
    for n,r in new.items():
        assert not (live(GAME)/uid(n)).exists()
        e = next(x for x in bank if x.name==n+'.wcg')
        assert sha(read_entry(LIVE,e.name))==r['sha256']
        files[n] = ART/n/('installed-'+r['sha256'][:12]+'.png')
        if not files[n].exists():
            jobs.append('\t'.join(map(str,(LIVE,e.absolute_offset,e.size,files[n],0))))
    if jobs:
        job = TMP/'decode-installed.tsv'
        job.write_text('\n'.join(jobs)+'\n','utf-8-sig')
        subprocess.run([str(ROOT/'tools/RasterBatch.exe'),str(job)],check=True)
    cmap = TTFont(str(FONT)).getBestCmap()
    proof = {}
    for n,installed in files.items():
        k = uid(n)
        old = pixels(fullpath(GAME,k))
        candidate = pixels(ART/n/'final.png')
        im = pixels(installed)
        with Image.open(ART/n/'ownership.png') as m:
            mask = np.asarray(m.convert('L'))!=0
        assert im.shape==(720,1280,4) and np.array_equal(im,candidate)
        assert np.array_equal(im[~mask],old[~mask]) and np.array_equal(im[:,:,3],old[:,:,3])
        assert all(cmap.get(ord(c)) for c in words[k]['target_ko'] if not c.isspace())
        rec = dict(installed_png=str(installed),original_sha256=sha(read_entry(ORG,n+'.wcg')),
                   previous_installed_sha256=OLD[n],sha256=new[n]['sha256'],geometry=[1280,720],
                   outside_owned_changes=0,roundtrip_pixel_differences=0,missing_font_characters=[])
        if n in BANDS:
            ref = pixels((ROOT/previous_by_id[n]['file']).with_suffix('.png'))
            changed=np.any(ref!=im,axis=2)
            l,t,r,b=BANDS[n]
            assert changed.any() and int(changed.sum())==int(changed[t:b,l:r].sum())
            ys,xs=np.nonzero(changed)
            rec.update(change_bounds_from_previous=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changed_pixels_from_previous=int(changed.sum()))
        if n=='3022':
            assert read_entry(LIVE,n+'.wcg')==read_entry(live('Encore')/'grpe.xfl',n+'.wcg')
            rec['matches_encore_installed_bytes']=True
        if n=='4010':
            clean=pixels(ART/n/'clean.png')
            donor=pixels(fullpath(GAME,uid('4009')))
            area=np.s_[307:343,512:768]
            assert np.array_equal(clean[area],donor[area]) and np.array_equal(im[345:],old[345:])
            old_ink=np.any(clean[area]!=old[area],axis=2)
            assert int(old_ink.sum())==1468
            votes=sum(np.all(pixels(fullpath(GAME,uid(str(other))))[area]==donor[area],axis=2).astype(int) for other in range(4002,4009))
            assert int(votes[old_ink].min())>=2
            rec.update(source_text_erased_pixels=1468,source_ink_bounds=[598,314,682,336],
                       preserved_logo_and_lower_card=True,min_other_original_cards_confirming_each_recovered_pixel=int(votes[old_ink].min()))
        proof[n]=rec
    return proof


def refresh_review(proof,bank_hash):
    folder=AUDIT/'cg_japanese_review'
    findings=read(folder/'findings.json')
    page=folder/'index.html'
    html=page.read_text('utf8')
    tag=re.search(r'(<script id="records" type="application/json">)(.*?)(</script>)',html,re.S)
    cards=json.loads(tag[2])
    for n,rec in proof.items():
        key=uid(n)
        row=next(x for x in findings['findings'] if x['game']==GAME and x['asset']==key)
        item=next(x for x in cards if x['game']==GAME and x['asset']==key)
        if row['status']!='resolved':
            row['before_detail']=row['detail']
            item['before_image']=item['image']
        row.update(status='resolved',title=CREDITS[n][0],detail=CREDITS[n][1],
                   original_sha256=rec['original_sha256'],previous_installed_sha256=OLD[n],
                   sha256=rec['sha256'],sources_identical_to_disc={GAME:False})
        item.update(row, before_caption='수정 전 설치본 보기' if n!='3022' else '일본어 원본 보기')
        with Image.open(rec['installed_png']) as img, io.BytesIO() as data:
            img.convert('RGB').crop(tuple(row['crop'])).save(data,format='PNG')
            item['image']='data:image/png;base64,'+base64.b64encode(data.getvalue()).decode('ascii')
    counts={kind:sum(x['status']==kind for x in findings['findings']) for kind in ('resolved','confirmed','uncertain')}
    assert counts==dict(resolved=5,confirmed=0,uncertain=2)
    findings.update(counts,verification='설치된 XFL의 이미지와 GSC 호출을 대조했다. 간호사실 간판과 심포니 크레딧 4장은 설치 후 다시 추출했다.')
    findings['archive_fingerprints'][GAME]['grpe'].update(sha256=bank_hash,matches_last_install=True)
    findings.setdefault('font_cmap_missing_before_credit_fix',findings['font_cmap_missing'])
    findings['font_cmap_missing']=[]
    html=html[:tag.start(2)]+json.dumps(cards,ensure_ascii=False,separators=(',',':'))+html[tag.end(2):]
    html=html.replace('앙코르의 병원 간판을 ‘간호사실’로 한국어화했다. 심포니에는 일본어가 확인된 이미지 4장이 남아 있다.',
                      '앙코르의 병원 간판 1장과 심포니의 크레딧 4장을 한국어화했다. 두 작품에 공통으로 쓰인 이미지 2장은 글씨가 작아 판독을 보류했다.')
    html=re.sub(r'<h2>일본어가 확인된 이미지</h2><div class="tablewrap"><table>.*?<tbody id="confirmed"></tbody></table></div>','',html,count=1)
    html=html.replace('앙코르 간판은 설치 아카이브에서 다시 추출해 확인했다.','앙코르 간판과 심포니 크레딧은 설치 아카이브에서 다시 추출해 확인했다.')
    html=html.replace("t.textContent='일본어 원본 보기';t.setAttribute","t.textContent=r.before_caption||'일본어 원본 보기';t.setAttribute")
    html=html.replace("t.textContent=show?'한국어 설치본 보기':'일본어 원본 보기';photo.alt=show?'병원 간판 일본어 원본':'병원 간판 한국어 설치본';",
                      "t.textContent=show?'한국어 설치본 보기':(r.before_caption||'일본어 원본 보기');photo.alt=r.work+' '+r.title+(show?' 수정 전':' 한국어 설치본');")
    html=html.replace("window.addEventListener('resize',fit);pick(0);",
                      "window.addEventListener('resize',fit);const number=new URLSearchParams(location.search).get('asset');const initial=number?rows.findIndex(r=>r.asset==='grpe/'+number+'.wcg'):-1;pick(initial<0?0:initial);")
    assert 'r.before_caption' in html and 'new URLSearchParams(location.search)' in html
    write_json(folder/'findings.json',findings)
    write_bytes(page,html.encode('utf8'))


def main():
    check_idle()
    records=read('audit/install.json')
    current=current_hash(LIVE)
    if current!=PRIOR:
        assert BACKUP.exists() and current_hash(BACKUP)==PRIOR
    baseline=LIVE if current==PRIOR else BACKUP
    previous=read('audit/encoded.json')
    old_by_id={}
    for n in BANDS:
        previous_entry=previous[GAME][uid(n)]
        if previous_entry['sha256']!=OLD[n]:
            old_proof=read('audit/credit_finish.json')['previous_encoded']
            previous_entry=old_proof[n]
        assert previous_entry['sha256']==OLD[n]
        old_by_id[n]=previous_entry
    words=read(TMP/'credit-rows.json')
    enc=encode({GAME:words},previous)[GAME]
    shared=previous['Encore'][uid('3022')]
    assert shared['sha256']==sha(read_entry(live('Encore')/'grpe.xfl','3022.wcg'))
    new={n:(shared if n=='3022' else enc[uid(n)]) for n in OLD}
    words[uid('3022')]=dict(read('audit/logos.json')['Encore'][uid('3022')])
    for row in words.values():row['translator_model']='Codex internal'
    pending=STAGE.with_name('grpe.credit-pending.xfl')
    unchanged=make_bank(baseline,pending,new)
    after=current_hash(pending)
    assert current in (PRIOR,after) and unchanged==145
    switched=checked_install(baseline,pending,after)
    try:
        entry_map.cache_clear()
        assert current_hash(LIVE)==after
        proof=verify_persisted(new,old_by_id,words)
    except Exception:
        if switched and current_hash(LIVE)==after:
            incoming=LIVE.with_name('grpe.credit-recovering')
            shutil.copyfile(BACKUP,incoming)
            assert current_hash(incoming)==PRIOR
            os.replace(incoming,LIVE)
        raise
    os.replace(pending,STAGE)
    report=records[GAME]
    bank=report['banks']['grpe']
    if bank['installed_sha256']==PRIOR:
        bank['changed_entries']+=1
        report['changed_image_states']['new']+=1
    else:assert bank['installed_sha256']==after
    for n,entry in new.items():previous[GAME][uid(n)]=entry
    bank.update(installed_sha256=after,asset_set_sha256=sha(repr(sorted((k,r['sha256']) for k,r in previous[GAME].items() if k.startswith('grpe/'))).encode()))
    plates=read('audit/plates.json')
    plates[GAME].update({uid(n):words[uid(n)] for n in BANDS})
    logos=read('audit/logos.json')
    logos.setdefault(GAME,{})[uid('3022')]=words[uid('3022')]
    summary=dict(game=GAME,translator_model='Codex internal',model_provenance='Codex desktop, GPT-6',sources=NAME_SOURCES,
                 previous_bank_sha256=PRIOR,installed_bank_sha256=after,entry_count=149,unchanged_other_entries=unchanged,
                 backup=str(BACKUP),previous_encoded=old_by_id,assets=proof,proper_names={'大木犬太郎':'오키 이누타로','禾刀郷':'노기 후나사토'})
    write_json(AUDIT/'credit_finish.json',summary)
    write_json(AUDIT/'plates.json',plates);write_json(AUDIT/'logos.json',logos)
    write_json(AUDIT/'encoded.json',previous);write_json(AUDIT/'install.json',records)
    progress=read('progress.json');progress['status'][GAME]=report
    progress['symphony_credit_finish']=dict(assets=list(map(uid,OLD)),installed_sha256=after,verification='audit/credit_finish.json')
    write_json(ROOT/'progress.json',progress)
    refresh_review(proof,after)
    print(json.dumps(dict(installed=after,unchanged=unchanged,assets={n:r['sha256'] for n,r in proof.items()}),ensure_ascii=False))


if __name__=='__main__':
    main()

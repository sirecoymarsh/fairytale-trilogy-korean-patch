"""Build one native-engine collection using the verified existing Korean patches."""
from pathlib import Path
import argparse, base64, json, os, shutil, sys, uuid
sys.dont_write_bytecode = True
from build_collection import (WORKS, SAVES, sha, emit, safe, overlap, copy,
                              decode, running, verify_file, is_save, execute)
import assemble, entries, album
from unified_entries import native_menu
KEYS = {'Requiem':'R', 'Encore':'A', 'Symphony':'S'}
ENGINE = '페어리테일 이야기 모음.exe'


def engine_patch(source, target, spec):
    if sha(source) != spec['input_sha256']:
        raise ValueError('지원하는 심포니 엔진이 아니에요.')
    data = bytearray(source.read_bytes())
    for part in spec['patches']:
        start = part['offset']; old = bytes.fromhex(part['before']); new = bytes.fromhex(part['after'])
        if data[start:start + len(old)] != old:
            raise ValueError('엔진 연결 위치가 달라요.')
        data[start:start + len(old)] = new
    target.write_bytes(data)
    verify_file(target, spec['output'])


def import_saves(roots, requested, stage, receipt):
    for w,root in roots.items():
        target = stage/'Save'/KEYS[w]; target.mkdir(parents=True,exist_ok=True)
        if not requested[w].get('import_save'): continue
        if running((root/assemble.EXES[w]).resolve()):
            raise ValueError(WORKS[w]+'을 종료한 뒤 다시 만들어 주세요.')
        source = safe(root,'save')
        if source.is_dir():
            for p in sorted(source.iterdir()):
                if not is_save(p,w): continue
                p = safe(source,p.name); before = sha(p); dest = target/p.name; copy(p,dest)
                if sha(dest) != before or sha(p) != before:
                    raise ValueError('복사하는 동안 세이브가 바뀌었어요. 게임을 종료해 주세요.')
                receipt['works'][w]['save_files'] += 1
                receipt['works'][w]['save_sha256'][p.name] = before
        if not receipt['works'][w]['save_files']:
            emit(WORKS[w]+' · 가져올 세이브가 없어 새 기록으로 시작해요.')


def build(config, package):
    package = package.resolve()
    manifest = json.loads((package/'manifest.json').read_text('utf-8-sig'))
    requested = config.get('games', {})
    if set(requested) != set(WORKS):
        raise ValueError('레퀴엠·앙코르·심포니 세 작품의 설치 폴더가 모두 필요해요.')
    out = Path(config['output']).resolve()
    if out.parent == out or overlap(out, package):
        raise ValueError('제작기와 겹치지 않는 새 출력 폴더를 선택해 주세요.')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('출력 폴더가 비어 있지 않아요. 새 폴더를 선택해 주세요.')
    roots = {w:Path(v['path']).resolve() for w,v in requested.items()}
    for w, root in roots.items():
        if not root.is_dir() or not (root/assemble.EXES[w]).is_file():
            raise ValueError(WORKS[w]+' 실행 파일이 있는 설치 폴더를 선택해 주세요.')
        if overlap(out, root) or overlap(root, package):
            raise ValueError('원본 게임·제작기·출력 폴더는 서로 겹칠 수 없어요.')
        if any(w != other and overlap(root, candidate) for other,candidate in roots.items()):
            raise ValueError('각 작품의 설치 폴더를 따로 선택해 주세요.')
        if running((root/assemble.EXES[w]).resolve()):
            raise ValueError(WORKS[w]+'을 종료한 뒤 만들어 주세요.')
    receipt = {'schema':2, 'builder':manifest['version'], 'mode':'single-native-engine',
               'sources_unchanged':True, 'works':{}, 'ui':'existing-castle-in-process'}
    emit('세 작품의 설치 파일과 제작 도구를 확인하고 있어요.')
    for item in manifest['tools'] + manifest['common']:
        verify_file(safe(package,item['payload']),item)
    plan = []; needed = sum(x['size'] for x in manifest['common']) + 2 * 1024**3
    scratch = 0
    for w,root in roots.items():
        info = receipt['works'][w] = {'import_save':bool(requested[w].get('import_save',False)),
                                      'files':[], 'save_files':0, 'save_sha256':{}}
        for row in manifest['games'][w]['files']:
            src = safe(root,row['path']); state = 'missing'
            if src.is_file():
                if src.stat().st_size not in {row['size'],row.get('source_size')}:
                    raise ValueError(WORKS[w]+'의 지원하지 않는 파일: '+row['path'])
                digest = sha(src)
                if digest == row['sha256']: state = 'korean'
                elif digest == row.get('source_sha256'): state = 'original'
                else: raise ValueError(WORKS[w]+'의 지원하지 않는 파일: '+row['path'])
            if state == 'missing' and row['kind'] != 'new':
                raise ValueError(WORKS[w]+' 설치 파일이 없어요: '+row['path'])
            if state != 'korean' and row['kind'] != 'same':
                verify_file(safe(package,row['payload']),{'size':row['payload_size'],'sha256':row['payload_sha256']})
                if row['kind'] == 'delta' and src.drive.lower() != out.drive.lower():
                    scratch = max(scratch,row.get('source_size',0))
            plan.append((w,src,row,state)); needed += row['size']
            info['files'].append({'path':row['path'],'input':state,'sha256':row['sha256']})
        if requested[w].get('import_save'):
            source = safe(root,'save')
            if source.is_dir():
                for p in source.iterdir():
                    if is_save(p,w): safe(source,p.name); needed += p.stat().st_size
    # Optional local reuse accepts only the exact verified gallery bytes.
    library = config.get('verified_library')
    cache = json.loads((package/'gallery-cache.json').read_text('utf-8-sig')) if library else []
    if library:
        library = Path(library).resolve()
        if overlap(out,library): raise ValueError('감상실 재사용 경로와 출력 폴더가 겹쳐요.')
        for row in cache: verify_file(safe(library,row['path']),row)
        emit('검증된 기존 감상실 파일을 재사용합니다.')
    needed += scratch
    out.parent.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(out.parent).free < needed:
        raise ValueError('출력 드라이브에 약 '+str((needed+1024**3-1)//1024**3)+' GB의 여유 공간이 필요해요.')
    stage = out.with_name('.'+out.name+'.building-'+uuid.uuid4().hex); stage.mkdir()
    try:
        tmp = stage/'.build-temp'; tmp.mkdir(); os.environ['TEMP'] = os.environ['TMP'] = str(tmp)
        for item in manifest['common']: copy(safe(package,item['payload']),safe(stage,item['path']))
        for i,(w,src,row,state) in enumerate(plan):
            emit('[%d/%d] %s · %s' % (i+1,len(plan),WORKS[w],row['path']))
            name = row['path']
            # Installation executables are verified above, but only Symphony's engine is used.
            if name == assemble.EXES[w]:
                if w != 'Symphony': continue
                dest = tmp/'engine.bin'
            elif name in ('FairytaleContent.dll','vorbis.acm'):
                if w != 'Symphony': continue
                dest = stage/name
            else: dest = safe(stage/'Data'/KEYS[w],name)
            dest.parent.mkdir(parents=True,exist_ok=True)
            if state == 'korean' or row['kind'] == 'same': copy(src,dest)
            elif row['kind'] == 'new': copy(safe(package,row['payload']),dest)
            else: decode(package/'Tools/xdelta3.exe',src,safe(package,row['payload']),dest,row['window'],tmp)
            verify_file(dest,row)
        engine_patch(tmp/'engine.bin',stage/ENGINE,manifest['engine'])
        import_saves(roots,requested,stage,receipt)
        emit('한 엔진에서 읽을 작품별 시작 경로를 만들고 있어요.')
        for w,key in KEYS.items():
            target = stage/'Integration'/key; target.mkdir(parents=True)
            bank = stage/'Data'/key/'scr.xfl'
            (target/'0001.gsc').write_bytes(native_menu(bank))
            for number,mode in [(59990,'story'),(59992,'replay')]+([(59993,'credits')] if w=='Symphony' else []):
                (target/(str(number)+'.gsc')).write_bytes(entries.launch_entry(w,bank,mode)['0000.gsc'])
        if library:
            for row in cache:
                dest = safe(stage/'Library',row['path']); copy(safe(library,row['path']),dest); verify_file(dest,row)
            receipt['gallery'] = 'reused-exact-verified-files'
        else:
            album.GAMES = {w:stage/'Data'/key for w,key in KEYS.items()}
            album.OUT = stage; album.PUB = stage/'Library'; album.ART = album.PUB/'media'
            album.TMP = tmp; album.TOOL = package/'Tools/UiAssetTool.exe'
            emit('기존 구성기로 CG와 음악 감상실을 만들고 있어요.'); album.main()
            for w,key in KEYS.items():
                for p in sorted((stage/'Data'/key/'mov').glob('*.mpg')):
                    if p.stem == '0002': continue
                    emit(WORKS[w]+' · 감상실 영상 '+p.stem+' 변환 중')
                    dest = stage/'Library/cinema'/w/(p.stem+'.mp4'); dest.parent.mkdir(parents=True,exist_ok=True)
                    execute([package/'Tools/ffmpeg.exe','-nostdin','-hide_banner','-loglevel','error',
                             '-i',p,'-map','0:v:0','-map','0:a:0?','-c:v','libx264','-preset','fast','-crf','19',
                             '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-threads','4',dest])
            receipt['gallery'] = 'generated-from-installed-games'
        # Keep every native MPG intact, including opening movies.
        receipt['engine_sha256'] = sha(stage/ENGINE)
        receipt['scenario_scripts'] = {w:len(assemble.entry_map(stage/'Data'/key/'scr.xfl')) for w,key in KEYS.items()}
        shutil.rmtree(tmp)
        assemble.jsonout(stage/'collection.json',receipt)
        if out.exists(): out.rmdir()
        stage.rename(out); emit('완료: '+str(out/ENGINE)); return receipt
    except BaseException:
        if stage.parent == out.parent and stage.name.startswith('.'+out.name+'.building-') and stage.is_dir():
            shutil.rmtree(stage)
        raise


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try: build(json.loads(args.config.read_text('utf-8-sig')),args.package)
    except Exception as e:
        text = str(e)
        if getattr(e,'winerror',None) in {4551,577}:
            text = 'Windows 앱 제어 정책이 서명되지 않은 도구를 차단했어요. 이 환경에는 서명된 배포본이 필요합니다. 원본은 변경하지 않았어요.'
        emit('실패: '+text); return 1
    return 0
if __name__ == '__main__': sys.exit(main())

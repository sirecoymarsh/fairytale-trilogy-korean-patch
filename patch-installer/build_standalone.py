"""Standalone title adapter for the existing verified Korean delta packages.

The builder writes a new sibling staging directory and never patches inputs.
Only exact original/final files listed in manifest.json are accepted. A mixture
of those two known hashes is supported per file and recorded in the receipt.
"""
from pathlib import Path
import argparse, ctypes, hashlib, json, os, shutil, stat, subprocess, sys, tempfile, uuid
sys.dont_write_bytecode = True
if sys.stdout is not None: sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr is not None: sys.stderr.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EXES={w:'フェアリーテイル・'+jp+'.exe' for w,jp in [('Requiem','レクイエム'),('Encore','アンコール'),('Symphony','シンフォニー')]}

WORKS = {'Requiem':'레퀴엠','Encore':'앙코르','Symphony':'심포니'}
SAVES = {'Requiem':'FRsave','Encore':'FAsave','Symphony':'FSsave'}

def is_save(p, work):
    return p.is_file() and p.name.startswith(SAVES[work]) and p.suffix.lower() in {'.dat','.wcg','.content-undo'}

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def emit(message): print(message, flush=True)

def safe(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or ':' in relative or not rel.parts:
        raise ValueError('잘못된 패키지 경로: ' + relative)
    p = root / rel
    if not p.resolve().is_relative_to(root.resolve()): raise ValueError('폴더 바깥을 가리키는 경로: ' + relative)
    for part in [p, *p.parents]:
        if part == root.parent: break
        if part.exists() and part.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('연결 폴더나 파일은 사용할 수 없어요: ' + str(part))
    return p

def overlap(a, b): return a == b or a.is_relative_to(b) or b.is_relative_to(a)

def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

def execute(args):
    p = subprocess.run([str(a) for a in args], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8', 'replace')[-1800:] or '변환 도구를 실행하지 못했어요.')

def decode(tool,source,patch,target,window,tmp):
    with tempfile.TemporaryDirectory(prefix='delta-',dir=tmp) as folder:
        alias=Path(folder)/'source.bin'
        try: os.link(source,alias)
        except OSError: shutil.copyfile(source,alias)
        with patch.open('rb') as inp,target.open('wb') as out:
            p=subprocess.run([str(tool),'-d','-c','-B',str(window),'-s','source.bin'],stdin=inp,stdout=out,stderr=subprocess.PIPE,cwd=folder,creationflags=subprocess.CREATE_NO_WINDOW)
        if p.returncode: raise RuntimeError('패치를 적용하지 못했어요: '+source.name+'\n'+p.stderr.decode('utf-8','replace')[-1000:])

def running(executable):
    # Compare full executable paths. Unrelated same-named processes are ignored.
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    ps = ctypes.WinDLL('psapi', use_last_error=True)
    from ctypes import wintypes as W
    k.OpenProcess.argtypes = [W.DWORD,W.BOOL,W.DWORD]; k.OpenProcess.restype = W.HANDLE
    k.CloseHandle.argtypes = [W.HANDLE]
    k.QueryFullProcessImageNameW.argtypes = [W.HANDLE,W.DWORD,W.LPWSTR,ctypes.POINTER(W.DWORD)]
    ids = (W.DWORD * 65536)(); used = W.DWORD()
    if not ps.EnumProcesses(ids, ctypes.sizeof(ids), ctypes.byref(used)): raise OSError('실행 중인 프로그램을 확인하지 못했어요.')
    for pid in ids[:used.value // 4]:
        h = k.OpenProcess(0x1000, False, pid)
        if not h: continue
        try:
            name = ctypes.create_unicode_buffer(32768); size = W.DWORD(len(name))
            if k.QueryFullProcessImageNameW(h, 0, name, ctypes.byref(size)) and Path(name.value).resolve() == executable:
                return True
        finally: k.CloseHandle(h)
    return False

def verify_file(p, expected):
    if not p.is_file() or p.stat().st_size != expected['size'] or sha(p) != expected['sha256']:
        raise ValueError('파일이 없거나 검증값이 달라요: ' + str(p))

def select_source(src, row, work):
    """Select a verified delta for original or previously released Korean bytes."""
    if not src.is_file(): return row, 'missing'
    alternatives = row.get('alternate_sources', [])
    sizes = {row['size'], row.get('source_size'), *(x['source_size'] for x in alternatives)}
    if src.stat().st_size not in sizes:
        raise ValueError(WORKS[work] + '의 지원하지 않는 파일: ' + row['path'])
    digest = sha(src)
    if digest == row['sha256']: return row, 'korean'
    if digest == row.get('source_sha256'): return row, 'original'
    for old in alternatives:
        if digest == old['source_sha256']:
            return dict(row, **old), 'previous-korean'
    raise ValueError(WORKS[work] + '의 지원하지 않는 파일: ' + row['path'])


def repair_imported_font(path, work, enabled):
    """Migrate only our legacy default in the copied Requiem system settings.

    The native preferences block is 0x872 bytes. Its font name begins at 0x83e.
    Do not edit slot saves, other fonts, truncated files, or the input directory.
    """
    if not enabled or work != 'Requiem' or path.name != 'FRsave.dat': return None
    data = path.read_bytes(); offset = 0x83e
    old = b'Malgun Gothic\0'; new = b'GulimChe\0'
    if len(data) < 0x872 or data[offset:offset+len(old)] != old: return None
    changed = data[:offset] + new.ljust(len(old), b'\0') + data[offset+len(old):]
    path.write_bytes(changed)
    return {'file':path.name, 'offset':offset, 'old_font':'Malgun Gothic',
            'new_font':'GulimChe', 'input_sha256':hashlib.sha256(data).hexdigest(),
            'output_sha256':hashlib.sha256(changed).hexdigest()}


def build(config, package):
    manifest = json.loads((package / 'manifest.json').read_text('utf-8-sig'))
    requested = config.get('games', {})
    if len(requested)!=1 or set(requested)!=set(manifest['games']): raise ValueError('이 패키지에 해당하는 작품의 설치 폴더를 선택해 주세요.')
    out = Path(config['output']).resolve()
    if out.parent == out or overlap(out, package.resolve()): raise ValueError('패키지와 겹치지 않는 새 출력 폴더를 선택해 주세요.')
    if out.exists() and (not out.is_dir() or any(out.iterdir())): raise ValueError('출력 폴더가 비어 있지 않아요. 새 폴더를 선택해 주세요.')
    roots = {w:Path(v['path']).resolve() for w,v in requested.items()}
    for w, root in roots.items():
        if not root.is_dir() or not (root / EXES[w]).is_file(): raise ValueError(WORKS[w] + ' 실행 파일이 있는 설치 폴더를 선택해 주세요.')
        if overlap(out, root): raise ValueError('원본 게임 폴더와 겹치지 않는 출력 폴더를 선택해 주세요.')
        if running((root / EXES[w]).resolve()): raise ValueError(WORKS[w] + '을 종료한 뒤 다시 만들어 주세요.')
    for w, root in roots.items():
        if any(w != other and overlap(root, candidate) for other,candidate in roots.items()):
            raise ValueError('각 작품의 설치 폴더를 따로 선택해 주세요.')

    plan = []; receipt = {'schema':1,'builder':manifest['version'],'works':{},'sources_unchanged':True,'mode':'standalone-korean-patch'}
    needed = sum(x['size'] for x in manifest['common']) + 512 * 1024 * 1024
    emit('패키지와 선택한 설치 파일을 확인하고 있어요.')
    for item in manifest['tools']: verify_file(safe(package, item['payload']), item)
    for item in manifest['common']: verify_file(safe(package, item['payload']), item)
    for w, root in roots.items():
        receipt['works'][w] = {'import_save':bool(requested[w].get('import_save',False)), 'files':[], 'save_files':0,'save_sha256':{}}
        for row in manifest['games'][w]['files']:
            src = safe(root, row['path'])
            row, state = select_source(src, row, w)
            if state == 'missing' and row['kind'] != 'new': raise ValueError(WORKS[w] + ' 설치 파일이 없어요: ' + row['path'])
            if state != 'korean' and row['kind'] != 'same':
                verify_file(safe(package, row['payload']), {'size':row['payload_size'],'sha256':row['payload_sha256']})
            plan.append((w, src, row, state)); needed += row['size']
            receipt['works'][w]['files'].append({'path':row['path'],'input':state,'sha256':row['sha256']})
        if requested[w].get('import_save'):
            save = safe(root, 'save')
            if save.is_dir():
                for p in save.iterdir():
                    if is_save(p,w):
                        safe(root, 'save/' + p.name); needed += p.stat().st_size
    needed += max((row.get('source_size',0) for _,_,row,_ in plan),default=0)
    out.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(out.parent).free < needed: raise ValueError('출력 드라이브의 여유 공간이 부족해요. 약 ' + str((needed+1073741823)//1073741824) + ' GB 이상 확보해 주세요.')
    stage = out.with_name('.' + out.name + '.building-' + uuid.uuid4().hex)
    stage.mkdir()
    try:
        tmp = stage / '.build-temp'; tmp.mkdir()
        os.environ['TEMP'] = os.environ['TMP'] = str(tmp)
        for item in manifest['common']: copy(safe(package,item['payload']),safe(stage,item['path']))
        for i,(w,src,row,state) in enumerate(plan):
            emit('[%d/%d] %s · %s' % (i+1,len(plan),WORKS[w],row['path']))
            dst = safe(stage,row['path']); dst.parent.mkdir(parents=True,exist_ok=True)
            if state == 'korean' or row['kind'] == 'same': copy(src,dst)
            elif row['kind'] == 'new': copy(safe(package,row['payload']),dst)
            else: decode(package/'Tools'/'xdelta3.exe',src,safe(package,row['payload']),dst,row['window'],tmp)
            verify_file(dst,row)
        for w,root in roots.items():
            target = stage
            (target/'save').mkdir(exist_ok=True)
            if requested[w].get('import_save'):
                if running((root/EXES[w]).resolve()): raise ValueError(WORKS[w]+'을 종료한 뒤 다시 만들어 주세요.')
                source = safe(root,'save')
                if source.is_dir():
                    for p in sorted(source.iterdir()):
                        if is_save(p,w):
                            p=safe(source,p.name); before=sha(p); dest=target/'save'/p.name; copy(p,dest)
                            if sha(dest)!=before or sha(p)!=before: raise ValueError('복사하는 동안 세이브가 바뀌었어요. 게임을 종료해 주세요.')
                            receipt['works'][w]['save_files'] += 1
                            migration = repair_imported_font(dest, w, manifest.get('repair_legacy_korean_font', False))
                            if migration:
                                receipt['works'][w].setdefault('font_migrations', []).append(migration)
                            receipt['works'][w]['save_sha256'][p.name] = sha(dest) if migration else before
                if not receipt['works'][w]['save_files']: emit(WORKS[w]+' · 가져올 세이브가 없어 새 저장 폴더를 만들었어요.')
        shutil.rmtree(tmp)
        (stage/'patch-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=1),encoding='utf-8')
        if out.exists(): out.rmdir()  # only the empty directory checked above
        stage.rename(out)
        emit('완료: '+str(out/EXES[next(iter(roots))]))
        return receipt
    except BaseException:
        # Only the freshly allocated, bounded staging directory belongs to us.
        if stage.parent==out.parent and stage.name.startswith('.'+out.name+'.building-') and stage.is_dir(): shutil.rmtree(stage)
        raise

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True);parser.add_argument('--package',type=Path,default=HERE.parent)
    args=parser.parse_args()
    try: build(json.loads(args.config.read_text('utf-8-sig')),args.package.resolve())
    except Exception as e:
        message=str(e)
        if getattr(e,'winerror',None) in {4551,577}:
            message='Windows 앱 제어 정책이 서명되지 않은 제작 도구를 차단했어요. 이 환경에서는 신뢰할 수 있는 서명이 있는 배포본이 필요합니다. 원본은 변경하지 않았어요.'
        emit('실패: '+message); return 1
    return 0

if __name__=='__main__': sys.exit(main())

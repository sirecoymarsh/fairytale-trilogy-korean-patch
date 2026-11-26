"""Split the verified collection delta manifest into portable per-title patch kits."""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,os,zipfile

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def meta(p):return {'size':p.stat().st_size,'sha256':sha(p)}
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=1),'utf8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 base=args.base.resolve();out=args.output.resolve();here=Path(__file__).resolve().parent
 out.mkdir(parents=True,exist_ok=True)
 original=json.loads((base/'manifest.json').read_text('utf8'));spec=json.loads(args.spec.read_text('utf8'))
 names={'Requiem':'레퀴엠','Encore':'앙코르','Symphony':'심포니'};result=[]
 csc=Path(os.environ['WINDIR'])/'Microsoft.NET/Framework/v4.0.30319/csc.exe'
 compiled=out/'PatchBuilder.exe'
 subprocess.run([str(csc),'/nologo','/target:winexe','/platform:anycpu','/optimize+','/codepage:65001',
  '/reference:System.dll','/reference:System.Core.dll','/reference:System.Drawing.dll','/reference:System.Windows.Forms.dll','/reference:System.Web.Extensions.dll',
  '/out:'+str(compiled),str(here/'PatchBuilder.cs')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 for w,ko in names.items():
  package=out/('Fairytale_'+w+'_Korean_Patch');assert not package.exists();package.mkdir()
  m={'schema':1,'version':'2026.11.26-preview.1','mode':'standalone-korean-patch','games':{w:original['games'][w]},'common':[],'tools':[],
     'ui_author':'Codex internal','translation':'Existing Korean patch reused; no new scenario translation'}
  for p in (base/'Runtime').iterdir():
   if p.is_file():cp(p,package/'Runtime'/p.name)
  cp(compiled,package/'한국어 패치 적용.exe');cp(here/'build_standalone.py',package/'Scripts/build_standalone.py')
  cp(here/'PatchBuilder.cs',package/'Source/PatchBuilder.cs')
  for item in original['tools']:
   if item['payload']=='Tools/xdelta3.exe':cp(base/item['payload'],package/item['payload']);m['tools'].append(item)
  cp(base/'Licenses/xdelta-Apache-2.0.txt',package/'Licenses/xdelta-Apache-2.0.txt')
  for row in m['games'][w]['files']:
   if row.get('payload'):cp(base/row['payload'],package/row['payload'])
  logo=Path(spec['games'][w]['original'])/'mov/0002.mpg'
  if logo.is_file():
   ko_logo=Path(spec['games'][w]['korean'])/'mov/0002.mpg';digest=sha(logo)
   if ko_logo.is_file():assert sha(ko_logo)==digest
   m['games'][w]['files'].append(dict(path='mov/0002.mpg',kind='same',source_size=logo.stat().st_size,source_sha256=digest,**meta(logo)))
  exe=m['games'][w]['exe']
  guide=f'''페어리테일 {ko} 한국어 패치 — 2026.11.26 미리보기

1. ZIP 전체를 풀고 「한국어 패치 적용.exe」를 실행합니다.
2. {exe} 파일이 있는 지원 원본 또는 한국어판 설치 폴더를 선택합니다.
3. 기존 저장 기록이 필요하면 「세이브 가져오기」를 선택합니다.
4. 새 빈 출력 폴더를 지정하고 「한국어판 만들기」를 누릅니다.
5. 완료된 폴더의 {exe} 파일을 실행합니다.

원본 설치본을 수정하지 않고 독립된 한국어판을 새 폴더에 만듭니다. 기존 출력을 덮어쓰지 않습니다. 저장 기록은 완성 폴더의 save에 있습니다.
사용자가 보유한 해당 작품의 설치 파일이 필요합니다. 지원 판본은 manifest.json의 파일 크기와 SHA-256으로 확인합니다. 다른 파일이면 중단하며, 원본 게임 전체나 개인 세이브는 배포 패키지에 포함하지 않습니다.
기존 번역·한국어 수정 그림·게임용 영상과 검증된 VCDIFF 패치를 그대로 재사용합니다. 이 설치기는 영상 재인코딩이나 브릿지 감상실 구성을 하지 않습니다.

환경: Windows 10/11 64비트, .NET Framework 4.8 이상. Python과 xdelta는 동봉되어 있습니다. 원본 크기와 패치 작업 공간이 필요하며 적용 전 여유 공간을 확인합니다.
코드 서명이 없는 미리보기입니다. Smart App Control 등 앱 제어 정책이 xdelta 실행을 차단한 환경이 확인됐습니다. 보안 설정을 우회하지 않으며 해당 PC에서의 동작을 보장하지 않습니다.

확인된 범위: 기존 원본→한국어 파일 해시 84개 검증과 세 작품 시작/복귀 기록을 재사용합니다. 새 작품별 설치기의 추가 확인 결과는 GitHub 릴리스의 검증 범위를 참고하세요. 전체 분기 완주, 모든 영상의 게임 내 연속 재생, 모든 PC 동작은 미검증입니다.
문제 제보: https://github.com/sirecoymarsh/fairytale-trilogy-korean-patch/issues
'''
  (package/'사용방법.txt').write_text(guide,'utf8');cp(package/'사용방법.txt',package/'Common/한국어 패치 사용 안내.txt')
  p=package/'Common/한국어 패치 사용 안내.txt';m['common']=[dict(path=p.name,payload='Common/'+p.name,**meta(p))]
  dump(package/'manifest.json',m)
  records=[]
  for p in sorted(package.rglob('*')):
   if p.is_file():records.append(dict(path=p.relative_to(package).as_posix(),**meta(p)))
  dump(package/'checksums.json',records)
  for row in m['games'][w]['files']:
   if row.get('payload'):
    p=package/row['payload'];assert p.stat().st_size==row['payload_size'] and sha(p)==row['payload_sha256']
  result.append({'work':w,'package':str(package),'input_files':len(m['games'][w]['files']),'file_count':len(records)+1})
 compiled.unlink()
 dump(out/'packages.json',result)
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()

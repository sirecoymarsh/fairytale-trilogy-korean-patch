# 페어리테일 통합판 만들기

레퀴엠·앙코르·심포니의 설치 폴더를 선택해 독립된 한국어 통합판을 만듭니다. 한 작품만 선택해도 됩니다. 선택하지 않은 작품은 흑백 문과 `미설치` 표시로 남고, 그 작품의 감상 목록은 나오지 않습니다.

1. 배포 ZIP을 모두 풉니다.
2. `페어리테일 통합판 만들기.exe`를 실행합니다.
3. 가지고 있는 작품마다 해당 게임의 EXE가 들어 있는 폴더를 선택합니다.
4. 필요한 작품만 `이 작품의 세이브 가져오기`를 체크합니다. 기본값은 새로 시작하기입니다.
5. 원본 게임과 겹치지 않는 빈 출력 폴더를 선택하고 `통합판 만들기`를 누릅니다.
6. 완료 후 출력 폴더의 `페어리테일 통합판.exe`를 실행합니다.

지원 대상은 manifest.json에 기록된 일본어 원본과 기존 한국어판의 정확한 파일입니다. 확인되지 않은 다른 판본은 원본을 건드리기 전에 거부합니다. 제작 도중 게임을 실행하지 마세요. 기존 한국어판의 알려진 파일과 원본 파일이 섞인 경우에도 각 파일의 해시가 확인되면 구성할 수 있습니다.

원본 게임과 원본 세이브는 읽기만 합니다. 게임 자료를 새 폴더로 복사하고 그 사본에 한국어 차분을 적용한 뒤, 기존 구성기로 감상실과 작품별 시작 파일을 만듭니다. 실패하면 이번에 만든 임시 출력만 정리합니다. 이미 내용이 들어 있는 출력 폴더를 덮어쓰지 않습니다.

세이브 가져오기는 시스템 기록·저장 슬롯·미리보기와 앙코르/심포니의 감상 기록 초기화 되돌리기 자료를 함께 복사합니다. 가져오지 않은 작품의 save 폴더는 비어 있는 상태로 만들어집니다. 이후 통합판에서 저장한 내용은 통합판 안에만 반영됩니다.

완성 폴더는 통째로 다른 위치나 PC로 옮길 수 있습니다. Games·Entries·Library·Support·User를 함께 옮기세요. 실행 파일 하나만 옮기면 안 됩니다. 원래 설치 폴더의 절대 경로, 제작자 PC의 드라이브, Python·Visual Studio 설치는 실행에 필요하지 않습니다.

Windows 10/11 64비트, .NET Framework 4.8 이상, Microsoft Edge WebView2 Runtime이 필요합니다. WebView2가 없으면 패키지의 `WebView2_설치.exe` 또는 완성 폴더의 `Support/WebView2_설치.exe`를 실행하세요. Microsoft가 서명한 오프라인 설치 파일입니다. Windows N처럼 미디어 기능이 제외된 에디션은 영상 재생을 별도로 확인해야 합니다.

새 감상실 영상은 WebView2에서 MP4로 재생합니다. 기존 Windows Media Player에 의존하던 감상실 재생 경로를 대체합니다. 게임 내부의 엔딩 MPEG는 원래 규격 그대로 보존합니다. 기존 통합판의 MPEG 전용 폴더를 여는 경우에는 이전 재생 경로를 유지합니다.

이 빌드는 아직 코드 서명되지 않았습니다. Windows Sandbox의 Smart App Control이 xdelta3 실행을 차단한 사례를 확인했습니다. 해당 정책이 적용된 PC의 동작을 보증하지 않습니다. 보안 설정 변경이나 차단 우회를 요구하지 않으며, 서명된 배포본이 필요한 환경은 현재 호환성 제한으로 기록합니다.

제작 중 여유 공간은 세 작품 기준 약 13 GB 이상을 권장합니다. 실제 필요량은 선택 작품에 따라 미리 확인합니다. 생성된 통합판에는 해당 PC의 게임 자료가 들어 있으므로 공개 배포용 패키지와 구분해야 합니다.

기존 구현 재사용: Claude의 collection/album.py, entries.py, Castle.cs 및 delta-kit의 VCDIFF 제작 방식을 사용합니다. codeX의 XFL/GSC 파서와 감상실 Ogg 보정도 재사용했습니다. 새 작성 범위는 폴더 선택, 해시 검증, 독립 복사와 세이브 선택, 배포 런타임 구성, MP4 감상 경로입니다. 게임 대사의 신규 번역은 하지 않았습니다. 새 화면 문구 작성: Codex internal.

소스: https://github.com/sirecoymarsh/fairytale-trilogy-korean-patch

참고한 공식 자료: [WebView2 배포](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution), [Python embeddable 배포](https://www.python.org/downloads/release/python-3119/), [Windows Sandbox CLI](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli), [xdelta](https://github.com/jmacd/xdelta), [FFmpeg 배포 빌드](https://www.gyan.dev/ffmpeg/builds/).

2026.11.28 preview.4: 레퀴엠 설정의 콘텐츠 개방·취소·기록 초기화·복원을 공통 감상실과 연동합니다. 기존 레퀴엠 한국어 패치와 시스템 글꼴 수정판에서도 제작할 수 있습니다.

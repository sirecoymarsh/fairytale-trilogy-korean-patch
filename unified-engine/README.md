# 페어리테일 이야기 모음 — 단일 엔진 제작기

[릴리스](https://github.com/sirecoymarsh/fairytale-trilogy-korean-patch/releases/tag/patches-preview-2026.11.26)의 `Fairytale_Story_Collection_Builder_20261126_preview.zip`은 **레퀴엠·앙코르·심포니를 모두 가진 사용자**가 자신의 설치본으로 단일 엔진 통합판을 만드는 패키지입니다.

세 작품의 설치 폴더를 각각 선택하고, 세이브를 가져올 작품을 고른 뒤 새 빈 출력 폴더에 만드세요. 완성 후 `페어리테일 이야기 모음.exe`를 실행합니다. 세 작품이 모두 필요하며 지원 파일은 크기와 SHA-256으로 확인합니다. 이 파일 확인은 계정·라이선스 인증을 대신하지 않습니다.

기존 브릿지의 성 메인과 감상실을 재사용합니다. 하나의 원작 게임 엔진이 `Data/R`, `Data/A`, `Data/S` 자료를 읽고 같은 게임 프로세스에서 작품을 전환합니다. 저장은 `Save/R`, `Save/A`, `Save/S`로 구분됩니다. WebView2 보조 프로세스는 생성되지만 세 작품의 게임 EXE를 번갈아 실행하는 구조는 아닙니다.

게임 설정의 **타이틀로**로 성 메인에 돌아옵니다. 창의 X 또는 성 메인의 종료는 이야기 모음을 종료합니다. 폴더를 옮길 때는 전체를 함께 옮기세요.

필요 환경은 Windows 10/11 64비트, .NET Framework 4.8 이상, WebView2이며 작업 여유 공간은 약 12~15 GB를 권장합니다. Python·Pillow·xdelta·FFmpeg와 WebView2 설치 파일을 동봉했습니다. 게임 원본과 개인 세이브는 포함하지 않습니다. 코드 서명이 없는 미리보기로, 다른 PC 전체 호환성과 전체 시나리오 완주는 아직 확인하지 않았습니다.

## 구현과 재사용

- `build_unified.py`: 지원 설치본 검증·독립 복사·기존 한국어 차분 적용·엔진 연결·선택 세이브 가져오기. 릴리스 `Scripts`에 공통 Python 의존성도 포함되어 있습니다.
- `unified_entries.py`: 원작 시나리오를 보존하면서 시작·회상·공통 화면 복귀 진입점 생성.
- `unified_native.cpp`, `native_hooks.h`: 원작 VM과 자료 로더를 재사용해 작품별 자료·진행 상태를 전환하는 연결 DLL.
- `UnifiedHome.cs`: 기존 성 화면·감상실을 같은 프로세스에 연결하는 .NET/WPF/WebView2 메인.
- `UnifiedBuilder.cs`: 세 설치 폴더와 선택 세이브를 받는 설치 화면.
- `engine-patch.json`: 지원 한국어 심포니 엔진의 입력 해시와 바이트 변경 범위. 게임 EXE 자체는 배포하지 않습니다.

기존 Claude의 collection/album/entries/성 UI, 기존 한국어 패치와 codeX의 XFL/GSC 파서를 재사용했습니다. 새 시나리오 번역은 하지 않았습니다. 새 화면 문구 작성: Codex internal. 이 디렉터리는 검증된 연결 소스를 보존하며, 실행용 의존성과 도구는 릴리스 패키지에 들어 있습니다. native DLL은 x86 MSVC C++17, 메인 DLL은 x86 .NET Framework 4와 WebView2 SDK 참조가 필요합니다.

검토한 공개 기반: [RaiLTools](https://github.com/EusthEnoptEron/RaiLTools), [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool), [rscript2renpy](https://github.com/Love-in-idleness/rscript2renpy). 대체 런타임 소스까지 검토한 뒤 세 작품의 엔진 동일성을 확인하여 원작 엔진을 직접 연결했습니다. CLR 호스팅 헤더 출처: [dotnet/runtime](https://github.com/dotnet/runtime/tree/main/src/coreclr/pal/prebuilt/inc).

[공개 검증 기록](../releases/verification-20261126.json)에 실제 플레이 확인과 보존된 시나리오 수를 구분해 기록했습니다. 원작 시나리오·메뉴 GSC 428개를 보존했다는 사실은 모든 루트 완주를 의미하지 않습니다.

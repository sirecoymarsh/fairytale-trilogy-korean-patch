# 레퀴엠 감상 기록 편의 기능

2026.11.28 preview.4. 기존 앙코르·심포니 ContentAction 및 원작 codeX 엔진을 재사용합니다.
환경 설정의 감상 기록에 모든 콘텐츠 해방·해방 취소·초기화·초기화 되돌리기를 추가합니다.
CG 63묶음/차분219개, 회상229개, 음악·영상·특전을 대상으로 합니다.

`content_options.cpp`와 `catalog.h`는 세 작품 공용 DLL의 실제 배포 소스입니다. MSVC x86 개발 명령창에서 이 폴더를 기준으로:

```bat
cl /nologo /O2 /EHsc /MT /std:c++17 /utf-8 /LD content_options.cpp /link /OUT:FairytaleContent.dll /EXPORT:ContentAction=_ContentAction@8 user32.lib
```

`menu_scripts.py`와 `settings_art.py`는 기존 encore-symphony/qol 구현의 레퀴엠 확장입니다. `build_requiem.py --help`에 필요한 입력을 명시했습니다. Python Pillow/pefile, 원본 코드 파서, 기존 UiAssetTool과 clean plate/한글 글꼴을 재사용합니다. 게임 자료와 clean plate 자체는 이 소스 폴더에 포함하지 않습니다. 배포판 설치에는 컴파일이 필요 없습니다.

레퀴엠 진행 플래그7001..7415/7700/7713은 보존하고, 감상 기록만8300..8530으로 별도 관리합니다. 개방은7988이며 초기 상태는 꺼짐입니다. 설정·슬롯을 초기화하지 않습니다. 초기화 백업 `.content-undo`는 작품 식별자와 CRC를 검사하며 이후 새 기록과 합칩니다. 앙코르/심포니의 기존 복구 파일 식별자는 유지합니다.

새 UI 문구: Codex internal. 새 시나리오 번역은 없습니다. 검증 범위는 [배포 기록](../../releases/requiem-content-options-20261128.md)을 참조하세요.

#!/usr/bin/env python3
"""Repair native UI encoding and the default Korean font in the released CP949 Requiem EXE.

Only fixed-size display-string and default-font slots change; code, imports, resources and game
logic are byte-identical. Input is the exact 2026.11.26 / preview.2 Korean EXE.
"""
from pathlib import Path
import argparse
import hashlib
import json

BASE_SHA256 = "e46f532811b3189669ccc74452a2bfb4f0f14362ef97e68018fc9cdc26b2b4f4"
# Offsets are raw file offsets in the original .data section. Each allocation
# ends at its existing 4-byte alignment boundary, before the next object.
STRINGS = [
    (0x81140, "default_font", "Malgun Gothic", "GulimChe"),
    (0x81808, "secondary_font", "Malgun Gothic", "GulimChe"),
    (0x81550, "confirm_title", "確認", "확인"),
    (0x81558, "return_to_title", "タイトル画面に戻ります。\nよろしいですか？", "제목 화면으로 돌아갈까요?"),
    (0x81584, "overwrite_save", "セーブデータを上書きします。\nよろしいですか？", "저장 데이터를 덮어쓸까요?"),
    (0x815B4, "load_save", "セーブデータをロードします。\nよろしいですか？", "저장 데이터를 불러올까요?"),
    (0x8161C, "quick_load", "クイックロードしますか？", "빠른 불러오기를 할까요?"),
    (0x818D0, "color_mode_notice", "このゲームは32Bitカラーモードで最適化されています。\nカラーモードを変更していただくとより一層お楽しみになれます。", "이 게임은 32비트 색상 모드에 최적화되어 있습니다.\n색상 모드를 변경하면 더 나은 화질로 즐길 수 있습니다."),
    (0x81944, "notice_title", "お知らせ", "알림"),
    (0x81A2C, "compile_error", "コンパイルエラー", "컴파일 오류"),
    (0x81A40, "script_nest_overflow", "スクリプトネストオーバーフロー", "스크립트 중첩 한도 초과"),
    (0x81A60, "script_nest_underflow", "スクリプトネストアンダーフロー", "스크립트 중첩 단계 부족"),
    (0x81A80, "invalid_layer", "レイヤー指定違反", "잘못된 레이어 지정"),
    (0x81AA0, "text_format_error", "テキストフォーマットエラー", "텍스트 형식 오류"),
    (0x82070, "font_preview", "あぃウェ５＃―壱弐鶴亀ＡｂAb", "가나다라 마바사 123 ABC"),
    (0x821D0, "exit_title", "終了確認", "종료 확인"),
    (0x821DC, "exit_game", "本当にゲームを終了しますか？", "정말 게임을 종료할까요?"),
]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def patch(data):
    if digest(data) != BASE_SHA256:
        raise ValueError("Unsupported input executable SHA-256")
    result = bytearray(data)
    occupied = set()
    rows = []
    for offset, uid, source, target in STRINGS:
        old = source.encode("cp932") + b"\0"
        size = (len(old) + 3) & ~3
        old = old.ljust(size, b"\0")
        new = target.encode("cp949") + b"\0"
        if len(new) > size or data[offset:offset + size] != old:
            raise ValueError(f"Slot mismatch or overflow: {uid}")
        span = set(range(offset, offset + size))
        if span & occupied:
            raise ValueError(f"Overlapping slot: {uid}")
        occupied |= span
        result[offset:offset + size] = new.ljust(size, b"\0")
        rows.append(dict(id=uid, offset=offset, size=size, source=source,
                         target=target, source_encoding="cp932", target_encoding="cp949"))
    changed = [i for i, (a, b) in enumerate(zip(data, result)) if a != b]
    assert len(data) == len(result) and set(changed) <= occupied
    report = dict(schema="requiem-native-system-ui-v1", translator_model="Codex internal",
                  source_sha256=BASE_SHA256, output_sha256=digest(result),
                  file_size=len(result), changed_bytes=len(changed), strings=rows,
                  code_imports_resources_unchanged=True)
    return bytes(result), report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    paths = [p.resolve() for p in (args.source, args.output, args.manifest)]
    if len(set(paths)) != 3 or args.output.exists() or args.manifest.exists():
        raise ValueError("Use distinct, absent output and manifest paths")
    data, report = patch(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        f.write(data)
    with args.manifest.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({k: report[k] for k in ("output_sha256", "changed_bytes")}, ensure_ascii=False))

if __name__ == "__main__":
    main()

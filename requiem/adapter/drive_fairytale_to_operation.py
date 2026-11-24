#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import time
from ctypes import wintypes
from pathlib import Path

import cv2
import numpy as np


def load_capture(path: Path):
    spec = importlib.util.spec_from_file_location("game_capture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import capture helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_window(pid: int) -> int:
    user32 = ctypes.windll.user32
    matches: list[int] = []
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @proc
    def callback(hwnd: int, _lparam: int) -> bool:
        window_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid and user32.IsWindowVisible(hwnd):
            matches.append(hwnd)
        return True

    user32.EnumWindows(callback, 0)
    if len(matches) != 1:
        raise RuntimeError(f"expected one target window, found {matches}")
    return matches[0]


def send_enter(hwnd: int) -> None:
    user32 = ctypes.windll.user32
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.08)
    user32.keybd_event(0x0D, 0, 0x0002, 0)

def move_cursor(hwnd: int, x: int, y: int) -> None:
    user32 = ctypes.windll.user32
    point = wintypes.POINT(x, y)
    user32.ClientToScreen(hwnd, ctypes.byref(point))
    user32.SetCursorPos(point.x, point.y)
    user32.PostMessageW(hwnd, 0x0200, 0, (y << 16) | x)


def click(hwnd: int, x: int, y: int) -> None:
    user32 = ctypes.windll.user32
    move_cursor(hwnd, x, y)
    time.sleep(0.7)
    packed = (y << 16) | x
    user32.PostMessageW(hwnd, 0x0201, 1, packed)
    time.sleep(0.12)
    user32.PostMessageW(hwnd, 0x0202, 0, packed)


def match_menu(image, template_rgba: np.ndarray) -> tuple[float, tuple[int, int]]:
    array = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    content = array[27:747, 1:1281]
    template_bgr = cv2.cvtColor(template_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    mask = ((template_rgba[:, :, 3] >= 250) * 255).astype(np.uint8)
    result = cv2.matchTemplate(content, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
    value, _, location, _ = cv2.minMaxLoc(result)
    return float(value), location


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--capture-helper", type=Path, required=True)
    parser.add_argument("--output-name", default="trial_operation_japanese_runtime.png")
    parser.add_argument("--report-name", default="runtime_operation_reproduction.json")
    args = parser.parse_args()
    project = args.project.resolve()
    capture = load_capture(args.capture_helper.resolve())
    hwnd = find_window(args.pid)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    template = cv2.imread(
        str(project / "staging" / "ui_first_pass" / "decoded_png" / "0001.png"),
        cv2.IMREAD_UNCHANGED,
    )
    if template is None:
        raise FileNotFoundError("0001.png")
    template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGBA)
    steps: list[dict[str, object]] = []
    move_cursor(hwnd, 10, 10)
    menu_found = False
    for index in range(25):
        image, printed = capture.capture_window(hwnd, 1282, 747)
        score, location = match_menu(image, template)
        steps.append({"step": index, "score": score, "xy": list(location), "print_window": printed})
        if score < 0.0001:
            menu_found = True
            break
        send_enter(hwnd)
        time.sleep(1.8)
    if not menu_found:
        raise RuntimeError("title menu not found")

    # Fifth small title-menu icon: operation instructions.
    target = (655, 394)
    click(hwnd, *target)
    time.sleep(3)
    image, printed = capture.capture_window(hwnd, 1282, 747)
    output = project / "evidence" / "runtime" / args.output_name
    image.save(output)
    report = {
        "schema": "fairytale-requiem-operation-runtime-v1",
        "pid": args.pid,
        "hwnd": hwnd,
        "menu_found": menu_found,
        "steps": steps,
        "clicked_client": list(target),
        "capture": str(output),
        "print_window": printed,
    }
    report_path = project / "audit" / args.report_name
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

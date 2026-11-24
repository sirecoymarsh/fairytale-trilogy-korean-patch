from __future__ import annotations

import math
import re
from dataclasses import dataclass

MAX_RUNTIME_WIDTH = 1000
SAFE_REFLOW_WIDTH = 992
MAX_DIALOGUE_LINES = 3
CONTROL_RE = re.compile(r"\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|n|m)")
RUBY_RE = re.compile(r"\|([^\[\]\|]+)\[([^\[\]\|]+)\]")
GOOD_END = set(".。!?！？…,:;，、：；───~～』」】）》〉”’\")")
BAD_START = set(".。!?！？…,:;，、：；』」】）》〉”’\")")
BAD_END = set("『「【（《〈“‘(")


def glyph_width(ch: str) -> int:
    return 16 if ord(ch) < 128 else 32


def display_text(text: str) -> str:
    text = RUBY_RE.sub(lambda m: m.group(1), text)
    return CONTROL_RE.sub(lambda m: "^n" if m.group(0) == "^n" else "", text)


def display_width(text: str) -> int:
    rendered = display_text(text).replace("^n", "")
    return sum(glyph_width(ch) for ch in rendered)


def line_widths(text: str) -> list[int]:
    return [sum(glyph_width(ch) for ch in part) for part in display_text(text).split("^n")]


def required_runtime_lines(text: str, max_width: int = MAX_RUNTIME_WIDTH) -> int:
    return sum(0 if width == 0 else math.ceil(width / max_width) for width in line_widths(text))


def non_newline_controls(text: str) -> list[str]:
    return [token for token in CONTROL_RE.findall(text) if token != "^n"]


def normalize_nonspace_content(text: str) -> str:
    return re.sub(r"\s+", "", text.replace("^n", ""))


def join_explicit_lines(text: str) -> str:
    parts = text.split("^n")
    if any(not part.strip() for part in parts):
        raise ValueError("cannot automatically reflow a target containing an empty explicit line")
    return re.sub(r"[ \t]+", " ", " ".join(part.strip() for part in parts)).strip()


def _boundary_penalty(text: str, pos: int) -> int:
    left = text[pos - 1]
    right = text[pos]
    if left.isspace() or right.isspace():
        penalty = 0
    elif left in GOOD_END:
        penalty = 1
    elif "가" <= left <= "힣" and "가" <= right <= "힣":
        penalty = 5
    else:
        penalty = 8
    if left in BAD_END:
        penalty += 30
    if right in BAD_START:
        penalty += 30
    return penalty


def reflow_to_three_lines(text: str, max_width: int = SAFE_REFLOW_WIDTH) -> tuple[str, dict]:
    if "^n" in text:
        joined = join_explicit_lines(text)
    else:
        joined = re.sub(r"[ \t]+", " ", text).strip()
    if not joined:
        raise ValueError("empty target")
    if RUBY_RE.search(joined):
        raise ValueError("ruby-bearing strings require a dedicated layout path")

    n = len(joined)
    invalid_breaks: set[int] = set()
    zero_positions: set[int] = set()
    for match in CONTROL_RE.finditer(joined):
        invalid_breaks.update(range(match.start() + 1, match.end()))
        zero_positions.update(range(match.start(), match.end()))
    prefix = [0]
    for i, ch in enumerate(joined):
        prefix.append(prefix[-1] + (0 if i in zero_positions else glyph_width(ch)))

    def trimmed_bounds(a: int, b: int) -> tuple[int, int]:
        while a < b and joined[a].isspace():
            a += 1
        while b > a and joined[b - 1].isspace():
            b -= 1
        return a, b

    def segment(a: int, b: int) -> tuple[str, int]:
        a, b = trimmed_bounds(a, b)
        return joined[a:b], prefix[b] - prefix[a]

    positions = [p for p in range(1, n) if p not in invalid_breaks and (joined[p - 1].isspace() or joined[p].isspace())]
    total = prefix[-1]
    ideal = total / 3.0
    best = None
    for p1_index, p1 in enumerate(positions):
        t1, w1 = segment(0, p1)
        if not t1 or w1 > max_width:
            continue
        for p2 in positions[p1_index + 1:]:
            t2, w2 = segment(p1, p2)
            t3, w3 = segment(p2, n)
            if not t2 or not t3 or w2 > max_width or w3 > max_width:
                continue
            widths = [w1, w2, w3]
            boundary = _boundary_penalty(joined, p1) + _boundary_penalty(joined, p2)
            balance = int(sum((width - ideal) ** 2 for width in widths))
            score = boundary * 250000 + balance + max(widths) * 100
            candidate = (score, max(widths), widths, [t1, t2, t3])
            if best is None or candidate[:2] < best[:2]:
                best = candidate
    if best is None:
        raise ValueError(f"text cannot fit in three lines of {max_width} units; total={total}")
    _, _, widths, lines = best
    output = "^n".join(lines)
    if non_newline_controls(output) != non_newline_controls(text):
        raise AssertionError("non-newline control sequence changed")
    return output, {
        "joined_width": total,
        "line_widths": widths,
        "max_width": max_width,
        "line_count": 3,
    }

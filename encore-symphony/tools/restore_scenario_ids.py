"""Restore a Gemini packet to the game's canonical IDs. Uses only Python's standard library."""
import argparse
import json
from pathlib import Path


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 키 중복: {key}")
        result[key] = value
    return result


def restore(result, packets):
    if not isinstance(result, dict):
        raise ValueError("응답은 JSON 객체여야 합니다.")
    number = result.get("packet")
    if number not in packets:
        raise ValueError(f"등록되지 않은 묶음: {number}")
    expected = packets[number]
    if ("scenes" in result) == ("lines" in result):
        raise ValueError("응답에는 scenes 또는 기존 형식의 lines 하나가 필요합니다.")
    if "scenes" in result:
        scenes = result["scenes"]
        if not isinstance(scenes, dict):
            raise ValueError("scenes는 장면을 키로 갖는 객체여야 합니다.")
        allowed = list(dict.fromkeys(uid.split("-")[0] for uid in expected))
        if set(scenes) != set(allowed):
            raise ValueError(f"{number} 장면 목록 불일치. 필요한 장면: {', '.join(allowed)}")
        lines = []
        for scene in allowed:
            if not isinstance(scenes[scene], list):
                raise ValueError(f"{scene}의 행 목록 형식 오류")
            for pair in scenes[scene]:
                if not isinstance(pair, list) or len(pair) != 2:
                    raise ValueError(f"{scene}에는 [번호, 한국어] 쌍이 필요합니다.")
                slot, ko = pair
                if type(slot) is not int or not 0 <= slot <= 99999 or not isinstance(ko, str):
                    raise ValueError(f"{scene}의 행 번호 또는 번역 문자열 형식 오류")
                lines.append({"id": f"{scene}-{slot:05d}", "ko": ko})
    else:
        lines = result["lines"]
    if not isinstance(lines, list) or any(not isinstance(r, dict) or not isinstance(r.get("ko"), str) for r in lines):
        raise ValueError("lines에는 ID와 번역 문자열이 필요합니다.")
    found = [r.get("id") for r in lines]
    if found != expected:
        pos = next((i for i, (got, need) in enumerate(zip(found, expected)) if got != need), min(len(found), len(expected)))
        raise ValueError(f"{number} {pos + 1}번째부터 ID 불일치. 기대 {expected[pos:pos+1]}, 응답 {found[pos:pos+1]}. 받은 행 {len(found)}/{len(expected)}")
    canonical = {k: v for k, v in result.items() if k not in ("lines", "scenes")}
    canonical["lines"] = lines
    return canonical


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--index", type=Path, default=Path(__file__).with_name("packet_index.json"))
    args = parser.parse_args()
    packets = {p["packet"]: p["ids"] for p in json.loads(args.index.read_text(encoding="utf-8-sig"))["packets"]}
    response = json.loads(args.response.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
    canonical = restore(response, packets)
    serialized = json.dumps(canonical, ensure_ascii=False, indent=2) + "\n"
    with args.output.open("x", encoding="utf-8", newline="\n") as out:
        out.write(serialized)


if __name__ == "__main__":
    main()

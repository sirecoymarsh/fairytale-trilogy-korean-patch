"""Install the verified opening movies without duplicating the Requiem film on P:."""
import argparse
import hashlib
import os
import shutil
from pathlib import Path

from assets import ROOT, RK, live, read, save
from opening_lyric_base import OLD


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check(path, expected):
    if digest(path) != expected:
        raise ValueError(f"Unexpected content at {path}")


def install(game):
    report = read(f"audit/opening_caption_{game}.json")
    file = Path(report["file"])
    evidence = read("audit/opening_caption_persisted.json")
    if report["decode"] != "OK" or not evidence.get(game):
        raise ValueError(f"Missing decoded caption evidence for {game}")
    check(file, report["sha256"])
    if game == "Encore":
        target = live(game) / "mov/0001.mpg"
        rollback = ROOT / "opening/0001-ko.mpg"
    else:
        target = RK / "mov/0001.mpg"
        rollback = OLD
    check(rollback, report["old_sha256"])
    already = digest(target)
    if already != report["sha256"]:
        if already != report["old_sha256"]:
            raise ValueError(f"Unexpected live opening at {target}")
        pending = target.with_name("0001.caption-pending.mpg")
        if os.path.lexists(pending):
            if not pending.is_file() or digest(pending) != report["sha256"]:
                raise ValueError(f"Unexpected pending file at {pending}")
            if game == "Requiem" and (not pending.is_symlink() or not pending.samefile(file)):
                raise ValueError(f"Unexpected pending link at {pending}")
        elif game == "Encore":
            shutil.copyfile(file, pending)
        else:
            os.symlink(file, pending)
        check(pending, report["sha256"])
        os.replace(pending, target)
    check(target, report["sha256"])
    mode = "file" if game == "Encore" else ("file symlink to Y" if target.is_symlink() and target.samefile(file) else "Y-backed movie directory")
    if game == "Requiem" and not target.samefile(file):
        raise ValueError("Requiem is not reading the verified movie on Y")
    result = {"game": game, "installed": str(target), "sha256": report["sha256"],
              "physical_movie": str(file), "previous_sha256": report["old_sha256"],
              "rollback": str(rollback), "mode": mode, "complete_audio_stream_match": True,
              "audio_sha256": report["audio_sha256"], "frames": int(report["streams"][0]["nb_read_frames"]),
              "build_evidence": f"audit/opening_caption_{game}.json",
              "caption_frame_evidence": "audit/opening_caption_persisted.json",
              "translator_model": "Codex internal"}
    if game == "Encore":
        previous = read("audit/opening_install.json")
        if previous["sha256"] == report["old_sha256"] and not (ROOT / "audit/opening_install_before_dialogue.json").exists():
            save("audit/opening_install_before_dialogue.json",previous)
        result["previous_install_evidence"] = "audit/opening_install_before_dialogue.json"
        result["unchanged_compressed_tail_frames"] = report["unchanged_compressed_tail_frames"]
        save("audit/opening_install.json", result)
    save(f"audit/opening_caption_install_{game}.json", result)
    progress = read("progress.json")
    progress.setdefault("opening_subtitles", {})[game] = result
    save("progress.json", progress)
    print(game, mode, target, flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("games", nargs="+", choices=["Encore", "Requiem"])
    for game in parser.parse_args().games:
        install(game)

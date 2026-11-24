from __future__ import annotations
import hashlib, json, re
from pathlib import Path

PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
LOCAL=Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work")
CONTROL=re.compile(r"\^(?:n|m|d\d+|s\d+)")
KANA=re.compile(r"[\u3040-\u30ff]")
SPECS={
 "3300":{"targets":{
   1:"나는 『하얀 방』으로 돌아왔다.",
   2:"나",
   3:"스케치북을 읽을까?^n아니면 다른 곳을 돌아다닐까?"
  },"slots":set(range(1,4)),"lookup":set(range(4,111)),"lookup_range":[4,110],"scope":"3300_slots_00001_00003_draft"},
 "3301":{"targets":{
   28:"앨리스와의 추억을 돌아보겠습니까?",29:"예",30:"아니요",
   31:"그레텔과의 추억을 돌아보겠습니까?",32:"예",33:"아니요",
   34:"오데트와 오딜의 추억을 돌아보겠습니까?",35:"예",36:"아니요",
   37:"라푼젤과의 추억을 돌아보겠습니까?",38:"예",39:"아니요",
   40:"게르다와의 추억을 돌아보겠습니까?",41:"예",42:"아니요"
  },"slots":set(range(28,43)),"lookup":set(range(1,27)),"lookup_range":[1,26],"scope":"3301_slots_00028_00042_draft"},
 "3600":{"targets":{
   1:"게르다",2:"어느 책을 읽을까.",3:"나",4:"어느 책을 읽을까.",5:"나",
   6:"(그래, 스케치북에 적힌 대로야.^n　다른 환자들의 『성서』가 전부 놓여 있어)",
   7:"나는 곧바로 손을 뻗었다.",8:"게르다",9:"이제 가야 해.",10:"나",11:"슬슬 다른 곳으로 갈까."
  },"slots":set(range(1,12)),"lookup":set(range(12,21)),"lookup_range":[12,20],"scope":"3600_slots_00001_00011_draft"}
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
rows={k:{} for k in SPECS}; lookups={k:set() for k in SPECS}
for line in (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8"):
 r=json.loads(line); stem=str(r.get("file","")).removesuffix(".gsc")
 if stem not in SPECS: continue
 i=int(r["slot"])
 if i in SPECS[stem]["slots"]: rows[stem][i]=r
 if "lookup_keys" in r.get("lanes",[]): lookups[stem].add(i)
for stem,s in SPECS.items():
 out=PROJECT/"packets"/"drafts"/f"{s['scope']}.json"
 if out.exists(): raise SystemExit(f"{stem} draft exists")
 if set(rows[stem])!=s["slots"] or lookups[stem]!=s["lookup"]: raise SystemExit(f"{stem} catalog mismatch")
 entries=[]
 for i in sorted(s["slots"]):
  r=rows[stem][i]; source=str(r["source_text"]); target=s["targets"][i]
  if CONTROL.findall(source)!=CONTROL.findall(target): raise SystemExit(f"{stem}:{i} control")
  if KANA.search(target): raise SystemExit(f"{stem}:{i} kana")
  target.encode("cp949")
  entries.append({"uid":r["uid"],"source_text":source,"source_raw_sha256":r["source_raw_sha256"],"target_text":target,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 정확히 1회 검수 대기"})
 data={"schema":"fairytale-requiem-translation-map-v1","scope":s["scope"],"semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries}
 out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (LOCAL/f"{stem}_targets.json").write_text(json.dumps({str(k):v for k,v in s["targets"].items()},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":"PASS","file":stem+".gsc","entries":len(entries),"lookup_slots_preserved":s["lookup_range"],"output":str(out),"sha256":sha(out)},ensure_ascii=True))

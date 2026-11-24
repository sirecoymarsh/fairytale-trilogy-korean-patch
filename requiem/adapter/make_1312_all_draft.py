from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"카드 키의 용도를^n늦은 밤까지 궁리하던 나는^n날이 밝아도 침대에서 꾸벅꾸벅 졸고 있었다.",
"──하지만.",
"갑자기 그 뻐꾸기시계 같은 소리가 울리기 시작해^n나는 황급히 침대에서 벌떡 일어났다.",
"나","(또 이 소리야.^n 이제 정말 그만했으면 좋겠어……)",
"나는 서둘러 옷을 갈아입고 방 밖으로 뛰쳐나갔다.",
"처음에는 멍하니 있었고,^n무슨 일이 벌어질까 하는 호기심까지 더해져^n그곳에 비치는 것을 보았다.",
"하지만 그곳에 비치는 것은^n언제나 어김없이 여자아이들의 부끄러운 모습이었다.",
"대부분은 진찰 장면이었지만,^n도저히 평범한 진찰로 보이지 않았다.",
"그래, 그레텔을 대할 때의^n코미야라는 그 의사와 똑같은 얼굴을 하고^n여자아이들의 몸을 더듬고 있다.",
"중간까지 본 라푼젤의 영상은^n진찰조차 아니었던 것 같다.",
"그것을 엿보는 건 그녀들에게 미안한 느낌이 들어^n요즘 나는 이 소리가 날 때마다 방을 나서고 있었다.",
"나","(기분 나빠……)",
"모니터에 비친 광경을 떠올리니 구역질이 났다.",
"그런데도──^n내 심장은 두근두근 요란하게 울렸다.",
"나","(오늘은…… 누가 비치고 있을까……?)",
"가슴속이 왠지 답답하고,^n무겁고 괴로운 무언가가 빙빙 도는 듯한 기분이 들었다.",
"나","(뭐지, 이 기분은……?)",
"내 안에서 고개 드는 그 감정의 이름을^n나는 아직 몰랐다."]
def main():
 expected=set(range(1,23))
 if len(TARGETS)!=23:raise SystemExit("target count mismatch")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1312.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(23,81)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1312_slots_00001_00022_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1312_slots_00001_00022_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[23,80],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

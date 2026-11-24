from __future__ import annotations

import hashlib, json, re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    2: "──병이라 해도 이런 것밖에 없어.",
    6: "오데트 자매의 방 문틈으로 모습을 드러낸 오딜이,^n문간에 선 게르다를 상대하는 중이었다.",
    8: "가느다란 병이라 꽃병으로는 안 어울리지 않아?",
    15: "장난삼아 정원에서 꺾은 장미를, 장난삼아 건넨 건,^n분명 그저께 밤이었던가.",
    20: "여기서도,^n활짝 핀 장미꽃잎이 완전히 메말라^n시들기 시작한 것을 알아볼 수 있었다.",
    27: "끈적하게 식은땀을 머금은 환자복을 벗어 던졌을 때의 끔찍한 기분과,^n모니터 너머로 보게 된 게르다의 진찰 모습.",
    30: "이건 겨우 손에 넣은 거야.^n──나는 정원에서 장미를 찾지 못했어.^n분명 꽤 많이 돌아다녔는데도.",
    32: "마치 『게르다』가 마법사 할머니에게^n망각의 마법을 받았던 것처럼?^n뭐, 넌 『게르다』니까.",
    41: "당연히 자신이 『오딜』인 것에 의문을 품지 않는^n오딜에게는 아무 의미도 없는 질문이다.^n어깨를 으쓱하며 내뱉는다.",
    43: "오데트로 변신해 지크프리트에게 거짓 맹세를 하게 한,^n로트바르트의 딸…….",
    45: "그래, 그래. 뭐야, 알고 있잖아.^n닮지 않으면 속일 수 없으니까 그년으로 변신한 거야.^n──하, 겉모습만 따라 했다고 속는 왕자도 참 한심하지.",
    47: "말도 안 돼. 그냥 쌍둥이 자매인 거잖아?",
    50: "그건 어렴풋이 나도 생각했던 일이다.^n사실은 쌍둥이고, 꼭 닮은 외모를 『변신했다』는 설정에^n이용하는 것이라고.",
    54: "뭐? 무슨 소리야.^n그런 건 『성서』에 안 쓰여 있어. 제대로 읽었어?",
    59: "나는 끈질기게 묻는 게르다 때문에 조마조마했다.^n오딜에게서 다른 대답이 돌아올 거라고^n어째서 기대하는 걸까?",
    60: "아니나 다를까 오딜은 겉도는 대화에 완전히 질린 듯^n깊은 한숨을 쉬며 귀찮다는 듯 머리카락 끝을 만지작거린다.",
    62: "난 오딜이잖아.^n오히려 넌 왜 네가 게르다라는 걸 인정하지 않아?",
    66: "이상한 걸 물어서 미안해.^n병은 잘 쓸게. 고마워.",
    68: "마지막으로 노골적인 경멸의 눈길을 던지고,^n오딜은 문을 닫는다.",
    79: "그저 방금 만든 꽃병을 들어 올려,^n시들기 시작한 장미의 얼굴을 내게 보여 준다.",
    81: "……고마워.^n나 나름대로 소중히 간직하기로 했어.",
    85: "게르다와 카이가 장미 화분을 기른다는^n『눈의 여왕』 도입부가 떠올라,^n결국 그 이야기를 따라가게 된 점을 얄궂게 느꼈기 때문이다.",
    88: "이건 『카이』가 아니라 네가 준 선물이니까.^n네 배려에 고마워하며, 나도 내 뜻으로 소중히 할 거야.^n그뿐이야.",
    92: "언제나 긴장의 끈을 놓지 않고 살아가는 게르다.",
    93: "조금이라도 그 위안이 되었다면,^n그날 밤 내가 부린 변덕은^n분명 좋은 일이었을 것이다.",
}
CARET_RE=re.compile(r"\^(?:n|d\d+)"); JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
def slot(uid):
    m=re.search(r"slot/(\d+)$",uid)
    if not m: raise ValueError(uid)
    return int(m.group(1))
def main():
    draft=PROJECT/"packets"/"drafts"/"1132_slots_00001_00093_draft.json"; data=json.loads(draft.read_text(encoding="utf-8"))
    if data.get("review_passes_completed")!=0: raise SystemExit("not draft")
    entries={slot(str(e["uid"])):dict(e) for e in data["entries"]}; expected=set(range(1,94))
    if set(entries)!=expected: raise SystemExit("coverage mismatch")
    changes=[]
    for i,t in CORRECTIONS.items():
        b=str(entries[i]["target_text"]); entries[i]["target_text"]=t
        if b!=t: changes.append({"slot":i,"before":b,"after":t})
    catalog={}; lookup=set()
    with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
        for line in h:
            r=json.loads(line)
            if r.get("file")!="1132.gsc": continue
            i=int(r["slot"])
            if i in expected: catalog[i]=r
            elif "lookup_keys" in r.get("lanes",[]): lookup.add(i)
    if set(catalog)!=expected or lookup!=set(range(94,152)): raise SystemExit("catalog/lookup mismatch")
    final=[]
    for i in sorted(expected):
        e=entries[i]; s,t=str(e["source_text"]),str(e["target_text"])
        if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]: raise SystemExit(f"source drift {i}")
        if CARET_RE.findall(s)!=CARET_RE.findall(t): raise SystemExit(f"caret mismatch {i}")
        if JAPANESE_RE.search(t): raise SystemExit(f"Japanese residue {i}")
        t.encode("cp949",errors="strict"); e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료"}); final.append(e)
    output={"schema":"fairytale-requiem-translation-map-v1","scope":"1132_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,93],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[94,151],"release_ready":False,"entries":final}
    out=PROJECT/"packets"/"reviewed"/"1132_all_translatable_slots_reviewed_once.json"; out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(draft)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,93],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"append_dialogue_slots_included":True,"lookup_slots_excluded":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    (PROJECT/"audit"/"translation_review_1132_complete.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({**audit,"changes":changes},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

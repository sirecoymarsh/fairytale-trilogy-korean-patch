from __future__ import annotations
import ast,hashlib,importlib.util,json,re,sys
from pathlib import Path
P=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
OUT=P/"audit"/"independent_validation_final_general_queue.json"
SPECS={"3300":{"slots":set(range(1,4)),"count":111,"lookup":[4,110]},"3301":{"slots":set(range(28,43)),"count":43,"lookup":[1,26]},"3600":{"slots":set(range(1,12)),"count":21,"lookup":[12,20]}}
CTRL=re.compile(r"\^[A-Za-z][0-9]*");KANA=re.compile(r"[\u3040-\u30ff]")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
spec=importlib.util.spec_from_file_location("gsc_codec_final_general",P/"adapter"/"gsc_codec.py");codec=importlib.util.module_from_spec(spec);sys.modules[spec.name]=codec;spec.loader.exec_module(codec)
progress=json.loads((P/"audit"/"translation_progress.json").read_text(encoding="utf-8"));prows={r["file"]:r for r in progress["completed_files"]}
files={};allchecks={}
for f,s in SPECS.items():
 mp=P/"packets"/"reviewed"/f"{f}_all_translatable_slots_reviewed_once.json";mf=P/"audit"/f"gsc_build_{f}_complete.json";srcp=P/"extracted"/"scr"/f"{f}.gsc";stagep=P/"staging"/"translation_batches"/f"{f}_complete"/f"{f}.gsc";trialp=P/"runtime"/"trial_ko"/"scr"/f"{f}.gsc"
 m=json.loads(mp.read_text(encoding="utf-8"));man=json.loads(mf.read_text(encoding="utf-8"));entries=m["entries"];slots={int(e["uid"].rsplit("/",1)[1]):e for e in entries};srcraw=srcp.read_bytes();straw=stagep.read_bytes();src=codec.parse_gsc(srcraw);st=codec.parse_gsc(straw);pr=prows[f+".gsc"]
 c={"map_hash_progress":sha(mp)==pr["review_map_sha256"],"map_hash_manifest":sha(mp)==man["translation_map"]["sha256"],"manifest_hash_progress":sha(mf)==pr["build_manifest_sha256"],"review_exactly_once":m["review_passes_completed"]==1 and all(e.get("review_status")=="reviewed_once" for e in entries),"scope_exact":m["scope"]==f"{f}_all_translatable_slots_reviewed_once","slot_coverage":set(slots)==s["slots"],"entry_count":len(entries)==len(s["slots"])==man["changed_slot_count"],"cp949":all(str(e["target_text"]).encode("cp949") is not None for e in entries),"no_kana":all(not KANA.search(str(e["target_text"])) for e in entries),"controls":all(CTRL.findall(str(e["source_text"]))==CTRL.findall(str(e["target_text"])) for e in entries),"lookup_declared":m["lookup_slots_preserved"]==s["lookup"],"source_roundtrip":codec.rebuild_gsc(src,src.strings)==srcraw,"command_identical":src.command==st.command,"trailing_identical":src.trailing==st.trailing,"string_count":len(src.strings)==len(st.strings)==s["count"],"targets_match":all(st.strings[i]==str(e["target_text"]).encode("cp949") for i,e in slots.items()),"non_targets_identical":all(src.strings[i]==st.strings[i] for i in set(range(s["count"]))-set(slots)),"manifest_roundtrip":man["files"][0]["no_change_roundtrip_byte_identical"] is True,"manifest_non_target":man["files"][0]["all_non_target_slots_identical"] is True,"stage_hash_manifest":sha(stagep)==man["files"][0]["output_sha256"],"trial_hash_stage":sha(trialp)==sha(stagep)}
 files[f+".gsc"]={"status":"PASS" if all(c.values()) else "FAIL","review_map_sha256":sha(mp),"build_manifest_sha256":sha(mf),"stage_sha256":sha(stagep),"checks":c};allchecks.update({f"{f}:{k}":v for k,v in c.items()})
tree=ast.parse((P/"adapter"/"build_sensitive_review_bundle.py").read_text(encoding="utf-8"));classified=set()
for n in tree.body:
 if isinstance(n,ast.Assign) and any(getattr(t,"id",None)=="CLASSIFIED" for t in n.targets):classified=set(ast.literal_eval(n.value))
done={r["file"].removesuffix(".gsc") for r in progress["completed_files"]}
catalog_files=set()
for line in (P/"catalog"/"scenario_catalog.jsonl").read_text(encoding="utf-8").splitlines():
 r=json.loads(line)
 if r.get("source_text") and "lookup_keys" not in r.get("lanes",[]):catalog_files.add(r["file"].removesuffix(".gsc"))
remaining=catalog_files-done
queuechecks={"progress_units":progress["catalog"]["translatable_nonempty_nonlookup_units"]==29376 and progress["completed"]["reviewed_once_units"]==15427 and progress["remaining"]["units"]==13949,"progress_files":progress["catalog"]["translatable_files"]==233 and progress["completed"]["files"]==148 and progress["remaining"]["files"]==85,"remaining_exactly_sensitive_bundle":remaining==classified and len(remaining)==85,"no_untranslated_general_files":len(remaining-classified)==0}
allchecks.update(queuechecks);status="PASS" if all(allchecks.values()) else "FAIL"
res={"schema":"fairytale-requiem-final-general-queue-validation-v1","status":status,"files":files,"queue_checks":queuechecks,"remaining_sensitive_file_count":len(remaining),"remaining_general_file_count":len(remaining-classified),"progress_sha256":sha(P/"audit"/"translation_progress.json")}
OUT.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**res,"audit_path":str(OUT)},ensure_ascii=True,indent=2));raise SystemExit(0 if status=="PASS" else 1)

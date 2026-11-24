from pathlib import Path
import sys
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");sys.path.insert(0,str(base/'adapter'))
from xfl_tool import parse_archive
out=base/'staging/non_wcg_graphics_audit_v1';out.mkdir(parents=True,exist_ok=True)
for n in ['grpe.xfl','grpo_cu.xfl','grpo_ef.xfl']:
 arc=base/'runtime/trial_ko'/n;a=parse_archive(arc);d=out/Path(n).stem;d.mkdir(exist_ok=True)
 with arc.open('rb') as f:
  for e in a.entries:
   if Path(e.name).suffix.lower() not in {'.bmp','.psd'}:continue
   f.seek(e.absolute_offset);(d/e.name).write_bytes(f.read(e.size));print(n,e.name)

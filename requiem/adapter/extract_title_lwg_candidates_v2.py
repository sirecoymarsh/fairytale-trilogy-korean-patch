from pathlib import Path
import sys,hashlib
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
sys.path.insert(0,str(base/'adapter'))
from xfl_tool import parse_archive
arc=base/'runtime/trial_ko/grpe.xfl'; out=base/'staging/title_lwg_audit_v2'; out.mkdir(parents=True,exist_ok=True)
a=parse_archive(arc); wanted={f'{i}.lwg' for i in range(3011,3021)}|{f'{i}.fsc' for i in range(3011,3021)}
with arc.open('rb') as f:
 for e in a.entries:
  if e.name not in wanted: continue
  p=out/e.name
  if not p.exists() or p.stat().st_size!=e.size:
   f.seek(e.absolute_offset); b=f.read(e.size); p.write_bytes(b)
  print(e.name,e.size,hashlib.sha256(p.read_bytes()).hexdigest().upper())

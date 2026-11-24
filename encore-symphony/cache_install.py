from pathlib import Path
p=Path('install.py');t=p.read_text(encoding='utf-8-sig')
t=t.replace("def encode(maps):\n    rows=", "def encode(maps,previous):\n    verified={r['file']:r for group in previous.values() for r in group.values()}\n    rows=")
a=t.index('        a=np.asarray(Image.open(fullpath(g,k))');b=t.index('        for g,k,*_ in group:',a)
body=t[a:t.index('        digest=sha(wcg.read_bytes())',a)]
t=t[:a]+"""        digest=sha(wcg.read_bytes()); file=str(wcg.relative_to(ROOT))
        cached=verified.get(file)
        if not (cached and cached['sha256']==digest and cached.get('outside_changed')==0):
"""+''.join('    '+line for line in body.splitlines(keepends=True))+t[b:]
t=t.replace("    enc=encode(merged);index=", "    old_enc=read('audit/encoded.json') if (ROOT/'audit/encoded.json').is_file() else {}\n    enc=encode(merged,old_enc);index=")
t=t.replace("            original_hash=current_hash(org);live_hash=current_hash(installed)", """            priorbank=previous.get(g,{}).get('banks',{}).get(b,{})
            old_subset={k:v['sha256'] for k,v in old_enc.get(g,{}).items() if k.startswith(b+'/')}
            new_subset={k:v['sha256'] for k,v in enc[g].items() if k.startswith(b+'/')}
            live_hash=current_hash(installed)
            if priorbank.get('installed_sha256')==live_hash and old_subset==new_subset:
                banks[b]=priorbank;continue
            original_hash=current_hash(org)""")
# The per-bank installation manifest itself is the digest baseline. A partial run must not
# permit input cache promotion to mark an unapplied bank as already installed.
t=t.replace("    save('audit/encoded.json',mapping)\n    return mapping","    return mapping")
t=t.replace("            if priorbank.get('installed_sha256')==live_hash and old_subset==new_subset:", "            source_set=sha(repr(sorted(new_subset.items())).encode())\n            if priorbank.get('installed_sha256')==live_hash and (priorbank.get('asset_set_sha256')==source_set or ('asset_set_sha256' not in priorbank and old_subset==new_subset)):")
t=t.replace("                banks[b]=priorbank;continue", "                banks[b]=dict(priorbank,asset_set_sha256=source_set);continue")
t=t.replace("dict(original_sha256=original_hash,installed_sha256=output_hash,","dict(original_sha256=original_hash,installed_sha256=output_hash,asset_set_sha256=source_set,")
t=t.replace("    save('progress.json',dict(phase=", "    save('audit/encoded.json',enc)\n    save('progress.json',dict(phase=")
p.write_text(t,encoding='utf-8')


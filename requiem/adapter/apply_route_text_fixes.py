"""Reproduce the ten verified text fixes using the existing XFL/GSC codecs."""
from pathlib import Path
import argparse, hashlib, json, sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'encore-symphony/collection'))
from collection_core import archive, read_entry
from gsc_codec import parse_gsc, rebuild_gsc

def apply(source, output):
    source=source.resolve();output=output.resolve()
    if source==output or output.exists(): raise ValueError('Choose a new output file; the source is preserved.')
    stage=output.with_suffix('.new')
    if stage.resolve()==source or stage.exists() or stage.is_symlink(): raise ValueError('Temporary archive path already exists or overlaps the source.')
    plan=json.loads((HERE/'route_text_fixes_20261128.json').read_bytes())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=plan['source_scr_sha256']: raise ValueError('Unsupported input scr.xfl')
    changes={}
    for item in plan['changes']:
        if item['file'] not in changes:
            parts=parse_gsc(read_entry(source,item['file']));changes[item['file']]=(parts,list(parts.strings))
        parts,strings=changes[item['file']]
        if strings[item['slot']].decode('cp949')!=item['before']: raise ValueError('Source slot differs')
        strings[item['slot']]=item['after'].encode('cp949')
    payloads={name:rebuild_gsc(parts,tuple(strings)) for name,(parts,strings) in changes.items()}
    for name,raw in payloads.items():
        old=changes[name][0];new=parse_gsc(raw)
        if old.command!=new.command or old.trailing!=new.trailing: raise ValueError('Non-text section changed')
    archive(source,output,payloads)
    if hashlib.sha256(output.read_bytes()).hexdigest()!=plan['target_scr_sha256']: raise ValueError('Output SHA256 differs from the runtime-tested archive')
    print('Verified: 5 script entries, 10 strings; runtime-tested SHA256 matched.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();apply(args.source,args.output)

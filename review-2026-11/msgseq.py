"""장면마다 말풍선 순서(MESSAGE 0x51 / APPEND 0x52)를 원본 명령 구간에서 뽑는다 → msgseq_{game}.json
칸 번호(slot)는 dump.py 와 같은 parts.strings 색인."""
import sys, json
sys.path.insert(0, r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter")
sys.stdout.reconfigure(encoding='utf-8')
from gsc_codec import parse_gsc
from build_scenario_catalog import parse_commands
from dump_lib import read_xfl, GAMES

fm = json.load(open(r"P:\AI\Codex\projects\fairytale-requiem-ko\adapter\command_formats.json", encoding='utf-8'))
FORMATS = {c['opcode']: (c['format'], c['name']) for c in fm['commands']}
W = r"Y:\AI\claude-work\fairytale-review"

for g in ('Requiem', 'Symphony'):
    ox = read_xfl(GAMES[g][0])
    out = {}
    for name, data in ox.items():
        if not name.lower().endswith('.gsc'):
            continue
        p = parse_gsc(data)
        off = 1 if p.has_leading_dummy_string else 0
        seq = []
        for c in parse_commands(p.command, FORMATS):
            if c.opcode == 0x51:
                seq.append(dict(kind='msg', spk=c.args[4], slot=c.args[5], off=off))
            elif c.opcode == 0x52:
                seq.append(dict(kind='app', spk=None, slot=c.args[4], off=off))
        if seq:
            out[name[:4]] = seq
    json.dump(out, open(f'{W}/msgseq_{g}.json', 'w', encoding='utf-8'))
    print(g, len(out), sum(len(v) for v in out.values()))

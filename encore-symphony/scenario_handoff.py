"""Prepare Japanese story packets for manual Gemini translation. No network calls."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from assets import ROOT, RBASE, RJ, entry_map, read, read_entry, source
from wording import EN, SY, ROUTES
from gsc_codec import parse_gsc
from build_scenario_catalog import parse_commands
from scenario_layout import RUBY_RE, display_text
from scenario_compact import compact_work, decode_rows


DEST = ROOT / '시나리오_제미나이'
BASE_KIT = RBASE / 'gemini_retranslation_kit_20260829_v2' / 'gemini'
QUALITY = Path('P:/AI/Codex/skills/contextual-game-localization/references/translation-quality.md')
FORMATS = {r['opcode']: (r['format'], r['name']) for r in read(RBASE / 'adapter/command_formats.json')['commands']}
WORKS = {'Encore': ('E', '앙코르', EN), 'Symphony': ('S', '심포니', SY)}
MAIN_TITLES = {int(r['id']): r['source_corrected'] for r in read(Path(read(RBASE / 'audit/grpo_ex_title_translation_postreview.json')['output']['path']))['scene_titles']}
SOURCE_URL = {'Encore': 'https://www.liar.co.jp/fairy_encore/', 'Symphony': 'https://www.liar.co.jp/fairy_symphony/'}
RECOVER = {('R',1518): (4526,84,85), ('R',1822): (586,21,22), ('S',1022): (2880,0,69)}
CONTROL = re.compile(r'\^(?:cr|cy|ck|g\d{3}|d\d+|s\d+|m|n)')
JP = re.compile(r'[\u3041-\u30fa\u4e00-\u9fff]')
SCENEFILES = {'E': sorted(set(EN) - {1601}), 'S': sorted(SY), 'R': sorted(MAIN_TITLES)}
TITLE_PATH = '01_작품원문과_첫요청.txt'
REF_PATH = '02_레퀴엠_발췌.txt'
SCHEMA = 'fairytale-gemini-handoff-v1'
TERMS = read(BASE_KIT / 'glossary.json')['entries']
OLD_LABELS = read(BASE_KIT / 'speaker_labels.json')['source_label_map']
QUALITY_BYTES = QUALITY.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(p):
    return digest(p.read_bytes())


def write_text(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((s.rstrip('\n') + '\n').encode('utf-8'))


def write_json(p, d):
    write_text(p, json.dumps(d, ensure_ascii=False, indent=2))


def jsonrow(r):
    return json.dumps(r, ensure_ascii=False, separators=(',', ':'))


def measured(s):
    s = re.sub(r'\[+[^\[\]\n]+\]+', '', display_text(s)).replace('|', '').replace('^n','').replace('^cr','')
    return len(re.sub(r'\s+', '', s))


def branch_intervals(commands):
    """Resolve the two option-dispatch trampolines and the merge, where present."""
    at = {c.offset: i for i,c in enumerate(commands)}
    spans = []
    for cmd in commands:
        if cmd.opcode != 14:
            continue
        assert cmd.args[0] == 2
        dests = []
        for address in cmd.args[2:4]:
            tri = commands[at[address]:at[address] + 5]
            dests.append(next(c.args[0] for c in tri if c.opcode == 5))
        a,b = dests
        jump = commands[at[b] - 1]
        assert jump.opcode == 5 and a < b < jump.args[0] and jump.args[0] in at
        spans.append((a,b,jump.args[0],cmd.args[1]))
    return spans


def get_scene(prefix, num, bank):
    filename = f'{num}.gsc'
    raw = read_entry(bank, filename)
    parts = parse_gsc(raw)
    commands = parse_commands(parts.command, FORMATS)
    members = [(c.offset,c.opcode,c.args) for c in commands if c.opcode in (81,82,14)]
    fix = RECOVER.get((prefix,num))
    if fix:
        off,sp,slot = fix
        assert struct.unpack_from('<H', parts.command, off)[0] == 81
        args = struct.unpack_from('<' + FORMATS[81][0], parts.command, off+2)
        assert args[4:6] == (sp,slot)
        if off not in {x[0] for x in members}:
            members.append((off,81,args))
    spans = branch_intervals(commands) if prefix == 'S' else []
    rows, label_map, used = [], {}, set()
    last = None
    for offset, op, args in sorted(members):
        if op == 81:
            speaker_slot, slot = args[4:6]
            name = parts.strings[speaker_slot].decode('cp932')
            if name:
                label_map[speaker_slot] = name
            last = (name,speaker_slot,slot)
            fields = [(slot,'발화' if name else '무표기',name,speaker_slot,None)]
        elif op == 82:
            assert last is not None
            name,speaker_slot,ancestor = last
            fields = [(args[4],'이어쓰기',name,speaker_slot,ancestor)]
        else:
            fields = [(args[1],'선택문','',None,None)]
            fields += [(args[j],f'보기{j-6}','',None,args[1]) for j in (7,8,9,10,11)]
        for slot,kind,speaker,sp,parent in fields:
            original = parts.strings[slot]
            if not original:
                continue
            ja = original.decode('cp932')
            if not measured(ja):
                continue
            uid = f'{prefix}{num}-{slot:05}'
            assert slot not in used and not any(ch in ja for ch in '\t\r\n'), (uid,kind)
            used.add(slot)
            branch = ''
            for a,b,merge,anchor in spans:
                if a <= offset < merge:
                    branch = f'선택{1 if offset < b else 2}'
                elif offset >= merge:
                    branch = '합류 뒤'
            rows.append(dict(id=uid,scene=num,slot=slot,offset=offset,kind=kind,speaker=speaker,
                             speaker_slot=sp,linked_id=(f'{prefix}{num}-{parent:05}' if parent is not None else ''),
                             branch=branch,ja=ja,controls=CONTROL.findall(ja),source_sha256=digest(original)))
    # Every Japanese string in a target story segment must be a covered text or name field.
    if prefix in ('E','S'):
        uncaptured = [(j,b.decode('cp932')) for j,b in enumerate(parts.strings) if j not in used and j not in label_map and JP.search(b.decode('cp932'))]
        assert not uncaptured, (prefix,num,uncaptured[:2])
        assert not any('^' in CONTROL.sub('',r['ja']) for r in rows)
        assert [r['slot'] for r in rows] == sorted(used)
    return rows, label_map, digest(raw)


def escape_field(v):
    assert '\t' not in v and '\n' not in v
    return v or '—'


def tsv(r):
    return '\t'.join((r['id'], r['kind'], escape_field(r['speaker']), escape_field(r['branch']), r['ja']))


# Main-game scene numbers and literal evidence anchors. Excerpts retain adjacent narration and replies.
# Names in the selectors are displayed speakers, never assigned addressees.
SAMPLES = {
 'Encore': [
    (1115,['イケノ','僕'],['先生']), (1116,['医者','グレーテル','アリス'],['おくすり']),
    (1718,['ドロシー','イケノ'],['ドロシー']), (1719,['ドロシー'],['おうち','イケノ','トト']),
    (1218,['ラプンツェル','アリス'],[]), (1125,['オディール','オデット'],[]),
    (1710,['ドロシー','オディール','オデット'],[]), (1152,['ラプンツェル'],['王子様']),
    (1815,['ゲルダ','ラプンツェル'],['あの子']), (1127,['僕','ゲルダ'],['聖書','カイ']),
    (1624,['カイ','ゲルダ'],[]), (1705,['黒の少女','僕'],[])
 ],
 'Symphony': [
    (1101,['僕','アリス'],[]), (1108,['僕'],['つみびと','スケッチブック']),
    (1124,['グレーテル','僕'],['パン']), (1125,['オデット','オディール'],[]),
    (1127,['ゲルダ','僕'],['カイ','聖書']), (1152,['ラプンツェル'],['王子様']),
    (1218,['ラプンツェル','アリス'],[]), (1316,['ゲルダ','グレーテル'],[]),
    (1616,['名無しの少年','ゲルダ'],['カイ']), (1705,['黒の少女','僕'],[]),
    (1706,['アリス','僕'],[]), (1717,['僕','ゲルダ','アリス'],['罪','つみびと']),
    (1718,['イケノ','僕'],['ドロシー','黒の少女']), (1720,[],['楽園','僕','物語'])
 ]
}


def excerpts(game, main):
    out = []
    for num,want,terms in SAMPLES[game]:
        story = main[num][0]
        options = []
        width = min(len(story),18)
        for i in range(len(story) - width + 1):
            cut = story[i:i+width]
            if cut[0]['kind'] == '이어쓰기' or (i+width < len(story) and story[i+width]['kind']=='이어쓰기'):
                continue
            named = Counter(r['speaker'] for r in cut if r['kind']=='발화')
            spoken = [r['speaker'] for r in cut if r['kind']=='발화' and r['speaker'] in want]
            flags = {k for k in terms if any(k in r['ja'] for r in cut)}
            score = (sum(n in named for n in want),len(flags),sum(min(3,named[k]) for k in want),
                     sum(a!=b for a,b in zip(spoken,spoken[1:])), min(6,len(spoken)))
            options.append((score,-i,cut))
        assert options
        cut = max(options,key=lambda x:x[:2])[2]
        out.append((num,cut))
    return out

def groupnum(game, n):
    return n//100 if game=='Encore' else 10


def make_packets(game, scenes):
    """Split long scenes at text windows and keep shorter consecutive scenes together within each route."""
    groups = []
    current = []
    size = 0
    prefix = WORKS[game][0]
    def flush():
        nonlocal current,size
        if current:
            groups.append(current)
        current, size = [],0
    for n,rows in scenes.items():
        lens = [measured(r['ja']) for r in rows]
        nchar = sum(lens)
        sections = max(1, math.ceil(nchar/6000), math.ceil(len(rows)/155))
        if sections == 1:
            if current and (len(current) + len(rows)>155 or size+nchar>6000 or groupnum(game,n)!=groupnum(game,current[-1]['scene'])):
                flush()
            current.extend(rows)
            size += nchar
            continue
        flush()
        # Keep appended pages and a choice prompt with all its alternatives.
        cuts = [j for j in range(1,len(rows)) if rows[j]['kind'] != '이어쓰기' and not rows[j]['kind'].startswith('보기')]
        first = 0
        for k in range(1,sections):
            target = len(rows)*k/sections
            eligible = [j for j in cuts if first < j < len(rows) - (sections-1-k)]
            boundary = min(eligible, key=lambda j: abs(j-target))
            groups.append(rows[first:boundary])
            first = boundary
        groups.append(rows[first:])
    flush()
    return {f'{prefix}{i:03}': g for i,g in enumerate(groups,1)}


def context_rows(rows, locs, allscenes):
    first,last = rows[0],rows[-1]
    firstpos,lastpos = locs[first['id']],locs[last['id']]
    before = allscenes[first['scene']][max(0,firstpos-4):firstpos]
    after = allscenes[last['scene']][lastpos+1:lastpos+5]
    return before,after


def scene_heading(game, n):
    ja,ko = WORKS[game][2][n]
    return f'[{n}  {ja}  /  {ko}]'


def scene_lines(game,rows):
    lines = []
    previous = None
    for r in rows:
        n = r['scene']
        if n!=previous:
            lines += ['',scene_heading(game,n)]
        lines.append(tsv(r))
        previous = n
    return lines


def glossary(game, rows):
    out = []
    for old in TERMS:
        if old['status'] != 'locked' or old['category'] == 'address_form':
            continue
        term = old['source']
        hits = [r['id'] for r in rows if r['speaker']==term or term in r['ja']]
        if not hits:
            continue
        termrec = {k:old[k] for k in ('term_id','source','target','category','part_of_speech','canonical_spelling','spacing_and_inflection','meaning','runtime_function','scene_specific_usage','allowed_variants','forbidden_or_deprecated_variants','status') if k in old}
        termrec.update(evidence_ids=hits[:3],requiem_evidence_ids=old.get('evidence_ids',[])[:2])
        out.append(termrec)
    return {'version':'1','provenance':'레퀴엠 용어집에서 두 작품에 실제 등장하는 항목만 재사용. 호칭과 말투는 작품별 해석에 맡김.','entries':out}


def voices(prefix, rows, refsets):
    names = list(dict.fromkeys(r['speaker'] for r in rows if r['speaker']))
    by_name = {s:[r for r in rows if r['speaker']==s and r['kind']=='발화'] for s in names}
    out = []
    for idx,name in enumerate(names,1):
        labeled = by_name[name]
        obs = {}
        for r in labeled:
            obs.setdefault(r['scene'],r['id'])
        evidence = list(obs.values())
        main_ids = [r['id'] for _,part in refsets for r in part if r['speaker']==name][:3]
        old = OLD_LABELS.get(name,{})
        target = old.get('target', '')
        out.append(dict(character_id=f'{prefix}-N{idx:02}',source_label=name,canonical_name=target or None,
                        label_status='본편 기사용 표기' if target else 'Gemini 판정 대기', role='원문 표시명',
                        baseline_traits=None, status='pending', evidence_ids=evidence,requiem_label_match=main_ids,
                        relationships=[dict(addressee=None,story_phase='해당 장면',situation=None,speech_level=None,
                                            address_terms=None,first_person=None,second_person=None,changes=None,
                                            evidence_ids=evidence[:3],status='pending')],
                        recovery='작품 통독 후 상대와 시점별로 발화·응답 ID를 제시. 이름이 같은 익명 표기는 인물 동일성의 근거로 사용하지 않음.'))
    return {'version':'1','interpretation_owner':'Gemini','characters':out}


HEADER = 'ID\t종류\t원문 화자 표시\t선택 구간\t일본어 원문'
COMMON_RULES = '''당신은 일본어 비주얼노벨을 한국어로 옮기는 번역가입니다. 작품 해석, 인물별·상대별 말투, 아직 정해지지 않은 호칭과 한국어 시나리오 초벌 번역을 맡습니다. 독자는 한국어로 플레이하는 성인입니다. 원작의 어조와 수위를 따르세요. 최종 원문 대조 검수는 사용자가 별도로 진행합니다.

# 읽는 순서
먼저 이 작품의 대본 전체를 읽으세요. 02 파일에 있는 레퀴엠 발췌는 같은 표기, 인물 간 주고받음, 앞선 설정을 확인할 때만 쓰세요. 작품 안에서 현재 화자와 상대가 무엇을 알고 있는지 확인하세요. 회상, 다른 선택의 전개, 이름 공개 전후를 구별하세요. 발췌 제목과 뒤 장면에서 밝혀진 사실을 앞 대사에 미리 넣지 마세요. 근거가 모자라면 필요한 화자·장면·어구를 적어 주세요. 본편에서 다른 일부 장면을 추가로 확인할 수 있습니다.

# 원고 읽기
열 순서는 ID, 줄 종류, 화면의 일본어 화자명, 선택 구간, 원문입니다. —는 해당 표시가 없다는 뜻입니다. 무표기는 지문·독백·인용일 수 있습니다. 이어쓰기는 앞 발화 또는 지문 칸의 연속입니다. 화자 표시만으로 청자가 정해지지는 않습니다. 동석자가 여러 명이면 누구에게 한 말인지 앞뒤 답변에서 확인하세요. 합창·불명 화자·별칭은 원작이 공개하는 범위를 따르세요.
장면은 원본 시나리오 파일의 수록 순서입니다. 선택1과 선택2는 같은 선택문의 대안 전개입니다. 합류 뒤에는 선택에 따른 내부 조건이 남아 있을 수 있습니다. 같은 장면 앞뒤가 잘린 번역 파일에는 참고 행이 따로 있습니다. 참고 행과 레퀴엠의 R로 시작하는 ID는 답에 번역하지 마세요.

# 작품의 표현
원문에 있는 비유·반복·거친 표현·긴장과 동화 어휘를 살리고, 단어별 직역으로 리듬을 깨지 마세요. 정보가 없는 부사, 감각 묘사, 감정, 동작, 동기, 친밀도, 원인 또는 복선을 더하지 마세요. 제출 직전 각 수식과 행동의 근거를 원문에서 조용히 확인하고 추가한 묘사를 덜어내세요. 외래어와 말장난, 진짜 방언은 해당 인물의 쓰임을 보세요. 일상 호칭과 알려진 별명, 동화 속 배역을 구분하세요. 번역 근거로 삼을 음성은 이 자료에 포함되어 있지 않습니다. 발음이 꼭 필요한 판정은 issue에 남기세요.

# 원본 형식
ID마다 원래 표시 칸 하나를 유지하세요. 이어지는 문장은 함께 해석하고 원래 ID 수에 맞춰 나누세요. 원문 ^n(강제 줄바꿈), ^m, ^cr 등 캐럿 제어는 종류·개수·순서를 그대로 두고 한국어의 대응 위치에 배치하세요. ^n을 JSON 개행이나 실제 줄바꿈으로 바꾸지 마세요. 루비 |표기[읽기]는 표기와 실제 읽기를 모두 해석하세요. 통상적인 발음 안내 루비는 한국어에서 자연스럽게 생략할 수 있습니다. 다른 명칭, 외래어 발음, 이중 의미나 말장난을 전달하는 루비는 두 층을 살려 |한국어표기[한국어읽기]로 반환하고 애매하면 issue에 남기세요. 숫자, 기호가 가진 의미와 선택지의 대응을 보존하세요. 대상 ID나 원문을 나누거나 합치지 마세요.

# 번역 응답
한 번에 요청한 묶음의 대상 ID만 원래 순서대로 반환하세요. JSON 하나에 packet, lines, issues를 넣으세요. lines의 항목은 {"id":"게임의 실제 ID","ko":"완성된 한국어"}입니다. issues에는 {"id":"대상 ID","reason":"확인이 필요한 이유","needed":"판정에 필요한 증거"}를 쓰세요. 확인 사항이 없으면 빈 배열을 쓰세요. 번역 본문에는 작업 메모를 끼워 넣지 마세요. 완료한 묶음에서 새로 확인한 호칭이나 용어는 필요한 경우 voice_updates 배열에 원문 ID와 함께 남겨 다음 묶음에 재사용하세요. 처음 해석표에서 잠정으로 둔 판정도 원문 근거가 생기면 바꿀 수 있습니다.'''

FIRST_TASK = '''이제 이 작품의 인물과 관계를 해석해 주세요. 번역은 다음 요청에서 시작합니다.
1. 작품의 시점·화자·선택지와 인물이 그때 알고 있는 사실을 짧게 정리하세요. 스포일러는 해석표에서만 다루세요.
2. 주요 인물을 화자 → 상대별로 정리하세요. 호칭, 일인칭, 존대, 문장 끝, 말투가 바뀌는 순간을 제안하고 작품 안의 발화·응답 ID를 붙이세요. 본편을 참고하면 R로 시작하는 별도 근거 ID를 덧붙이세요.
3. 화자 표시표의 모든 ID에 한국어 표시명을 하나씩 결정하세요. 같은 사람일 가능성이 있어도 원작이 달리 표시한 이름은 각각 남기세요. 기존 표기와 결정을 함께 저장할 수 있도록 labels 배열에 {"id":"화자 ID","ko":"한국어 표시명"} 형식을 쓰세요.
4. 핵심 용어·동화 속 배역·중의적인 표현과 미해결 사항을 따로 적으세요. 확신할 수 없는 항목은 미정으로 두고, 필요한 본편 장면이나 화자 또는 원문 검색어를 요청하세요. 다음 묶음에서도 이 해석표를 참조할 수 있게 간결하게 작성하세요.'''

def first_request(game):
    if game == 'Encore':
        return '앙코르는 본편의 앞선 이야기입니다. 도로시와 이케노가 처음 접하는 일과, 이케노가 맡는 동화 속 배역의 말투를 구분하세요. 1100·1200·1300·1400번대 각 이야기와 1501의 시점을 작품 안에서 확인하세요.'
    return '심포니는 본편에서 다루지 않은 또 하나의 결말입니다. 이 작품의 소년·앨리스와 과거를 가리키는 표기, 익명 화자가 무엇을 알고 있는지 장면마다 확인하세요. 본편의 한 루트 결말을 전제하려면 양쪽 원문에서 근거를 확인하세요.'

def instructions(game):
    return COMMON_RULES + '\n\n# 이 작품의 시점\n' + first_request(game)

def input_header(pid,rows,game,scenes,locs):
    before, after = context_rows(rows,locs,scenes)
    parts = [f'{WORKS[game][1]}  {pid}  |  번역 대상 {len(rows)}행',
             '공통 지침과 이 작품의 해석표를 사용하세요. 출력할 ID는 [번역 대상] 아래에 있습니다.', HEADER]
    for scene in dict.fromkeys(r['scene'] for r in rows):
        selection = [r for r in scenes[scene] if r['kind']=='선택문' or r['kind'].startswith('보기')]
        if selection and any(r['scene']==scene and r['branch'] for r in rows) and not any(r in rows for r in selection):
            parts += ['','[이 장면 선택지 · 참고]'] + [tsv(r) for r in selection]
    if before:
        parts += ['', '[직전 문맥 · 참고]'] + [tsv(r) for r in before]
    if after:
        parts += ['', '[직후 문맥 · 참고]'] + [tsv(r) for r in after]
    parts += ['', '[번역 대상]'] + scene_lines(game,rows)
    parts += ['','[요청]',f'{pid}의 대상 {len(rows)}행을 순서대로 한국어로 번역해 주세요. JSON의 packet 값은 "{pid}"입니다.']
    return '\n'.join(parts)


def prepare_game(base, game, main):
    prefix, short, dictionary = WORKS[game]
    bank = source(game)/'scr.xfl'
    out = base/short
    kit = out/'검수자료'/'gemini'
    titles = SCENEFILES[prefix]
    scope = sorted(int(n[:4]) for n in entry_map(bank) if n.endswith('.gsc') and 1000<=int(n[:4])<1999 and not (game=='Encore' and n=='1001.gsc'))
    assert scope==titles, (game,scope,titles)
    data = {n:get_scene(prefix,n,bank) for n in titles}
    scenes = {n:d[0] for n,d in data.items()}
    rows = [r for rs in scenes.values() for r in rs]
    samples = excerpts(game,main)
    gterms = glossary(game,rows)
    voice = voices(prefix,rows,samples)
    char_to_id = {c['source_label']:c['character_id'] for c in voice['characters']}
    labels_by_file = {str(n):{str(slot):char_to_id[name] for slot,name in d[1].items()} for n,d in data.items()}
    groups = make_packets(game,scenes)
    locs = {r['id']:i for part in scenes.values() for i,r in enumerate(part)}
    owner = {r['id']:pid for pid,rs in groups.items() for r in rs}
    for r in rows:
        r['speaker_id'] = char_to_id.get(r['speaker'])
        r['packet'] = owner[r['id']]
    reference_rows = [r for _,part in samples for r in part]
    ref_count = sum(measured(r['ja']) for r in reference_rows)
    nchar = sum(measured(r['ja']) for r in rows)
    profile = Counter(r['kind'] for r in rows)
    expected = {'Encore':(48,4122,150313,0),'Symphony':(24,2329,76207,4)}[game]
    assert (len(scenes),len(rows),nchar,profile['선택문'])==expected
    branches = [n for n in scenes if any(r['kind']=='선택문' for r in scenes[n])]
    for n in branches:
        assert {'선택1','선택2'} <= {r['branch'] for r in scenes[n]}
    sha_sources = {str(n):d[2] for n,d in data.items()}
    registry = [{k:c[k] for k in ('character_id','source_label','canonical_name','label_status')} for c in voice['characters']]
    write_json(kit/'glossary.json',gterms)
    write_json(kit/'character_voice.json',voice)
    write_json(kit/'protected_tokens.json',dict(version='1',controls=sorted({s for r in rows for s in r['controls']}),
               rule='ID별 캐럿 제어의 종류·순서·개수 보존. 원문 전체·루비는 catalog.jsonl의 ja에 보존. 통상 읽기와 의미가 갈리는 루비는 지침에 따라 별도 처리.'))
    (kit/'quality_authority.md').write_bytes(QUALITY_BYTES)
    write_text(out/'검수자료'/'catalog.jsonl','\n'.join(jsonrow(r) for r in rows))
    write_json(out/'검수자료'/'speaker_slots.json',dict(labels=registry,by_file=labels_by_file))
    hints = [f'# 레퀴엠 원문 발췌 · {short} 해석 참고',
             f'레퀴엠 원본의 {len(samples)}개 장면에서 뽑은 연속 구간입니다. 일본어 본문 {ref_count:,}자입니다.',
             '아래 장면은 각기 다른 시점과 루트에서 가져왔습니다. 번호는 레퀴엠 장면 ID입니다. 각 줄의 R 번호로 원문을 다시 찾을 수 있습니다.',
             '화자명은 화면 표기입니다. 줄 앞뒤의 응답과 지문을 함께 읽고, 현재 작품에 적용할 수 있는지 판단하세요. 발췌 사이의 사건은 생략되어 있습니다.',
             '발췌에 없는 인물·화법의 근거는 이번 작품 원문에서 찾으세요. 같은 표기만으로 익명 화자나 동화 속 배역의 정체를 합치지 마세요.', '',HEADER]
    for n, part in samples:
        hints += ['',f'[레퀴엠 {n}  {MAIN_TITLES[n]}  /  {part[0]["id"]} ~ {part[-1]["id"]}]'] + [tsv(r) for r in part]
    write_text(out/REF_PATH,'\n'.join(hints))

    listpack = []
    index = []
    for pid,rs in groups.items():
        a,b = rs[0],rs[-1]
        fname = f'번역/{pid}_{a["scene"]}-{b["scene"]}.txt'
        write_text(out/fname,input_header(pid,rs,game,scenes,locs))
        listpack.append(f'{pid}  {a["id"]} ~ {b["id"]}  ({len(rs)}행)')
        index.append(dict(packet=pid,file=fname,sha256=file_hash(out/fname),ids=[r['id'] for r in rs],
                          source_chars=sum(measured(r['ja']) for r in rs),scene_ids=list(dict.fromkeys(r['scene'] for r in rs))))
    write_json(out/'검수자료'/'packet_index.json',dict(work=game,packets=index))
    authority_hash = digest(QUALITY_BYTES)
    contract_inputs = {fn:file_hash(kit/fn) for fn in ['quality_authority.md','glossary.json','character_voice.json','protected_tokens.json']}
    catalog_hash = file_hash(out/'검수자료'/'catalog.jsonl')
    hashes = [f'{k}  {v}' for k,v in contract_inputs.items()] + [f'catalog.jsonl  {catalog_hash}',f'{REF_PATH}  {file_hash(out/REF_PATH)}']
    instruction = instructions(game)
    write_text(kit/'translation_instructions.md',instruction+'\n\n# 첫 요청\n'+FIRST_TASK+'\n\n# 입력 판본 SHA-256\n'+'\n'.join(hashes))
    sheet = [f'# 페어리테일 {short} · 일본어 원문과 해석 의뢰',
             f'{len(scenes)}개 장면 · {len(rows):,}개 표시 칸 · 일본어 본문 {nchar:,}자',
             instruction,'','# 레퀴엠 한국어판에서 이어 쓰는 표기',
             '같은 대상을 가리킬 때의 표기입니다. 원문이 다른 발음을 루비로 따로 제시하면 그 효과도 살리세요. 호칭과 존대는 현재 상대와 시점에 따라 판단하세요.']
    sheet += [e['source']+'  →  '+e['target'] for e in gterms['entries']]
    sheet += ['','# 이번 작품의 화자 표시표','화자 ID\t원문 표시\t기존 한국어 표기']
    sheet += ['\t'.join((c['character_id'],c['source_label'],c['canonical_name'] or '판정 요청')) for c in voice['characters']]
    sheet += ['','# 번역 묶음과 대상 범위']+listpack
    sheet += ['','# 공통 한국어 번역 기준','사용자가 이 두 작품의 해석과 번역을 Gemini에 지정했습니다. 아래는 공통 품질 기준의 고정본입니다.',
              QUALITY_BYTES.decode('utf-8-sig').strip(), '', '# 일본어 원문', HEADER]
    for n,rs in scenes.items():
        sheet += scene_lines(game,rs)
    sheet += ['','# 첫 요청',FIRST_TASK]
    write_text(out/TITLE_PATH,'\n'.join(sheet))
    pack_example = list(groups)[0]
    guide = f'''페어리테일 {short} · Gemini 의뢰 방법

1. 이 작품 전용 Gemini 대화를 열고 {TITLE_PATH}와 {REF_PATH}를 함께 첨부하세요. “두 파일을 읽고 01 파일 끝의 첫 요청에 따라 해석표와 화자 표시명을 만들어 줘.”라고 보내세요. 분석 답변을 보관하세요.
2. 같은 대화에서 “확정한 해석표로 {pack_example}을 번역해 줘.”라고 요청하세요. 01 파일에 묶음별 ID 범위가 있습니다. 특정 범위를 놓치거나 대화가 길어지면 번역 폴더에서 해당 번호 TXT를 첨부하세요. 답변이 중간에 멈추면 같은 묶음에서 마지막으로 받은 ID 다음부터 이어 달라고 하세요.
3. 새 대화를 쓸 때는 이 작품의 01·02 파일과 최신 해석표를 처음에 한 번 넣고, 그다음에는 필요한 묶음만 보내세요. 긴 대화에서 예전 첨부가 기억된다는 보장은 없습니다. 묶음의 처음·끝 ID와 행 수는 각 요청 파일에 있습니다.
4. 번역 응답은 묶음 번호별 UTF-8 JSON으로 저장하세요. 해석표와 화자 표시명, 선택한 Gemini 모델의 실제 표시 이름이나 API 모델 ID, 가능하면 생성 설정을 함께 보관하세요. 나중에 그대로 검수에 넘길 수 있습니다. 검수자료 폴더는 로컬 원문 대조용입니다.

준비 범위
원본 디스크 설치 자료의 시나리오 {len(scenes)}개, {len(rows):,}행입니다. 화자 표시 {len(registry)}종은 첫 요청에서 별도로 다룹니다. 선택문은 {len(branches)}곳입니다. 각 묶음은 대상 ID 하나를 한 번씩 소유합니다. 본편은 {len(samples)}개 장면의 일부만 첨부했습니다. 추가 확인이 필요하면 레퀴엠 화자·상대·장면 번호 또는 원문 어구를 알려 주세요.
{('별매·특전 자료에서 추가되는 앙코르 FC 어펜드 「禁断の闘争録」의 대본 1601.gsc는 이 디스크 원본에 없습니다.' if game=='Encore' else '선택이 있는 장면은 1004, 1005, 1009, 1013입니다. 독립 전개와 다시 합류하는 위치를 원본 점프 위치에서 확인했습니다.')}
작품 공식 소개  {SOURCE_URL[game]}
'''
    write_text(out/'사용법.txt',guide)
    files = {p.relative_to(out).as_posix():file_hash(p) for p in sorted(out.rglob('*')) if p.is_file()}
    summary = dict(work=game,title=short,scenes=len(scenes),rows=len(rows),characters=nchar,packets=len(groups),
                   speaker_labels=len(registry),choice_scenes=branches,reference_scenes=len(samples),reference_rows=len(reference_rows),
                   reference_characters=ref_count, packet_max_rows=max(len(x) for x in groups.values()),
                   packet_max_characters=max(x['source_chars'] for x in index))
    manifest = dict(schema=SCHEMA,version=1,work=game,created_utc=datetime.now(timezone.utc).isoformat(),
                    source_language='ja-JP',target_language='ko-KR',preparation_model='Codex internal',
                    preparation_model_family='GPT-6 / Codex',intended_provider='Gemini',translator_model=None,
                    actual_provider_model_id=None,authorization='사용자가 작품별 인물 해석과 시나리오 번역을 Gemini에 직접 의뢰할 수 있도록 준비. 검수는 Codex.',
                    transmission='not_sent',result_records=[],glossary_version='1',voice_version='1',
                    voice_decisions_pending=len(registry), label_spellings_pending=sum(not c['canonical_name'] for c in voice['characters']),
                    semantic_review_status='pending_provider_response',unsupported_addition_audit={'checked_lines':0,'violations':None,'retranslated_ids':[],'reviewer':None},
                    summary=summary,source_archive_sha256=file_hash(bank),source_entry_sha256=sha_sources,
                    requiem_archive_sha256=file_hash(RJ/'scr.xfl'),requiem_excerpt_entry_sha256={str(n):main[n][2] for n,_ in samples},
                    requiem_glossary_sha256=file_hash(BASE_KIT/'glossary.json'),requiem_label_map_sha256=file_hash(BASE_KIT/'speaker_labels.json'),
                    catalog_sha256=catalog_hash,quality_authority_sha256=authority_hash,
                    style_guide_sha256=file_hash(kit/'translation_instructions.md'),protected_token_contract_sha256=contract_inputs['protected_tokens.json'],
                    validation='source-fields, coverage, packet ownership, branch labels, excerpts and ZIP verified before delivery',
                    files_sha256=files,sources=[SOURCE_URL[game],'https://www.liar.co.jp/fairy_symphony/','https://ai.google.dev/gemini-api/docs/long-context'])
    write_json(kit/'manifest.json',manifest)
    return summary

def read_rows(text, prefix, version):
    if version == 2:
        return decode_rows(text)
    pattern = r'^' + prefix + r'\d{4}-\d{5}\t'
    return [line.split('\t') for line in text.splitlines() if re.match(pattern,line)]


def validate(out, game):
    prefix,short,titles = WORKS[game]
    kit = out/'검수자료'/'gemini'
    mf = read(kit/'manifest.json')
    for file,expected in mf['files_sha256'].items():
        assert file_hash(out/file)==expected, file
    assert (kit/'quality_authority.md').read_bytes()==QUALITY_BYTES
    rows = [json.loads(l) for l in (out/'검수자료'/'catalog.jsonl').read_text('utf-8').splitlines()]
    by_id = {r['id']:r for r in rows}
    story = (out/TITLE_PATH).read_text('utf-8').split('# 일본어 원문\n',1)[1].rsplit('# 첫 요청\n',1)[0]
    rs = read_rows(story,prefix,mf['version'])
    assert len(by_id)==len(rows) and [x[0] for x in rs]==list(by_id)
    bank = source(game)/'scr.xfl'
    raw_per_scene = {n:parse_gsc(read_entry(bank,f'{n}.gsc')) for n in SCENEFILES[prefix]}
    sp = read(out/'검수자료'/'speaker_slots.json')
    speaker_by_id = {x['character_id']:x['source_label'] for x in sp['labels']}
    for fields in rs:
        uid,kind,speaker,branch,ja = fields
        r = by_id[uid]
        seg = raw_per_scene[r['scene']]
        raw = seg.strings[r['slot']]
        assert ja==raw.decode('cp932') and digest(raw)==r['source_sha256'] and fields==tsv(r).split('\t')
        if r['speaker_id']:
            key = sp['by_file'][str(r['scene'])][str(r['speaker_slot'])]
            assert key==r['speaker_id'] and speaker_by_id[key]==speaker==seg.strings[r['speaker_slot']].decode('cp932')
        if r['linked_id']:
            assert r['linked_id'] in by_id
    for n, table in sp['by_file'].items():
        assert all(raw_per_scene[int(n)].strings[int(k)].decode('cp932')==speaker_by_id[v] for k,v in table.items())
    assignments = []
    for packet in read(out/'검수자료'/'packet_index.json')['packets']:
        data = (out/packet['file']).read_text('utf-8')
        body = data.split('\n[번역 대상]\n',1)[1].split('\n[요청]\n',1)[0]
        inputs = read_rows(body,prefix,mf['version'])
        ids = [x[0] for x in inputs]
        assert ids==packet['ids'] and all(tsv(by_id[x[0]]).split('\t')==x for x in inputs)
        assert all(by_id[i]['packet']==packet['packet'] for i in ids)
        assignments.extend(ids)
    assert assignments==list(by_id)
    ref = read_rows((out/REF_PATH).read_text('utf-8'),'R',mf['version'])
    assert len(ref)==len({v[0] for v in ref})==mf['summary']['reference_rows']
    ref_scene_ids = {int(v[0][1:5]) for v in ref}
    mr = {n:parse_gsc(read_entry(RJ/'scr.xfl',f'{n}.gsc')).strings for n in ref_scene_ids}
    for uid,_,__,___,ja in ref:
        n=int(uid[1:5])
        assert mr[n][int(uid.split('-')[1])].decode('cp932')==ja
    assert sum(measured(v[-1]) for v in ref)==mf['summary']['reference_characters']
    assert all(x['evidence_ids'] and all(uid in by_id for uid in x['evidence_ids']) for x in read(kit/'glossary.json')['entries'])
    assert all(x['evidence_ids'] and all(uid in by_id for uid in x['evidence_ids']) for x in read(kit/'character_voice.json')['characters'])
    return mf['summary']


def main():
    import tempfile
    if DEST.exists():
        raise FileExistsError(f'Existing handoff retained: {DEST}')
    sample_ids = {n for specs in SAMPLES.values() for n,_,_ in specs}
    main_scenes = {n:get_scene('R',n,RJ/'scr.xfl') for n in sorted(sample_ids)}
    parent = (ROOT/'tmp').resolve(strict=True)
    summaries = []
    with tempfile.TemporaryDirectory(prefix='gemini_scenario_',dir=parent) as d:
        stage = Path(d).resolve(strict=True)
        assert stage.parent==parent and stage.name.startswith('gemini_scenario_')
        payload = stage/'deliver'
        for game,(_,short,_) in WORKS.items():
            summary = prepare_game(payload,game,main_scenes)
            target = payload/short
            assert validate(target,game)==summary
            compact_work(target)
            name = f'{short}_제미나이_번역의뢰.zip'
            archive = payload/name
            packed = sorted(f for f in target.rglob('*') if f.is_file())
            with ZipFile(archive,'x',compression=ZIP_DEFLATED,compresslevel=6) as z:
                for p in packed:
                    z.write(p, p.relative_to(target).as_posix())
            with ZipFile(archive,'r') as z:
                assert z.testzip() is None
                assert z.namelist()==[p.relative_to(target).as_posix() for p in packed]
                assert all(digest(z.read(p.relative_to(target).as_posix()))==file_hash(p) for p in packed)
            summary = dict(summary,zip=name,zip_sha256=file_hash(archive))
            summaries.append(summary)
        assert DEST.resolve().parent==ROOT.resolve() and payload.resolve().parent==stage
        payload.rename(DEST)
    # Preserve earlier UI/CG/movie records and append only the handoff stage.
    record = ROOT/'progress.json'
    current = json.loads(record.read_text('utf-8-sig'))
    current['scenario_gemini_handoff'] = {'location':str(DEST),'state':'작품별 의뢰 자료 준비 및 검증 완료','external_submission':False,
                                          'next':'Gemini 해석표, 화자 표기와 묶음별 응답을 받으면 ID·제어 코드와 해당 일본어 원문 대조.',
                                          'works':summaries}
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=ROOT/'tmp',prefix='handoff_progress_',suffix='.json',delete=False) as f:
        json.dump(current,f,ensure_ascii=False,indent=1)
        f.write('\n')
        temp_path = Path(f.name)
    assert temp_path.resolve().parent==parent
    temp_path.replace(record)
    print(json.dumps(summaries,ensure_ascii=False,indent=1))


if __name__=='__main__':
    main()


"""Compact the presentation of a verified Japanese scenario handoff. Keep canonical review data."""
import hashlib
import json
import re
from pathlib import Path

from tools.restore_scenario_ids import restore

FIRST = '01_작품원문과_첫요청.txt'
REF = '02_레퀴엠_발췌.txt'
RESTART = '03_새대화용_공통지침.txt'
RESTORER = '검수자료/응답_ID_복원.py'
OLD_HEADER = 'ID\t종류\t원문 화자 표시\t선택 구간\t일본어 원문'
HEADER = '번호\t[화자 또는 줄 표시]\t일본어 원문'
OLD_ROW = re.compile(r'^([ESR]\d{4})-(\d{5})\t')
SCENE = re.compile(r'^\[([ESR]\d{4})(?:\s.*)?\]$')
OLD_SCENE = re.compile(r'^\[(\d{4})  (.+)\]$')
OLD_REF = re.compile(r'^\[레퀴엠 (\d{4})  (.+)  /  R(\d{4})-(\d{5}) ~ R(\d{4})-(\d{5})\]$')
CHOICE = re.compile(r'^(?:선택문|보기[1-5])$')
SECTIONS = {'[번역 대상]', '[요청]', '[직전 문맥 · 참고]', '[직후 문맥 · 참고]', '[이 장면 선택지 · 참고]'}
BRANCHES = {'[선택1]': '선택1', '[선택2]': '선택2', '[합류 뒤]': '합류 뒤', '[공통]': ''}
GUIDE_DIR = '검수자료/gemini'


def get(path):
    return path.read_bytes().decode('utf-8')


def put(path, text):
    path.write_bytes(text.encode('utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    put(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'기존 문구를 한 번만 찾을 수 있어야 합니다: {old[:60]}')
    return text.replace(old, new, 1)


def fields_tag(kind, name):
    if kind == '무표기' and name == '—':
        return None
    if kind == '발화' and name != '—':
        if name.startswith(('+', '@')) or CHOICE.fullmatch(name):
            return '@' + name
        return name
    if kind == '이어쓰기':
        return '+' + ('' if name == '—' else name)
    if CHOICE.fullmatch(kind) and name == '—':
        return kind
    raise ValueError(f'지원하지 않는 줄 표기: {kind} {name}')


def decode_rows(text):
    scene, branch = None, ''
    rows = []
    for line in text.split('\n'):
        line = line.removesuffix('\r')
        if line in SECTIONS:
            scene, branch = None, ''
        elif match := SCENE.fullmatch(line):
            scene, branch = match[1], ''
        elif line in BRANCHES:
            if scene is None:
                raise ValueError(f'장면 없는 분기: {line}')
            branch = BRANCHES[line]
        elif re.match(r'^\d+\t', line):
            if scene is None:
                raise ValueError('번호가 있는 행에 장면 제목이 없습니다.')
            parts = line.split('\t')
            if len(parts) == 2:
                slot, ja = parts
                kind, speaker = '무표기', '—'
            elif len(parts) == 3:
                slot, tag, ja = parts
                if tag.startswith('+'):
                    kind, speaker = '이어쓰기', tag[1:] or '—'
                elif CHOICE.fullmatch(tag):
                    kind, speaker = tag, '—'
                else:
                    kind, speaker = '발화', tag.removeprefix('@')
            else:
                raise ValueError(f'{scene}: 탭 열 개수 오류')
            rows.append([f'{scene}-{int(slot):05d}', kind, speaker, branch or '—', ja])
    return rows


def compact_rows(old, prefix):
    scene, branch = None, ''
    output, original = [], []
    for src in old.split('\n'):
        line = src.removesuffix('\r')
        if match := OLD_ROW.match(line):
            full_id, kind, name, raw_branch, ja = line.split('\t')
            original.append([full_id, kind, name, raw_branch, ja])
            if match[1][0] != prefix:
                raise ValueError(f'다른 작품 ID: {full_id}')
            if scene != match[1]:
                scene, branch = match[1], ''
                output.append(f'[{scene}]')
            next_branch = '' if raw_branch == '—' else raw_branch
            if next_branch != branch:
                mark = '[' + (next_branch or '공통') + ']'
                if mark not in BRANCHES:
                    raise ValueError(f'알 수 없는 분기: {mark}')
                output.append(mark)
                branch = next_branch
            tag = fields_tag(kind, name)
            cols = [str(int(match[2]))]
            if tag is not None:
                cols.append(tag)
            cols.append(ja)
            output.append('\t'.join(cols))
        elif match := OLD_SCENE.fullmatch(line):
            scene, branch = prefix + match[1], ''
            output.append(f'[{scene}  {match[2]}]')
        elif match := OLD_REF.fullmatch(line):
            if not (prefix == 'R' and match[1] == match[3] == match[5]):
                raise ValueError(f'발췌 범위 불일치: {line}')
            scene, branch = 'R' + match[1], ''
            output.append(f'[{scene}  {match[2]}  /  {int(match[4])}~{int(match[6])}]')
        else:
            if line in SECTIONS:
                scene, branch = None, ''
            output.append(HEADER if line == OLD_HEADER else src)
    converted = '\n'.join(output)
    if not original or decode_rows(converted) != original:
        raise ValueError('장면/번호/화자/분기/원문 왕복 불일치')
    return converted


def new_rules(text, example):
    legacy = '열 순서는 ID, 줄 종류, 화면의 일본어 화자명, 선택 구간, 원문입니다. —는 해당 표시가 없다는 뜻입니다.'
    fr = example['ids'][0]
    scene, slot = fr.split('-')
    legend = (f'장면 머리의 {scene}와 줄 번호 {int(slot)}을 합치면 검수 ID {fr}입니다. '
              '두 열은 번호·무표기 원문, 세 열은 번호·화자·원문입니다. 가운데 +는 이어쓰기이며 뒤의 이름은 원래 화자입니다. '
              '가운데 선택문·보기1·보기2 등은 선택지입니다. [선택1]·[선택2]·[합류 뒤]·[공통]은 다음 표시나 장면까지 적용됩니다.')
    text = once(text, legacy, legend)
    old_format = 'JSON 하나에 packet, lines, issues를 넣으세요. lines의 항목은 {"id":"게임의 실제 ID","ko":"완성된 한국어"}입니다.'
    new_format = (f'JSON 형식은 {{"packet":"{example["packet"]}","scenes":{{"{scene}":[[{int(slot)},"번역문"]]}},"issues":[]}}입니다. '
                  '각 장면에 [숫자, 한국어] 쌍을 원래 순서로 넣으세요. '
                  'issues와 해석표의 근거는 장면을 포함한 전체 검수 ID로 적으세요.')
    return once(text, old_format, new_format)


def compact_work(work):
    review = work/'검수자료'
    kit = work/GUIDE_DIR
    mf = json.loads(get(kit/'manifest.json'))
    if mf['version'] != 1:
        raise ValueError(f'기준 자료는 v1이어야 합니다: {work}')
    index_path = review/'packet_index.json'
    idx = json.loads(get(index_path))
    packets = {p['packet']: p['ids'] for p in idx['packets']}
    sample = idx['packets'][0]
    prefix = sample['packet'][0]
    touched = set()
    def original(name):
        path = work/name
        if sha(path) != mf['files_sha256'][name]:
            raise ValueError(f'기존 자료가 변경됐습니다: {name}')
        return get(path)
    def save(name, value):
        put(work/name, value)
        touched.add(name)

    first = original(FIRST)
    pre, body = first.split('# 일본어 원문\n', 1)
    story, tail = body.rsplit('# 첫 요청\n', 1)
    new_pre = new_rules(pre, sample)
    compact_story = compact_rows(story, prefix)
    rows = [json.loads(line) for line in (review/'catalog.jsonl').read_bytes().splitlines()]
    expected = [[r['id'],r['kind'],r['speaker'] or '—',r['branch'] or '—',r['ja']] for r in rows]
    if decode_rows(compact_story) != expected:
        raise ValueError('작품 원문과 검수 목록 불일치')
    save(FIRST, new_pre + '# 일본어 원문\n' + compact_story + '# 첫 요청\n' + tail)
    reference = compact_rows(original(REF), 'R')
    reference = once(reference, '각 줄의 R 번호로 원문을 다시 찾을 수 있습니다.', 'R 장면 번호와 각 줄 번호로 원문을 다시 찾을 수 있습니다.')
    save(REF, reference)

    restart = new_pre[new_pre.index('당신은 일본어'):new_pre.index('# 번역 묶음과 대상 범위')]
    restart += new_pre[new_pre.index('# 공통 한국어 번역 기준\n'):]
    restart = once(restart, '먼저 이 작품의 대본 전체를 읽으세요.', '이 작품의 통독을 마친 뒤 새 대화에서 쓰는 지침입니다. 첨부된 해석표와 해당 묶음을 사용하세요.')
    save(RESTART, restart.rstrip('\n') + '\n')

    all_ids = []
    for p in idx['packets']:
        data = compact_rows(original(p['file']), prefix)
        targets = data.split('\n[번역 대상]\n', 1)[1].split('\n[요청]\n', 1)[0]
        returned = decode_rows(targets)
        if [row[0] for row in returned] != p['ids']:
            raise ValueError(f'{p["packet"]}: 대상 ID 불일치')
        all_ids.extend(p['ids'])
        # Check scene-local slots against a representative return for this actual packet.
        groups = {}
        for uid, *_ in returned:
            scene, slot = uid.split('-')
            groups.setdefault(scene, []).append([int(slot), uid])
        replay = restore({'packet':p['packet'],'scenes':groups,'issues':[]}, packets)
        if [r['ko'] for r in replay['lines']] != p['ids']:
            raise ValueError(f'{p["packet"]}: 번역 응답 ID 복원 불일치')
        save(p['file'], data)
        p['sha256'] = sha(work/p['file'])
    if all_ids != [r['id'] for r in rows]:
        raise ValueError('번역 묶음 전체 범위 불일치')
    dump(index_path, idx)
    touched.add('검수자료/packet_index.json')

    style = GUIDE_DIR + '/translation_instructions.md'
    text = new_rules(original(style), sample)
    save(style, once(text, REF + '  ' + mf['files_sha256'][REF], REF + '  ' + sha(work/REF)))
    manual = original('사용법.txt')
    start = manual.index('3. 새 대화')
    end = manual.index('\n4. ', start)
    manual = manual[:start] + ('3. 통독 후 새 대화로 옮길 때는 03_새대화용_공통지침.txt, 보관한 해석표와 현재 묶음 TXT를 보내세요. '
             '그 대화에서는 지침과 해석표를 한 번만 첨부하세요. 필요한 본편 장면은 02 파일에서 골라 보낼 수 있습니다.') + manual[end:]
    manual = once(manual, '검수자료 폴더는 로컬 원문 대조용입니다.',
                  '검수자료 폴더는 로컬 원문 대조용입니다. 각 줄의 짧은 번호는 장면별로 관리하며, 검수 때 응답_ID_복원.py로 전체 ID를 복원합니다.')
    save('사용법.txt', manual)
    (work/RESTORER).write_bytes(Path(__file__).with_name('tools').joinpath('restore_scenario_ids.py').read_bytes())
    touched.add(RESTORER)

    mf.update(schema='fairytale-gemini-handoff-v2',version=2,style_guide_sha256=sha(work/style),
              presentation='scene prefix once, numeric slot, sparse type/speaker, branch sections',
              response_format='packet + scenes grouped by scene ID with [slot,ko] pairs; canonical v1 lines also accepted',
              validation='Every source row, reference row and packet context reconstructed with original ID, type, speaker, branch and text. All packet response IDs round-tripped.')
    for name in sorted(touched):
        mf['files_sha256'][name] = sha(work/name)
    dump(kit/'manifest.json', mf)
    return mf['summary']

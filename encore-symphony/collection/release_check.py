"""Check the shipped collection against the Korean game installations and their gallery tables."""
import json
import os
from PIL import Image
from album import remove_empty_vorbis_stream
from assemble import BASE, HERE, OUT, EXES, GAMES, digest, entry_map, jsonout, read_entry


def check_music_file(path):
    data = path.read_bytes()
    if path.suffix.lower() == '.ogg':
        assert data == remove_empty_vorbis_stream(data), f'{path.name} contains ACM padding'
    else:
        assert data[:4] == b'RIFF' and data[8:12] == b'WAVE', path.name


def archive_check(path, original):
    members = entry_map(original)
    assert set(entry_map(path)) == set(members)
    different = [n for n in members if read_entry(path, n) != read_entry(original, n)]
    assert different == ['0000.gsc'], (path, different)
    return {'members': len(members), 'changed': different}


def main():
    library = OUT / 'Library'
    catalog = json.loads((library / 'catalog.json').read_text(encoding='utf-8'))
    report = {'install': str(OUT), 'launcher_sha256': digest(OUT / '페어리테일 통합판.exe'), 'works': {}}
    pictures, music = set(), set()
    for work, original in GAMES.items():
        installed = OUT / 'Games' / work
        entries = OUT / 'Entries' / work
        native = original / 'scr.xfl'
        reference = HERE / 'qa' / 'entry-archives' / work
        assert read_entry(native, '0000.gsc') == (entries / 'native.gsc').read_bytes()
        assert digest(installed / EXES[work]) == digest(original / EXES[work])
        archive_results = {}
        for p in sorted(reference.glob('*.xfl')):
            archive_results[p.stem] = archive_check(p, native)
            assert read_entry(p, '0000.gsc') == (entries / (p.stem + '.gsc')).read_bytes()
        original_scenes = [n for n in entry_map(native) if n != '0000.gsc']
        assert all(read_entry(installed / 'scr.xfl', n) == read_entry(native, n) for n in original_scenes)
        saves = [p for p in (original / 'save').iterdir() if p.is_file()]
        copied = []
        for source in saves:
            dst = installed / 'save' / source.name
            assert dst.is_file() and not os.path.samefile(dst, source)
            copied.append({'name': source.name, 'initial_bytes_match': digest(source) == digest(dst)})
        group = catalog[work]
        variants = [v for g in group['cg'] for v in g['variants']]
        pictures.update(v['image'] for v in variants)
        music.update(t['audio'] for t in group['music'])
        movie_checks = []
        for item in group['movies']:
            if item['kind'] == 'native':
                assert item['id'] == 'credits' and (entries / 'credits.gsc').is_file()
                continue
            filename = item['id'] + '.mpg'
            source = original / 'mov' / filename
            published = OUT / 'Cinema' / work / filename
            assert source.is_file() and published.is_file()
            assert os.path.samefile(source, published) or digest(published) == digest(source)
            if item['id'] != '0001':
                assert (installed / 'mov' / filename).is_file()
            movie_checks.append(filename)
        assert not any((installed / 'mov' / f).exists() for f in ('0001.mpg', '0002.mpg'))
        report['works'][work] = dict(entries=archive_results, native_archive_sha256=digest(native), independent_save_files=copied,
            cg_groups=len(group['cg']), cg_variants=len(variants), native_music_slots=len(group['music']),
            gallery_mpeg=movie_checks, native_credits=any(m['kind']=='native' for m in group['movies']))
    media = library / 'media'
    for stem in pictures:
        with Image.open(media / (stem + '.png')) as picture:
            assert picture.width > 0 and picture.height > 0
            picture.verify()
        with Image.open(media / (stem + '-s.jpg')) as picture:
            picture.verify()
    for filename in music:
        check_music_file(media / filename)
    report['unique_full_size_cg'] = len(pictures)
    report['unique_music'] = len(music)
    report['references'] = [
        'https://api.playnite.link/docs/manual/library/games/gameActions.html',
        'https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.workingdirectory',
        'https://www.liar.co.jp/fairy_symphony/'
    ]
    jsonout(HERE / 'release-check.json', report)
    print({w:(x['cg_groups'], x['cg_variants']) for w, x in report['works'].items()}, len(pictures), len(music))


if __name__ == '__main__':
    main()

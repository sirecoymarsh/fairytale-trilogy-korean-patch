import ctypes
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import psutil
import win32gui

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT))
import verify_hub as ui
from trial_game import U, windows, children, capture, home
from assemble import EXES

def check(ev, hit, wait, pid, photo):
    result = {'folder':str(ui.QA), 'fresh_profile':True, 'games':{}}
    result['menu'] = ev("Array.from(document.querySelectorAll('#title button'),b=>b.getAttribute('aria-label'))")
    assert '시작' in result['menu'] and set(ev("Object.keys(catalog)")) == set(EXES)
    photo('relocated-main')
    for work, label in [('Requiem','레퀴엠'),('Encore','앙코르'),('Symphony','심포니')]:
        target = ui.QA / 'Games' / work / EXES[work]
        hit("#title button[aria-label='시작']")
        wait("screen==='doors'")
        hit("#doors button[aria-label='" + label + "']")
        limit=time.monotonic()+18
        child=None
        game_window=None
        while time.monotonic()<limit:
            for process in psutil.Process(pid).children():
                if process.name()==EXES[work] and os.path.samefile(process.exe(),target):
                    child=process
                    game_window=home(process.pid)
                    break
            if game_window:break
            time.sleep(.2)
        assert game_window,(work,'no native window',ev("document.getElementById('notice').textContent"))
        time.sleep(8)
        image=capture(game_window)
        image.save(ui.EVID/('relocated-'+work+'.png'))
        assert image.size[0]>=640
        win32gui.PostMessage(game_window,0x10,0,0)
        limit=time.monotonic()+7
        while child.is_running() and time.monotonic()<limit:
            for h,kind,*_ in windows(child.pid):
                if kind=='#32770':
                    button=next((x[0] for x in children(h) if x[1]=='Button' and x[3] in (6,1)),None)
                    if button:win32gui.PostMessage(button,0xf5,0,0)
            time.sleep(.14)
        assert not child.is_running(),work
        wait("screen==='title' && !busy")
        result['games'][work]={'native_window':True,'returned':True,'size':image.size,'private_save_files':[p.name for p in (target.parent/'save').glob('*')]}
        print('RELOCATED',work,flush=True)
    (ui.EVID/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return 'completed'

def main():
    folder=HERE/'host'
    ui.EVID=HERE/'host-evidence'
    ui.EVID.mkdir(exist_ok=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    target='\\??\\'+str(folder)
    mounted=None
    for letter in ['T:','R:','U:','V:','Q:','W:','I:','J:']:
        buffer=ctypes.create_unicode_buffer(1024)
        if kernel.QueryDosDeviceW(letter,buffer,len(buffer)):continue
        if kernel.DefineDosDeviceW(9,letter,target):mounted=letter;break
    ui.QA=Path(mounted+'/Fairytale') if mounted else folder/'Fairytale'
    try:
        assert os.path.samefile(ui.QA,folder/'Fairytale')
        assert not (ui.QA/'User').exists()
        cmd="__import__('runpy').run_path("+repr(str(Path(__file__).resolve()))+")['check'](ev,hit,wait,pid,photo)"
        sys.stdin=io.StringIO(cmd+'\nend\n')
        with ThreadPoolExecutor(1) as pool:pool.submit(ui.run).result()
        assert (ui.EVID/'result.json').is_file()
    finally:
        if mounted: kernel.DefineDosDeviceW(15,mounted,target)

if __name__=='__main__': main()

"""Start the retail gallery routines in the isolated fixture, with identical mixed progress."""
from build_options import *
from menu_scripts import op,parse_gsc,MODE,READY
import time
def run(g,num,mode):
    d=QA/g;arc=BUILT/g/'scr.xfl';src=read_entry(arc,'0001.gsc')
    p=parse_gsc(src);assert p.command[0:2]==op(5,0)[:2]
    # Test-only entry point. All CG, replay, input and drawing scripts are the exact release bytes.
    data=bytearray(src);ln=p.header_length
    data[ln:ln+10]=op(12,num,0)
    archive(arc,d/'scr.xfl',{'0001.gsc':bytes(data)})
    sav=next((d/'save').glob('*save.dat'));b=bytearray(sav.read_bytes())
    struct.pack_into('<h',b,0x872+(MODE-7000)*2,mode);struct.pack_into('<h',b,0x872+(READY-7000)*2,1);sav.write_bytes(b)
    environ=os.environ.copy();environ['FAIRY_QA_SCREEN']=str(num)+'-'+str(mode)
    subprocess.run([sys.executable,'-B',str(HERE/'trial_game.py'),g,'gallery_screen.py'],env=environ,check=True)
def main():
    for g in sys.argv[1:] or GAMES:
        try:
            for n in (201,301):
                for mode in (0,1):run(g,n,mode)
        finally:
            # Restore release scripts in the isolated copy for any future input tests.
            s=QA/g/'scr.xfl';tmp=s.with_suffix('.qa-restore');os.link(BUILT/g/'scr.xfl',tmp);tmp.replace(s)
if __name__=='__main__':main()

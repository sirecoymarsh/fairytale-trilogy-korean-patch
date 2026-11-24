from assemble import *
from menu_scripts import READY,assign
def launch_entry(work,base,mode):
 name='0000.gsc';p=parse_gsc(read_entry(base,name));title=parse_gsc(read_entry(base,'0001.gsc'))
 assert p.command[-10:]==op(12,1,0)
 # Retain codeX bootstrap assignments and the edition's exact option registration/legacy mark migration.
 cmd=p.command[:-10]
 if work!='Requiem':
  first=parse_commands(title.command,FMT)[0];assert first.opcode==5
  start=first.args[0]
  seq=[c for c in parse_commands(title.command,FMT) if c.offset>=start]
  assert seq[0].raw==op(115,9,1)
  for c in seq:
   if c.opcode==5:
    assert c.args==(14,);break
   if c.opcode==3:cmd+=op(3,c.args[0]-start+28)
   else:cmd+=c.raw
 else:
  assert title.command[:14]==const(3,8);cmd+=title.command[:14]
 cmd+=const(821,0)+const(822,0)+const(814,0)+const(804,0)+const(803,0)
 if mode=='story':cmd+=op(12,500,0)
 elif mode=='replay':cmd+=op(15,301,*([0]*11))+op(12,1,0)
 elif mode=='credits' and work=='Symphony':cmd+=op(15,4000,*([0]*11))+op(12,1,0)
 else:raise ValueError(mode)
 h=list(p.header);delta=len(cmd)-h[2];h[0]+=delta;h[2]=len(cmd)
 built=struct.pack('<'+'I'*len(h),*h)+cmd+p.source[p.header_length+p.command_length:]
 assert parse_gsc(built).command==cmd
 return {name:built}
import struct
if __name__=='__main__':
 base=OUT/'Entries/Symphony/native.xfl'
 archive(base,HERE/'tmp'/'bootcheck.xfl',launch_entry('Symphony',base,'story'))


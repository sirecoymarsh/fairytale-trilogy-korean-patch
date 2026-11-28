"""Extend only the game's menu expressions and duplicate earned scene marks.
Original command addresses, string IDs, line numbers and all text bytes stay stable.
"""
from pathlib import Path
import struct, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assets import ROOT,RBASE,read,entry_map,read_entry
from gsc_codec import parse_gsc
from build_scenario_catalog import parse_commands
FMT={r['opcode']:(r['format'],r['name']) for r in read(RBASE/'adapter/command_formats.json')['commands']}
MODE,READY,PENDING,MANUAL,TEMPVAR=7988,7987,7986,7985,5937
FIRST=7910
def op(k,*args):
    fmt=FMT.get(k,('hh' if k>>12==15 else 'hhh',''))[0]
    return struct.pack('<H'+fmt,k,*args)
def const(var,val):return op(0x1800,1,var,val)+op(0xf100,0,1)
def assign(var,src):return op(0x1a00,1,var,src)+op(0xf100,0,1)
def truth(var):
    return op(0x9800,2,var,0)+op(0xf100,1,2)+op(0xf100,0,1)
def if_true(var,body,addr):
    cond=truth(var)
    return cond+op(3,addr+len(cond)+6+len(body))+body
def table_offset(p):
    length=p.header[5]
    return struct.unpack('<'+'I'*(length//4),p.trailing[:length])
def word_at(p,ix):return struct.unpack_from('<h',p.trailing,p.header[5]+2*ix)[0]
def pages(p,stride):
    for t in table_offset(p)[2:]:
        count=word_at(p,t)
        assert count%stride==0
        for row in range(0,count,stride):
            i=t+1+row
            values=[word_at(p,i+k) for k in range(stride)]
            if values[0]>=0:yield i,values
def catalog(game,archive):
    fetch=lambda n:parse_gsc(read_entry(archive,f'{n:04}.gsc'))
    cg=set(); images=set(); rows=0
    for _,v in pages(fetch(201),63):
        rows+=1
        for img,override in zip(v[3:33],v[33:63]):
            if img<0:continue
            assert 0<img<2000
            images.add(img)
            cg.add(override if override!=-1 else img+(9000 if img<1000 else 7000))
    scenes=[v[0] for _,v in pages(fetch(301),10)]
    specials=[7700,7713] if game=='Requiem' else [7713] if game=='Encore' else list(range(7511,7516))
    first=8300 if game=='Requiem' else FIRST
    shadow={key:first+n for n,key in enumerate(sorted(set(scenes+specials)))}
    assert max(shadow.values())<(8700 if game=='Requiem' else MANUAL) and all(8000<=k<10000 for k in cg)
    assert not set(shadow.values()).intersection(cg)
    return dict(shadow=shadow,cg=sorted(cg),images=sorted(images),groups=rows,scenes=len(scenes))
class Append:
    def __init__(self,p):
        self.p=p;self.buf=bytearray(p.command);self.original_size=len(self.buf)
        self.used=set();self.tail=bytearray(p.trailing)
    def replace(self,off,span,make):
        assert span>=6 and 0<=off<=self.original_size-span
        assert not self.used.intersection(range(off,off+span))
        self.used.update(range(off,off+span))
        start=len(self.buf)
        body=make(start)+op(5,off+span)
        self.buf[off:off+span]=op(5,start)+b'\0'*(span-6)
        self.buf.extend(body)
    def build(self):
        h=list(self.p.header);extra=len(self.buf)-h[2];h[0]+=extra;h[2]+=extra
        p=self.p
        data=struct.pack('<'+'I'*len(h),*h)+bytes(self.buf)+p.source[p.header_length+p.command_length:len(p.source)-len(p.trailing)]+bytes(self.tail)
        check=parse_gsc(data)
        assert p.strings==check.strings and p.offsets==check.offsets
        dec=parse_commands(check.command,FMT); bounds={c.offset for c in dec}|{len(check.command)}
        for c in dec:
            if c.opcode in (3,4,5) and c.args[0]>=0 and c.offset>=self.original_size:
                assert c.args[0] in bounds,(c.offset,c.args)
        return data
def script(game,n,data,cat):
    p=parse_gsc(data); cs=parse_commands(p.command,FMT); b=Append(p)
    sh=cat['shadow']; count={}; original=p.command
    def record(k):count[k]=count.get(k,0)+1
    def initialize(addr):
        condition=op(0x4800,2,READY,0)+op(0xf100,1,2)+op(0xf100,0,1)
        migration=b''.join(assign(dest,src) for src,dest in sh.items())+const(READY,1)
        return condition+op(3,addr+len(condition)+6+len(migration))+migration
    if n==1:
        def start(addr):
            setup=op(115,9,1)
            return setup+initialize(addr+len(setup))+original[:14]
        assert cs[0].args[:2]==(1,3) and cs[1].args==(0,1)
        b.replace(0,14,start);record('title_init')
    if n==301:
        for i,v in pages(p,10):
            struct.pack_into('<h',b.tail,p.header[5]+2*i,sh[v[0]])
        for c in cs:
            if c.opcode==0x1a01 and c.args==(1,36,35):
                off=c.offset;code=original[off:off+14]
                b.replace(off,14,lambda a:code+if_true(MODE,const(36,MODE),a+len(code)))
                record('replay_list')
    if n==201:
        for j,c in enumerate(cs):
            if c.opcode in (0x9810,0x4810) and c.args==(2,49,0):
                off=c.offset;code=original[off:off+20];assert cs[j+2].args==(0,1)
                b.replace(off,20,lambda a:if_true(MODE,const(49,MODE),a)+code)
                record('cg_cell_or_variant')
    if (game in ('Encore','Requiem') and n==1) or (game=='Symphony' and n==302):
        for j,c in enumerate(cs):
            if c.opcode==0x9800 and c.args[1] in sh and c.args[1] in ({7020,7713} if n==1 else set(range(7511,7516))):
                off=c.offset;end=j+1
                while cs[end].opcode!=0xf100 or cs[end].args[0]!=0:end+=1
                span=cs[end].offset+len(cs[end].raw)-off
                expr=bytearray(original[off:off+span])
                struct.pack_into('<h',expr,4,TEMPVAR)
                for old in cs[j+1:end]:
                    if old.opcode==0x4800 and old.args[1] in sh:
                        struct.pack_into('<h',expr,old.offset-off+4,sh[old.args[1]])
                prefix=assign(TEMPVAR,sh[c.args[1]])
                b.replace(off,span,lambda a:prefix+if_true(MODE,const(TEMPVAR,1),a+len(prefix))+expr)
                record('special_menu')
    if game=='Requiem' and n==401:
        for j,c in enumerate(cs):
            if c.opcode not in (0x4800,0x9800) or c.args[1]!=7700:continue
            off=c.offset;end=j+1
            while cs[end].opcode!=0xf100 or cs[end].args[0]!=0:end+=1
            span=cs[end].offset+len(cs[end].raw)-off
            expr=bytearray(original[off:off+span]);struct.pack_into('<h',expr,4,TEMPVAR)
            prefix=assign(TEMPVAR,sh[7700])
            b.replace(off,span,lambda a,prefix=prefix,expr=expr:prefix+if_true(MODE,const(TEMPVAR,1),a+len(prefix))+expr)
            record('music_menu')
    for j,c in enumerate(cs):
        if c.opcode in (0x1800,0x1a00) and c.args[1] in sh:
            assert c.args[0]==1 and cs[j+1].opcode==0xf100 and cs[j+1].args==(0,1)
            off=c.offset;src=c.args[1]; body=original[off:off+14]+assign(sh[src],src)
            b.replace(off,14,lambda a:body);record('earned_scene')
    if not count:return data,{}
    return b.build(),count

"""Reuse native title menus, returning to the common castle on menu exit."""
from collection_core import parse_gsc, read_entry, parse_commands, FMT, op
import struct

def native_menu(bank):
    original = parse_gsc(read_entry(bank,'0001.gsc'))
    command = bytearray(original.command)
    instructions = parse_commands(command,FMT)
    case = next(i for i,c in enumerate(instructions) if c.opcode==0x4800 and c.args==(2,811,5))
    end = next(i for i in range(case+1,len(instructions)) if instructions[i].opcode==0x4800 and instructions[i].args[1]==811)
    returns = [c for c in instructions[case:end] if c.opcode==5]
    assert len(returns)==1 and returns[0].args==(158,)
    # Redirect only the native settings screen's return. Original branches retain their offsets.
    struct.pack_into('<i',command,returns[0].offset+2,len(command))
    command.extend(op(12,1,0))
    header=list(original.header);header[0]+=len(command)-header[2];header[2]=len(command)
    tail=original.source[original.header_length+original.command_length:]
    data=struct.pack('<'+'I'*len(header),*header)+bytes(command)+tail
    assert parse_gsc(data).command==command
    return data

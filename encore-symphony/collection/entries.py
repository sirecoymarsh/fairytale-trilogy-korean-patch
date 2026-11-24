"""Build collection entry archives without changing scene text or title-screen behavior."""
import struct
from assemble import EXES, GAMES, HERE, OUT, FMT, archive, const, op, parse_commands, parse_gsc, read_entry


def launch_entry(work, base, mode):
    boot = parse_gsc(read_entry(base, '0000.gsc'))
    title = parse_gsc(read_entry(base, '0001.gsc'))
    native_title = op(12, 1, 0)
    assert boot.command.endswith(native_title)
    command = bytearray(boot.command[:-len(native_title)])

    if work == 'Requiem':
        assert title.command.startswith(const(3, 8))
        command.extend(const(3, 8))
    else:
        # The Korean title first registers the edition's options and migrates older save flags.
        # Reuse its exact setup and relocate its branches, leaving the normal title untouched.
        instructions = parse_commands(title.command, FMT)
        assert instructions[0].opcode == 5
        start = instructions[0].args[0]
        prefix = len(command)
        setup = [step for step in instructions if step.offset >= start]
        assert setup[0].raw == op(115, 9, 1)
        for step in setup:
            if step.opcode == 5:
                assert step.args == (14,)
                break
            if step.opcode == 3:
                command.extend(op(3, prefix + step.args[0] - start))
            else:
                command.extend(step.raw)
        else:
            raise ValueError('Korean option initialization has no return to the native title')

    for index in (821, 822, 814, 804, 803):
        command.extend(const(index, 0))
    if mode == 'story':
        command.extend(op(12, 500, 0))
    elif mode == 'replay' or (mode == 'credits' and work == 'Symphony'):
        entry = 301 if mode == 'replay' else 4000
        command.extend(op(15, entry, *([0] * 11)) + native_title)
    else:
        raise ValueError((work, mode))

    header = list(boot.header)
    header[0] += len(command) - header[2]
    header[2] = len(command)
    tail = boot.source[boot.header_length + boot.command_length:]
    built = struct.pack('<' + 'I' * len(header), *header) + bytes(command) + tail
    assert parse_gsc(built).command == command
    return {'0000.gsc': built}


def main():
    for work in EXES:
        directory = OUT / 'Entries' / work
        base = GAMES[work] / 'scr.xfl'
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'native.gsc').write_bytes(read_entry(base, '0000.gsc'))
        reference = HERE / 'qa' / 'entry-archives' / work
        modes = ['story', 'replay']
        if work == 'Symphony':
            modes.append('credits')
        for mode in modes:
            changes = launch_entry(work, base, mode)
            (directory / (mode + '.gsc')).write_bytes(changes['0000.gsc'])
            archive(base, reference / (mode + '.xfl'), changes)
        print(work, 'entries ready', flush=True)


if __name__ == '__main__':
    main()

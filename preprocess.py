#!/usr/bin/python
import sys
from process import ProcessMKV, ProcessFFMPEG


def ProcessClean(b, u, t, f, x, d):
    run = 1
    if d['Format'] == 'MPEG-4':
        result = ProcessFFMPEG(b, u, t, f, x + '.mkv', d, 0)
        if result is None:
            d['Format'] = 'Matroska'
            run = 2
            del result
        else:
            sys.stdout.write(
                'Something went wrong converting ' +
                f +
                ' to Matroska\n'
            )
            sys.exit(1)

    if d['Format'] == 'Matroska':
        v = d['V_StreamOrder']
        a = d['A_StreamOrder']

        if run == 1:
            result = ProcessMKV(b, u, t, f, x + '.clean.mkv', v, a)

        if run == 2:
            f = x + '.mkv'
            result = ProcessMKV(b, t, t, x + '.mkv', x + '.clean.mkv', v, a)

        if result == 0:
            return result
        else:
            sys.stdout.write(
                'Something went wrong cleaning ' +
                f +
                '\n'
            )
            sys.exit(1)

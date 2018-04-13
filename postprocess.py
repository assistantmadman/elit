#!/usr/bin/python
from info import GetMediaInfo


def SanityCheck(b, t, d, f):
    print('Sanity Check')
    n = GetMediaInfo(b, t, f)
    result = False

    if n['Duration'] == d['Duration']:
        result = True
    if n['FrameCount'] == d['FrameCount']:
        result = True
    if n['Format'] == 'MPEG-4':
        result = True
    if n['FileSize'] < d['FileSize']:
        result = True
    return result

#!/usr/bin/python
import re
import string
from info import GetMediaInfoOld


def BuildDictionary(b, u, f):
    d = {
        'title': '',
        'year': '',
        'container': '',
        'fCount': '',
        'vTrack': '',
        'vFormat': '',
        'vRes': '',
        'aTrack': '',
        'aCodec': '',
        'aLang': ''
    }

    # Get movie title and year from filename
    fdate = re.findall('\d\d\d\d', f)

    for n in range(len(fdate)):
        if fdate[n] not in ['1080', '2160']:
            d['year'] = fdate[n]
        else:
            break
    fsplit = f.split(d['year'])

    ftitle = fsplit[0]

    for char in string.punctuation:
        ftitle = ftitle.replace(char, ' ')

    d['title'] = ftitle.strip()

    # Start building dictionary from mediainfo using info.py
    # General media file attributes
    v = GetMediaInfoOld(
        b,
        u,
        '--Inform="General;%Format%"',
        f
    )
    d['container'] = v.decode('utf-8')

    v = GetMediaInfoOld(
        b,
        u,
        '--Inform="Video;%FrameCount%"',
        f
    )
    d['fCount'] = v.decode('utf-8')

    # Video track attributes
    v = GetMediaInfoOld(
        b,
        u,
        '--Inform="Video;%ID% %Format% %Width%"',
        f
    )
    v2 = v.decode('utf-8')
    d['vTrack'], d['vFormat'], d['vRes'] = v2.split(' ', 2)

    # Audio Track attributes
    v = GetMediaInfoOld(
        b,
        u,
        '--Inform="Audio;%ID%:%Codec%:%Language%!"',
        f
    )
    v2 = v.decode('utf-8')
    v3 = []
    v3 = v2.split('!')

    # Do we have more than one audio Track
    if len(v3) > 1:
        a_tracks = {}
        found = False
        for a in range(len(v3)):
            if v3[a].endswith(':'):
                v3[a] = v3[a] + 'none'
            if len(v3[a]) > 0:
                v3_id, v3_codec, v3_lang = v3[a].split(':', 2)
            else:
                continue

            if v3_lang == 'en':
                a_tracks[v3_id] = [v3_codec, v3_lang]

        for k in a_tracks:
            found = False

            if a_tracks[k][0] == 'AC3':
                found = True
                d['aTrack'], d['aCodec'], d['aLang'] = k, a_tracks[k][0], a_tracks[k][1]

        if found is False:
            if v3[0].endswith(':'):
                v3[0] = v3[0] + 'none'
            d['aTrack'], d['aCodec'], d['aLang'] = v3[0].split(':', 2)
    else:
        if v3.endswith(':'):
            v2 = v2 + 'none'
        d['aTrack'], d['aCodec'], d['aLang'] = v3[0].split(':', 2)

    return d

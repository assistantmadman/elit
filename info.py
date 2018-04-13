#!/usr/bin/python
import os
import subprocess
import sys
import re
import string
import xml.etree.ElementTree as ET
import tmdbsimple as tmdb
from imdbpie import Imdb


def GetMediaInfo(b, u, f):
    lang = 'en'

    cmd = [
        os.path.join(b, 'mediainfo'),
        '--Language=raw',
        '--Output=XML',
        os.path.join(u, f)
    ]

    process = subprocess.check_output(cmd)

    root = ET.fromstring(process.strip())

    result = {
        'ref': '',
        'Title': '',
        'Year': '',
        'VideoCount': '',
        'AudioCount': '',
        'MenuCount': '',
        'Format': '',
        'FileSize': '',
        'Duration': '',
        'FrameRate': '',
        'FrameCount': '',
        'V_StreamOrder': '',
        'V_ID': '',
        'V_Format': '',
        'V_BitRate': '',
        'V_Width': '',
        'A_StreamOrder': '',
        'A_ID': '',
        'A_Format': '',
        'A_BitRate': '',
        'A_BitDepth': '',
        'A_Language': ''
    }
    # Get movie title and year from filename
    fdate = re.findall('\d\d\d\d', f)

    for n in range(len(fdate)):
        if fdate[n] not in ['1080', '2160']:
            result['Year'] = fdate[n]
        else:
            break
    fsplit = f.split(result['Year'])

    ftitle = fsplit[0]

    for char in string.punctuation:
        ftitle = ftitle.replace(char, ' ')

    result['Title'] = ftitle.strip()

    a_loop = 0
    a_dict = {}
    found = False
    for t in root:
        if t.tag == '{https://mediaarea.net/mediainfo}media':
            media = t
            result['ref'] = os.path.basename(t.attrib['ref'])
    for t in media:
        if t.attrib['type'] == 'General':
            for c in t:
                if c.tag == '{https://mediaarea.net/mediainfo}VideoCount':
                    result['VideoCount'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}AudioCount':
                    result['AudioCount'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}MenuCount':
                    result['MenuCount'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}Format':
                    result['Format'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}FileSize':
                    result['FileSize'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}Duration':
                    result['Duration'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}FrameRate':
                    result['FrameRate'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}FrameCount':
                    result['FrameCount'] = c.text
        if t.attrib['type'] == 'Video':
            for c in t:
                if c.tag == '{https://mediaarea.net/mediainfo}StreamOrder':
                    result['V_StreamOrder'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}ID':
                    result['V_ID'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}Format':
                    result['V_Format'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}BitRate':
                    result['V_BitRate'] = c.text
                if c.tag == '{https://mediaarea.net/mediainfo}Width':
                    result['V_Width'] = c.text
        if t.attrib['type'] == 'Audio':
            if int(result['AudioCount']) > 1:
                iter = 'A_Track' + str(a_loop)
                iter_dict = {
                    'A_StreamOrder': '',
                    'A_ID': '',
                    'A_Format': '',
                    'A_BitRate': '',
                    'A_BitDepth': '',
                    'A_Language': ''
                }
                for c in t:
                    if c.tag == '{https://mediaarea.net/mediainfo}StreamOrder':
                        iter_dict['A_StreamOrder'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}ID':
                        iter_dict['A_ID'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}Format':
                        iter_dict['A_Format'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}BitRate':
                        iter_dict['A_BitRate'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}BitDepth':
                        iter_dict['A_BitDepth'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}Language':
                        iter_dict['A_Language'] = c.text
                a_dict[iter] = iter_dict
                a_loop = a_loop + 1
            elif int(result['AudioCount']) == 1:
                for c in t:
                    if c.tag == '{https://mediaarea.net/mediainfo}StreamOrder':
                        result['A_StreamOrder'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}ID':
                        result['A_ID'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}Format':
                        result['A_Format'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}BitRate':
                        result['A_BitRate'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}BitDepth':
                        result['A_BitDepth'] = c.text
                    if c.tag == '{https://mediaarea.net/mediainfo}Language':
                        result['A_Language'] = c.text
            else:
                print('Error: No audio tracks found')
                sys.exit(1)
    if len(a_dict) > 0:
        for k, v in a_dict.items():
            if v['A_Language'] == lang:
                if v['A_Format'] == 'AC-3':
                    result['A_StreamOrder'] = v['A_StreamOrder']
                    result['A_ID'] = v['A_ID']
                    result['A_Format'] = v['A_Format']
                    result['A_BitRate'] = v['A_BitRate']
                    result['A_BitDepth'] = v['A_BitDepth']
                    result['A_Language'] = v['A_Language']
                    found = True
                    break
                if found is False:
                    result['A_StreamOrder'] = v['A_StreamOrder']
                    result['A_ID'] = v['A_ID']
                    result['A_Format'] = v['A_Format']
                    result['A_BitRate'] = v['A_BitRate']
                    result['A_BitDepth'] = v['A_BitDepth']
                    result['A_Language'] = v['A_Language']
                    found = True
            if found is False:
                # Figure out how to make this work properly
                if result['A_Language'] == '':
                    result['A_StreamOrder'] = v['A_StreamOrder']
                    result['A_ID'] = v['A_ID']
                    result['A_Format'] = v['A_Format']
                    result['A_BitRate'] = v['A_BitRate']
                    result['A_BitDepth'] = v['A_BitDepth']
                    result['A_Language'] = 'none'
                    found = True
            if found is False:
                break
    return result


def GetMediaInfoOld(b, u, i, f):
    cmd = [
        os.path.join(b, 'mediainfo'),
        '--Language=raw',
        i,
        os.path.join(u, f)
    ]
    cmd[2] = cmd[2].replace('"', '')
    process = subprocess.check_output(cmd)
    result = process.strip()
    return result


def GetMeta(t, y):
    tmdb.API_KEY = 'b888b64c9155c26ade5659ea4dd60e64'
    search = tmdb.Search()
    search.movie(query=t)
    for s in search.results:
        year = s['release_date'].split('-', 2)
        if year[0] == y:
            d = s
            state = True
            break
        else:
            state = False

    imdb = Imdb()
    results = imdb.search_for_title(t)
    if state is True:
        for i in results:
            if i['type'] == 'feature' and i['year'] == y:
                result = i
                g = imdb.get_title_genres(result['imdb_id'])
                d['genre_ids'] = g['genres']
                break
            else:
                d['genre_ids'] = ''
        return d
    else:
        d = {}
        return d

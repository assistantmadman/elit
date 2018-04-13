#!/usr/bin/python
import os
import sys
import shlex
import subprocess
import pexpect
from datetime import datetime
from utilities import ProgressBar


def ProcessMKV(b, u, t, f, x, v, a):
    cmd = (
        os.path.join(b, 'mkvmerge') +
        ' --quiet'
        ' --output ' +
        shlex.quote(os.path.join(t, x)) +
        ' --audio-tracks ' +
        a +
        ' --video-tracks ' +
        v +
        ' --no-subtitles' +
        ' --no-attachments' +
        ' --no-global-tags' +
        ' --default-track ' +
        v +
        ' --default-track ' +
        a +
        ' ' + shlex.quote(os.path.join(u, f))
    )

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        shell=True
        )
    return process.returncode


def ProcessFFMPEGOld(b, u, t, f, x, p):
    if p == 0:
        cmd = (
            os.path.join(b, 'ffmpeg') +
            ' -i ' +
            shlex.quote(os.path.join(u, f)) +
            ' -loglevel error' +
            ' -c copy ' +
            shlex.quote(os.path.join(t, x))
        )
    if p == 1:
        cmd = (
            os.path.join(b, 'ffmpeg') +
            ' -i ' +
            shlex.quote(os.path.join(u, f)) +
            ' -loglevel info' +
            ' -movflags +faststart' +
            ' -map_metadata -1'
            ' -ss 0 -t 120' +
            ' -profile:v high' +
            ' -level 4.2' +
            ' -c:a ac3 ' +
            shlex.quote(os.path.join(t, x))
        )
    process = subprocess.run(
        cmd,
        check=True,
        shell=True
    )

    return process.returncode


def ProcessFFMPEG(b, u, t, f, x, d, p):
    if p == 0:
        cmd = (
            os.path.join(b, 'ffmpeg') +
            ' -i ' +
            shlex.quote(os.path.join(u, f)) +
            ' -loglevel error' +
            ' -c copy ' +
            shlex.quote(os.path.join(t, x))
        )
    if p == 1:
        cmd = (
            os.path.join(b, 'ffmpeg') +
            ' -i ' +
            shlex.quote(os.path.join(u, f)) +
            ' -loglevel info' +
            ' -movflags +faststart' +
            ' -map_metadata -1'
            # ' -ss 0 -t 120' +  # Uncomment if in test mode
            ' -profile:v high' +
            ' -level 4.2' +
            ' -c:a ac3 ' +
            shlex.quote(os.path.join(t, x))
        )
    time_now = datetime.now()
    process = pexpect.spawn(cmd)

    cpl = process.compile_pattern_list([
        pexpect.EOF,
        'frame= *\d+',
        '(.+)'
    ])

    while True:
        i = process.expect_list(cpl, timeout=None)
        if i == 0:
            break
        elif i == 1:
            frame = process.match.group(0)

            a = frame.decode('utf-8').split('=', 1)
            e = int(a[1])
            r = int(d['FrameCount'])
            # r = int(float(d['FrameRate'])) * 120  # Uncomment if in test mode

            ProgressBar(
                e,
                r,
                status='Time: ' + str(
                    datetime.now() - time_now
                ) + 'Processing: ' + d['Title']
            )
            sys.stdout.flush()
            process.close
        elif i == 2:
            # unknown_line = thread.match.group(0)
            # print unknown_line
            pass
    sys.stdout.write('\n')
    return process.exitstatus


def ProcessMP4BOX(b, u, t, f, x, p):
    if p == 0:
        cmd = (
            os.path.join(b, 'MP4Box') +
            ' -raw 1' +
            ' -raw 2' +
            ' -dump-chap ' +
            shlex.quote(os.path.join(u, f))
        )
    if p == 1:
        f_chap = shlex.quote(os.path.join(t, x + '.chap'))
        if os.stat(f_chap).st_size == 0:
            chap = ' '
        else:
            chap = ' -chap ' + f_chap + ' '
        cmd = (
            os.path.join(b, 'MP4Box') +
            ' -add ' +
            shlex.quote(os.path.join(t, x + '_track1.h264')) +
            ' -add ' +
            shlex.quote(os.path.join(t, x + '_track2.ac3')) +
            ' -lang 2=eng' +
            chap +
            shlex.quote(os.path.join(t, x + '.box.mp4'))
        )

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        shell=True
    )
    return process.returncode


def ProcessWriteMeta(b, t, f, i, d):
    g = ','.join(map(str, d['genre_ids']))

    cmd = (
        os.path.join(b, 'AtomicParsley') +
        ' ' +
        os.path.join(t, f) +
        ' --title "' + d['title'] + '"' +
        ' --genre "' + g + '"' +
        ' --comment "' + d['overview'] + '"' +
        ' --year "' + d['release_date'] + '"' +
        ' --artwork "' + os.path.join(t, i) + '"' +
        ' --stik value=9'
    )
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # check=True,
        shell=True
    )
    return process.returncode

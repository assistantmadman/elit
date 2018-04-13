#!/usr/bin/python
import os
import sys
import shutil
import datetime
import uuid
import urllib.request
import time


def GetDatetime():
    try:
        result = datetime.datetime.now()
    except Exception:
        sys.exit(1)
    return result


def DirList(u):
    r = []
    try:
        for f in os.listdir(u):
            if os.path.isfile(os.path.join(u, f)):
                r.append(f)
    except Exception:
        sys.exit(1)
    return r


def CreateUUID():
    try:
        str_uuid = uuid.uuid4()
    except Exception:
        sys.exit(1)
    return str_uuid


def CreateDir(n, p):
    os.chdir(p)
    # Is this name in use
    if os.path.exists(n):
        result = False
    else:
        os.makedirs(n)
        result = True
    return result


def MoveFile(t, c, f, z):
    shutil.move(
        os.path.join(t, f),
        os.path.join(c, z)
    )


def DeleteDir(t):
    shutil.rmtree(t)


def DownloadFile(t, x, u):
    urllib.request.urlretrieve(u, os.path.join(t, x + '.jpg'))


def ProgressBar(c, t, status=''):
    bar_len = 50
    filled_len = int(round(bar_len * c / float(t)))

    percents = round(100.0 * c / float(t), 1)
    bar = '\u2588' * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
    # sys.stdout.flush()

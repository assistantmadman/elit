#!/usr/bin/python
import os
import logging
import tempfile
import sys
from datetime import datetime
from conf_get import ConfGet
from info import GetMediaInfo, GetMeta
from utilities import DirList, CreateUUID, MoveFile, DownloadFile
from preprocess import ProcessClean
from process import ProcessFFMPEG, ProcessMP4BOX, ProcessWriteMeta
from postprocess import SanityCheck

# Import the config files
conf = ConfGet('elit.conf.yaml')

# Global variables
path_bin = conf['path']['GlobalBinPath']  # formerly b
if conf['path']['UseSystemTmp'] is False:
    tempfile.tempdir = conf['path']['Path_tmp']
path_log = conf['path']['Path_log']  # formerly g
path_unprocessed = conf['path']['Path_unprocessed']  # formerly u
path_completed = conf['path']['Path_complete']  # formerly c
path_processed = conf['path']['Path_processed']  # formerly p
allowed_extensions = ['.mkv', '.mp4', '.m4v']  # formerly q

# Logging configuration
log = logging.getLogger('elit')
log_file = os.path.join(path_log, 'elit.log')
log_hdlr = logging.FileHandler(
    log_file,
    mode='w'
)
log_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_hdlr.setFormatter(log_format)
log.addHandler(log_hdlr)
log.setLevel(logging.DEBUG)

list_unprocessed = DirList(path_unprocessed)  # formerly r

for i in range(len(list_unprocessed)):
    file_original = list_unprocessed[i]
    file_ext = file_original[-4:]

    if file_ext in allowed_extensions:
        pass
    else:
        continue
    del file_ext

    log.info(
        'Begin processing: ' +
        file_original
    )
    sys.stdout.write(
        'Begin processing: ' +
        file_original +
        '\n'
    )
    x = str(CreateUUID())

    with tempfile.TemporaryDirectory() as tmp:
        media_info = GetMediaInfo(path_bin, path_unprocessed, file_original)
        log.info(
            'Initiate: Cleaning Cycle'
        )
        sys.stdout.write(
            'Initiate: Cleaning Cycle' +
            '\n'
        )
        ProcessClean(
            path_bin,
            path_unprocessed,
            tmp,
            file_original,
            x,
            media_info
        )
        log.info(
            'Initiate: Conversion Cycle'
        )
        sys.stdout.write(
            'Initiate: Conversion Cycle' +
            '\n'
        )

        time_start = datetime.now()

        result = ProcessFFMPEG(
            path_bin,
            tmp,
            tmp,
            x + '.clean.mkv',
            x + '.mp4',
            media_info,
            1
        )

        time_end = datetime.now() - time_start

        log.info(
            'Conversion Cycle completed in: ' +
            str(time_end)
        )
        sys.stdout.write(
            'Conversion Cycle completed in: ' +
            str(time_end) +
            '\n'
        )

        del time_start
        del time_end

        log.info(
            'Initiate: Container Format Cycle'
        )
        sys.stdout.write(
            'Initiate: Container Format Cycle' +
            '\n'
        )

        ProcessMP4BOX(path_bin, tmp, tmp, x + '.mp4', x, 0)

        ProcessMP4BOX(path_bin, tmp, tmp, x + '.mp4', x, 1)

        log.info(
            'Initiate: Tag Cycle'
        )
        sys.stdout.write(
            'Initiate: Tag Cycle' +
            '\n'
        )

        meta_data = GetMeta(media_info['Title'], media_info['Year'])
        media_info['Title'] = meta_data['title']

        DownloadFile(
            tmp,
            x,
            'https://image.tmdb.org/t/p/w780' + meta_data['poster_path']
        )

        result = ProcessWriteMeta(
            path_bin,
            tmp,
            x + '.box.mp4',
            x + '.jpg',
            meta_data
        )

        log.info(
            'Initiate: Post-processing Cycle'
        )
        sys.stdout.write(
            'Initiate: Post-processing Cycle' +
            '\n'
        )

        if result == 0:
            list_tmp = DirList(tmp)

            for j in range(len(list_tmp)):
                f = list_tmp[j]
                if 'temp' in f:
                    file_completed = f
                del f
            del list_tmp
        else:
            sys.stdout.write(
                'Error: Tag cycle returned error, ' +
                'completed file will be untagged'
            )

            file_completed = x + '.box.mp4'

        del result

        # Sanity check
        log.info(
            'Initiate: Verification Cycle'
        )
        sys.stdout.write(
            'Initiate: Verification Cycle' +
            '\n'
        )

        result = SanityCheck(path_bin, tmp, media_info, file_completed)

        if result is True:
            log.info(
                'Moving files into place'
            )
            sys.stdout.write(
                'Moving files into place' +
                '\n'
            )

            MoveFile(
                tmp,
                path_completed,
                file_completed,
                media_info['Title'].replace(':', '-') +
                ' (' + media_info['Year'] + ').mp4'
            )

            MoveFile(
                path_unprocessed,
                path_processed,
                file_original,
                file_original
            )

            log.info(
                'Processing complete: ' +
                file_original
            )
            sys.stdout.write(
                'Processing complete: ' +
                file_original +
                '\n'
            )
        else:
            log.error(
                'Error: Completed file did not pass verification'
            )
            sys.stdout.write(
                'Error: Completed file did not pass verification'
            )
            continue

        del result

    # Garbage Collection
    del file_original
    del x
    del media_info
    del meta_data

sys.stdout.write(
    'All tasks completed!' +
    '\n'
)

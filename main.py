#!/usr/bin/env python

"""Usage: mcam timelapse [--output=PATH] [--period=MILISEC]
        mcam -h | --help

Commands:
    timelapse               Runs timelapse

Arguments:

Options:
    -o PATH --output=PATH                       Output folder eg: '/media/pi/sd128'
                                                If not specified, it will be current folder
    -p MILISEC --period=MILISEC                 Delay between shots in seconds, eg 500ms
                                                If not specified, it will be 0 (shot after pervious shot)
"""

import picamera
import time
import os
from docopt import docopt
import logging


def get_session_folder(path):
    path = os.path.join(path, time.strftime("%Y_%m_%d_%H_%M"))
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print "Cannot create folder " + path
        raise
    return path


def get_arg(args, name, default=None):
    if not args[name]:
        return default
    return args[name]


def get_arg_float(args, name, default=0.0):
    return float(get_arg(args, name, default))


def get_arg_int(args, name, default="0"):
    return int(get_arg(args, name, default))


def setup_logger(logPath):
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)

    fileHandler = logging.FileHandler(os.path.join(logPath, "timelapse.log"))
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)


def get_ticks():
    return int(round(time.time() * 1000))


def main():
    args = docopt(__doc__)

    path = get_arg(args, "--output", os.getcwd())
    path = get_session_folder(path);
    period = get_arg_int(args, "--period", 0)

    setup_logger(path)

    logging.info("""Timelapse started.
     Output directory = "{0}"
     Period = {1}ms
""".format(path, period)
    )

    with picamera.PiCamera() as camera:
        camera.resolution = (3280, 2464)  # (2048, 1080)

        time.sleep(1)  # warm up

        start_time = get_ticks()
        for filename in camera.capture_continuous(
                os.path.join(path, 'image{counter:06d}.jpg'),
                format="jpeg", use_video_port=False, resize=None, splitter_port=0, quality=100):

            shot_time = get_ticks() - start_time;

            delay = float(period - shot_time) / 1000.0;
            if (delay < 0):
                logging.warning('Captured {0} in {1} ms (more then desired period {2}ms)'.format(filename, shot_time, period))
            else:
                logging.info('Captured {0} in {1} ms. delay={2}'.format(filename, shot_time, delay))
                time.sleep(delay)
            start_time = get_ticks()
    pass

main()

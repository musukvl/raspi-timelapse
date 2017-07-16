#!/usr/bin/env python

"""Usage: mcam timelapse [--output=PATH] [--delay=SECONDS]
        mcam -h | --help

Commands:
    timelapse               Runs timelapse

Arguments:

Options:
    -o PATH --output=PATH                       Output folder eg: '/media/pi/sd128'
                                                If not specified, it will be current folder
    -d SECONDS --delay=SECONDS                  Delay between shots in seconds, eg 0.5 - 500ms
                                                If not specified, it will be 0 (shot after shot)
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

def get_arg(args, name, default = None):
    if not args[name]:
        return default
    return args[name]

def get_arg_float(args, name, default = 0.0):
    return float(get_arg(args, name, default))


def setup_logger():
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)


def main():
    args = docopt(__doc__)

    path = get_arg(args, "--output", os.getcwd())
    path = get_session_folder(path);
    delay = get_arg_float(args, "--delay", 0)

    setup_logger()

    logging.info(
"""Timelapse started. 
     Output directory = "{0}"
     Delay = {1}
""".format(path, delay)
    )

    camera = picamera.PiCamera()
    camera.resolution = (3280, 2464) # (2048, 1080)

    time.sleep(1) # warm up

    get_ticks = lambda: int(round(time.time() * 1000))

    start_time = get_ticks()
    for filename in camera.capture_continuous(os.path.join(path, 'image{counter:06d}.jpg')):
        logging.info('Captured %s in %i ms' % (filename, start_time - get_ticks()))
        time.sleep(delay)
        start_time = get_ticks()

main()

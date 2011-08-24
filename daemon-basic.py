#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: Example of usage of standar python daemon module (based on example
given on http://www.python.org/dev/peps/pep-3143/).
"""
__author__ = "$Author$"
__version__ = "$Rev$"
__date__ = "$Date$"
__id__ = "$Id$"

import os
import signal
import daemon
import lockfile
import argparse
import logging
from time import sleep


# contants

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_SLEEP = 5  # seconds
DEFAULT_PID = os.path.join(CURRENT_DIR, "daemon.pid")
DEFAULT_STDOUT = os.path.join(CURRENT_DIR, "daemon-out.log")
DEFAULT_STDERR = os.path.join(CURRENT_DIR, "daemon-err.log")
FORMAT_LOG = '%(asctime)-15s %(levelname)s %(module)s PID#%(process)d '\
        '%(message)s'


# parser configuration

parser = argparse.ArgumentParser(description="Daemon example receiving "\
        "parameters to customize context.")

parser.add_argument("-p", "--pidfile", type=str, default=DEFAULT_PID,
        help="PID file path. Default: %s" % DEFAULT_PID)

parser.add_argument("-w", "--working-dir", type=str, default=CURRENT_DIR,
        help="Working directory. Default: current directory (%s)." %
        CURRENT_DIR, dest="workingdir")

parser.add_argument("-o", "--stdout", type=str, default=DEFAULT_STDOUT,
        help="stdout stream. Default: %s" % DEFAULT_STDOUT)

parser.add_argument("-e", "--stderr", type=str, default=DEFAULT_STDERR,
        help="stderr stream. Default: %s" % DEFAULT_STDERR)

parser.add_argument("-s", "--sleep", type=int, default=DEFAULT_SLEEP,   
        help="Time to sleep. Default: %d" % DEFAULT_SLEEP)


def stop(signum=None, frame=None):
    """
    """
    logger.info("Stopping.")
    logger.debug("Arguments for hup(): signum=%d frame=%s" % (signum, frame))


def reload(signum=None, frame=None):
    """
    """
    logger.info("Reloading config.")
    logger.debug("Arguments for hup(): signum=%d frame=%s" % (signum, frame))


def hup(signum=None, frame=None):
    """
    """
    logger.info("Catched HUP signal.")
    logger.debug("Arguments for hup(): signum=%d frame=%s" % (signum, frame))


def do_work():
    """
    """
    logger.info("Doing work... :)")
    


if __name__ == '__main__':
    args = parser.parse_args()

    logging.basicConfig(format=FORMAT_LOG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logger.info(">>> Begin daemon.")

    logger.debug("Opening context.")
    context = daemon.DaemonContext(
        working_directory=args.workingdir,
        umask=0o002,
        pidfile=lockfile.FileLock(args.pidfile),
        stdout=open(args.stdout, "a+"),
        stderr=open(args.stderr, "a+"),
        )

    context.signal_map = {
        signal.SIGTERM: stop,
        signal.SIGHUP: hup,
        signal.SIGUSR1: reload,
        }

    # important_file = open(os.path.join(CURRENT_DIR, "import.txt"), 'w')
    # interesting_file = open(os.path.join(CURRENT_DIR, "interest.txt"), 'w')
    # context.files_preserve = [important_file, interesting_file]

    with context:
        # yes, I hate to do this. But I need this running as it is doing some 
        # stuff
        while True:  
            sleep(args.sleep)
            do_work()

    logger.info(">>> Finished daemon.")


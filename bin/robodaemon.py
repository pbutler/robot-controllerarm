#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

#try:
#    import json
#except ImportError:
#    import simplejson as json
#import socket

# Echo server program
import time
import sys
import os
import logging
import datetime
import subprocess

TEST = False

mainpath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append( mainpath )
os.environ["DJANGO_SETTINGS_MODULE"] = "robotarm.settings"
os.environ["PATH"] = os.path.join(mainpath, "robotarm","bin") + ":" +  os.environ["PATH"]

from robotarm.controller.models import *

def run_command(command, args = None):
    bufsize = 4096

    if args is None:
        cmd = command.command
    else:
        cmd = [ command.command ] + args

    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    (stdout, stderr) = p.communicate()
    if stdout:
        for l in stdout.split("\n"):
            logging.debug("%s: %s" % (command.cmd(), l))
    if stderr:
        for l in stderr.split("\n"):
            logging.warn("%s: %s" % (command.cmd(), l))

    if p.returncode != 0:
        logging.error( "%s returned with returncode: %d" % ( command.cmd, p.returncode))

def run_experiment(args = None):
    bufsize = 4096

    cmd = [ "runexp.py" ]
    if args is not None:
        cmd += args
    cmd = " ".join(cmd)
    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    (stdout, stderr) = p.communicate()
    if stdout:
        for l in stdout.split("\n"):
            logging.debug("%s: %s" % (cmd, l))
    if stderr:
        for l in stderr.split("\n"):
            logging.warn("%s: %s" % (cmd, l))

    if p.returncode != 0:
        logging.error( "%s returned with returncode: %d" % ( cmd, p.returncode))

def apply_com(command):
    real = command.child
    logging.debug("Executing %s" % real.cmd() )
    if isinstance(real, CommandBasic):
        if not TEST:
            run_command(real)
    if isinstance(real, CommandExperiment):
        args = [str(real.experiment.id)]
        if TEST:
            args = [ "-t" ] + args
        run_experiment(args)
        real.delete()
    elif isinstance(real, CommandMulti):
        for subc in real.commands.all():
            apply_com(subc)
    elif isinstance(real, CommandPause):
        time.sleep(real.time)

def check_halt():
    i = 0
    while len(Status.objects.all().filter(value="halt")) > 0:
        i += 1
        if i % 60 == 0:
            logging.info("Halting... waited for %d minutes" % (i / 60))
        time.sleep(1)

def daemon():
    while True:
        cq = CommandQueue.objects.all()
        logging.debug(cq)
        while len(cq) > 0:
            check_halt()
            command = cq[0]
            apply_com(command.command)
            cq[0].delete()
            cq = CommandQueue.objects.all()
        time.sleep(1)

def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="don't print status messages to stdout")

    parser.add_option("-b", "--background",
                      action="store_true", dest="background", default=False,
                      help="don't print status messages to stdout")
    parser.add_option("-l", "--logfile",
                      action="store", dest="filename", default=None,
                      help="don't print status messages to stdout")

    parser.add_option("-t", "--test",
                      action="store_true", dest="test",
                      help="don't really do anything")

    (options, args) = parser.parse_args()

    if len(args) < 0:
        parser.error("Not enough arguments given")

    global TEST
    if options.test:
        TEST = True

    if options.background:
        if os.fork() != 0:
            return 0
        if not options.filename:
            options.filename = os.path.join(mainpath, "daemon.log")

    if options.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(filename = options.filename, level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    if options.test:
        logging.info("Testing mode")

    daemon()
    return 0



if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )



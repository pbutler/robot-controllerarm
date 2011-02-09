#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

import serial
import subprocess
import time
import os
import sys
import datetime

mainpath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append( mainpath )
os.environ["DJANGO_SETTINGS_MODULE"] = "robotarm.settings"
#os.environ["PATH"] = os.path.join(mainpath, "robotarm","bin") + ":" + os.environ["PATH"]

from  robotarm.controller.models import *


def send(cmd):
    print cmd
    s.write(cmd + "\r\n")

def setDC(val):
    send("++auto 0")
    send("++addr 10")
    send("APPL:DC DEF, DEF, %0.03f" % val )
    send("++addr 5")
    send("++auto 1")

def readField():
    send("++addr 2")

    while True:
        try:
            time.sleep(2)
            send("measure1")
            fs = s.readline().strip()
            if "Error" in fs:
                print "Retry"
                raise Exception(fs)

            f = float(fs.strip()[1:-2])
            if fs[0] == "-":
                f *= -1.
            ok = s.readline()
            return f
        except Exception, e:
            print e
            time.sleep(2)
            send("++clr")
            send("++ifc")
            send("status")
            print s.readline()
            time.sleep(2)

def readR():
    send("++addr 7")
    send("++eos 2")
    send("OUTP? 3")
    send("++eos 0")
    return float(s.readline())*1000


def init():
    send("++auto 1")
    send("++addr 7")
    send("++eos 2")

    send("OUTX 1")
    send("SLVL 2.4")
    send("OFLT 9")
    send("SENS 23")
    send("FREQ 1000")

    send("++eos 0")
    setDC(0.0)


def setACField(goal, dc):
    setDC(dc)
    time.sleep(3)
    while True:
        delta = 0.001
        field = readField()
        if abs(field - goal) < .0003:
            time.sleep(1.2)
            #field2 = readField()
            #time.sleep(1.2)
            #field3 = readField()
            #time.sleep(1.2)
            #field = (field + field2 + field3)/ 3.

        derr = abs(field - goal)
        if goal > 0.01:
            err = 0.002
        else:
            err = 0.0002
        if abs(field - goal) < err:
            print " found"
            break
        print field, "<>",goal, err
        if abs(field-goal) > 0.01:
            delta = 0.01
        if field > goal:
            dc -= delta
        elif field < goal:
            dc += delta
        if abs(dc) > 5:
            break
        setDC(dc)
        time.sleep(1.2)
    return dc

def frange(x,y,z):
    a = x
    while a < z:
        yield  a
        a += y

def runexperiment(experiment):
    init()

    dc = 0.0
    for goal in frange(0.0, 0.02, 1.0):
        #dc = setACField(goal, dc)
        setDC(goal)
        time.sleep(3)
        x = readField()
        y = readR()
        yield x,y
    setDC(0.0)

def runtest(experiment):
    for goal in frange(0, .02, 1.0):
        yield goal, goal**2
        time.sleep(1.0)

def send_notification(experiment, TEST):
    import smtplib
    if not TEST:
        SERVER = smtplib.SMTP('smtp.vt.edu')
    fromaddr = "no-reply@vt.edu"
    toaddrs = [ str(experiment.user.email) ]
    msg = ("From: %s\r\nTo: %s\r\n" % (fromaddr, ", ".join(toaddrs)))
    msg += "Subject: Experiment Complete\r\n\r\n";
    msg += "This is a notification that your experiment is completed and may"
    msg += " be viewed at http://cimss-telelab.dyndns-ip.com"
    msg += experiment.get_absolute_url()
    if not TEST:
        SERVER.sendmail(fromaddr, toaddrs, msg)
        SERVER.quit()
    else:
        print msg


def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-q", "--quiet",
            action="store_false", dest="verbose", default=True,
            help="don't print status messages to stdout")
    parser.add_option("-t", "--test",
            action="store_true", dest="test", default=False,
            help="don't really doing return false values for testing")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("Not enough arguments given")

    experiment = Experiment.objects.get(pk=int(args[0]))
    experiment.started = datetime.datetime.now()
    experiment.save()
    if options.test:
        runner = runtest(experiment)
    else:
        serialport = "/dev/ttyUSB0"
        s = serial.Serial(serialport, timeout = 3)
        runner = runexperiment(experiment)
    for x,y in runner:
        data = Data(x=x, y=y, experiment=experiment)
        data.save()
    experiment.finished = datetime.datetime.now()
    experiment.save()
    send_notification(experiment, options.test)
    return 0




if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )



#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

import serial

def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()
    if len(args) < 3:
        parser.error("Not enough arguments given")
    s = serial.Serial("/dev/ttyUSB1", baudrate=115200)
    #print "#%sP%sS%s\r\n" % ( args[0], args[1], args[2])
    s.write("#%sP%sS%s\r\n" % ( args[0], args[1], args[2]))
    return 0



if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )



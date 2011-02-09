#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

import urllib


cmds = { "step" : 131,
        "numoption" : 142,
        "cmd" : 21,
        "group" : '',
        "nom1" : "GROUP1.POSITIONER",
        "velocity1" : 200,
        "absMoveA1" : 0,
        "absMoveB1" : 0,
        "relMove1" : "",
        "nom2" : "GROUP2.POSITIONER",
        "velocity2" : "100",
        "absMoveA2" : 0,
        "absMoveB2" : 0,
        "relMove2" : "",
        }
def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-x", "",
                      action="store", dest="x", type="int",
                      help="don't print status messages to stdout")
    parser.add_option("-y", "",
                      action="store", dest="y", type="int",
                      help="don't print status messages to stdout")

    parser.add_option("-v", "--velocity-x",
                      action="store", dest="vx", type="int", default = 200,
                      help="don't print status messages to stdout")
    parser.add_option("-w", "--velocity-y",
                      action="store", dest="vy", type="int", default = 200,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    if len(args) < 0:
        parser.error("Not enough arguments given")

    if options.x:
        cmds['absMoveA2'] = options.x
        cmds['velocity2'] = options.vx

    if options.y:
        cmds['absMoveA1'] = options.y
        cmds['velocity1'] = options.vy

    if options.x:
        cmds['cmd'] = 21
        req = urllib.urlopen("http://192.168.0.254/cgi/post.cgi", urllib.urlencode(cmds))
        data = req.read()

    if options.y:
        cmds['cmd'] = 11
        req = urllib.urlopen("http://192.168.0.254/cgi/post.cgi", urllib.urlencode(cmds))
        data = req.read()
    return 0



if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )



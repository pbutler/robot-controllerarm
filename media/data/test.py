#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

a = """
id : "hi okay bye"
id2 : "hi okay \
 bye"
id3 : "hi okay bye"
"""


def foo(x):
    """
    >>> foo(range(5))
    [2, 3, 4, 5, 6]
    """
    return map(lambda e: e+2, x)

def lines(a):
    """
    makes a string look like a file.readlines()
    """
    return [ l+'\n' for l in a.split("\n") ]

def main(args):
    print [ l for l in foo(lines(a)) ]
    return 0

if __name__ == "__main__":
     import doctest
     doctest.testmod()


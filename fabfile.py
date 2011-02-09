from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm


__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

def reset_db():
    if not confirm("Are you sure?"):
        abort("Not resetting database")
    local("./manage.py reset controller", capture=False)
    local("./manage.py syncdb", capture=False)



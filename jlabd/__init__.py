from .autod import def_init

from os import path
import sys

prename = 'jlabd_preload.py'
dname = path.dirname(__file__)
if dname != '':
    prename = dname + '/' + prename

def_init(prename, 'jlabd.socket')

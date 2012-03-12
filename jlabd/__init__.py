from .autod import check_a_start

from os import path
import sys

prename = 'jlabd_preload.py'
dname = path.dirname(__file__)
if dname != '':
    prename = dname + '/' + prename

def init():
    check_a_start(prename, 'jlabd.socket', sys.argv)

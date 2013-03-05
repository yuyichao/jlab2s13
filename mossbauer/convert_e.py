#!/usr/bin/env python

import jlab
from pylab import *
import calib

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    if iname.endswith('_res.py'):
        calib_file = iname[:-6] + 'calib.py'
        oname = iname[:-6] + 'e.py'
    try:
        calib_file = sys.argv[2]
    except:
        pass
    try:
        oname = sys.argv[3]
    except:
        pass
    calib_file = 'pos_cal/' + jlab.load_pyfile(calib_file).calib + '_calib.py'
    calib.load(calib_file)
    peaks = array(jlab.load_pyfile(iname).peaks).T
    jlab.save_pyfile(calib.convert(peaks[0], peaks[1]), oname)

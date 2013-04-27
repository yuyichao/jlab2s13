#!/usr/bin/env python

from pylab import *
import jlab
import itertools
import re

def _csv_line_iter(line):
    return (f.strip() for f in line.split(','))

def load_doppler_fh(fh):
    axis = next(fh)
    unit = next(fh)
    data = []
    for line in fh:
        try:
            line = [float(f) for f in _csv_line_iter(line) if f]
            if len(line) <= 1:
                raise ValueError
        except:
            break
        data.append(line)
    data = array(data).T
    # it = itertools.chain([line], fh)
    return data

def load_doppler(fname):
    with open(fname) as fh:
        return load_doppler_fh(fh)

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    data = load_doppler(iname)
    if iname.lower().endswith('.csv'):
        oname = iname[:-4] + '.py'
    else:
        oname = iname + '.py'
    jlab.save_pyfile(jlab.Ret('data'), oname)

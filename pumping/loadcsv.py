#!/usr/bin/env python

from pylab import *
import jlab
import itertools
import re

_prob_regex = re.compile('Ch *(?P<ch>[0-9]+): *(?P<n>[.0-9]*) *: *(?P<d>[0-9]*)')
def get_ratio(line):
    m = _prob_regex.search(line)
    return int(m.group('ch')), float(m.group('n')) / int(m.group('d'))

def _csv_line_iter(line):
    return (f.strip() for f in line.split(','))

def load_pump_fh(fh):
    axis = next(fh)
    unit = next(fh)
    data = []
    for line in fh:
        try:
            line = [float(f) for f in _csv_line_iter(line)]
            if len(line) <= 1:
                raise ValueError
        except:
            break
        data.append(line)
    data = array(data).T
    it = itertools.chain([line], fh)
    for line in it:
        if not line.endswith('Probe'):
            continue
        for line in it:
            try:
                ch, ratio = get_ratio(line)
                data[ch] *= ratio
            except:
                break
    return data

def load_pump(fname):
    with open(fname) as fh:
        return load_pump_fh(fh)

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    data = load_pump(iname)
    if iname.lower().endswith('.csv'):
        oname = iname[:-4] + '.py'
    else:
        oname = iname + '.py'
    jlab.save_pyfile(jlab.Ret('data'), oname)

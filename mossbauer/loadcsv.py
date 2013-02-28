#!/usr/bin/env python

import jlab
import re

_var_regex = re.compile('(^[0-9]|[^a-z1-9]+)')

def _replace_var(s):
    return _var_regex.sub('_', s)

def _to_num(s):
    try:
        return int(s)
    except:
        return float(s)

def _csv_line_iter(line):
    return (f.strip() for f in line.split(','))

def load_moss_fh(fh):
    res = jlab.Ret()
    for line in fh:
        line = list(_csv_line_iter(line))
        try:
            first = line[0]
        except IndexError:
            break
        if not first:
            break
        first.endswith(':')
        first = first[:-1]
        key = _replace_var(first.lower())
        if len(line) <= 1:
            res[key] = None
        elif len(line) == 2:
            res[key] = line[1]
        else:
            res[key] = line[1:]
    next(fh)
    res.cols = list(_csv_line_iter(next(fh)))
    res.data = [[_to_num(f) for f in _csv_line_iter(line)] for line in fh]
    return res

def load_moss(fname):
    with open(fname) as fh:
        return load_moss_fh(fh)


if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    res = load_moss(iname)
    if iname.lower().endswith('.csv'):
        oname = iname[:-4] + '.py'
    else:
        oname = iname + '.py'
    jlab.save_pyfile(res, oname)

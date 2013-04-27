#!/usr/bin/env python

from jlab import *

def select_region(iname):
    data = load_pyfile(iname).data
    plot(data[2])
    plot(data[3])
    title(iname)
    selector = RegionSelect()
    return [(rect.x1, rect.x2) for rect in selector.run()]

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    region = select_region(iname)
    if iname.lower().endswith('.py'):
        oname = iname[:-3] + '_region.py'
    else:
        oname = iname + '_region.py'
    save_pyfile(Ret('region'), oname)

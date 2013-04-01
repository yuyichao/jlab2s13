#!/usr/bin/env python

from pylab import *
from jlab import *
from itertools import groupby

def handle_point(iname):
    data = load_pyfile(iname)
    poss = [[] for i in range(4)]
    poss_s = [[] for i in range(4)]
    heights = [[] for i in range(4)]
    heights_s = [[] for i in range(4)]

    for i, pos in enumerate(data.pos):
        _i = i % 4
        poss[_i].append(pos - (i // 4) * 2.5)
        poss_s[_i].append(data.pos_s[i])
        heights[_i].append(data.height[i])
        heights_s[_i].append(data.height_s[i])

    poss = [mean(v) for (i, v) in enumerate(poss)]
    heights = [mean(v) for (i, v) in enumerate(heights)]

    poss_s = [sqrt(sum(array(v)**2)) / len(v) for (i, v) in enumerate(poss_s)]
    heights_s = [sqrt(sum(array(v)**2)) / len(v)
                 for (i, v) in enumerate(heights_s)]

    return (poss, poss_s), (heights, heights_s)

def rfscan_baxis_combine(oname_pos, oname_height, rfname, inames):
    poss, heights = zip(*tuple(handle_point(iname) for iname in inames))
    rfdata = loadtxt(rfname)
    with open(oname_pos, 'w') as fh:
        for i, (pos, pos_s) in enumerate(poss):
            fh.write(' '.join([repr(v) for v in (rfdata[i], pos[2], pos_s[2],
                                                 pos[3], pos_s[3])]) + '\n')
    with open(oname_height, 'w') as fh:
        for i, height in enumerate(heights):
            fh.write(repr(rfdata[i]))
            for h, s in zip(*height):
                fh.write(' %a %a' % (h, s))
            fh.write('\n')

if __name__ == '__main__':
    import sys
    oname_pos, oname_height, rfiname, *inames = sys.argv[1:]
    rfscan_baxis_combine(oname_pos, oname_height, rfiname, inames)

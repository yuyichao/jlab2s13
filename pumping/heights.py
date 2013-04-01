#!/usr/bin/env python

from pylab import *
from jlab import *

def cal_heights(heights_iname, gs_iname):
    _y, h1, h1_s, h2, h2_s, h3, h3_s, h4, h4_s = loadtxt(heights_iname).T
    gs, gs_s = load_pyfile(gs_iname)['gs', 'gs_s']
    gr = r_[h4 / h3]
    gr_s = sqrt(r_[(h3_s / h3)**2 + (h4_s / h4)**2]) * gr
    gr_a = mean(gr)
    gr_as = sqrt(std(gr)**2 / (len(gr) - 1) + sum(gr_s**2) / len(gr_s)**2)
    r = gr_a * (gs[1] / gs[0])**2
    r_s = sqrt((gr_as / gr_a)**2 + (2 * gs_s[0] / gs[0])**2 +
               (2 * gs_s[1] / gs[1])**2) * r
    present1 = 1 / (1 + r) * 100
    present2 = 100 - present1
    present_s = r_s / (1 + r) * present1
    return Ret('r', 'r_s', 'present1', 'present2', 'present_s')

if __name__ == '__main__':
    import sys
    heights_iname, gs_iname, oname = sys.argv[1:]
    res = cal_heights(heights_iname, gs_iname)
    save_pyfile(res, oname)

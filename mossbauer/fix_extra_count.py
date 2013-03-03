#!/usr/bin/env python

import jlab
from pylab import *

def extra_count(fname):
    total, extra = loadtxt(fname).T
    rate = extra / (total - extra)
    return rate.mean(), rate.std() / sqrt(len(rate) - 1)

if __name__ == '__main__':
    import sys
    rate_a, unc_a = zip(*(extra_count(f) for f in sys.argv[2:]))
    extra_rate = mean(rate_a)
    extra_unc = sqrt(std(rate_a)**2 / (len(rate_a) - 1) +
                     mean(array(unc_a)**2) / len(unc_a))
    jlab.save_pyfile(jlab.Ret('extra_rate', 'extra_unc'), sys.argv[1])

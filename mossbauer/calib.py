#!/usr/bin/env python

import jlab
from pylab import *

def calib(v_fit, iname):
    v_fit = jlab.load_pyfile(v_fit)
    peaks = array(jlab.load_pyfile(iname).peaks).T
    peaks_v = v_fit.a[0] + peaks[0] * v_fit.a[1]
    peaks_2 = repeat([peaks_v], len(peaks_v), axis=0)
    peaks_cov = (v_fit.cov[0][0] + v_fit.cov[0][1] * (peaks_2 + peaks_2.T) +
                 v_fit.cov[1][1] * peaks_2 * peaks_2.T)
    return jlab.Ret('peaks_v', 'peaks_cov')

if __name__ == '__main__':
    import sys
    v_fit, iname, oname = sys.argv[1:]
    res = calib(v_fit, iname)
    jlab.save_pyfile(res, oname)

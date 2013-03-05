#!/usr/bin/env python

import jlab
from pylab import *

E_0 = 14.4e3
c_0 = 299792458
r_0 = E_0 / c_0

def calib(v_fit, iname):
    v_a, v_cov = jlab.load_pyfile(v_fit)['a', 'cov']
    v_a = array(v_a)
    v_cov = array(v_cov)
    v_a *= r_0
    v_cov *= r_0**2

    peaks = array(jlab.load_pyfile(iname).peaks).T
    peaks_e = v_a[0] + peaks[0] * v_a[1]
    peaks_2 = repeat([peaks_e], len(peaks_e), axis=0)
    peaks_cov = (v_cov[0, 0] + v_cov[0, 1] * (peaks_2 + peaks_2.T) +
                 v_cov[1, 1] * peaks_2 * peaks_2.T)
    peaks_cov += diag((peaks[1] * v_a[1])**2)
    peaks_s = sqrt(diag(peaks_cov))
    return jlab.Ret('peaks_e', 'peaks_s', 'peaks_cov')

if __name__ == '__main__':
    import sys
    v_fit, iname, oname = sys.argv[1:]
    res = calib(v_fit, iname)
    jlab.save_pyfile(res, oname)

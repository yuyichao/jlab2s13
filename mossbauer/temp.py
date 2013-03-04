#!/usr/bin/env python

import jlab
from pylab import *
import calib
import re
from scipy import constants as consts

__temp_re = re.compile("[^-]-(?P<t>[-0-9][0-9]*)c")
E_0 = 14.4e3

def get_temp(fname):
    return int(__temp_re.search(fname).group('t'))

if __name__ == '__main__':
    import sys
    oname, *inames = sys.argv[1:]
    if not inames[0].endswith('_res.py') or not len(inames) == 2:
        raise ValueError
    calib_file = inames[0][:-6] + 'calib.py'
    calib_file = 'pos_cal/' + jlab.load_pyfile(calib_file).calib + '_calib.py'
    calib.load(calib_file)
    peaks = array(list(zip(*(jlab.load_pyfile(iname).peaks[0]
                             for iname in inames))))
    diff = (peaks[0, 0] - peaks[0, 1])
    unc = sqrt(peaks[1, 1]**2 + peaks[1, 0]**2)
    diff_res = calib.diff(diff, unc)
    diff_res.a /= E_0
    diff_res.s /= E_0

    temps = [get_temp(iname) for iname in inames]
    dT4 = temps[1]**4 - temps[0]**4
    dT4_s = (6 / sqrt(3)) * 4 * temps[1]**3

    theta3 = (3 * pi**4 * consts.k * dT4 / 5 / consts.c**2 /
              consts.atomic_mass / 57 / diff_res.a)
    theta = theta3**(1 / 3)
    theta_s = sqrt((diff_res.s / diff_res.a)**2 + (dT4_s / dT4)**2) / 3 * theta
    jlab.save_pyfile(jlab.Ret('theta', 'theta_s',
                              delta=diff_res.a, delta_s=diff_res.s), oname)

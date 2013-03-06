#!/usr/bin/env python

import jlab
from pylab import *
import calib
import re
from scipy import constants as consts
from scipy import integrate

__temp_re = re.compile("[^-]-(?P<t>[-0-9][0-9]*)c")
E_0 = 14.4e3

def get_temp(fname):
    return int(__temp_re.search(fname).group('t')) + 273.15

def get_peak(fname):
    data = jlab.load_pyfile(fname)
    for i, peak in enumerate(data.peaks):
        if data.peaks_width[i][0] == data.peaks_width[i][0]:
            return peak

if __name__ == '__main__':
    import sys
    oname, *inames = sys.argv[1:]
    if not inames[0].endswith('_res.py') or not len(inames) == 2:
        raise ValueError
    calib_file = inames[0][:-6] + 'calib.py'
    calib_file = 'pos_cal/' + jlab.load_pyfile(calib_file).calib + '_calib.py'
    calib.load(calib_file)
    peaks = array(list(zip(*(get_peak(iname) for iname in inames))))
    diff = (peaks[0, 0] - peaks[0, 1])
    unc = sqrt(peaks[1, 1]**2 + peaks[1, 0]**2)
    diff_res = calib.diff(diff, unc)
    diff_res.a /= E_0
    diff_res.s /= E_0
    print("dE / E = ", jlab.a_pm_s([diff_res.a, diff_res.s]))

    U = diff_res.a * consts.atomic_mass * 57 * consts.c**2 / consts.e
    U_s = U * diff_res.s / diff_res.a
    print("U = ", jlab.a_pm_s([U, U_s], unit='eV'))

    temps = [get_temp(iname) for iname in inames]
    temps_s1 = 6 / sqrt(3)

    Ue1 = 3 * consts.k * (temps[1] - temps[0]) / 2 / consts.e
    Ue1_s = temps_s1 / temps[1] * Ue1
    print("Ue1 = ", jlab.a_pm_s([Ue1, Ue1_s], unit='eV'))

    Theta = 470

    dT4 = temps[1]**4 - temps[0]**4
    dT4_s = temps_s1 * 4 * temps[1]**3

    Ue2 = (3 * pi**4 * consts.k * dT4 / 5 / consts.c**2 /
           consts.atomic_mass / 57 / Theta**3 / 2 / consts.e)
    Ue2_s = dT4_s / dT4 * Ue2
    print("Ue2 = ", jlab.a_pm_s([Ue2, Ue2_s], unit='eV'))

    D0 = integrate.quad(lambda x: x**3 / (exp(x) - 1), 0, temps[0] / Theta)[0]
    D1 = integrate.quad(lambda x: x**3 / (exp(x) - 1), 0, temps[1] / Theta)[0]
    DD0 = temps[0]**4 * D0
    DD1 = temps[1]**4 * D1
    DD1_s = (4 * temps[1]**3 * D1 +
             temps[1]**7 / (exp(temps[1] / Theta) - 1) / Theta**4) * temps_s1
    DDD = (DD1 - DD0)
    Ue3 = (9 * consts.k * DDD / Theta**3 / 2 / consts.e)
    Ue3_s = Ue3 * DD1_s / DDD
    print("Ue3 = ", jlab.a_pm_s([Ue3, Ue3_s], unit='eV'))

    jlab.save_pyfile(jlab.Ret('U', 'U_s', 'Ue1', 'Ue1_s', 'Ue2', 'Ue2_s',
                              'Ue3', 'Ue3_s',
                              delta=diff_res.a, delta_s=diff_res.s), oname)

#!/usr/bin/env python

from pylab import *
from jlab import *

@curve_fit_wrapper
def fit_t(x, a, b, c, d):
    return a + b * sqrt((x - c)**2 + d)

def fit_delay(I, t, t_s):
    min_i = argmin(t)
    c0 = I[min_i]
    a0 = t[min_i]
    d0 = 0
    max_i = argmax(t)
    b0 = (t[max_i] - a0) / abs(I[max_i] - c0)
    fitres = fit_t(I, t, sig=t_s, p0=[a0, b0, c0, d0])

    I0 = fitres.a[2]
    I0_s = sqrt(fitres.s[2]**2 + 1e-4**2)

    return Ret(chi2=fitres.chi2, I0=I0, I0_s=I0_s, fitres=fitres)

def ItoB(I, I_s, coil):
    B = I * coil.B
    B_s = B * sqrt((I_s / I)**2 + (coil.B_s / coil.B)**2)
    return B, B_s

def rfscan_baxis(iname, coil_name, coil_file, fig_prefix):
    I, t1, t1_s, t2, t2_s = loadtxt(iname).T
    I /= 1e3
    coil = Ret(load_pyfile(coil_file)[coil_name])
    fit1 = fit_delay(I, t1, t1_s)
    fit2 = fit_delay(I, t2, t2_s)

    xs = r_[min(I):max(I):1000j]

    errorbar(I, t1, t1_s, fmt='o', linewidth=2, label="Peak1")
    plot(xs, fit1.fitres.func(xs), linewidth=2, label="Peak1 (fit)")
    axvline(fit1.I0, color='r')
    axvline(fit1.I0 + fit1.I0_s, color='c')
    axvline(fit1.I0 - fit1.I0_s, color='c')

    errorbar(I, t2, t2_s, fmt='o', linewidth=2, label="Peak2")
    plot(xs, fit2.fitres.func(xs), linewidth=2, label="Peak2 (fit)")
    axvline(fit2.I0, color='r')
    axvline(fit2.I0 + fit2.I0_s, color='c')
    axvline(fit2.I0 - fit2.I0_s, color='c')

    figtext(0.5, 0.88,
            '$\\chi_1^2=%.2f$\n$\\chi_2^2=%.2f$' % (fit1.chi2, fit2.chi2),
            fontsize=18, ha='right', va='top',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat'})

    xlabel("Current / $A$")
    ylabel("Position of peak / $s$")
    legend(loc='best', fancybox=True)
    grid()
    savefig(fig_prefix + '_fit.png')

    B1, B1_s = ItoB(fit1.I0, fit1.I0_s, coil)
    B2, B2_s = ItoB(fit2.I0, fit2.I0_s, coil)

    B0 = (B1 + B2) / 2 * 1e4
    B0_s = sqrt(B1_s**2 + B2_s**2) / 2 * 1e4
    return Ret('B0', 'B0_s')

if __name__ == '__main__':
    import sys
    iname, oname, coil_name, coil_file, fig_prefix = sys.argv[1:]
    res = rfscan_baxis(iname, coil_name, coil_file, fig_prefix)
    save_pyfile(res, oname)

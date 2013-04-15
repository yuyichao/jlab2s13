#!/usr/bin/env python

from pylab import *
from jlab import *

def load_peaks(iname):
    return load_pyfile(iname)['h', 'h_s', 'tau', 'tau_s']

def bswitch_od(figprefix, rfname, inames):
    ods = loadtxt(rfname)
    hs, hs_s, taus, taus_s = array(tuple(zip(*(load_peaks(iname)
                                               for iname in inames))))
    oI = 10**(-ods)

    figure()
    errorbar(oI, hs, hs_s, fmt='o')
    xlabel("Light Intensity")
    ylabel("Height of Peaks")
    grid()
    savefig(figprefix + '_height.png')
    # show()
    close()

    ty = 1 / taus
    ty_s = taus_s / taus**2

    fitres = fitlin(oI, ty, ty_s)
    ty_s = sqrt(ty_s**2 + (fitres.a[1] * oI * 0.04)**2)

    fitres = fitlin(oI, ty, ty_s)

    figure()
    errorbar(oI, ty, ty_s, fmt='o')
    plot(oI, fitres.yfit, linewidth=2)
    figtext(0.88, 0.12, "$\\chi^2=%.2f$" % fitres.chi2,
            fontsize=18, ha='right', va='bottom',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat'})
    xlabel("Light Intensity")
    ylabel("Pumping rate / $s^{-1}$")
    grid()
    savefig(figprefix + '_tau.png')
    # show()
    close()

    return Ret(k=fitres.a[1], k_s=fitres.s[1])

if __name__ == '__main__':
    import sys
    oname, figprefix, rfname, *inames = sys.argv[1:]
    res = bswitch_od(figprefix, rfname, inames)
    save_pyfile(res, oname)

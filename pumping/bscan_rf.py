#!/usr/bin/env python

from pylab import *
from jlab import *

def peaks_iter(peaks):
    for peak in peaks:
        yield abs(peak[1] - peak[2]), abs(peak[0] - peak[2])
        yield abs(peak[3] - peak[2]), abs(peak[4] - peak[2])

def peaks_s_iter(peaks_s):
    for peak_s in peaks_s:
        yield peak_s[1]**2 + peak_s[2]**2, peak_s[0]**2 + peak_s[2]**2
        yield peak_s[3]**2 + peak_s[2]**2, peak_s[4]**2 + peak_s[2]**2

def combine_peaks(iname):
    data = load_pyfile(iname)
    peaks = array(tuple(peaks_iter(data.peaks))).T
    peaks_s = array(tuple(peaks_s_iter(data.peaks_s))).T
    peaks = mean(peaks, axis=1)
    peaks_s = sqrt(sum(peaks_s, axis=1)) / len(peaks_s)
    return array([peaks, peaks_s]) / 49.4

def bscan_rf(figprefix, coil_file, rfname, inames):
    coil_data = Ret(load_pyfile(coil_file).z)
    rfdata = loadtxt(rfname)
    data = array([r_[[[rf, rf]], combine_peaks(iname)].T
                  for (rf, iname) in zip(rfdata, inames)])
    chi2s = []
    gs = []
    gs_s = []
    for i, (freq, v, v_s) in enumerate([data[:, 0].T, data[:, 1].T]):
        errorbar(freq, v * coil_data.B * 1e4, v_s * coil_data.B * 1e4,
                 fmt='o', label="Peak %d" % i)
        fitres = fitlin(freq, v, v_s)
        chi2s.append(fitres.chi2)
        g = 1 / (fitres.a[1] * coil_data.B * 1e10) # MHz / Gs
        gs.append(g)
        g_s = sqrt((fitres.s[1] / fitres.a[1])**2 +
                   (coil_data.B_s / coil_data.B)**2) * g
        gs_s.append(g_s)
        plot(freq, fitres.yfit * coil_data.B * 1e4,
             linewidth=2, label="Peak %d (fit)" % i)

    figtext(0.88, 0.12,
            '\n'.join(["$\\chi_%d^2=%.2f$" % (i, chi2)
                       for (i, chi2) in enumerate(chi2s)]),
            fontsize=18, ha='right', va='bottom',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat'})
    legend(fancybox=True, loc='best')
    xlabel("RF frequency / $Hz$")
    ylabel("Magnetic Field / $Gs$")
    grid()
    savefig(figprefix + '_fit.png')

    return Ret('gs', 'gs_s')

if __name__ == '__main__':
    import sys
    oname, figprefix, coil_file, rfname, *inames = sys.argv[1:]
    res = bscan_rf(figprefix, coil_file, rfname, inames)
    print(res)
    save_pyfile(res, oname)

#!/usr/bin/env python

import jlab
from pylab import *

wavelength = 632.8e-9
extra_fix = jlab.load_pyfile('extra_count/res.py')
r_0 = 1 / (1 + extra_fix.extra_rate)
rel_s = extra_fix.extra_unc / (1 + extra_fix.extra_rate)

def read_cal_file(fname):
    f = jlab.load_pyfile(fname)
    index, data = array([(d[0], d[2]) for d in f.data]).T
    passes = int(f.elapsed_passes)
    c_time = float(f.mossbauer_dwell_time.split()[0]) * 1e-3
    return index, wavelength * data / 2 / passes / c_time * r_0

def fit_v(iname, fig_name):
    index, data = read_cal_file(iname)
    max_i = data[:len(data) // 2].argmax()
    v = data[max_i]
    for start in range(max_i + 1, len(data)):
        if v < data[start]:
            break
        v = data[start]

    fig1 = figure()
    plot(index, data * 1000)
    plot(start, data[start] * 1000, 'o')
    xlim(0, len(data))
    xlabel("Channel No.")
    ylabel(r"Speed ($mm\cdot s^{-1}$)")
    grid()
    savefig(fig_name + '_raw.png')
    close()

    index = index[start:]
    data = data[start:]
    min_i = data.argmin()
    data[:min_i] = -data[:min_i]
    fit = jlab.fitlin(index, data)
    rel_cov = jlab.abs2relcov(fit.a, fit.cov) + rel_s**2
    abs_cov = array(jlab.rel2abscov(fit.a, rel_cov))
    fit.cov = abs_cov
    fit.s = sqrt([abs_cov[0, 0], abs_cov[1, 1]])

    fig2 = figure()
    plot(index, data * 1000, label="Measure")
    plot(index, fit.yfit * 1000, label="Fit")
    legend(loc=2)
    xlim(index[0], index[-1])
    xmin, xmax = xlim()
    ymin, ymax = ylim()
    b, a = jlab.a_pm_s([fit.a * 1000, fit.s * 1000], tex=True)
    text(xmin * .95 + xmax * 0.05, ymin * .4 + ymax * .6,
         "$y = a\cdot x + b$\n$a=%s mm\cdot s^{-1}$\n$b=%s mm\cdot s^{-1}$" %
         (a, b), fontsize=20)
    xlabel("Channel No.")
    ylabel(r"Velocity ($mm\cdot s^{-1}$)")
    grid()
    savefig(fig_name + '_fit.png')
    close()

    return jlab.Ret('start', a=fit.a, s=fit.s, cov=fit.cov)

if __name__ == '__main__':
    import sys
    iname, oname, fig_name = sys.argv[1:]
    res = fit_v(iname, fig_name)
    jlab.save_pyfile(res, oname)

#!/usr/bin/env python

import jlab
from pylab import *

def calib(iname, fig_name):
    index, data = array([(d[0], d[2]) for d in jlab.load_pyfile(iname).data]).T
    max_i = data[:len(data) // 2].argmax()
    v = data[max_i]
    for start in range(max_i + 1, len(data)):
        if v < data[start]:
            break
        v = data[start]

    fig1 = figure()
    plot(index, data)
    plot(start, data[start], 'o')
    xlim(0, len(data))
    xlabel("Channel No.")
    ylabel("Count per channel")
    grid()
    savefig(fig_name + '_raw.png')
    close()

    index = index[start:]
    data = data[start:]
    min_i = data.argmin()
    data[:min_i] = -data[:min_i]
    fit = jlab.fitlin(index, data)

    fig2 = figure()
    plot(index, data, label="Measure")
    plot(index, fit.yfit, label="Fit")
    legend(loc=2)
    xlim(index[0], index[-1])
    xmin, xmax = xlim()
    ymin, ymax = ylim()
    b, a = jlab.a_pm_s(fit)
    text(xmin * .9 + xmax * .1, ymin * .4 + ymax * .6,
         "$y = a\cdot x + b$\n$a=%s$\n$b=%s$" % (a, b), fontsize=20)
    xlabel("Channel No.")
    ylabel("Count per channel")
    grid()
    savefig(fig_name + '_fit.png')
    close()

    return jlab.Ret('start', a=fit.a, s=fit.s, cov=fit.cov)

if __name__ == '__main__':
    import sys
    iname, oname, fig_name = sys.argv[1:]
    res = calib(iname, fig_name)
    jlab.save_pyfile(res, oname)

#!/usr/bin/env python

from pylab import *
from jlab import *

def plot_data(iname, pname):
    data = load_pyfile(iname).data
    ax1 = axes()
    lines = []
    if len(data) > 2:
        ax2 = twinx()
        lines += ax1.plot(data[0], data[2], 'r', linewidth=2.0,
                          label="$B_z$ scan")
        lines += ax2.plot(data[0], data[1], 'b', linewidth=2.0,
                          label="Intensity")
        ax2.set_ylabel("Light Intensity")
        ax1.set_ylabel("$V_z/V$")
    else:
        lines += ax1.plot(data[0], data[1], 'b', linewidth=2.0,
                          label="Intensity")
        ax1.set_ylabel("Light Intensity")
    grid()
    xlim([min(data[0]), max(data[0])])
    ax1.set_xlabel("Scan Time/$s$")
    legend(lines, [line.get_label() for line in lines],
           fancybox=True, loc='best')
    savefig(pname)

if __name__ == '__main__':
    import sys
    iname, pname = sys.argv[1:]
    plot_data(iname, pname)

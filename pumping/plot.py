#!/usr/bin/env python

from pylab import *
from jlab import *

def plot_data(iname, pname):
    data = load_pyfile(iname).data
    lines = []
    ax1 = axes()
    lines += ax1.plot(data[0], data[1], 'b', linewidth=2.0,
                      label="Intensity")
    if len(data) > 2:
        ax2 = twinx()
        lines += ax2.plot(data[0], data[2], 'r', linewidth=2.0,
                          label="$B_z$ scan")
        ax2.set_zorder(ax1.get_zorder() - 1)
        ax2.set_ylabel("$V_z/V$")
        ax1.patch.set_visible(False)
    grid()
    xlim([min(data[0]), max(data[0])])
    xlabel("Scan Time/$s$")
    ylabel("Light Intensity")
    legend(lines, [line.get_label() for line in lines],
           fancybox=True, loc='best')
    savefig(pname)

if __name__ == '__main__':
    import sys
    iname, pname = sys.argv[1:]
    plot_data(iname, pname)

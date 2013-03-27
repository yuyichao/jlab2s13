#!/usr/bin/env python

from pylab import *
from jlab import *

def plot_data(iname, pname):
    data = load_pyfile(iname).data
    ax1 = axes()
    ax1.plot(data[0], data[1], 'b', linewidth=2.0)
    if len(data) > 2:
        ax2 = twinx()
        ax2.plot(data[0], data[2], 'r', linewidth=2.0)
        ax2.set_zorder(ax1.get_zorder() - 1)
        ax1.patch.set_visible(False)
    grid()
    xlim([min(data[0]), max(data[0])])
    savefig(pname)

if __name__ == '__main__':
    import sys
    iname, pname = sys.argv[1:]
    plot_data(iname, pname)

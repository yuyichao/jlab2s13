#!/usr/bin/env python

from pylab import *
from jlab import *

mpinch = 0.0254
mu0 = 4 * pi * 1e-7

def cal_coil(data):
    coil = Ret(data)
    coil.D *= mpinch
    coil.dD *= mpinch
    coil.H *= mpinch
    coil.dH *= mpinch
    r = coil.D / 2
    x = coil.H / 2
    r_s = coil.dD / 10 + 0.2 * mpinch
    x_s = coil.dH / 10 + 0.2 * mpinch
    B = mu0 * coil.N * r**2 / (r**2 + x**2)**(3 / 2)
    r**2 / (r**2 + x**2)**(3 / 2)
    B_s = B * sqrt((3 * x * x_s / (r**2 + x**2))**2 +
                   (2 * r_s / r - 3 * r * r_s / (r**2 + x**2))**2)
    return Ret('B', 'B_s')

def cal_all_coil(iname):
    all_coil = load_pyfile(iname)
    res = Ret()
    for axis in 'x', 'y', 'z':
        res[axis] = cal_coil(all_coil[axis])
    return res

if __name__ == '__main__':
    import sys
    iname, oname = sys.argv[1:]
    res = cal_all_coil(iname)
    save_pyfile(res, oname)

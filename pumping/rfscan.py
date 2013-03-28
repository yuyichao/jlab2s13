#!/usr/bin/env python

from pylab import *
from jlab import *

def smooth(data, w):
    l = len(data)
    krnl_x = r_[-l:l]
    krnl = exp(-(krnl_x / w)**2) / w / sqrt(pi)
    f_krnl = fft(krnl)
    l_data = r_[data, data]
    fl_data = fft(fftshift(l_data))
    return real(ifft(f_krnl * fl_data)[:l])

def find_base(vs):
    ma = max(vs)
    mi = min(vs)
    thresh = ma * .9 + mi * .1
    me = median([v for v in vs if v > thresh])
    return mean([v for v in vs if v >= me])

def fit_rfscan(iname):
    ts, vs = array(load_pyfile(iname).data)
    base = find_base(vs)
    vs = base - vs
    me = median(vs)
    ma = max(vs)
    thresh1 = me * .9 + ma * .1
    thresh2 = me * .7 + ma * .3
    l = len(ts)

    dt = (ts[-1] - ts[0]) / (l - 1)
    t0_i = int(-ts[0] / dt)
    state = 1
    start_i = 0
    p_sections = []
    for i, v in enumerate(vs[t0_i:], start=t0_i):
        if v > thresh2:
            if state == -1:
                continue
            state = -1
            start_i = i
        elif v <= thresh1:
            if state == 1:
                continue
            if i - start_i > 15:
                p_sections.append((start_i, i))
            state = 1
    if (state == -1 and l - start_i > 15):
        max_i = argmax(vs[start_i:l]) + start_i
        if vs[max_i] > ma * .4 + me * .6 and (l - max_i) * 2 > max_i - start_i:
            p_sections.append((start_i, l))

    fitexp = curve_fit_wrapper(lambda x, a, b: a * exp(-x / b))
    pos = []
    pos_s = []
    height = []
    height_s = []
    for start, end in p_sections:
        ys = vs[start:end]
        xs = r_[start:end]
        width = (end - start) // 10
        if width < 1:
            width = 1
        y_smooth = smooth(ys, width * 2)

        max_i = argmax(y_smooth) + start
        max_i_s = width / 2
        peaks = vs[max_i - width:max_i + width + 1]
        peak = mean(peaks)
        peak_s = std(peaks) / sqrt(width * 2)

        decay = vs[max_i:end]
        decay_x = r_[:end - max_i]
        fit_res = fitexp(decay_x, decay, p0=[decay[0], (end - max_i) * 2])
        yleft = fit_res.func(r_[:l - max_i])
        vs[max_i:] -= yleft

        pos.append(ts[max_i])
        pos_s.append(dt * max_i_s)
        height.append(peak)
        height_s.append(peak_s)
    return Ret('pos', 'pos_s', 'height', 'height_s')

if __name__ == '__main__':
    import sys
    iname, oname = sys.argv[1:]
    res = fit_rfscan(iname)
    save_pyfile(res, oname)

#!/usr/bin/env python

from pylab import *
from jlab import *

def find_base(vs):
    ma = max(vs)
    mi = min(vs)
    thresh = ma * .96 + mi * 0.04
    me = median([v for v in vs if v > thresh])
    return mean([v for v in vs if v >= me])

def _next_peak_iter(data, start_i, increasing):
    if increasing:
        l = len(data)
        i_range = range(start_i, l)
    else:
        i_range = range(start_i, -1, -1)
    for i in i_range:
        yield i, data[i]

def _update_p_neg(p_i, p_v, i, v):
    if p_v > v:
        return i, v
    return p_i, p_v

def _update_p_pos(p_i, p_v, i, v):
    if p_v < v:
        return i, v
    return p_i, p_v

def _check_found_neg(p_v, v, start_v, thresh):
    thresh += p_v
    if thresh < start_v and thresh < v:
        return True
    return False

def _check_found_pos(p_v, v, start_v, thresh):
    thresh = p_v - thresh
    if thresh > start_v and thresh > v:
        return True
    return False

def find_next_peak(data, start_i, thresh, increasing=True, negetive=False):
    it = _next_peak_iter(data, start_i, increasing)
    if negetive:
        _update_p = _update_p_neg
        _check_found = _check_found_neg
    else:
        _update_p = _update_p_pos
        _check_found = _check_found_pos

    start_i, start_v = next(it)
    p_i = start_i
    p_v = start_v
    for i, v in it:
        p_i, p_v = _update_p(p_i, p_v, i, v)
        if _check_found(p_v, v, start_v, thresh):
            return p_i

def find_0peaks(vs):
    ma = max(vs)
    thresh0 = ma * .8
    thresh1 = ma * .9

    state = -1
    start_i = 0
    p_sections = []
    for i, v in enumerate(vs):
        if v > thresh1:
            if state == 1:
                continue
            state = 1
            start_i = i
        elif v <= thresh0:
            if state == -1:
                continue
            p_sections.append((start_i, i))
            state = -1

    for start, end in p_sections:
        max_i = start + argmax(vs[start:end])
        yield max_i

@curve_fit_wrapper
def fitexp(x, a, b):
    return a * exp(-x / b)

def fit_bscan(iname):
    ts, vs, zs = array(load_pyfile(iname).data)
    base = find_base(vs)
    vs = base - vs
    l = len(ts)
    dt = (ts[-1] - ts[0]) / (l - 1)
    ma = max(vs)

    peaks0 = find_0peaks(vs)
    plot(vs)
    for peak0 in peaks0:
        deep1 = find_next_peak(vs, peak0, ma / 25, True, True)
        peak0_end = deep1

        peak0_x = r_[peak0:peak0_end]
        peak0_y = vs[peak0:peak0_end]
        peak0_fit = fitexp(peak0_x, peak0_y,
                           p0=[peak0_y[0], peak0_end - peak0])
        decay_b = peak0_fit.a[1]

        peak_p1 = find_next_peak(vs, peak0_end, ma / 25, True, False)
        deep2 = find_next_peak(vs, peak_p1, ma / 25, True, True)
        peak_p2 = find_next_peak(vs, deep2, ma / 25, True, False)

        deep3 = find_next_peak(vs, peak0, ma / 25, False, True)
        peak_n1 = find_next_peak(vs, deep3, ma / 25, False, False)
        deep4 = find_next_peak(vs, peak_n1, ma / 25, False, True)
        peak_n2 = find_next_peak(vs, deep4, ma / 25, False, False)
        deep5 = find_next_peak(vs, peak_n2, ma / 25, False, True)

        for i in (deep5, deep4, deep3, deep1, deep2):
            if i is not None:
                vs[i:l] -= vs[i] * exp(-r_[:l - i] / decay_b)

        axvline(peak0, color='r')
        axvline(peak_p1, color='g')
        axvline(peak_p2, color='g')
        axvline(peak_n1, color='g')
        axvline(peak_n2, color='g')
    plot(vs, 'r', linewidth=2)
    show()

    return

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
    res = fit_bscan(iname)
    # save_pyfile(res, oname)

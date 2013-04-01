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

def find_dz(zs):
    min_i = argmin(zs)
    max_i = argmax(zs)
    l = len(zs)
    if abs(min_i - l) > abs(max_i - l):
        m_i = max_i
        negetive = True
    else:
        m_i = min_i
        negetive = False
    if m_i * 2 > l:
        increasing = False
    else:
        increasing = True
    p_i = find_next_peak(zs, m_i, (zs[max_i] - zs[min_i]) / 50,
                         increasing, negetive)
    dz = abs((zs[p_i] - zs[m_i]) / (p_i - m_i))
    return dz

def fit_bscan(iname):
    ts, vs, zs = array(load_pyfile(iname).data)
    base = find_base(vs)
    dz = find_dz(zs)
    vs = base - vs
    l = len(ts)
    dt = (ts[-1] - ts[0]) / (l - 1)
    ma = max(vs)

    peaks0 = find_0peaks(vs)
    peaks = []
    peaks_s = []
    heights = []
    heights_s = []
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
        deep6 = find_next_peak(vs, peak_p2, ma / 25, True, True)
        if deep6 is None:
            deep6 = l

        deep3 = find_next_peak(vs, peak0, ma / 25, False, True)
        peak_n1 = find_next_peak(vs, deep3, ma / 25, False, False)
        deep4 = find_next_peak(vs, peak_n1, ma / 25, False, True)
        peak_n2 = find_next_peak(vs, deep4, ma / 25, False, False)
        deep5 = find_next_peak(vs, peak_n2, ma / 25, False, True)
        if deep5 is None:
            deep5 = 0

        for i in (deep5, deep4, deep3, deep1, deep2):
            vs[i:l] -= vs[i] * exp(-r_[:l - i] / decay_b)

        peaks5 = []
        peaks5_s = []
        heights5 = []
        heights5_s = []
        for p, d in ((peak_n2, deep4), (peak_n1, deep3), (peak0, deep1),
                     (peak_p1, deep2), (peak_p2, deep6)):
            start = p
            end = (p + d) // 2
            pos = argmax(vs[start:end]) + start
            for i in range(pos, 0, -1):
                if vs[i] < vs[pos] * .95:
                    break
            width = (pos - i)
            peak_ys = vs[pos - width:pos + width + 1]
            height = mean(peak_ys)
            height_s = std(peak_ys)
            pos_s = sqrt((pos - i)**2 + (pos - p)**2) / 8

            peaks5.append(zs[pos])
            peaks5_s.append(pos_s * dz)
            heights5.append(height)
            heights5_s.append(height_s)
        peaks.append(peaks5)
        peaks_s.append(peaks5_s)
        heights.append(heights5)
        heights_s.append(heights5_s)

    return Ret('peaks', 'peaks_s', 'heights', 'heights_s')

if __name__ == '__main__':
    import sys
    iname, oname = sys.argv[1:]
    res = fit_bscan(iname)
    save_pyfile(res, oname)

#!/usr/bin/env python

from pylab import *
from jlab import *

def average_sections(data, sections):
    n = 0
    s = 0
    s2 = 0
    for start, end in sections:
        i1 = (start * 19 + end) // 20
        i2 = (start + end * 19) // 20
        if i1 >= i2:
            continue
        n += i2 - i1
        s += sum(data[i1:i2])
        s2 += sum(data[i1:i2]**2)
    m = s / n
    m2 = s2 / n
    return m, sqrt((m2 - m**2) / (n - 1))

def fit_square(res, data):
    min_v = min(data)
    max_v = max(data)
    thresh_h = min_v * .1 + max_v * .9
    thresh_l = min_v * .9 + max_v * .1
    state = 0
    start_i = 0
    l_sections = []
    h_sections = []
    for i, v in enumerate(data):
        if v < thresh_l:
            if state == -1:
                continue
            elif state == 1:
                h_sections.append((start_i, i))
            state = -1
            start_i = i
        elif v > thresh_h:
            if state == 1:
                continue
            elif state == -1:
                l_sections.append((start_i, i))
            state = 1
            start_i = i
        else:
            if state == 1:
                h_sections.append((start_i, i))
            elif state == -1:
                l_sections.append((start_i, i))
            else:
                continue
            state = 0
    if state == 1:
        h_sections.append((start_i, len(data)))
    elif state == -1:
        l_sections.append((start_i, len(data)))

    res.min_vz, res.min_vz_s = average_sections(data, l_sections)
    res.max_vz, res.max_vz_s = average_sections(data, h_sections)

def check_long_decay(p_sections):
    last_len = .1
    last_end = 0
    for s in p_sections:
        if (s[0] - last_end) < (3 * last_len):
            return False
        last_len = s[1] - s[0]
        last_end = s[1]
    return True

def get_full_sections(p_sections, vs):
    prev_i = None
    prev_w = None
    for s in p_sections:
        if not prev_i is None:
            yield prev_i, s[0], prev_w
        prev_i = s[0]
        prev_w = s[1] - s[0]
    yield prev_i, len(vs), prev_w

def fit_peaks_long_decay(p_sections, vs):
    last_len = 0
    last_end = 0
    xs = []
    ys = []
    for s in p_sections:
        start = int(last_end + 3 * last_len)
        end = int(s[0] - max((s[0] - start) * .1, 10))
        last_len = s[1] - s[0]
        last_end = s[1]
        if end <= start:
            continue
        xs += range(start, end)
        ys += list(vs[start:end])
    fit_base = fitpow(xs, ys, 2)
    all_x = r_[:len(vs)]
    base_y = vectorize(fit_base.func)(all_x)
    vs = base_y - vs
    fitexp = curve_fit_wrapper(lambda x, a, b: a * exp(-x / b))
    hs = []
    ts = []
    covs = []
    for start, end, width in get_full_sections(p_sections, vs):
        start += argmax(vs[start:end])
        end -= int((end - start) * .1)
        ys = vs[start:end]
        if ys[0] / 3 < ys[-1]:
            continue
        xs = r_[:end - start]
        fit_res = fitexp(xs, ys, p0=[ys[0], width])
        hs.append(fit_res.a[0])
        ts.append(fit_res.a[1])
        covs.append(fit_res.cov)
    return hs, ts, covs

def fit_peaks_short_decay(p_sections, vs):
    fitexp = curve_fit_wrapper(lambda x, a, b, c: c - a * exp(-x / b))
    hs = []
    ts = []
    covs = []
    for start, end, width in get_full_sections(p_sections, vs):
        start += argmin(vs[start:end])
        end = start + argmax(vs[start:end])
        ys = vs[start:end]
        xs = r_[:end - start]
        fit_res = fitexp(xs, ys, p0=[ys[-1] - ys[0], width, ys[-1]])
        hs.append(fit_res.a[0])
        ts.append(fit_res.a[1])
        covs.append(fit_res.cov)
    return hs, ts, covs

def fit_peaks(res, t_s, vs):
    min_p = min(vs)
    max_p = max(vs)
    thresh = min_p * .35 + max_p * .65
    thresh2 = min_p * .25 + max_p * .75
    state = 1
    start_i = 0
    p_sections = []
    for i, v in enumerate(vs):
        if v < thresh:
            if state == -1:
                continue
            state = -1
            start_i = i
        elif v >= thresh2:
            if state == 1:
                continue
            p_sections.append((start_i, i))
            state = 1
    if state == -1:
        p_sections.append((start_i, len(vs)))
    if check_long_decay(p_sections):
        hs, ts, covs = fit_peaks_long_decay(p_sections, vs)
    else:
        hs, ts, covs = fit_peaks_short_decay(p_sections, vs)
    h = mean(hs)
    t = mean(ts)
    cov = mean(covs, axis=0)
    cov[0][0] += std(hs)**2 / (len(hs) - 1)
    cov[1][1] += std(ts)**2 / (len(ts) - 1)

    dt = (t_s[-1] - t_s[0]) / (len(t_s) - 1)
    t *= dt
    cov[1] *= dt
    cov[:, 1] *= dt
    res.h = h
    res.tau = t
    res.h_tau_cov = cov

def fit_bswitch(iname):
    res = Ret()
    data = array(load_pyfile(iname).data)
    try:
        fit_square(res, data[2])
    except:
        pass
    fit_peaks(res, data[0], data[1])
    return res

if __name__ == '__main__':
    import sys
    iname, oname = sys.argv[1:]
    res = fit_bswitch(iname)
    save_pyfile(res, oname)

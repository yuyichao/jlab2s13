#!/usr/bin/env python

from jlab import *
from itertools import chain
from scipy.linalg import block_diag

L = .552
L_s = 0.002
c = 299792458
n = 1.0003

def cal_ratio(fit_a, fit_s):
    fsr = c / 2 / n / L
    r = abs(1 / fit_a * fsr)
    r_s = r * sqrt((fit_s / fit_a)**2 + (L_s / L)**2)
    return r, r_s

def get_coeff(line_names, names):
    return array([line_names[name] for name in names]).mean(axis=0)

def unpack_lists(l):
    return tuple(chain(*l))

def load_data(fname, line_names):
    res = load_pyfile(fname)
    fit2_a, fit2_s = res.fit2_a, res.fit2_s
    fit2_a = array(fit2_a)
    fit2_s = array(fit2_s)
    if len(fit2_s) > 1:
        fit2_s = sqrt(std(fit2_a)**2 / (len(fit2_a) - 1) +
                      sum(fit2_s**2) / len(fit2_s)**2)
        fit2_a = mean(fit2_a)
    else:
        fit2_a, = fit2_a
        fit2_s, = fit2_s
    r, r_s = cal_ratio(fit2_a, fit2_s)
    try:
        res.peaks.sort(key=lambda x: x['pos_i'])
        it = enumerate(res.peaks)
        i, p = next(it)
        prev_pos = p['pos']
        for i, p in it:
            pos = p['pos']
            if prev_pos < pos:
                break
            prev_pos = pos
        res.peaks = res.peaks[:i]
    except:
        pass
    for p in res.peaks:
        p['coeff'] = get_coeff(line_names, p['name'])
        p['pos_i'] *= -r
        p['pos_i_s'] *= r
    ps = [p['pos_i'] for p in res.peaks]
    rel_cov = diag([(p['pos_i_s'] / p['pos_i'])**2
                    for p in res.peaks]) + (r_s / r)**2
    cov = (rel_cov.T * ps).T * ps
    return res.peaks, cov

def fit_res(line_fname, inames):
    line_names = load_pyfile(line_fname)
    print(inames)
    peaks, covs = zip(*(load_data(f, line_names) for f in inames))
    peaks = [p for p in peaks if p]
    l = len(peaks)
    for i, ps in enumerate(peaks):
        ary = zeros(l - 1)
        if i != 0:
            ary[i - 1] = 1
        for p in ps:
            p['coeff'] = r_[p['coeff'], ary]
    peaks = unpack_lists(peaks)
    pos, coeff = zip(*((p['pos_i'], p['coeff']) for p in peaks))
    pos = array(pos)
    coeff = array(coeff)
    cov = block_diag(*covs)
    res = fit_lin_comb(coeff, pos, cov)
    para_a = res.a
    para_s = res.s

    # print(a_pm_s([r, r_s]))
    print(a_pm_s([para_a[:7], para_s[:7]]))
    print(a_pm_s([pos, sqrt(diag(cov))]))
    print(a_pm_s([res.b_fit, abs(res.b_e)]))
    # for p in peaks:
    #     print(p['name'], a_pm_s([-p['pos'] * r, abs(p['pos_s'] * r)]))

if __name__ == '__main__':
    import sys
    oname, line_fname, *inames = sys.argv[1:]
    res = fit_res(line_fname, inames)
    print(res)
    # save_pyfile(res, oname)

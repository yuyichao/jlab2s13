#!/usr/bin/env python

from jlab import *
from itertools import chain

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
    for p in res.peaks:
        p['coeff'] = get_coeff(line_names, p['name'])
    return res.fit_a, res.fit_s, res.peaks

def fit_res(line_fname, inames):
    line_names = load_pyfile(line_fname)
    fit_a, fit_s, peaks = zip(*(load_data(f, line_names) for f in inames))
    fit_a = array(unpack_lists(fit_a))
    fit_s = array(unpack_lists(fit_s))
    peaks = [p for p in peaks if p]
    l = len(peaks)
    for i, ps in enumerate(peaks):
        ary = zeros(l - 1)
        if i != 0:
            ary[i - 1] = 1
        for p in ps:
            p['coeff'] = r_[p['coeff'], ary]
    peaks = unpack_lists(peaks)
    pos, pos_s, coeff = zip(*((p['pos'], p['pos_s'], p['coeff']) for p in peaks))
    pos = array(pos)
    pos_s = array(pos_s)
    coeff = array(coeff)
    cov = diag(pos_s**2)
    res = fit_lin_comb(coeff, pos, cov)
    para_a = res.a
    para_s = res.s

    fit_s = sqrt(std(fit_a)**2 / (len(fit_a) - 1) +
                 sum(fit_s**2) / len(fit_s)**2)
    fit_a = mean(fit_a)

    r, r_s = cal_ratio(fit_a, fit_s)

    para_s = sqrt((para_s / para_a)**2 + (r_s / r)**2)
    para_a *= r
    para_s *= abs(para_a)
    # print(a_pm_s([r, r_s]))
    print(a_pm_s([para_a, para_s]))
    print(a_pm_s([pos, pos_s]))
    print(a_pm_s([res.b_fit, abs(res.b_e)]))
    # for p in peaks:
    #     print(p['name'], a_pm_s([-p['pos'] * r, abs(p['pos_s'] * r)]))

if __name__ == '__main__':
    import sys
    oname, line_fname, *inames = sys.argv[1:]
    res = fit_res(line_fname, inames)
    print(res)
    # save_pyfile(res, oname)

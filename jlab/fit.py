# coding=utf-8

from .general import *

from scipy.optimize import curve_fit

def fitlin(x, y, sig=None):
    x = array(x)
    y = array(y)

    l = x.size
    if sig is None:
        w = ones(l)
    else:
        w = (ones(l) / sig)**2

    wx = w * x
    wy = w * y

    wxs = sum(wx)
    wx2s = sum(wx * x)
    wys = sum(wy)
    wy2s = sum(wy * y)
    wxys = sum(wx * y)
    ws = sum(w)
    xa = wxs / ws
    x2a = wx2s / ws
    ya = wys / ws
    y2a = wy2s / ws
    xya = wxys / ws

    dx = x2a - xa**2
    dy = y2a - ya**2
    dxy = xya - xa * ya

    a = array([0, dxy / dx])
    a[0] = ya - a[1] * xa
    yfit = a[0] + a[1] * x

    if sig is None:
        chi2 = None
        ws = l * (l - 2) / sum((y - yfit)**2)
    else:
        chi2 = redchi2(y - yfit, sig, 2)

    Da = matrix(zeros([2, 2]))

    Da[1, 1] = 1 / (ws * dx)
    Da[0, 0] = Da[1, 1] * x2a
    s = sqrt(array([Da[0, 0], Da[1, 1]]))
    Da[1, 0] = Da[0, 1] = -Da[1, 1] * xa
    return Ret('a', 's', 'yfit', 'chi2', cov=Da)

def fitpow(x, y, n, sig=None):
    x = array(x)
    y = array(y)
    l = x.size

    if sig is None:
        w = ones(l)
    else:
        w = (ones(l) / sig)**2

    x_pow = ones([n + l + 1, l])

    for i in range(1, n + l + 1):
        x_pow[i] = x_pow[i - 1] * x

    wx_pow = x_pow * w
    wyx_pow = y * wx_pow[0:n + 1]

    wx_pow_s = sum(wx_pow, axis=1)
    wyx_pow_s = sum(wyx_pow, axis=1)

    p_matrix = matrix([wx_pow_s[i:i + n + 1] for i in range(0, n + 1)])

    inv_p = p_matrix**-1

    b_matrix = matrix(wx_pow[0:n + 1])

    a = inv_p * matrix(wyx_pow_s).T
    dady = array(inv_p * b_matrix)

    yfit = array(matrix(x_pow[0:n + 1]).T * a).T

    epsilon2 = (y - yfit)**2

    if sig is None:
        chi2 = None
        w = ones(l) * (l - n - 1) / sum(epsilon2)
    else:
        chi2 = sum(epsilon2 * w) / (l - n - 1)

    D2 = matrix([[sum(dady[i] * dady[j] / w) for j in range(0, n + 1)]
                for i in range(0, n + 1)])

    a = array(a).T[0]
    s = sqrt(array([D2[i, i] for i in range(0, n + 1)]))

    return Ret('a', 's', 'yfit', 'chi2', cov=D2)

def curve_fit_wrapper(fitfun):
    # http://www.physics.utoronto.ca/~phy326/python/curve_fit_to_data.py
    #     Notes: maxfev is the maximum number of func evaluations tried; you
    #               can try increasing this value if the fit fails.
    #            If the program returns a good chi-squared but an infinite
    #               covariance and no parameter uncertainties, it may be
    #               because you have a redundant parameter;
    #               try fitting with a simpler function.
    def curve_fitter(x, y, sig=None):
        popt, pcov = curve_fit(fitfun, x, y, sigma=sig)
        return Ret(a=popt, s=sqrt(diag(pcov)),
                   chi2=chi2sigma(y, fitfun(x, *popt), sig),
                   yfit=fitfun(x, *popt),
                   cov=pcov)
    return curve_fitter

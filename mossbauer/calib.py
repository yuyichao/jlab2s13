#!/usr/bin/env python

import jlab
from pylab import *

class _Calib(object):
    __slots__ = ['a', 'cov']
    def __init__(self, a=None, cov=None):
        self.a = a
        self.cov = cov
    def _init(self, fname, *index):
        l = len(index)
        if l <= 1:
            raise ValueError
        peaks, peaks_s = zip(*jlab.load_pyfile(fname).peaks)
        calib_e = _calib_e[list(index)]
        calib_cov = _calib_cov[list(index), list(index)]
        cov = matrix(zeros((l * 2, l * 2)))
        cov[:l, :l] = diag(array(peaks_s)**2)
        cov[l:, l:] = calib_cov
        if l == 2:
            self._init_2(peaks, calib_e, cov)
        else:
            self._init_n(peaks, calib_e, cov)
    def _init_2(self, peaks, calib_e, cov):
        a0 = ((peaks[1] * calib_e[0] - peaks[0] * calib_e[1]) /
              (peaks[1] - peaks[0]))
        da0 = [((peaks[1] * calib_e[0] - peaks[1] * calib_e[1]) /
               (peaks[1] - peaks[0])**2),
               ((peaks[0] * calib_e[1] - peaks[0] * calib_e[0]) /
               (peaks[1] - peaks[0])**2),
               peaks[1] / (peaks[1] - peaks[0]),
               peaks[0] / (peaks[0] - peaks[1])]
        a1 = (calib_e[1] - calib_e[0]) / (peaks[1] - peaks[0])
        da1 = [(calib_e[1] - calib_e[0]) / (peaks[1] - peaks[0])**2,
               (calib_e[0] - calib_e[1]) / (peaks[1] - peaks[0])**2,
               1 / (peaks[0] - peaks[1]),
               1 / (peaks[1] - peaks[0])]
        da = array([da0, da1])
        cov_a = da * cov * da.T
        self.a = array([a0, a1])
        self.cov = cov_a
    def _init_n(self, peaks, calib_e, cov):
        l = len(peaks)
        peaks = array(peaks)
        calib_e = array(calib_e)
        mx = mean(peaks)
        my = mean(calib_e)
        mxy = mean(calib_e * peaks)
        mxx = mean(peaks**2)
        a = array([(mxx * my - mxy * mx) / (mxx - mx**2),
                   (mxy - my * mx) / (mxx - mx**2)])
        da = zeros((2, l * 2))
        da[0, :l] = (((peaks * my - calib_e * mx) * (mxx - mx**2) -
                      (mxx * my - mxy * mx) * (peaks - 2 * mx)) /
                      (mxx - mx**2)**2 / l)
        da[0, l:] = ((mxx * calib_e - peaks * mx) / (mxx - mx**2) / l)
        da[1, :l] = (((calib_e - my) * (mxx - mx**2) -
                      (mxy - my * mx) * (calib_e - 2 * mx)) /
                      (mxx - mx**2)**2 / l)
        da[1, l:] = (peaks - mx) / (mxx - mx**2) / l
        cov_a = da * cov * da.T
        self.a = a
        self.cov = cov_a
    def _load(self, fname):
        self.a, self.cov = jlab.load_pyfile(fname)['a', 'cov']
    def _convert(_peaks_a, _peaks_s):
        _peaks_a = array(_peaks_a)
        _peaks_s = array(_peaks_s)

        peaks_e = self.a[0] + _peaks_a * self.a[1]
        peaks_2 = repeat([peaks_e], len(peaks_e), axis=0)
        peaks_cov = (self.cov[0, 0] + self.cov[0, 1] * (peaks_2 + peaks_2.T) +
                     self.cov[1, 1] * peaks_2 * peaks_2.T)
        peaks_cov += diag((_peaks_s * self.a[1])**2)
        peaks_s = sqrt(diag(peaks_cov))
        return jlab.Ret('peaks_e', 'peaks_s', 'peaks_cov')

_calib = _Calib()
_calib_data = jlab.load_pyfile('pos_cal/pos_cal.py')
_calib_e = array(_calib_data.peaks_e)
_calib_cov = array(_calib_data.peaks_cov)

def init(fname, *index):
    return _calib._init(fname, *index)

def load(fname):
    return _calib._load(fname)

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    if iname.endswith('_res.py'):
        num_file = iname[:-6] + 'num.py'
        oname = iname[:-6] + 'calib.py'
    try:
        num_file = sys.argv[2]
    except:
        pass
    try:
        oname = sys.argv[3]
    except:
        pass
    init(iname, *jlab.load_pyfile(num_file).index)
    jlab.save_pyfile(jlab.Ret(a=_calib.a, cov=_calib.cov), oname)

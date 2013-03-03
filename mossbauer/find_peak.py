#!/usr/bin/env python

import jlab
from pylab import *

calib_res = jlab.load_pyfile('pos_cal_1/res_v.py')

def smooth_diff(data, w):
    l = len(data)
    krnl_x = r_[-l:l]
    krnl = krnl_x * exp(-(krnl_x / w)**2) / w**2.5
    krnl2 = krnl**2
    f_krnl = fft(krnl)
    f_krnl2 = fft(krnl2)
    l_data = zeros(l * 2)
    l_data[:l] = data
    fl_data = fft(fftshift(l_data))
    return (real(ifft(f_krnl * fl_data)[:l]),
            sqrt(abs(ifft(f_krnl2 * fl_data)[:l])))

def find_start(it):
    i, (previous, s) = next(it)
    for i, (v, s) in it:
        if v < previous:
            return
        previous = v

def find_drop(it, thresh_area, thresh_height):
    start_i, (start_v, s) = next(it)
    min_max = start_v + s
    i = start_i
    v = start_v
    for i, (v, s) in it:
        if v - s > min_max:
            break
        new_min = v + s
        if min_max > new_min:
            min_max = new_min
    d_v = start_v - v
    if d_v > thresh_height and (i - start_i) * d_v > thresh_area:
        return start_i, i
    return None, None

def find_next(it, thresh_area, thresh_height):
    find_start(it)
    return find_drop(it, thresh_area, thresh_height)

class FindRes(object):
    __slots__ = ['a', 's', 'thresh_area', 'thresh_height']
    def __init__(self, a, s, thresh_area, thresh_height):
        self.a = a
        self.s = s
        self.thresh_area = thresh_area
        self.thresh_height = thresh_height
    def __iter__(self):
        it = enumerate(zip(self.a, self.s))
        return FindIter(it, self.thresh_area, self.thresh_height)

class FindIter(object):
    __slots__ = ['it', 'thresh_area', 'thresh_height']
    def __init__(self, it, thresh_area, thresh_height):
        self.it = it
        self.thresh_area = thresh_area
        self.thresh_height = thresh_height
    def __next__(self):
        return find_next(self.it, self.thresh_area, self.thresh_height)

def find_width(index, data, hint=None, w=30):
    a, s = smooth_diff(data, w)
    _w = w * 3
    a = a[_w:-_w]
    s = s[_w:-_w]
    index = index[_w:-_w]
    data = data[_w:-_w]
    max_a = max(a)
    min_a = min(a)
    thresh_height = (max_a - min_a) / 4 + max(s)
    thresh_area = w * (max_a - min_a) / 2
    res = [(start, end) for start, end in
           FindRes(a, s, thresh_area, thresh_height) if start is not None]
    return jlab.Ret('a', 's', 'index', 'data', peaks=res)

def find_peak(iname, fig_name):
    index, data = array([(d[0], d[2]) for d in
                         jlab.load_pyfile(iname).data[calib_res.start:]]).T
    try:
        hint = jlab.load_pyfile(iname[:-3] + '_hint.py')
    except:
        hint = None
    # filter_data = _filter_data(data)
    # filter_data = _filter_data(data, filter_data)
    # plot(index, [not v for v in filter_data] * data)
    # plot(index, data)
    res = find_width(index, data, hint, 30)
    for s, e in res.peaks:
        plot(res.index[[s, e]], res.a[[s, e]], 'g-o')
    errorbar(res.index, res.a, res.s)
    xlim(res.index[0], res.index[-1])
    figure()
    plot(res.index, res.data)
    xlim(res.index[0], res.index[-1])
    show()

if __name__ == '__main__':
    import sys
    iname, oname, fig_name = sys.argv[1:]
    res = find_peak(iname, fig_name)
    print(res)

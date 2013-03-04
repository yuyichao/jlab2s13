#!/usr/bin/env python

import jlab
from pylab import *

calib_res = jlab.load_pyfile('pos_cal_1/res_v.py')

def smooth(data, w):
    l = len(data)
    krnl_x = r_[-l:l]
    krnl = exp(-(krnl_x / w)**2) / w / sqrt(pi)
    krnl2 = krnl**2
    f_krnl = fft(krnl)
    f_krnl2 = fft(krnl2)
    l_data = r_[data, data]
    fl_data = fft(fftshift(l_data))
    return (real(ifft(f_krnl * fl_data)[:l]),
            sqrt(abs(ifft(f_krnl2 * fl_data)[:l])))

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
    end_i = start_i
    end_v = start_v
    zero_i = None
    for i, (v, s) in it:
        if v - s > min_max:
            break
        new_min = v + s
        if v < 0 and zero_i is None:
            zero_i = i
        if min_max > new_min:
            min_max = new_min
            end_i = i
            end_v = v
    d_v = start_v - end_v
    if (d_v > thresh_height and
        (end_i - start_i) * d_v > thresh_area and
        (zero_i - start_i) * 3 > (end_i - zero_i) and
        (end_i - zero_i) * 3 > (zero_i - start_i)):
        return start_i, zero_i, end_i
    return None, None, None

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

    # magic numbers
    thresh_height = (max_a - min_a) * .4 + max(s)
    thresh_area = w * (max_a - min_a) / 2

    res = [(start, zero, end) for start, zero, end in
           FindRes(a, s, thresh_area, thresh_height) if start is not None]
    return jlab.Ret('a', 's', 'index', 'data', peaks=res)

def find_exact_pos(zero, index, diff, diff_s):
    center_i = int(zero - index[0])
    l = min(center_i, len(diff) - center_i) // 2
    diff_a = (diff[center_i - l] - diff[center_i + l]) / l / 2
    for start_i in range(center_i - l, -1, -1):
        if start_i == 0 or diff[start_i - 1] - diff[start_i] < diff_a:
            break
    for end_i in range(center_i + l, len(diff)):
        if end_i == len(diff) or diff[end_i] - diff[end_i + 1] < diff_a:
            break
    fit_res = jlab.fitlin(diff[start_i:end_i], index[start_i:end_i])
    a = fit_res.a[0]
    s = sqrt((fit_res.s[0]**2 +
             (mean(diff_s[start_i:end_i]) * fit_res.a[1])**2) / 3)
    return jlab.Ret('a', 's')

def find_peak(iname, fig_name):
    index, data = array([(d[0], d[2]) for d in
                         jlab.load_pyfile(iname).data[calib_res.start:]]).T
    try:
        hint = jlab.load_pyfile(iname[:-3] + '_hint.py')
    except:
        hint = None
    res = find_width(index, data, hint, 30)

    find_exact_pos_data = array([res.index, res.a, res.s])
    peaks = [find_exact_pos(res.index[z], *find_exact_pos_data[:, s:e])
             for s, z, e in res.peaks]
    data_a, data_s = smooth(data, 20)
    m = median(data_a)
    max_s = max(data_s)
    base = mean([d for d in data_a if d > m - max_s]) - max_s

    fig1 = figure()
    plot(res.index, res.data, color='c')
    errorbar(index, data_a, data_s, color='b')
    axhline(base, color='r', linestyle='dashed', linewidth=2)
    xlim(res.index[0], res.index[-1])
    xlabel("Channel No.")
    ylabel("Count per channel")
    for peak in peaks:
        # uncertainty is multiplied by 4 or it can never be seen.
        axvline(peak.a, color='r', linestyle='dashed')
        axvline(peak.a + peak.s * 4, color='g', linestyle='dashed')
        axvline(peak.a - peak.s * 4, color='g', linestyle='dashed')
    grid()
    # show()
    savefig(fig_name + '_raw.png')
    close()

    fig2 = figure()
    errorbar(res.index, res.a, res.s)
    xlim(res.index[0], res.index[-1])
    xlabel("Channel No.")
    for peak in peaks:
        # uncertainty is multiplied by 4 or it can never be seen.
        axvline(peak.a, color='r', linestyle='dashed')
        axvline(peak.a + peak.s * 4, color='g', linestyle='dashed')
        axvline(peak.a - peak.s * 4, color='g', linestyle='dashed')
    grid()
    # show()
    savefig(fig_name + '_diff.png')
    close()

    for peak in peaks:
        cut = min(data_a) * .1 + base * .9
        try:
            start = where((index < peak.a) & (data_a > cut))[0][-1] + 1
        except:
            start = 0
        try:
            end = where((index > peak.a) & (data_a > cut))[0][0] - 1
        except:
            end = len(data_a) - 1
        center = int(peak.a - index[0])
        l = int(max(min(end - center, center - start) / 4, 30))
        start = center - l
        end = center + l
        trans_x = (index[start:end] - peak.a)**2
        trans_y = 1 / (base - data_a[start:end])
        trans_s = trans_y * (max_s / (base - data_a[start:end]))
        width_fit = jlab.fitlin(trans_x, trans_y)
        width_fit.cov[0, 0] += mean(trans_s)**2
        width_res = jlab.uncp_div(width_fit.a, cov=width_fit.cov)
        width = sqrt(width_res.a)
        width_s = width * (width_res.s / width_res.a / 2)
        peak.width = width
        peak.width_s = width_s

    return jlab.Ret('base', peaks=[list(peak['a', 's']) for peak in peaks],
                    peaks_width=[list(peak['width', 'width_s'])
                                 for peak in peaks])

if __name__ == '__main__':
    import sys
    iname = sys.argv[1]
    if iname.endswith('.py'):
        base_name = iname[:-3]
        oname = base_name + '_res.py'
        fig_name = base_name
    try:
        oname = sys.argv[2]
        fig_name = sys.argv[3]
    except:
        pass
    res = find_peak(iname, fig_name)
    jlab.save_pyfile(res, oname)

#!/usr/bin/env python

from jlab import *
import itertools

def find_region_iter(data, thresh):
    i = 0
    # end_i = find_next_peak(data, 0, thresh, True, True)
    # if end_i is not None:
    #     yield 0, end_i
    #     i = end_i
    while True:
        start_i = find_next_peak(data, i, thresh, True, False)
        if start_i is None:
            return
        end_i = find_next_peak(data, start_i, thresh, True, True)
        if end_i is None:
            yield start_i, len(data) - 1
            return
        i = end_i
        yield start_i, end_i

def _check_increasing(ys, thresh):
    it = iter(ys)
    y0 = next(it)
    for y in ys:
        if y > y0 + thresh:
            return True
        elif y < y0 - thresh:
            return False

def find_next_wave_iter(y):
    min_y = min(y)
    max_y = max(y)
    thresh = (max_y - min_y) / 10
    i = 0
    if not _check_increasing(y, thresh):
        i = find_next_peak(y, i, thresh, True, True)
        if i is None:
            return
        yield i
    while True:
        i = find_next_peak(y, i, thresh, True, False)
        if i is None:
            return
        yield i
        i = find_next_peak(y, i, thresh, True, True)
        if i is None:
            return
        yield i

def fix_min_max(m, area, data):
    start_i = max(int(m - area), 0)
    end_i = min(int(m + area), len(data))
    y = abs(data[start_i:end_i] - data[m])
    y = -y / max(y) * 3
    x = r_[start_i:end_i]
    w = exp(y)
    return int(sum(x * w) / sum(w))

def find_mid(start_i, end_i, data):
    start_v = data[start_i]
    end_v = data[end_i]
    mean_v = (start_v + end_v) / 2
    while True:
        i = (start_i + end_i) // 2
        v = data[i]
        if (mean_v < v and start_v < end_v) or (mean_v > v and start_v > end_v):
            end_i = i
            end_v = data[end_i]
        else:
            start_i = i
            start_v = data[start_i]
        if end_i - start_i < 2:
            return i

def wave_point_iter(ms, y):
    it = iter(ms)
    last_i = next(it)
    yield last_i
    for m in it:
        yield find_mid(last_i, m, y)
        yield m
        last_i = m

def fit_wave(x, y):
    min_max_s = [m for m in find_next_wave_iter(y) if m > 50]
    distance = (min_max_s[-1] - min_max_s[0]) / (len(min_max_s) - 1)
    area = distance / 6
    min_max_s = (fix_min_max(m, area, y) for m in min_max_s)
    points = list(wave_point_iter(min_max_s, y))
    fit_y = x[points]
    fit_x = arange(len(points))
    fitres = fitlin(fit_x, fit_y)
    return fitres.a[1] * 4, fitres.s[1] * 4

def fit_scan(start_i, end_i, data, regions):
    interesting_regions = [(int(max(r_start, start_i)), int(max(r_end, end_i)))
                           for (r_start, r_end) in regions
                           if r_end > start_i and r_start < end_i]
    if not interesting_regions:
        return
    fit_a, fit_s = fit_wave(data[4][start_i:end_i], data[1][start_i:end_i])
    return fit_a, fit_s, interesting_regions

def combine_regions(data_name, region_name):
    data = array(load_pyfile(data_name).data)
    regions = load_pyfile(region_name).region
    scan = data[4]
    scan_max = max(scan)
    scan_min = min(scan)

    diff = scan_max - scan_min

    tilt_scan = r_[0:diff:(len(scan) * 1j)] + scan

    scan_regions = list(find_region_iter(tilt_scan, diff / 50))

    it = (fit_scan(start_i, end_i, data, regions)
          for (start_i, end_i) in scan_regions)
    it = tuple(v for v in it if v is not None)
    if not it:
        return {}
    fit_a, fit_s, interesting_regions = zip(*it)
    interesting_regions = tuple(itertools.chain(*interesting_regions))
    return Ret('fit_a', 'fit_s', 'interesting_regions')

if __name__ == '__main__':
    import sys
    data_name, region_name, oname = sys.argv[1:]
    res = combine_regions(data_name, region_name)
    save_pyfile(res, oname)

#!/usr/bin/env python

from jlab import *

def cal_peak(name, pos, pos_s, data):
    scan = data[4]
    pos_v = scan[int(pos)]
    for i in range(int(pos), len(scan)):
        if abs(pos_v - scan[i]) > 0.001:
            dv = abs(scan[i] - pos_v)
            end_i = i
            break
    for i in range(int(pos), 0, -1):
        if abs(pos_v - scan[i]) > 0.001:
            dv = abs(scan[i] - pos_v)
            start_i = i
            break
    d = end_i - start_i
    start_i -= 5 * d
    end_i += 5 * d

    xfit = r_[start_i:end_i]
    yfit = scan[start_i:end_i]

    fitres = fitlin(xfit, yfit)

    pos_s = sqrt((dv / 4)**2 +
                 (fitres.func(pos + pos_s) - fitres.func(pos - pos_s))**2)
    pos = fitres.func(pos)

    return Ret('name', 'pos_s', 'pos')

def combine_for_peak(data_fname, combine_fname, peaks_fname,
                     peak_names_fname, line_fname):
    data = array(load_pyfile(data_fname).data)
    combine_data = load_pyfile(combine_fname)
    peaks = load_pyfile(peaks_fname).peaks_types
    peak_names = load_pyfile(peak_names_fname).peak_names
    line_names = load_pyfile(line_fname)

    fit_a = combine_data.fit_a
    fit_s = combine_data.fit_s

    peaks = [cal_peak(name, pos, pos_s, data)
             for ((pos, pos_s), name)
             in zip(peaks, peak_names)
             if name]

    return Ret('fit_a', 'fit_s', 'peaks')

if __name__ == '__main__':
    import sys
    (data_fname, combine_fname, peaks_fname,
     peak_names_fname, line_fname, oname) = sys.argv[1:]
    res = combine_for_peak(data_fname, combine_fname, peaks_fname,
                           peak_names_fname, line_fname)
    save_pyfile(res, oname)

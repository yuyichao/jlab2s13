#!/usr/bin/env python

from jlab import *

def select_peaks(data_name, combine_name):
    data = array(load_pyfile(data_name).data)
    regions = load_pyfile(combine_name).interesting_regions
    peaks = []
    for start_i, end_i in regions:
        xs = r_[start_i:end_i]
        plot(xs, data[2][start_i:end_i])
        plot(xs, data[3][start_i:end_i])
        plot(xs, (data[3] - data[2])[start_i:end_i])
        title(data_name)
        selector = RegionSelect()
        for rect in selector.run():
            peaks.append((rect.x1, rect.x2))
    return peaks

if __name__ == '__main__':
    import sys
    data_name, combine_name, oname = sys.argv[1:]
    peaks_region = select_peaks(data_name, combine_name)
    save_pyfile(Ret('peaks_region'), oname)

#!/usr/bin/env python

from jlab import *

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

def _line_id_to_name(name):
    f, g, e = name[1:].split('_')
    return r"$(%s \rightarrow %s)_{%s}$" % (g, e, f)

def line_ids_to_name(names):
    return '+'.join(_line_id_to_name(name) for name in names)

def plot_region(data, peaks, start_i, savefunc):
    pc = len(peaks)
    t = data[0]
    max_t = max(t)
    min_t = min(t)
    d = data[3]
    plot(t, d, lw=2)
    diff = max(d) - min(d)
    for i, p in enumerate(peaks):
        pos = int(p['pos_i']) - start_i
        corr = t[pos], d[pos]
        text_corr = corr[0], corr[1] + diff / 10
        annotate(i + 1, xy=corr, xytext=text_corr,
                 arrowprops={'facecolor': 'black', 'shrink': 0.1,
                             'width': 2, 'headwidth': 4},
                 horizontalalignment='center', verticalalignment='buttom')
    xlabel("Scan time/s")
    ylabel("Intensity (with offset)")
    xlim(min_t, max_t)
    subplots_adjust(right=.7)
    ax = axes([.72, .1, .25, .8])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.text(0.04, 0.5, '\n'.join([str(i + 1) + ': ' + line_ids_to_name(p['name'])
                                 for i, p in enumerate(peaks)]),
            transform=ax.transAxes, fontsize=14,
            verticalalignment='center', horizontalalignment='left')
    savefunc('probe')

    d = data[2]
    plot(t, d, lw=2)
    xlabel("Scan time/s")
    ylabel("Intensity (with offset)")
    xlim(min_t, max_t)
    savefunc('ref')

    d = data[3] - data[2]
    plot(t, d, lw=2)
    diff = max(d) - min(d)
    for i, p in enumerate(peaks):
        pos = int(p['pos_i']) - start_i
        corr = t[pos], d[pos]
        text_corr = corr[0], corr[1] + diff / 10
        annotate(i + 1, xy=corr, xytext=text_corr,
                 arrowprops={'facecolor': 'black', 'shrink': 0.1,
                             'width': 2, 'headwidth': 4},
                 horizontalalignment='center', verticalalignment='buttom')
    xlabel("Scan time/s")
    ylabel("Intensity Difference")
    xlim(min_t, max_t)
    subplots_adjust(right=.7)
    ax = axes([.72, .1, .25, .8])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.text(0.04, 0.5, '\n'.join([str(i + 1) + ': ' + line_ids_to_name(p['name'])
                                 for i, p in enumerate(peaks)]),
            transform=ax.transAxes, fontsize=14,
            verticalalignment='center', horizontalalignment='left')
    savefunc('balance')

def plot_data(data_name, peaks_name, fprefix):
    peaks = load_pyfile(peaks_name).peaks
    if not peaks:
        return
    peaks.sort(key=lambda x: x['pos_i'])
    data = array(load_pyfile(data_name).data)
    scan = data[4]
    scan_max = max(scan)
    scan_min = min(scan)

    diff = scan_max - scan_min

    tilt_scan = r_[0:diff:(len(scan) * 1j)] + scan

    def savefunc(name):
        savefig(fprefix + '_' + name +
                ('' if i == 0 else '_' + str(i)) + '.png')
        close()

    for i, (start_i, end_i) in enumerate(find_region_iter(tilt_scan,
                                                          diff / 50)):
        ps = []
        for p in peaks:
            if start_i < p['pos_i'] < end_i:
                ps.append(p)
        if not ps:
            continue
        plot_region(data[:, start_i:end_i], ps, start_i, savefunc)

if __name__ == '__main__':
    import sys
    data_name, peaks_name, fprefix = sys.argv[1:]
    plot_data(data_name, peaks_name, fprefix)

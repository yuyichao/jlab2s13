#!/usr/bin/env python

from jlab import *
from os import path as _path
from matplotlib.widgets import CheckButtons

class PeakIdentifier:
    def __click_cb(self, label):
        self.all_names[label] = not self.all_names[label]
    def __init_fig__(self, data_name):
        self.fig = figure()
        self.ax = subplot(111)
        self.fig.subplots_adjust(left=0.3)
        title(_path.basename(data_name))
        self.button_ax = plt.axes([0.05, 0.1, 0.15, 0.8])
        self.check = CheckButtons(self.button_ax, sorted(self.all_names.keys()),
                                  [False] * len(self.all_names))
        self.check.on_clicked(self.__click_cb)
    def __init_data__(self, data, start_i, end_i, pos, pos_s):
        start_i = int(start_i)
        end_i = int(end_i) + 1
        self.start_i = start_i
        self.end_i = end_i
        self.__pos = pos
        self.__pos_s = pos_s
        self.d = end_i - start_i
        new_start = start_i - 10 * self.d
        if new_start < 0:
            new_start = 0
        new_end = end_i + 10 * self.d
        if new_end >= len(data[2]):
            new_end = len(data[2] - 1)
        self.new_start = new_start
        self.new_end = new_end
        self.xs = r_[self.new_start:self.new_end]
        y1 = data[2][new_start:new_end]
        y2 = data[3][new_start:new_end]
        self.y = y2 - y1

    def __init_plot__(self):
        self.ax.axvline(self.__pos, color='m', linewidth=2)
        self.ax.axvline(self.__pos - self.__pos_s, color='g')
        self.ax.axvline(self.__pos + self.__pos_s, color='g')

        self.ax.plot(self.xs, self.y, color='c')

        self.ax.set_ylim(min(self.y), max(self.y))
        self.ax.set_xlim(self.new_start, self.new_end)
    def __init_names__(self, names):
        self.all_names = {}
        for n in names:
            self.all_names[n] = False

    def __init__(self, names, data, start_i, end_i, data_name, pos, pos_s):
        self.__init_names__(names)
        self.__init_fig__(data_name)
        self.__init_data__(data, start_i, end_i, pos, pos_s)
        self.__init_plot__()
    def run(self):
        show()
        close()
        return [k for k, v in self.all_names.items() if v]

def identify_peaks(data_name, peaks_region_name, peaks_name, line_names):
    data = array(load_pyfile(data_name).data)
    peaks_regions = load_pyfile(peaks_region_name).peaks_region
    peaks = load_pyfile(peaks_name).peaks_types
    line_names = sorted(load_pyfile(line_names).keys())
    return [PeakIdentifier(line_names, data, start_i, end_i,
                           data_name, pos, pos_s).run()
            for ((start_i, end_i), (pos, pos_s))
            in zip(peaks_regions, peaks)]

if __name__ == '__main__':
    import sys
    data_name, peaks_region_name, peaks_name, line_names, oname = sys.argv[1:]
    peak_names = identify_peaks(data_name, peaks_region_name,
                                peaks_name, line_names)
    save_pyfile(Ret('peak_names'), oname)

#!/usr/bin/env python

from jlab import *
from os import path as _path

class PeakClassifier:
    def __get_peak_pos(self, x, y, r=3):
        l = len(x)
        y = max(y) - y
        y = -y / max(y) * 3
        w = exp(y)
        xm = sum(x * w) / sum(w)
        xs = sqrt(sum((x - xm)**2 * w) / sum(w) / (len(x) - 1))
        return xm, xs
    def __big_cb(self, e):
        self.big = True
    def __small_cb(self, e):
        self.big = False
    def __init_fig__(self, data_name):
        self.fig = figure()
        self.ax = subplot(111)
        self.fig.subplots_adjust(bottom=0.2)
        title(_path.basename(data_name))
        self.ax_big = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.ax_small = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.big_button = Button(self.ax_big, 'Big')
        self.small_button = Button(self.ax_small, 'Small')
        self.big_button.on_clicked(self.__big_cb)
        self.small_button.on_clicked(self.__small_cb)
    def __init_data__(self, data, start_i, end_i):
        start_i = int(start_i)
        end_i = int(end_i) + 1
        self.start_i = start_i
        self.end_i = end_i
        self.d = end_i - start_i
        new_start = start_i - 3 * self.d
        if new_start < 0:
            new_start = 0
        new_end = end_i + 3 * self.d
        if new_end >= len(data[2]):
            new_end = len(data[2] - 1)
        self.new_start = new_start
        self.new_end = new_end
        self.xs = r_[self.new_start:self.new_end]
        self.y1 = data[2][new_start:new_end]
        self.y2 = data[3][new_start:new_end]
        self.y3 = self.y2 - self.y1

        x4 = r_[start_i:end_i]
        y4 = data[3][start_i:end_i] - data[2][start_i:end_i]
        xfit = r_[x4[:int(self.d / 4)], x4[-int(self.d / 4):]]
        yfit = r_[y4[:int(self.d / 4)], y4[-int(self.d / 4):]]
        fitres = fitlin(xfit, yfit)

        self.y4 = self.y3 - fitres.func(self.xs)

        self.__big_pos, self.__big_s = self.__get_peak_pos(x4, y4, 10)
        small_x = x4[self.d // 5:self.d * 4 // 5]
        small_y = y4[self.d // 5:self.d * 4 // 5] - fitres.func(small_x)
        self.__small_pos, self.__small_s = self.__get_peak_pos(small_x,
                                                               small_y, 2)

    def __init_plot__(self):
        self.ax.axvline(self.start_i, color='c', linewidth=2)
        self.ax.axvline(self.end_i, color='c', linewidth=2)
        self.__blines = [
            self.ax.axvline(self.__big_pos, color='m', linewidth=2),
            self.ax.axvline(self.__big_pos - self.__big_s, color='g'),
            self.ax.axvline(self.__big_pos + self.__big_s, color='g')]
        self.__slines = [
            self.ax.axvline(self.__small_pos, color='m', linewidth=2),
            self.ax.axvline(self.__small_pos - self.__small_s, color='g'),
            self.ax.axvline(self.__small_pos + self.__small_s, color='g')]
        self.p3, = self.ax.plot(self.xs, self.y3, 'r', linewidth=2)
        self.p4, = self.ax.plot(self.xs, self.y4, 'r', linewidth=2)
        self.big = True
        self.ax.set_ylim(min(min(self.y3), min(self.y4)),
                         max(max(self.y3), max(self.y4)))

    @property
    def big(self):
        return self.__big
    @big.setter
    def big(self, value):
        value = bool(value)
        if self.__big == value:
            return
        self.__big = value
        if value:
            self.p3.set_visible(True)
            self.p4.set_visible(False)
            for l in self.__blines:
                l.set_visible(True)
            for l in self.__slines:
                l.set_visible(False)
            self.ax.set_xlim(self.new_start, self.new_end)
        else:
            self.p4.set_visible(True)
            self.p3.set_visible(False)
            for l in self.__slines:
                l.set_visible(True)
            for l in self.__blines:
                l.set_visible(False)
            self.ax.set_xlim(self.start_i - self.d, self.end_i + self.d)
        plt.draw()
    @property
    def pos(self):
        if self.__big:
            return self.__big_pos
        return self.__small_pos
    @property
    def pos_s(self):
        if self.__big:
            return self.__big_s
        return self.__small_s

    def __init__(self, data, start_i, end_i, data_name):
        self.__big = False
        self.__init_fig__(data_name)
        self.__init_data__(data, start_i, end_i)
        self.__init_plot__()
    def run(self):
        show()
        close()
        return self.pos, self.pos_s

def classify_peaks(data_name, peaks_name):
    data = array(load_pyfile(data_name).data)
    peaks_regions = load_pyfile(peaks_name).peaks_region
    return [PeakClassifier(data, start_i, end_i, data_name).run()
            for (start_i, end_i) in peaks_regions]

if __name__ == '__main__':
    import sys
    data_name, peaks_name, oname = sys.argv[1:]
    peaks_types = classify_peaks(data_name, peaks_name)
    save_pyfile(Ret('peaks_types'), oname)

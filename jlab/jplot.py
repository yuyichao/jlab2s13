# coding=utf-8

# Copyright 2013~2013 by Yu Yichao
# yyc1992@gmail.com
#
# This file is part of Jlab.
#
# Jlab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jlab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jlab.  If not, see <http://www.gnu.org/licenses/>.

from .general import *

class SelectionRect:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.set(x1, y1, x2, y2)

    def set(self, x1=0, y1=0, x2=0, y2=0):
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2

    def get_handle(self, x, y, threshx, threshy):
        if (x < self.x1 - threshx or x > self.x2 + threshx or
            y < self.y1 - threshy or y > self.y2 + threshy):
            return
        dx = abs(self.__x1 - x), abs(self.__x2 - x)
        dy = abs(self.__y1 - y), abs(self.__y2 - y)
        if dx[0] < dx[1] and dx[0] < threshx:
            old_x1 = self.__x1
            def setx(new_x):
                self.__x1 = new_x - x + old_x1
        elif dx[1] <= dx[0] and dx[1] < threshx:
            old_x2 = self.__x2
            def setx(new_x):
                self.__x2 = new_x - x + old_x2
        else:
            setx = None
        if dy[0] < dy[1] and dy[0] < threshy:
            old_y1 = self.__y1
            def sety(new_y):
                self.__y1 = new_y - y + old_y1
        elif dy[1] <= dy[0] and dy[1] < threshy:
            old_y2 = self.__y2
            def sety(new_y):
                self.__y2 = new_y - y + old_y2
        elif setx is None:
            return
        else:
            sety = lambda new_y: None
        if setx is None:
            setx = lambda new_x: None
        def set_func(new_x, new_y):
            setx(new_x)
            sety(new_y)
        return set_func
    @property
    def x1(self):
        return min(self.__x1, self.__x2)
    @property
    def y1(self):
        return min(self.__y1, self.__y2)
    @property
    def x2(self):
        return max(self.__x1, self.__x2)
    @property
    def y2(self):
        return max(self.__y1, self.__y2)

class RegionSelect:
    def __init__(self, ax=None):
        if ax is None:
            ax = gca()
        self.ax = ax
        self.__boxes = []
        canvas = ax.figure.canvas
        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('key_release_event', self.key_release_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas
        self.init()

    def init(self):
        self.rects = []
        self.motion_handler = None
        self.pressed_keys = set()

    def run(self):
        self.init()
        show()
        return self.rects

    def __new_box(self):
        rect = Rectangle((0, 0), 0, 0,
                         fill=False, ls='dashed', lw=1, animated=True)
        self.ax.add_patch(rect)
        return rect

    def update_box(self):
        if len(self.__boxes) < len(self.rects):
            for i in range(len(self.rects) - len(self.__boxes)):
                self.__boxes.append(self.__new_box())
        for i, rect in enumerate(self.rects):
            self.__boxes[i].set_bounds(rect.x1, rect.y1,
                                       rect.x2 - rect.x1,
                                       rect.y2 - rect.y1)

    def key_press_callback(self, event):
        key = self._getkey(event)
        self.pressed_keys.add(key)

    def key_release_callback(self, event):
        key = self._getkey(event)
        try:
            self.pressed_keys.remove(key)
        except:
            pass

    def __draw_boxes(self):
        for i, rect in enumerate(self.rects):
            self.ax.draw_artist(self.__boxes[i])

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.__draw_boxes()
        self.canvas.blit(self.ax.bbox)

    def redraw(self):
        self.update_box()
        self.canvas.restore_region(self.background)
        self.__draw_boxes()
        self.canvas.blit(self.ax.bbox)

    def get_thresh(self):
        width, height = self.canvas.get_width_height()
        x1, x2 = self.ax.get_xlim()
        y1, y2 = self.ax.get_ylim()
        return 5 * abs(x1 - x2) / width,  5 * abs(y1 - y2) / height

    def __find_rect(self, x, y):
        thresh = self.get_thresh()
        for i, rect in enumerate(self.rects):
            setter = rect.get_handle(x, y, *thresh)
            if not setter is None:
                return i, setter
        return -1, None

    def button_press_callback(self, event):
        try:
            if event.xdata is None or event.ydata is None:
                return
            x, y = event.xdata, event.ydata
        except:
            return
        if 'alt' in self.pressed_keys:
            i, s = self.__find_rect(x, y)
            if i < 0:
                return
            self.rects.pop(i)
        elif 'control' in self.pressed_keys:
            i, s = self.__find_rect(x, y)
            if s is None:
                return
            self.motion_handler = s
        else:
            rect = SelectionRect(x, y, x, y)
            def setter(new_x, new_y):
                rect.set(x, y, new_x, new_y)
            self.rects.append(rect)
            self.motion_handler = setter
        self.redraw()

    def button_release_callback(self, event):
        self.motion_handler = None

    def _getkey(self, event):
        if event.key.endswith('+'):
            return '+'
        return event.key.split('+')[-1]

    def motion_notify_callback(self, event):
        if self.motion_handler is None:
            return
        try:
            if event.xdata is None or event.ydata is None:
                return
            x, y = event.xdata, event.ydata
        except:
            return
        self.motion_handler(x, y)
        self.redraw()

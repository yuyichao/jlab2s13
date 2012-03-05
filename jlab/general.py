# coding=utf-8

# Copyright 2012 Yu Yichao, Rudy H Tanin
# yyc1992@gmail.com
# rudyht@gmail.com
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

from __future__ import print_function
from pylab import *
from scipy.interpolate import spline #for smooth plot
import os
from os import path
import sys
import inspect

# http://utcc.utoronto.ca/~cks/space/blog/python/EmulatingStructsInPython
class Ret(object):
    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '__dict__', {})
        for arg in args:
            try:
                self._a(**arg)
            except:
                frame = inspect.currentframe().f_back
                pair = {arg: eval(arg, frame.f_globals, frame.f_locals)}
                self._a(**pair)
        self._a(**kwargs)
    def _a(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v
        return self
    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        real = False
        try:
            object.__getattribute__(self, key)
            real = True
        except AttributeError:
            self.__dict__[key] = value
        if real:
            raise AttributeError
    def __delattr__(self, name):
        pass
    def __getitem__(self, keys):
        if issubclass(type(keys), str):
            return self.__dict__[keys]
        res = ()
        for k in keys:
            res += (getattr(self, k, None),)
        return res
    def __setitem__(self, keys, items):
        if type(keys) == type(()):
            for i in range(0, len(keys)):
                setattr(self, keys[i], items[i])
            return
        setattr(self, keys, items)
    def __delitem__(self, name):
        pass
    def __repr__(self):
        return "Ret(%s)" % self.__dict__
    def __str__(self):
        return str(self.__dict__)

    def keys(self):
        return self.__dict__.keys()
    def items(self):
        return self.__dict__.items()
    def values(self):
        return self.__dict__.values()

def a_pm_s(a_s, unit='', sci=None):
    try:
        a = a_s.a
        s = a_s.s
    except AttributeError:
        try:
            a = a_s[0]
            s = a_s[1]
        except KeyError:
            a = a_s['a']
            s = a_s['s']

    try:
        a = [i for i in a]
        l = len(a)
    except TypeError:
        a = [a]
        l = 1

    try:
        s = [i for i in s]
    except TypeError:
        s = [s]

    if len(s) < l:
        s += [0] * (l - len(s))

    if type(unit) == type(''):
        unit = [unit] * l
    else:
        try:
            unit = [u for u in unit]
        except TypeError:
            unit = [unit] * l

    if len(unit) < l:
        unit += [''] * (l - len(unit))
    if l == 1:
        return _a_pm_s(a[0], s[0], unit[0], sci)
    return array([_a_pm_s(a[i], s[i], unit[i], sci) for i in range(0, l)])

def _a_pm_s(a, s, unit, sci):
    '''input: observable,error
       output: formatted observable +- error in scientific notation'''
    if s <= 0:
        return '%f%s' % (a, unit)

    if sci == None:
        if s < 100 and (abs(a) > 1 or s > 1):
            sci = False
        else:
            sci = True

    la = int(floor(log10(abs(a))))
    ls = int(floor(log10(s)))
    fs = floor(s * 10**(1 - ls))
    if sci:
        fa = a * 10**-la
        dl = la - ls + 1
    else:
        fa = a
        dl = 1 - ls
    dl = dl if dl > 0 else 0

    if dl == 1:
        ss = '%.1f' % (fs / 10)
    else:
        ss = '%.0f' % fs

    if sci:
        return ('%.' + ('%d' % dl) + 'f(%s)*10^%d%s') % (fa, ss, la, unit)
    else:
        return ('%.' + ('%d' % dl) + 'f(%s)%s') % (fa, ss, unit)

def smoothplot(x, y, *args, **kwargs):
    '''because pylab doesn't know how to plot smoothly out of the box yet'''
    # http://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot
    # wrapper for plot to make it smooth
    xnew = np.linspace(x.min(), x.max(), 300)
    ynew = spline(x, y, xnew)
    return plot(xnew, ynew, *args, **kwargs)

def chi2sigma(y, expectedy, sig):
    '''chi2 but with sigma instead of expected value as denominator'''
    return sum(((y - expectedy) / sig) ** 2)

def redchi2(delta, sigma, n):
    '''chi2/dof'''
    return sum((delta / sigma)**2) / (delta.size - n)

def obj2ret(obj):
    ret = Ret()
    for name in dir(obj):
        if not name.startswith('__'):
            ret[name] = getattr(obj, name)
    return ret

def py2ret(fname):
    dir_name = path.dirname(path.abspath(fname))
    name, ext = path.splitext(path.basename(fname))
    if ext != '.py':
        return None
    if dir_name:
        sys.path.insert(0, dir_name)
        mod = __import__(name)
        del sys.path[0]
    return obj2ret(mod)

# coding=utf-8

# Copyright 2012~2012 by Rudy H Tanin
# rudyht@gmail.com
# Copyright 2012~2013 by Yu Yichao
# yyc1992@gmail.com
# Copyright 2013~2013 by Giacomo Resta
# gresta@mit.edu
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
from numpy import power
from scipy.interpolate import spline #for smooth plot
import os
from os import path
import sys
import inspect

# stolen from https://github.com/gak/automain
def automain(func):
    '''
    Limitation: the main function can only be defined at the end of the file.
    '''
    parent = inspect.currentframe().f_back
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        func()
    return func

class Ret(dict):
    def __init__(self, *args, **kwargs):
        for arg in args:
            try:
                self._a(**arg)
            except:
                frame = inspect.currentframe().f_back
                try:
                    self[arg] = frame.f_locals[arg]
                except:
                    self[arg] = frame.f_globals[arg]
        self._a(**kwargs)
    def _a(self, **kwargs):
        self.update(kwargs)
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value
    def __delattr__(self, name):
        del self[name]
    def __getitem_iter__(self, keys):
        for k in keys:
            yield dict.__getitem__(self, k)
    def __getitem__(self, keys):
        if isscalar(keys):
            return dict.__getitem__(self, keys)
        return self.__getitem_iter__(keys)
    def __setitem__(self, keys, items):
        if isscalar(keys):
            dict.__setitem__(self, keys, items)
            return
        for k, v in zip(keys, items):
            dict.__setitem__(self, k, v)
    def __dir__(self):
        return list(self.keys()) + dict.__dir__(self)

def a_pm_s(a_s, unit='', sci=None, tex=False):
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
        return _a_pm_s(a[0], s[0], unit[0], sci, tex)
    return array([_a_pm_s(a[i], s[i], unit[i], sci, tex) for i in range(0, l)])

def _a_pm_s(a, s, unit, sci, tex):
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
        if tex:
            return (('%.' + ('%d' % dl) + r'f(%s)\times10^{%d}{%s}') %
                    (fa, ss, la, unit))
        else:
            return ('%.' + ('%d' % dl) + 'f(%s)*10^%d%s') % (fa, ss, la, unit)
    else:
        return ('%.' + ('%d' % dl) + 'f(%s)%s') % (fa, ss, unit)

# Don't use when plotting a function.
# And probably don't need to use when plotting data.
def smoothplot(x, y, *args, **kwargs):
    """because pylab doesn't know how to plot smoothly out of the box yet"""
    # http://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot
    # wrapper for plot to make it smooth
    xnew = np.linspace(x.min(), x.max(), 300)
    ynew = spline(x, y, xnew)
    return plot(xnew, ynew, *args, **kwargs)

def redchi2(delta, sigma, n):
    '''chi2 / dof'''
    return sum((delta / sigma)**2) / (delta.size - n)

_nan = float('nan')

def load_pyfh(fh, fname=''):
    gs = {'nan': _nan}
    ls = {}
    exec(compile(fh.read() + "\n", fname, 'exec'), gs, ls)
    return Ret(ls)

def load_pyfile(fname):
    '''
    Read the namespace of a file to a Ret object.
    '''
    with open(fname, "r") as fh:
        return load_pyfh(fh, fname)

def __numpy_repr(obj):
    if isscalar(obj):
        return repr(obj)
    elif isinstance(obj, dict):
        return '{%s}' % ', '.join((repr(key) + ': ' + __numpy_repr(value))
                                  for (key, value) in obj.items())
    else:
        return '[%s]' % ', '.join(__numpy_repr(value) for value in array(obj))

def save_pyfh(obj, fh):
    for key in obj:
        fh.write("%s = %s\n" % (key, __numpy_repr(obj[key])))

def save_pyfile(obj, fname):
    '''
    Save members of a iterable object to a file.
    '''
    with open(fname, "w") as fh:
        save_pyfh(obj, fh)

def frel2abs(rel_fname):
    """
    Turn a filename relative to caller's file location to absolute path.
    Directly return if it is already an absolute path.
    """
    if path.isabs(rel_fname):
        return rel_fname
    import inspect
    f = inspect.currentframe().f_back
    try:
        caller_f = eval('__file__', f.f_globals, f.f_locals)
        dirname = path.dirname(path.abspath(caller_f))
    except NameError:
        dirname = '.'
    return path.abspath('%s/%s' % (dirname, rel_fname))

# FIXME also return lambda in fit functions
def showfit(data, fitobj):
    '''
    Just because plotting scatter(data) and plot(x, yfit)
    simultaneously is a very often-used idiom
    '''
    x, y, s = data
    errorbar(x, y, s, fmt='o')
    plot(fitobj.x, fitobj.yfit)

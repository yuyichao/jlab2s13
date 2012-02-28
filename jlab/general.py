# coding=utf-8
from __future__ import print_function
from pylab import *
from scipy.interpolate import spline #for smooth plot

# http://utcc.utoronto.ca/~cks/space/blog/python/EmulatingStructsInPython
class Ret:
    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '__dict__', {})
        for arg in args:
            self._a(**arg)
        self._a(**kwargs)
    def _a(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
        return self
    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    def __getitem__(self, keys):
        if issubclass(type(keys), str):
            return self.__dict__[keys]
        res = ()
        for k in keys:
            res += (getattr(self, k, None),)
        return res
    def __setitem__(self, keys, items):
        try:
            items.__getitem__
        except:
            setattr(self, keys[0], items)
            return
        for i in range(0, len(keys)):
            try:
                setattr(self, keys[i], items[i])
            except IndexError:
                break
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

    # FIXME, remove these~~
    def show(self):
        for i in zip(*(self.a, self.s)):
            print( "  %.03f ± %.03f     " % i, end='')
        print("   chi2 %.03f" % self.chi2)
    def aands(self, index):
        return array((self.a, self.s)).T[index]
    def stras(self, index):
        return str("  %.03f ± %.03f  " % tuple(self.aands(index)))


def a_pm_s(a_s, unit=''):
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

    try:
        unit = [u for u in unit]
    except TypeError:
        unit = [unit]

    if len(unit) < l:
        unit += [''] * (l - len(unit))
    return array([_a_pm_s(a[i], s[i], unit[i]) for i in range(0, l)])

def _a_pm_s(a, s, unit):
    if s <= 0:
        return '%f%s' % (a, unit)

    if s < 100 and (a > 0 or s > 0):
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
    # http://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot
    # wrapper for plot to make it smooth
    xnew = np.linspace(x.min(), x.max(), 300)
    ynew = spline(x, y, xnew)
    return plot(xnew, ynew, *args, **kwargs)

def chi2sigma(y, expectedy, sig):
    '''chi2 but with sigma instead of expected value as denominator'''
    return sum(((y - expectedy) / sig) ** 2)

def redchi2(delta, sigma, n):
    return sum((delta / sigma)**2) / (delta.size - n)

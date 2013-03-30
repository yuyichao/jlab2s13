'''
A python script with useful functions for 8.13 at MIT.

To use it for a single script, place it in the directory where your
script is. To use it for any python script, place it in a directory
(i.e.  ~/scripts/python) and then add the following line to your
~/.bashrc file.

export PYTHONPATH=$PYTHONPATH:$HOME/scripts/python

Where $HOME/scripts/python is for the ~/scripts/python directory

Now you can now import and use the module with the following,
  >>> import jlab as j
  >>> j.__version__
'''

from __future__ import division
import numpy as _np
import numpy.linalg as _npla
import math as _math
import unicodedata as _unicodedata

import sympy as _sy
import re as _re

__version__ = 'pre_release'

class Bundle:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def greek(name):
    ''' Returns unicode for greek letters
    Example:
    >>> print greek('nu')
    >>> print greek('lamda')
    '''
    return _unicodedata.lookup('GREEK SMALL LETTER '+name.upper())

def sup(integer):
    ''' Returns unicode for superscript of integer numbers
    Example:
    >>> print '10'+sup(2)
    '''
    digits = {'-':'MINUS', '1':'ONE', '2':'TWO', '3':'THREE', '4':'FOUR',
         '5':'FIVE', '6':'SIX', '7':'SEVEN', '8':'EIGHT', '9':'NINE',
         '0':'ZERO'}
    return ''.join([_unicodedata.lookup('SUPERSCRIPT '+digits[i])
                                   for i in list('%i'%(integer))])

def mean(data):
    ''' Returns the mean of a 1d array '''
    data = _np.array(data)
    return _np.sum(data)/len(data)

def std(data):
    ''' Returns the standard deviation of a 1d array.
    Different from numpy.std in that it divides by 1/(N-1) instead of 1/N.
    '''
    data = _np.array(data)
    return _np.sqrt(1./(len(data) - 1)*_np.sum((data-mean(data))**2))

def error(data):
    ''' Computes error associated with mean of Gaussian
    distributed 1d array'''
    data = _np.array(data)
    return std(data)/_np.sqrt(len(data))

def weighted_mean(x_mean, x_error):
    '''
    Computes weighted mean and combined error of a series of measurements
    x_mean - 1d array with means of a series of measurements
    x_error - 1d array with associated uncertainties for each measurement

    returns (weighted mean, combined error)
    '''
    x_mean = _np.array(x_mean)
    x_error = _np.array(x_error)
    if len(x_mean) != len(x_error):
        raise ValueError('Mean and error input arrays must have same size')
    return (_np.sum(x_mean/(x_error**2))/_np.sum(1/(x_error**2)),
            _np.sqrt(1/_np.sum(1/(x_error**2))))

def gauss(g_mean, g_std):
    '''
    Returns a function object that provides a Gaussian probability
    distribution with a mean of gauss_mean and an std of gauss_std
    '''
    return lambda x: _np.exp(-(x-g_mean)**2/(2*g_std**2))/(_np.sqrt(
            2.0*_np.pi*g_std**2))

def hist_chisq(hist_info, func):
    '''
    Returns the chi**2 value of fitting to a histogram where
    hist_info is the output tuple of either the pylab 'hist(...)'
    command or numpy 'histogram(...)' command and func is the model
    being fitted to as a function object.
    '''
    return _np.sum([(hist_info[0][n]-_np.sum(hist_info[0])*
         abs(hist_info[1][0]-hist_info[1][1])*
         func((hist_info[1][n+1]+hist_info[1][n])/2.))**2/hist_info[0][n]
        for n in range(len(hist_info[0])) if hist_info[0][n] != 0])

def hist_reduced_chisq(hist_info, func, n_free):
    '''
    Returns the value of the reduced chi**2 where hist_info is the
    output tuple of either the pylab 'hist(...)' command or numpy
    'histogram(...)' command, func is the theoretically calculated curve
    as a function object, and n_free is the number of degrees of freedom
    (the number of parameters) used to fit p onto the data (ex. for
    Gaussian fit n_free is 2, for there is only the mean and pstd).
    '''
    return hist_chisq(hist_info, func)/(len(hist_info[0])-n_free)

def prob_chisq(chisq, dof):
    '''
    Returns the probability density of measuring the non-normalized
    chisq, given the degrees of freedom (dof), where nu typically equals
    n-n_free, that is total number of data points (n), minus degrees of
    freedom used to fit theoretical curve onto data (n_free).
    '''
    return (chisq)**(dof/2.0-1.0)*_np.exp(-chisq/2.0)/(2**(dof/2.0)*
            _math.gamma(dof/2.0))

def prob_getting_larger_chisq(chisq, dof, large_number=None, dx=0.001):
    '''
    Returns the probability of getting a larger chisq. Effectively
    integrates prob_chisq(...) from chisq = chisq to chisq =
    large_number. Large_number is upper limit of integral (ideally
    should be infinity if left None will be 100*chisq), dx is related to
    the accuracy of the integral ideally infinitely small. dof typically
    equals n-n_free, that is the total number of data points (n), minus
    degrees of freedom used to fit theoretical curve onto data (n_free).
    Suggestions on a better way of doing this are welcomed.
    '''
    if large_number == None:
        large_number = 100*chisq
    return _np.trapz(prob_chisq(_np.arange(chisq, large_number, dx),
                                dof), None, dx)


## Styling
print_styles = ['python', 'latex', 'latex_m', 'pretty']
print_style = 'latex'

def _fmt_unit_string(string):
    '''Formats unit string based on global style'''
    if print_style == 'pretty':
        return string.replace('**', '^').replace('*', ' ')
    if print_style == 'latex':
        nu = _re.compile(r'(\d+)')
        return '$'+nu.sub(r'{\1}', string).replace('**',
                '^').replace('*',' ')+'$'
    if print_style == 'latex_m':
        nu = _re.compile(r'(\d+)')
        return nu.sub(r'{\1}', string).replace('**',
                '^').replace('*',' ')
    return string

# FIXME: pretty complains :(
def _pm():
    '''Returns how plus-minus symbol based on global style'''
    return {'python':'+/-', 'pretty':'\xB1',
            'latex':'$\pm$', 'latex_m':'\pm'}[print_style]

## Fuzzy Number Class
class fz:
    '''Represents a value with associated error and units
    Examples:
        >>> x = fz(0.0012, 0.00004, u='kg*g**20/kg', error_type='sys')
        >>> x = fz(1.23, 0.020, u='kg*g**2/kg', error_type=None)
    '''
    def __init__(self, m, e=0, u='1', error_type='stat'):
        self.m = float(m)
        self.e = float(e)
        self.u = str(u)
        self.error_type = error_type

    def __str__(self):
        # No uncertainty
        if not abs(self.e) > 0.0:
            return '{:e} [{}]'.format(self.m,
                    _fmt_unit_string(self.u))
        # Get last two digits in uncertainty
        sv = ('{:.1e}'.format(self.e)).split('e')
        # Base ten power of second uncertainty digit
        sv[1] = int(sv[1])-1

        def fmt(x, n, e):
            s = ('%.*e'%(n-1, x)).split('e')
            s[1] = int(s[1])
            if s[1] == e:
                return ('%.*e'%(n-1, x)).split('e')[0]
            elif s[1] < e:
                return ''.join(['0.']+(e-s[1]-1)*['0']+[
                    (s[0]).replace('.','')])
            elif s[1] > e:
                return ''.join([s[0].replace('.','')]+(e-s[1]-1)*['0'])
        sm = ('%.e'%(self.m)).split('e')
        sm[1] = int(sm[1])
        px = sm[1]-sv[1]
        ret = ('%.*e'%(px, self.m)).split('e')
        ret[0] += ' ' + _pm() + ' ' +\
            fmt(self.e, 2, sm[1])
        if self.error_type:
            ret[0] += '('+self.error_type+')'
        sret = '('+ret[0]+')'
        if int(ret[1]) != 0:
            sret += 'e'+ret[1]
        return sret + ' [{}]'.format(_fmt_unit_string(self.u))
    def __repr__(self):
        return str(self)

var = _sy.var
## Functions for Fuzzy Numbers
def prop(sympy_function, units='1', **kargs):
    '''Evaluate function using **kargs. Function propagates
    errors in fz.  Returns a fz object.
    Example:
    >>> import sympy
    >>> x, y = var('x y')
    >>> f = x**2+y**2
    >>> prop(f, x=fz(5.2, 0.1), y=3)
    '''
    m = {}
    e = {}
    for k in kargs.keys():
        if isinstance(kargs[k], fz):
            m[k] = kargs[k].m
            e[k] = kargs[k].e
        else:
            m[k] = kargs[k]
            e[k] = 0
    return fz(sympy_function.subs(m).n(),
         _math.sqrt(sum([(sympy_function.diff(x).subs(m).n())**2*e[str(x)]**2
                for x in sympy_function.free_symbols if e[str(x)] != 0])),
              u=units)

# FIXME: IF SYS IS << ERR, IT SHOULD NOT APPEAR IN VALUE
# TODO: CLEAN UP, SIMPLIFY
def fmt_m_e(x, err=0.0, sys=0.0, pm=_pm()):
    ''' Formats a value x with error err and systematic error sys such
    that the err/sys (which ever larger) has 2 significant digits and x
    has precision up to last place of err. Uses pm as character for plus
    and minus.
    '''
    serr = ('%.*e'%(2-1, err)).split('e')
    serr[1] = int(serr[1])-1

    ssys = ('%.*e'%(2-1, sys)).split('e')
    ssys[1] = int(ssys[1])-1

    p = None
    if abs(sys) > 0.0:
        if abs(err) > 0.0:
            p = max([ssys[1], serr[1]])
        else:
            p = ssys[1]
    elif abs(err) > 0.0:
        p    = serr[1]
    if p == None:    # FIXME: now infinite precision, should it be 2?
        return '%e'%(x)
    else:
        def fmt(x, n, e):
            ''' Formats a number given degree of precision '''
            s = ('%.*e'%(n-1, x)).split('e')
            s[1] = int(s[1])
            if s[1] == e:
                return ('%.*e'%(n-1, x)).split('e')[0]
            elif s[1] < e:
                return ''.join(['0.']+(e-s[1]-1)*['0']+[(s[0]).replace(
                    '.','')])
            elif s[1] > e:
                return ''.join([s[0].replace('.','')]+(e-s[1]-1)*['0'])
        sx = ('%.e'%(x)).split('e')
        sx[1] = int(sx[1])
        px = sx[1]-p
        ret = ('%.*e'%(px, x)).split('e')
        if abs(err) > 0.0:
            ret[0] += ' ' + pm + ' ' + fmt(err, 2, sx[1]) + '(stat)'
        if abs(sys) > 0.0:
            ret[0] += ' ' + pm + ' ' + fmt(sys, 2, sx[1]) + '(sys)'
        sret = '('+ret[0]+')'
        if int(ret[1]) != 0:
            sret += 'e'+ret[1]
        #return '('+ret[0]+') x 10'+uni.sup(int(ret[1]))
        return sret

def fitline(x, y, sig):
    ''' Fit a linear function to data.

      Inputs:
        x - x data to fit as numpy array
        y - y data to fit as numpy array
        sig - the uncertainties on the data points as numpy array

      Outputs:
        a - the best fit parameters
        aerr - the errors on these parameters
        chisq - the value of chi-squared
        yfit - the value of the fitted function at the points x

      Example Usage:
        >>> (a, aerr, chisq, yfit) = fitlin(x, y, sig)

      The least-squares fit to a straight line can be done in closed
      form. See Bevington and Robinson Ch. 6 (p. 114).

      Function ported to python from 8.13 matlab fitlin function.
    '''
    if (x.shape != y.shape and x.shape != sig.shape):
        raise ValueError('x, y and sig must have same shape')
    term1 = _np.sum(1/sig**2)
    term2 = _np.sum(x**2/sig**2)
    term3 = _np.sum(y/sig**2)
    term4 = _np.sum(x*y/sig**2)
    term5 = _np.sum(x/sig**2)

    delta = term1*term2-term5**2
    a = _np.zeros(2)
    a[0] = (term2*term3-term5*term4)/delta
    a[1] = (term1*term4-term5*term3)/delta

    aerr = _np.zeros(2)
    aerr[0] = _np.sqrt(term2/delta)
    aerr[1] = _np.sqrt(term1/delta)

    yfit = a[0] + a[1]*x

    chisq = _np.sum(((y-a[0]-a[1]*x)/sig)**2)

    return (a, aerr, chisq, yfit)

def levmar(x, y, sig, fitfun, a0, lamda=0.001, dYda=None, print_dev=False):
    ''' Fit a nonlinear function to data using Marquardt

       Inputs:
           x - x data to fit as numpy array
           y - y data to fit as numpy array
           sig - the uncertainties on the data points as numpy array
           fitfun - the function to fit to as a python function object
           a0 - initial guess of fit parameters in a numpy array
           lamda - float number which moderates algorithm.
                           For small lamda solution is an expansion
                           algorithm, for large
                           lamda solution is a gradient algorithm
           dYda - (optional) if not None will use as derivatives of function
           print_dev - prints debug information (default silent)

       Outputs:
           a - the best fit parameters
           aerr - the errors on these parameters
           chisq - the value of chi-squared
           yfit - the value of the fitted function at the points x
           corr - error matrix = inverse of the curvature matrix alpha

       Example Usage:
           >>> x = linspace(0, 10, 10)    # Data x
           >>> y = 5*exp(-x/2)+4            # Data y
           >>> sig = sqrt(y)                    # Uncertainty in data
           >>> model = lambda x, a:a[0]*exp(-x/a[1])+a[2]    # Fit function
           >>> guesses = array([4.8, 1.8, 3.3])    # Initial Guesses
           >>> a = levmar(x, y, sig, model, guesses, print_dev=True)
           >>> dof = len(x)-len(guesses)         # Degree of Freedom
           >>> best_fit_parm = a[1]
           >>> chisq = a[2]
           >>> rchisq = chisq/dof
           >>> yfit = a[3]

       See Bevington and Robinson in Section 8.5 & 8.6 for discussion of
       algorithm.

       Function ported to python from 8.13 matlab levmar function.
    '''
    ## Useful Functions
    # FIXME: Below just calculates chisq
    calcchi2 = lambda x, y, sig, fitfun, a : _np.sum(((y-fitfun(x,
                                                                a))/sig)**2)

    def calcderiv(x, y, sig, fitfun, a, stepsize, dYda):
        nparm = len(a)
        ndata = len(x)
        der = _np.zeros((ndata, nparm))

        if dYda == None:
            for i in range(ndata):
                y0 = fitfun(x[i], a)
                for j in range(nparm):
                    a[j] += stepsize[j]
                    y1 = fitfun(x[i], a)
                    a[j] -= stepsize[j]
                    der[i, j] = (y1-y0)/stepsize[j]
        else:
            for i in range(ndata):
                for j in range(nparm):
                    der[i, j] = dYda[j](x[i], a)
        return der

    def calcinvalpha(x, y, sig, fitfun, a, stepsize, lamda, dYda):
        nparm = len(a)
        ndata = len(x)
        alpha = _np.zeros((nparm, nparm))
        der = calcderiv(x, y, sig, fitfun, a, stepsize, dYda)
        for j in range(nparm):
            for k in range(nparm):
                for i in range(ndata):
                    alpha[j, k] += der[i, j]*der[i, k]/sig[i]**2
        for j in range(nparm):
            alpha[j, j] *= (1+lamda)
        return _npla.inv(alpha)

    def calcdeltaa(x, y, sig, fitfun, a, stepsize, lamda, dYda):
        nparm = len(a)
        ndata = len(x)
        beta = _np.zeros(nparm)
        corr = calcinvalpha(x, y, sig, fitfun, a, stepsize, lamda, dYda)
        der = calcderiv(x, y, sig, fitfun, a, stepsize, dYda)
        for k in range(nparm):
            for i in range(ndata):
                beta[k] += (y[i] - fitfun(x[i], a))*der[i, k]/sig[i]**2
        return _np.dot(beta, corr)

    def printd(s, p):
        if p:
            print s
    ##

    ## FIXME: Adjustable Parameters ??
    stepsize = abs(a0)*0.001
    chicut = 0.01

    a = a0
    chi2 = calcchi2(x, y, sig, fitfun, a)
    chi1 = chi2 + chicut*2
    nparm = len(a)
    i = 0
    printd('Marquardt Gradient-Expansion Algorithm', print_dev)
    printd(' '.join(['i', 'Chisqr', 'lamda'] + ['a'+str(ii) for ii in
        range(len(a0))]),
                 print_dev)
    while    abs(chi2-chi1) > chicut:
        i += 1
        printd(((3+len(a))*'{:.3e} ').format(i, chi2, lamda, *list(a)),
               print_dev)
        chinew = chi2 + 1
        while chinew > chi2+chicut:
            deltaa = calcdeltaa(x, y, sig, fitfun, a, stepsize, lamda, dYda)
            anew = a + deltaa
            chinew = calcchi2(x, y, sig, fitfun, anew)
            if chinew > chi2:
                lamda *= 10
        lamda = lamda/10.0
        a = anew
        chi1 = chi2
        chi2 = chinew
    corr = calcinvalpha(x, y, sig, fitfun, a, stepsize, lamda, dYda)
    aerr = _np.array([_np.sqrt(corr[ii, ii]) for ii in range(nparm)])
    chisq = calcchi2(x, y, sig, fitfun, a)
    yfit = fitfun(x, a)
    return (a, aerr, chisq, yfit, corr)

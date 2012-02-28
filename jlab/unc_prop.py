# coding=utf-8

from .general import *

def _uncp_prep_arg(a, s=None, cov=None):
    a = matrix(a)
    l = a.size
    covm = matrix(zero([4, 4]))
    if cov:
        covm[0:l, 0:l] = matrix(cov)[0:l, 0:l]
    elif s:
        covm[0:l, 0:l] = diag(a)[0:l, 0:l]

    return Ret(a=a, cov=covm)

def uncp_add(a, s=None, cov=None):
    args = _uncp_prep_arg(a, s, cov)
    a = args.a
    cov = args.cov

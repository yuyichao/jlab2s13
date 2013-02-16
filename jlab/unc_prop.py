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

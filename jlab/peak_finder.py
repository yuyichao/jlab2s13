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

def _next_peak_iter(data, start_i, increasing):
    if increasing:
        l = len(data)
        i_range = range(start_i, l)
    else:
        i_range = range(start_i, -1, -1)
    for i in i_range:
        yield i, data[i]

def _update_p_neg(p_i, p_v, i, v):
    if p_v > v:
        return i, v
    return p_i, p_v

def _update_p_pos(p_i, p_v, i, v):
    if p_v < v:
        return i, v
    return p_i, p_v

def _check_found_neg(p_v, v, start_v, thresh):
    thresh += p_v
    if thresh < start_v and thresh < v:
        return True
    return False

def _check_found_pos(p_v, v, start_v, thresh):
    thresh = p_v - thresh
    if thresh > start_v and thresh > v:
        return True
    return False

def find_next_peak(data, start_i, thresh, increasing=True, negetive=False):
    it = _next_peak_iter(data, start_i, increasing)
    if negetive:
        _update_p = _update_p_neg
        _check_found = _check_found_neg
    else:
        _update_p = _update_p_pos
        _check_found = _check_found_pos

    start_i, start_v = next(it)
    p_i = start_i
    p_v = start_v
    for i, v in it:
        p_i, p_v = _update_p(p_i, p_v, i, v)
        if _check_found(p_v, v, start_v, thresh):
            return p_i

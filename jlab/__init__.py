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

from .general import *
from .fit import *
from .unc_prop import *
from .tex import *
from .unicode import *
from .jplot import *
from .peak_finder import find_next_peak

__import__("matplotlib").rcParams.update({'axes.labelsize': 20,
                                          'axes.titlesize': 30})

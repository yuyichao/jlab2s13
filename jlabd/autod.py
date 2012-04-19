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

from socket import *
try:
    from .read import *
except ValueError:
    from read import *

def check_a_start(preload, name, argv=None, fname=None, cwd=None, env=None):
    import sys, os, os.path

    # Check if interactive.
    import __main__
    if not hasattr(__main__, '__file__'):
        return
    if hasattr(__main__, '__autod_started') and __main__.__autod_started:
        return

    if argv == None:
        argv = sys.argv
    if fname == None:
        fname = argv[0]
    fname = os.path.abspath(fname)
    preload = os.path.realpath(preload)
    if cwd == None:
        cwd = os.getcwd()
    if env == None:
        env = os.environ
    # Now start.
    # Don't want to deal with funny ../ or ./ in the name(path).
    name = name.replace('/', '.')

    from .send import try_start
    try_start(name, argv, fname, cwd, env)
    from .listen import try_start_daemon
    from time import sleep

    # Try 10 times.
    for i in range(0, 10):
        try_start_daemon(preload, name)
        sleep(.1)
        try_start(name, argv, fname, cwd, env)
    print("Fail to connect.")

def def_init(preload, name, argv=None, fname=None, cwd=None, env=None):
    import inspect, os
    f = inspect.currentframe().f_back
    # well, FIXME
    def init():
        if os.uname()[0] == 'Linux':
            check_a_start(preload, name, argv=argv,
                          fname=fname, cwd=cwd, env=env)
    f.f_locals['init'] = init

#!/usr/bin/env python

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

import os, sys, socket, select, struct
from .read import *

def try_start(name, argv, fname, cwd, env):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        # Linux
        s_path = '\0' + name
        s.connect(s_path)
    except socket.error as error:
        if error.errno == os.errno.ECONNREFUSED:
            return -1
        elif error.errno == os.errno.ENOENT:
            # POSIX
            s_dir = '/tmp/autod/'
            s_path = s_dir + name
            try:
                s.connect(s_path)
            except socket.error as error:
                if error.errno in [os.errno.ENOENT, os.errno.ECONNREFUSED]:
                    return -1
                else:
                    exit(-1)
        else:
            exit(-1)

    sd_str(s, repr(argv))
    sd_str(s, fname)
    sd_str(s, cwd)
    #sd_str(s, env)
    s_fn = s.fileno()
    poll = select.poll()
    poll.register(0, select.POLLHUP | select.POLLIN)
    poll.register(s_fn, select.POLLIN | select.POLLHUP)

    while True:
        events = poll.poll()
        for filno, event in events:
            if filno == 0:
                if event & select.POLLIN:
                    buff = os.read(0, 65536)
                    sd_package(s, buff)
                if event & select.POLLHUP:
                    poll.unregister(filno)
            elif filno == s_fn:
                if event & select.POLLIN:
                    n, buff = rd_int_pkg(s)
                    if n == -1:
                        if buff == b'FINISH':
                            exit()
                    else:
                        try:
                            os.write(n, buff)
                        except:
                            pass
                if event & select.POLLHUP:
                    poll.unregister(filno)
                    exit(0)

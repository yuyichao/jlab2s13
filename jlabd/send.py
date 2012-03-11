#!/usr/bin/env python

import os, sys, socket, select, struct
from .read import *

def try_start(name, argv, fname, cwd, env):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        # Linux
        s_path = '\0' + name
        s.connect(s_path)
    except socket.error as error:
        if error.errno == 111:
            return -1
        elif error.errno == 2:
            # POSIX
            s_dir = '/tmp/autod/'
            s_path = s_dir + name
            try:
                s.connect(s_path)
            except socket.error as error:
                if error.errno == 2 or error.errno == 61:
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

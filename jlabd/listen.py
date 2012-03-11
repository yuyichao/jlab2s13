#!/usr/bin/env python

import os, sys, socket, select, struct, signal
from os import fork
from .read import *

'''
# Errr, used for debug only (since stdout/stderr are already redirected.)
def mprint(*args):
    try:
        fd = os.open('/dev/pts/2', os.O_WRONLY)
        for arg in args:
            os.write(fd, str(arg).encode('utf-8'))
            os.write(fd, b'\n')
        os.close(fd)
    except:
        pass
'''

def rmsock(s_path):
    if s_path[0] != '\0':
        os.unlink(s_path)

try:
    execfile
except:
    def execfile(file, globals=globals(), locals=locals()):
        with open(file, "r") as fh:
            exec(fh.read()+"\n", globals, locals)

def daemonlize(s_path, s):
    pid = os.fork()
    if pid < 0:
        rmsock(s_path)
        exit(1)
    elif pid:
        return pid
    for fd in [0, 1, 2]:
        try:
            os.close(fd)
        except:
            pass
    os.setsid()
    pid = os.fork()
    if pid < 0:
        rmsock(s_path)
        exit(1)
    elif pid:
        exit()
    os.chdir('/')
    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    except:
        pass
    return 0

def try_start_daemon(preload, name):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        # Linux
        s_path = '\0' + name
        s.bind(s_path)
    except socket.error as error:
        if error.errno == os.errno.ENOENT:
            # POSIX
            s_dir = '/tmp/autod/'
            s_path = s_dir + name
            try:
                os.symlink('%d' % os.getpid(), s_path + '.lck')
            except:
                return -1
            os.makedirs(s_dir)
            try:
                s.bind(s_path)
            except socket.error as error:
                if error.errno == os.errno.EADDRINUSE:
                    try:
                        pid = int(os.readlink(s_path + '.pid'))
                    except:
                        os.unlink(s_path + '.lck')
                        return -1
                    try:
                        os.kill(pid, 0)
                        os.unlink(s_path + '.lck')
                        return -1
                    except OSError as error:
                        if error.errno == 3:
                            os.unlink(s_path)
                        else:
                            os.unlink(s_path + '.lck')
                            return -1
                else:
                    os.unlink(s_path + '.lck')
                    return -1
            os.unlink(s_path + '.lck')
        elif error.errno == os.errno.EADDRINUSE:
            return -1
    s.listen(20)
    s.setblocking(1)
    if daemonlize(s_path, s):
        s.close()
        return 0
    if s_path[0] != '\0':
        try:
            os.symlink('%d' % os.getpid(), s_path + '.pid')
        except:
            os.unlink(s_path)
            exit(1)
    execfile(preload)
    conn = main_listen(s)
    conn.settimeout(20)
    argv = eval(rd_str(conn))
    fname = rd_str(conn)
    cwd = rd_str(conn)
    #env = eval(rd_str(conn))
    conn.settimeout(None)
    fork_sub(conn)
    sys.argv = argv
    os.chdir(cwd)
    empty_globals = {'__builtins__': __builtins__,
                     '__file__': fname,
                     '__package__': None,
                     '__cached__': None,
                     '__name__': '__main__',
                     '__doc__': None}
    execfile(fname, globals=empty_globals, locals=empty_globals)
    exit(0)

def main_listen(s):
    while True:
        conn, addr = s.accept()
        mprint(conn)
        mprint(addr)
        if not conn:
            exit(0)
        pid = fork()
        if pid < 0:
            exit(1)
        elif pid == 0:
            # Child.
            s.close()
            return conn
        conn.close()

def close_quit(fds):
    for fd in fds:
        try:
            os.close(fd)
        except:
            pass
    exit()

def redirect(s, pipes):
    poll = select.poll()
    s_fn = s.fileno()
    for fd in [s_fn, pipes[1], pipes[2]]:
        poll.register(fd, select.POLLIN | select.POLLHUP)
    while True:
        events = poll.poll()
        for fileno, event in events:
            mprint("Pid: %d, Fileno: %d, Event: %d" %
                   (os.getpid(), fileno, event))
            if fileno == s_fn:
                if event & select.POLLIN:
                    os.write(pipes[0], rd_package(s))
                if event & select.POLLHUP:
                    close_quit([s_fn] + pipes)
            if fileno in pipes:
                i = pipes.index(fileno)
                if event & select.POLLIN:
                    sd_int_pkg(s, i, os.read(fileno, 65536))
                if event & select.POLLHUP:
                    try:
                        sd_int_str(s, -1, 'FINISH')
                    except:
                        pass
                    close_quit([s_fn] + pipes)

def fork_sub(s):
    pipes = [os.pipe() for i in [0, 1, 2]]
    pid = fork()
    if pid < 0:
        exit(1)
    elif pid:
        # Parent
        os.close(pipes[0][0])
        pipes[0] = pipes[0][1]
        os.close(pipes[1][1])
        pipes[1] = pipes[1][0]
        os.close(pipes[2][1])
        pipes[2] = pipes[2][0]
        sd_int_str(s, -1,'START')
    else:
        # Child
        s.close()
        os.close(pipes[0][1])
        os.dup2(pipes[0][0], 0)
        os.close(pipes[0][0])

        os.close(pipes[1][0])
        os.dup2(pipes[1][1], 1)
        os.close(pipes[1][1])

        os.close(pipes[2][0])
        os.dup2(pipes[2][1], 2)
        os.close(pipes[2][1])
        return
    redirect(s, pipes)

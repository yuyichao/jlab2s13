#!/usr/bin/env python

import os, sys, socket, select, struct, signal, time
from os import fork, path
try:
    from .read import *
except ValueError:
    from read import *

def mprint(*args):
    pass
'''
# Errr, used for debug only (since stdout/stderr are already redirected.)
def mprint(*args):
    try:
        fd = os.open('/dev/pts/2', os.O_WRONLY)
        for arg in args:
            os.write(fd, str(arg).encode('utf-8'))
            os.write(fd, b'\n')
        os.close(fd)
    except OSError:
        pass
'''
def fake_func(*args, **kwargs):
    pass

def lock_opt(s_path):
    if s_path[0] == '\0':
        return True
    try:
        os.symlink('%d' % os.getpid(), s_path + '.lck')
        return True
    except OSError:
        return False

def unlock_opt(s_path):
    if s_path[0] == '\0':
        return
    os.unlink(s_path + '.lck')

def rd_pid(s_path):
    if s_path[0] == '\0':
        return
    try:
        return int(os.readlink(s_path + '.pid'))
    except OSError:
        return 0

def rm_pid(s_path):
    if s_path[0] == '\0':
        return
    try:
        os.unlink(s_path + '.pid')
    except OSError:
        pass

def save_pid(s_path):
    if s_path[0] == '\0':
        return True
    try:
        os.symlink('%d' % os.getpid(), s_path + '.pid')
        return True
    except OSError:
        return False

def rmsock(s_path):
    if s_path[0] != '\0':
        try:
            os.unlink(s_path)
        except OSError:
            pass

try:
    execfile
except NameError:
    def execfile(file, globals=globals(), locals=locals()):
        with open(file, "r") as fh:
            code = compile(fh.read() + "\n", file, 'exec')
        exec(code, globals, locals)

def daemonlize(s, s_path, preload):
    pid = os.fork()
    if pid < 0:
        rmsock(s_path)
        exit(1)
    elif pid:
        return pid
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
    except AttributeError:
        pass
    except OSError:
        pass
    ifposix = '0' if s_path[0] == '\0' else '1'
    filename = path.realpath(__file__)
    basename = path.basename(filename)
    os.execv(filename, [basename, "%d" % s.fileno(),
                        ifposix, s_path[1:], preload])
    rmsock(s_path)
    exit(-1)

def listen_func(s, s_path, preload):
    import __main__
    __main__.__autod_started = True
    if s_path[0] != '\0':
        try:
            os.symlink('%d' % os.getpid(), s_path + '.pid')
        except OSError:
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
    sys.path.insert(0, cwd)
    empty_globals = {'__builtins__': __builtins__,
                     '__file__': fname,
                     '__package__': None,
                     '__cached__': None,
                     '__name__': '__main__',
                     '__doc__': None}
    execfile(fname, empty_globals, empty_globals)
    exit(0)

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
                os.makedirs(s_dir)
            except OSError as error:
                if error.errno != os.errno.EEXIST:
                    return -1
            if not lock_opt(s_path):
                return -1
            fail = False
            try:
                s.bind(s_path)
            except socket.error as error:
                if error.errno == os.errno.EADDRINUSE:
                    pid = rd_pid(s_path)
                    if not pid:
                        unlock_opt(s_path)
                        return -1
                    try:
                        os.kill(pid, 0)
                    except OSError as error:
                        if error.errno == os.errno.ESRCH:
                            os.unlink(s_path)
                            rm_pid(s_path)
                        else:
                            fail = True
                else:
                    fail = True
            unlock_opt(s_path)
            if fail:
                return -1
        elif error.errno == os.errno.EADDRINUSE:
            return -1
    s.listen(20)
    s.setblocking(1)
    if daemonlize(s, s_path, preload):
        s.close()
        return 0
    listen_func(s, s_path, preload)

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

def close_kill_quit(fds, pid):
    for fd in fds:
        try:
            os.close(fd)
        except OSError:
            pass
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    time.sleep(.5)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    exit()

def redirect(s, pipes, pid):
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
                if event & select.POLLHUP:
                    close_kill_quit([s_fn] + pipes, pid)
                if event & select.POLLIN:
                    os.write(pipes[0], rd_package(s))
            if fileno in pipes:
                i = pipes.index(fileno)
                if event & select.POLLIN:
                    try:
                        sd_int_pkg(s, i, os.read(fileno, 65536))
                    except OSError:
                        pass
                    except socket.error:
                        pass
                if event & select.POLLHUP:
                    try:
                        sd_int_str(s, -1, 'FINISH')
                    except socket.error:
                        pass
                    close_kill_quit([s_fn] + pipes, pid)

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
        sd_int_str(s, -1, 'START')
        redirect(s, pipes, pid)
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

def main():
    for fd in [0, 1, 2]:
        try:
            os.close(fd)
        except OSError:
            pass
    s_fd = int(sys.argv[1])
    try:
        s = socket.socket(fileno=s_fd)
    except TypeError:
        s = socket.fromfd(s_fd, socket.AF_UNIX, socket.SOCK_STREAM)
    if int(sys.argv[2]):
        prefix = '/'
    else:
        prefix = '\0'
    s_path = prefix + sys.argv[3]
    preload = sys.argv[4]
    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    except AttributeError:
        pass
    except OSError:
        pass
    listen_func(s, s_path, preload)

if __name__ == '__main__':
    main()

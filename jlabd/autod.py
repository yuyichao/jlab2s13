# coding=utf-8

from socket import *
try:
    from .read import *
except ValueError:
    from read import *

def check_a_start(preload, name, argv, fname=None, cwd=None, env=None):
    import sys, os, os.path

    # Check if interactive.
    import __main__
    if not hasattr(__main__, '__file__'):
        return
    if hasattr(__main__, '__autod_started') and __main__.__autod_started:
        return

    if fname == None:
        fname = argv[0]
    fname = os.path.abspath(fname)
    preload = os.path.abspath(preload)
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

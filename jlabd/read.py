#!/usr/bin/env python

import os, socket, sys, select, struct, fcntl

def int2byte(n):
    return struct.pack('<L', n % (1 << 32))

def byte2int(buff):
    n = struct.unpack('<L', buff[:4])[0]
    return (n + (1 << 31)) % (1 << 32) - (1 << 31)

def rd_l(s, l):
    buff = b''
    while len(buff) < l:
        buff += s.recv(l - len(buff))
    return buff

def rd_package(s):
    l = byte2int(rd_l(s, 4))
    return rd_l(s, l)

def sd_package(s, buff):
    s.send(int2byte(len(buff)) + buff)

def sd_str(s, st):
    sd_package(s, st.encode('utf-8'))

def rd_str(s):
    return rd_package(s).decode('utf-8')

def sd_int_pkg(s, n, buff):
    sd_package(s, int2byte(n) + buff)

def rd_int_pkg(s):
    buff = rd_package(s)
    return (byte2int(buff), buff[4:])

def sd_int_str(s, n, st):
    sd_int_pkg(s, n, st.encode('utf-8'))

def rd_int_str(s):
    n, buff = rd_int_pkg(s)
    return (n, buff.decode('utf-8'))

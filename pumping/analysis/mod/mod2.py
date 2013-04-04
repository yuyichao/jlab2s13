''' Model for Rubidium gas as a two level system '''
from __future__ import division
import pylab as p

def up(d,times=1,change=1):
    ch = 0
    for i in range(times):
        s = (d != int(.5*change+.5))*(p.rand(*d.shape) > .90)
        d[s] += change
        ch += sum(sum(s.astype('int16')))
        rs = p.logical_not(s)*(p.rand(*d.shape) > .999)
        d[rs] = (p.rand(*d[rs].shape)+.5).astype('int16')
    return ch

d = (p.rand(600,600) + .5).astype('int16')
# p.plot([1 - up(d,1,i)/(d.shape[0]*d.shape[1])
#     for i in p.hstack([-1*p.ones(200),1*p.ones(200)])])
x = p.array([up(d,1,i)/(d.shape[0]*d.shape[1])
    for i in p.hstack([-1*p.ones(200),1*p.ones(200)])])
p.savetxt('mod2.dat',x)
p.plot(x)
p.show()

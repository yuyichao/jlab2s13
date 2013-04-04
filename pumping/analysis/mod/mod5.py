''' Model for Rubidium gas as a seven level system '''
from __future__ import division
import pylab as p
max_val = 3
p1,p2 = 8,4
def up(d,times=1,change=1):
    ch = 0
    for i in range(times):
        s = (d != change*max_val)*(p.rand(*d.shape) > .90)
        d[s] += change
        ch += sum(sum(s.astype('int16')))
        rs = p.logical_not(s)*(p.rand(*d.shape) > .999)
        d[rs] = (p1*p.rand(*d[rs].shape)-p2).astype('int16')
    return ch

d = (p1*p.rand(600,600) - p2).astype('int16')
print set(d.flatten())
# p.plot([1 - up(d,1,i)/(d.shape[0]*d.shape[1])
#     for i in p.hstack([-1*p.ones(200),1*p.ones(200)])])
x = p.array([up(d,1,i)/(d.shape[0]*d.shape[1])
    for i in p.hstack([-1*p.ones(200),1*p.ones(200)])])
p.savetxt('mod5.dat',x)
p.plot(1-x)
p.show()


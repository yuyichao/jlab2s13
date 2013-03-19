from __future__ import division, print_function
import jlab as j
import pylab as p

# Get X,Y,Z data
d = [(x,p.genfromtxt('data/'+x+'_cal_d4.dat')) for x in ['x','y','z']]

f = lambda x, a: a[0]*(p.exp(a[1]*(x-a[2]))+p.exp(-a[1]*(x-a[2])))+a[3]

# Plot Data
for k,v in d:
    p1 = j.Bundle()
    p1.x, p1.y, p1.ye, p1.name = v[:,4], v[:,0], v[:,1], 'Peak 1'
    p1.color = 'b'
    p2 = j.Bundle()
    p2.x, p2.y, p2.ye, p2.name = v[:,4], v[:,2], v[:,3], 'Peak 2'
    p2.color = 'r'

    def pre(pe):
        pe.a0 = p.array([min(pe.y)/1e3,
        2*(max(pe.y)-min(pe.y))/abs(pe.x[p.argmax(pe.y)]-pe.x[p.argmin(pe.y)]),
            pe.x[p.argmin(pe.y)], min(pe.y)])
        return pe

    def fit(pe):
        pe.a, pe.aerr, pe.chisq, pe.yfit, pe.corr = j.levmar(pe.x,
                pe.y, pe.ye, f, pe.a0)
        pe.new_x = p.linspace(min(pe.x), max(pe.x), 1000)
        pe.new_y = f(pe.new_x, pe.a)
        pe.min_x = j.fz(pe.a[2], pe.aerr[2], 'mA')
        return pe

    def plot(pe):
        p.errorbar(pe.x, pe.y, pe.ye, fmt='.', label=pe.name, c=pe.color)
        # p.plot(pe.x, f(pe.x,pe.a0))
        if 'yfit' in pe.__dict__:
            p.plot(pe.new_x, pe.new_y, c=pe.color)
            [p.axvline(pe.min_x.m+i*pe.min_x.e, -10, 10, ls='--', c='k')
                    for i in [-1,1]]
            p.axvline(pe.min_x.m, -10, 10, c=pe.color)
        return pe

    def text(pe):
        return '{}\n$\chi^2_\\nu$: {}\nx min: {}\n\n'.format(pe.name,
                pe.chisq/(len(pe.x)-len(pe.a)), pe.min_x)

    p.figure()
    p.title(k)
    [plot(fit(pre(x))) for x in  [p1,p2]]
    p.text(p.axis()[0], p.axis()[2], text(p1)+text(p2))
    p.xlabel('Current [mA]')
    p.ylabel('Time [sec]')
    p.legend()
    p.savefig('graphics/'+k+'_cal.png')

p.show()

from __future__ import division
import pylab as p
import numpy as np
import jlab as j
import os

plot = True

def sq_peak_detect(x, peak_min_diff=0.05, peak_min_width=0.2, points_drop=10):
    g = j.Bundle()
    g.ygrad = x[1:,2]-x[:-1,2]
    g.xgrad = (x[1:,0]+x[:-1,0])/2
    g.dpeaks = p.argwhere(abs(g.ygrad[1:]) > peak_min_diff).flatten()
    g.peaks = [v for k,v in enumerate(g.dpeaks)
           if k == 0 or g.xgrad[v]-g.xgrad[g.dpeaks[k-1]] > peak_min_width]
    g.xpeaks = [g.xgrad[k] for k in g.peaks]
    # g.ixwf = [x[s+p.argmin(x[s:e,1])+points_drop:e,0]
    #             for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    # g.iywf = [x[s+p.argmin(x[s:e,1])+points_drop:e,1]
    #             for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    g.ixwf = [x[s+points_drop:e,0] for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    g.iywf = [x[s+points_drop:e,1] for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    ml = min(map(len, g.iywf))
    g.x = [i-min(i) for i in g.ixwf if len(i) == ml][0]
    g.y = [p.mean([y[i] for y in g.iywf if len(y) > i]) for i in range(ml)]
    g.ey = [j.error([y[i] for y in g.iywf if len(y) > i])+1e-6 for i in range(ml)]
    return g

def fit_wf(g):
    f = lambda x,a: a[4]-a[0]*(x+a[1])*p.exp(-a[2]*(x-a[3]))
    a0 = lambda x: p.array([20*(max(x)-min(x)),1/20.,20.,0.001,x[-1]])
    g.a0 = a0(g.y)
    g.a,g.aerr,g.chisq,g.yfit,g.corr = j.levmar(g.x,g.y,g.ey,f,g.a0)

directory = '../bswitch_nf'
for scan in ['od','temp','z','x']:
    print 'Processing',scan,'...'
    scan_di = None
    if scan != 'z':
        scan_di = p.genfromtxt('data/wf_{}_nf.dat'.format(scan))
        scan_di = dict(zip([str(int(x)) for x in scan_di[:,1]],[float(x) for x in scan_di[:,0]]))
    l = []
    for i in [x for x in os.listdir(directory) if 'csv' in x and scan in x]:
        print '\t',i
        x = p.genfromtxt(os.path.join(directory,i), skip_header=2, skip_footer=19, delimiter=',')
        g = sq_peak_detect(x)
        fit_wf(g)
        if scan == 'z':
            l.append([max(g.y)-min(g.y)]+list(g.a)+list(g.aerr)+[g.chisq/(len(g.x)-len(g.a))])
        else:
            l.append([scan_di[i[i.find(scan)+len(scan):-4]]]+list(g.a)+list(g.aerr)
                    +[g.chisq/(len(g.x)-len(g.a))])
        if plot:
            p.figure()
            # p.plot(x[:,0],(x[:,1]-min(x[:,1]))/(max(x[:,1]-min(x[:,1]))),
            #         '-', label='ch1')
            # p.plot(x[:,0],(x[:,2]-min(x[:,2]))/(max(x[:,2]-min(x[:,2]))),
            #         '-', label='ch2')
            # [p.axvline(x, -10, 10, c='r') for x in g.xpeaks]
            #[p.plot(wx-min(wx),wy,'g') for wx,wy in zip(g.ixwf,g.iywf)]
            p.errorbar(g.x, g.y, g.ey, label=str(i))
            #p.plot(g.x, f(g.x,g.a0))
            p.plot(g.x, g.yfit, label=str(i))
    p.show()
    f = open('storage/wf_{}_nf.dat'.format(scan),'w')
    f.write('# {} a[0] a[1] a[2] a[3] a[4] aerr[0] aerr[1] aerr[2] aerr[3] aerr[4] nchisq\n'.format(
        scan))
    np.savetxt(f,p.array(l))
    f.close()

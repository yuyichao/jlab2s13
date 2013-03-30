from __future__ import division
import pylab as p
import jlab as j

csv = lambda x: p.genfromtxt(x, skip_header=2, skip_footer=19, delimiter=',')
reg = p.genfromtxt('data/rabi_selected.dat')

def sq_peak_detect(x, peak_min_diff=0.0012, peak_min_width=0.00001):
    g = j.Bundle()
    g.y = abs(x[:,1]-p.mean(x[:,1]))#(max(x[:,1])+min(x[:,1]))/2.)
    g.x = x[:,0]
    g.dpeaks = p.argwhere(g.y < peak_min_diff).flatten()
    g.peaks = [v for k,v in enumerate(g.dpeaks)
           if k==0 or g.x[v]-g.x[g.dpeaks[k-1]] > peak_min_width]
    g.xpeaks = [g.x[k] for k in g.peaks]
    g.ix = [x[p.argmax(g.y[s:e])+s,0] for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    g.iy = [x[p.argmax(g.y[s:e])+s,1] for s,e in zip(g.peaks[:-1], g.peaks[1:])]
    return g

tv = dict([(str(int(k)),[]) for k in set(reg[:,3])])
for ireg in reg:
    f,s,vpp,freq = ireg
    d = csv('../{}/PRINT_{:02d}.CSV'.format(int(f),int(s)))
    g = sq_peak_detect(d)
    if False:
        p.figure()
        p.title(str(ireg))
        p.plot(g.x, g.y)
        p.plot(d[:,0],d[:,1]-p.mean(g.iy))
        p.plot(g.ix,abs(g.iy-p.mean(g.iy)),'o')
        [p.axvline(i,-10,10,c='r') for i in g.xpeaks]
    T = [g.ix[x]-g.ix[x-1] for x in range(1,min([len(g.ix),4]))]
    error = j.error(p.array(T))
    tv[str(int(freq))].append([vpp, p.mean(T), error if abs(error) > 1e-13 else 1e-6])

# Sort according to vpp
for k in tv.keys():
    tv[k] = p.array(tv[k])
    tv[k] = tv[k][p.argsort(tv[k][:,0])]

# Fit Rb
fits = dict([(i,j.fitline(1./tv[i][:,0],tv[i][:,1]*1e6,tv[i][:,2]*1e6))
        for i in ['23','24','34','35','36']])

# Determine Ratio
Rb85 = j.weighted_mean([fits[i][0][1] for i in ['23','24']],
        [fits[i][1][1] for i in ['23','24']])
Rb87 = j.weighted_mean([fits[i][0][1] for i in ['34','35','36']],
        [fits[i][1][1] for i in ['34','35','36']])

ratio = j.fz(Rb85[0]/Rb87[0],p.sqrt(1/Rb87[0]**2*Rb85[1]**2+(Rb85[0]**2/Rb87[0]**4)*Rb87[1]**2))
print 'ratio', ratio
print 'Sigma Off', (ratio.m-3/2.)/ratio.e

p.figure()
# [p.errorbar(tv[k][1],tv[k][0]*1e6,tv[k][2]*1e6,fmt='o--',label=k) for k in tv.keys() if int(k) < 30]
# [p.errorbar(tv[k][1],tv[k][0]*1e6,tv[k][2]*1e6,fmt='^--',label=k) for k in tv.keys() if int(k) > 30]
[p.errorbar(tv[k][:,0],tv[k][:,1]*1e6,tv[k][:,2]*1e6,fmt='o--',label=k+' kHz') for k in ['23','24']]
[p.errorbar(tv[k][:,0],tv[k][:,1]*1e6,tv[k][:,2]*1e6,fmt='^--',label=k+' kHz') for k in ['34','35','36']]
[p.plot(tv[k][:,0],fits[k][3],'-') for k in ['23','24']]
[p.plot(tv[k][:,0],fits[k][3],'-') for k in ['34','35','36']]
p.xlabel('RF Amplitude [mV]')
p.ylabel('Oscillation Period [$\mu$sec]')
p.text(410,240,'Decay Ratio:{}'.format(ratio))
p.legend()
p.savefig('graphics/rabi_fit.png')
p.show()

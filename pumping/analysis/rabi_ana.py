import pylab as p

csv = lambda x: p.genfromtxt(x, skip_header=2, skip_footer=19, delimiter=',')

# Peak Figure
d = csv('../5/PRINT_01.CSV')
p.figure()
# FIXME: something strange
p.plot(30*d[p.argmin(abs(d[:,0])):p.argmin(abs(d[:,0]-.8)),0]/d[p.argmin(abs(d[:,0]-.8)),0]+15,
        d[p.argmin(abs(d[:,0])):p.argmin(abs(d[:,0]-.8)),1])
[p.axvline(x,-10,10,c='r') for x in [23,24]]
[p.axvline(x,-10,10,c='b') for x in [34,35,36]]
p.xlabel('Frequency [kHz]')
p.ylabel('Intensity [V]')
p.savefig('graphics/rabi_peaks.png')

# General Wave Form Figure
d = csv('../5/PRINT_00.CSV')
p.figure()
p.fill([5.21065e-5,5.21065e-5,0.00834466,0.00834466],
        [2.830,2.846,2.846,2.830],alpha=.5,fc='.5',ec='none')
p.text(.00318671,2.84446,'RF Pulse',ha='center')
p.text(.0180343,2.84446,'RF',ha='center')
p.fill([.0167742,.01677425,d[-1,0],d[-1,0]],
        [2.830,2.846,2.846,2.830],alpha=.5,fc='.5',ec='none')
p.plot(d[:,0],d[:,1])
p.xlabel('Time [sec]')
p.ylabel('Intensity [V]')
p.savefig('graphics/rabi_overview.png')
p.show()

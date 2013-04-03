import pylab as p

# Example Signal
p.figure()
d = p.genfromtxt('../bswitch_nf/03-15-bswitch_nf_temp10.csv',
        skip_header=2, skip_footer=19, delimiter=',')
p.plot(d[:,0],(d[:,1]-min(d[:,1]))/max(d[:,1]-min(d[:,1])))
p.plot(d[:,0],(d[:,2]-min(d[:,2])/2.)/max(d[:,2]-min(d[:,2])/2.))
p.xlabel('Time [sec]')
p.ylabel('Normalized Intensity [1]')
p.savefig('graphics/wf_overview.png')
p.close()

for scan in ['od','temp','z','x']:
    g = p.genfromtxt('storage/wf_{}_nf.dat'.format(scan))

    xlabel = lambda : p.xlabel({'od':'OD Factor [1]', 'temp':'Temperature [$^{\circ} C$]',
        'z':'Z Square Wave Amplitude [V]', 'x':'X Current [mA]'}[scan])

    # Amplitude
    p.figure()
    p.title(scan+' Amplitude')
    p.errorbar(g[:,0], g[:,1], g[:,6], fmt='.')
    xlabel()

    # Baseline
    p.figure()
    p.title(scan+' Baseline')
    p.errorbar(g[:,0], g[:,5], g[:,10], fmt='.')
    xlabel()

    # Rise-Time-Constant
    p.figure()
    p.title(scan+' Rise-Time Constant')
    p.errorbar(g[:,0], g[:,3], g[:,8], fmt='.')
    xlabel()

    print g[:,-1]
    '''
    # Baseline
    p.figure()
    p.title(scan+' Amplitude to Baseline Ratio')
    p.errorbar(g[:,0], g[:,1]/g[:,3],
            p.sqrt((1/g[:,3])**2*g[:,5]**2+(g[:,1]/g[:,3]**2)**2*(g[:,7])**2), fmt='.')
    xlabel()

    # Baseline
    p.figure()
    p.title(scan+' Baseline - Amplitude')
    p.errorbar(g[:,0], g[:,1]-g[:,3], p.sqrt(g[:,5]**2+g[:,7]**2), fmt='.')
    xlabel()
    '''

p.show()

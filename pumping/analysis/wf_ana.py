from __future__ import division
import pylab as p
import jlab as j

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

    xlabel = lambda : p.xlabel({'od':'Relative Light Intensity [1]',
        'temp':'Temperature [$^{\circ} C$]', 'z':'Z Square Wave Amplitude [V]',
        'x':'X Current [mA]'}[scan])
    u = {'od':'1','temp':'$^{{\circ}} C^{{-1}}$','z':'V^{-1}','x':'mA^{-1}'}[scan]

    if scan == 'od':
        g[:,0] = 1/10**g[:,0]

        # Inverse Rise-Time-Constant
        p.figure()
        #p.title(scan+' Rise-Time Constant')
        a,aerr,chisq,yfit = j.fitline(g[:,0], g[:,3], g[:,8])
        g[:,8] = p.sqrt(g[:,8]**2 + (a[1]*g[:,0]*0.05)**2)
        a,aerr,chisq,yfit = j.fitline(g[:,0], g[:,3], g[:,8])
        sort = p.argsort(g[:,0])
        p.plot(g[:,0][sort], yfit[sort])
        p.errorbar(g[:,0], g[:,3], g[:,8], fmt='.')
        p.text(0.03,27,
                'Model: a+bx\na:{} [$sec^{{-1}}$]\nb:{} [$sec^{{-1}}$]'.format(*[j.fmt_m_e(a[i],
                    aerr[i]) for i in [0,1]])
                +'\n$\chi^2_\\nu$:{:.2}'.format(chisq/(len(g[:,0])-len(a))),va='top')
        p.xlabel('Relative Light Intensity [1]')
        p.ylabel('Inverse Decay Constant [$sec^{-1}$]')
        p.savefig('graphics/od_decay_time.png')

        # Amplitude
        p.figure()
        #p.title(scan+' Amplitude')
        f = lambda x, a: a[0]*p.exp(a[1]*x)+a[2]
        a,aerr,chisq,yfit,corr = j.levmar(g[:,0], g[:,1], g[:,6], f,
                p.array([max(g[:,1]), (g[0,1]-g[-1,1])/(g[0,0]-g[-1,0]), g[-1,1]]))
        g[:,6] = p.sqrt(g[:,6]**2 + (a[0]*a[1]*p.exp(a[1]*g[:,0]))**2*(g[:,0]*0.05)**2)
        a,aerr,chisq,yfit,corr = j.levmar(g[:,0], g[:,1], g[:,6], lambda x, a: a[0]*p.exp(a[1]*x)+a[2],
                p.array([max(g[:,1]), (g[0,1]-g[-1,1])/(g[0,0]-g[-1,0]), g[-1,1]]))
        x = p.linspace(min(g[:,0]), max(g[:,0]), 1000)
        p.plot(x,f(x,a))
        p.errorbar(g[:,0], g[:,1], g[:,6], fmt='.')
        p.text(.03, .28,
                ('Model: a exp(bx)+c\na:{} [V]\nb:{} ['+u+']\nc:{} [V]').format(*[j.fmt_m_e(a[i],
                    aerr[i]) for i in [0,1,2]])
                +'\n$\chi^2_\\nu$:{:.2}'.format(chisq/(len(g[:,0])-len(a))), va='top')
        xlabel()
        p.ylabel('Amplitude Constant [V]')
        p.savefig('graphics/{}_amplitude.png'.format(scan))
        p.show();continue

    if scan == 'temp':
        # Inverse Rise-Time-Constant
        p.figure()
        f = lambda x, a: a[0]*x+a[1]/x+a[2]
        x = p.linspace(min(g[:,0]), max(g[:,0]), 1000)
        a = p.array([1/40.,-40.,0.1])
        g[:,8] = g[:,8]/g[:,3]**2
        g[:,3] = 1/g[:,3]
        a,aerr,chisq,yfit,corr = j.levmar(g[:,0],g[:,3],g[:,8],f,a)
        g[:,8] = p.sqrt(g[:,8]**2 + ((a[0]+a[1]/g[:,0]**2))**2*(0.25)**2)
        a,aerr,chisq,yfit,corr = j.levmar(g[:,0],g[:,3],g[:,8],f,a)
        p.plot(x,f(x,a))
        p.errorbar(g[:,0], g[:,3], g[:,8], fmt='.')
        p.text(p.axis()[0]+0.5,0.99*p.axis()[3],
                 ('Model: ax+b/x+c\na:{} [$sec$/C]\nb:{} [C$sec$]\nc:{} [$sec$]').format(*[j.fmt_m_e(a[i],
                    aerr[i]) for i in [0,1,2]])
                +'\n$\chi^2_\\nu$:{:.2}'.format(chisq/(len(g[:,0])-len(a))), va='top')
        xlabel()
        p.ylabel('Decay Constant [$sec$]')
        p.savefig('graphics/{}_decay_constant.png'.format(scan))
        p.show();continue

    if scan == 'x':
        p.errorbar(g[:,0], g[:,3], g[:,7], fmt='.')
        p.show();continue

    if scan == 'z':
        p.errorbar(g[:,0], g[:,3], g[:,7], fmt='.')
        p.show();continue

p.show()

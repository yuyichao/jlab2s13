from __future__ import division, print_function
from abs_cal import *

make_ta = False
make_fe_cal = False
if 'fit' in sys.argv:
    make_ta = True
    make_fe_cal = True

class TempAbsorber(FeData):
    pass

fe_cal = '../pos_cal_2/02-25-2.csv'
if make_fe_cal:
    fe_cal = FeData([fe_cal], peaks=2, channels_to_bin=2)
    approx = j.Bundle()
    approx.peak_channel = array([665, 1335])
    approx.peak_max_count = max(fe_cal.y)*ones(2)/2
    approx.peak_mins =  min(fe_cal.y)*ones(2) - approx.peak_max_count*1
    approx.peak_fwhm = 100*ones(2)
    fe_cal.prep_fit(approx)
    fe_cal.fit()
    fe_cal.extract_cal(vel)
    fe_cal.gen_cal(fe, [2,3])
    fe_cal.save('storage/temp_fe.p')
else:
    fe_cal = FeData('storage/temp_fe.p')

ta = zeros(2)
tae = zeros(ta.shape)
tac = []
for i,(d,t) in enumerate([(25,21),(26,130)]):   #(22,21),(22,120),
    tao = None
    if make_ta:
        tao = TempAbsorber(['../temp/02-{}-{}c.csv'.format(d,t)],
                peaks=1, channels_to_bin=2)

        approx = j.Bundle()
        approx.peak_channel = array([967])
        approx.peak_max_count = array([max(tao.y)])
        approx.peak_mins = array([min(tao.y)])
        approx.peak_fwhm = array([150])

        tao.prep_fit(approx)
        tao.fit()
        tao.extract_cal(fe_cal)
        tao.temp = t
        tao.save('storage/ta{}.p'.format(i+1))
    else:
        tao = TempAbsorber('storage/ta{}.p'.format(i+1))
    ta[i] = tao.peaks_E[0]
    tae[i] = tao.peaks_Ee[0]
    tac.append(tao)

# Compute temperature coefficient
dch = j.fz(tac[0].peaks_ch[0] - tac[1].peaks_ch[0],
        sqrt(tac[0].peaks_che[0]**2 + tac[1].peaks_che[0]**2))
de = j.fz(fe_cal.ca[1]*dch.m,
        sqrt(dch.m**2*fe_cal.caerr[1]**2+fe_cal.ca[1]**2*dch.e**2))

de1,t1,t2 = j.var('de1 t1 t2')
t_coeff = j.prop(de1/(t2-t1), de1 = de,
             t1=j.fz(tac[0].temp, 4.0), t2=j.fz(tac[1].temp, 4.0),
             units='eV/{^\circ}C')

figure()
title('Temperature Induced Shift in Absorption Peak in Stainless Steel')
c=['r','b','g','c','y','k']
for i,x in enumerate(tac):
    errorbar(x.E, x.y, x.ye, c=c[i+2], label=r'{} $\degree C$'.format(x.temp),
            fmt='.')
    plot(x.E, x.yfit, c=c[i])
    #[axvline(x.peaks_E[0]+s*x.peaks_fwhm_E[0]/2, -10, 10, c=c[i]) for s in [-1,1]]
    axvline(x.peaks_E[0], -10, 10, c=c[i])
    [axvline(x.peaks_E[0]+s*x.peaks_Ee[0], -10, 10, c=c[i], ls='--') for s in [-1,1]]
    print('{} {}'.format(tao.temp, j.fz(tao.peaks_E[0], tao.peaks_Ee[0])))

text((axis()[1]), mean(axis()[2:4]),
        r'$\Delta E/\Delta T$: {}   '.format(t_coeff),
        horizontalalignment='right')
legend()
xlabel('Energy [eV]')
ylabel('Counts [1]')

show()

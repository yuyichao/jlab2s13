from __future__ import division, print_function
from abs_cal import *

# TODO: Use other fe calibrations
make_lw = False
if 'fit' in sys.argv:
    make_lw = True

def thickness(absorb_number):
    # Absorber number -> thickness [mm]
    return j.fz(d/(12.0), d/(12.)*0.5)

d = array([25,50,75,100,125,150])
lwfe_cal = [fe26,fe,fe26,fe,fe26,fe21]

class LWAbsorber(FeData):
    pass

lw = zeros(6)
lwe = zeros(6)
lwc = []
for i,f in enumerate([27,15,27,15,26,21]):
    lwo = None
    if make_lw:
        lwo = LWAbsorber(['../line_shape/02-{}-Na4FeCN6-{}.csv'.format(f,i+1)],
                peaks=1, channels_to_bin=1, bin_cutoff=800, upper_cutoff=1270)
#                peaks=1, channels_to_bin=1, bin_cutoff=920, upper_cutoff=1160)
#                peaks=1, channels_to_bin=2, bin_cutoff=960, upper_cutoff=1130)
        approx = j.Bundle()
        approx.peak_channel = array([1038])
        approx.peak_max_count = array([2800])
        approx.peak_mins = array([min(lwo.y)])
        approx.peak_fwhm = array([30])

        lwo.prep_fit(approx)
        lwo.fit()
        lwo.extract_cal(lwfe_cal[i])
        lwo.save('storage/lw{}.p'.format(i+1))
    else:
        lwo = LWAbsorber('storage/lw{}.p'.format(i+1))
    lw[i] = lwo.peaks_fwhm_E
    lwe[i] = lwo.peaks_fwhm_Ee
    lwc.append(lwo)

# Resulting line fit
a,aerr,chisq,yfit = j.fitline(d,lw,lwe)

# Fit Graphic
figure()
errorbar(d, lw, lwe, fmt='k.', ecolor='0.75')
plot(d,yfit, 'r')
text(axis()[0], 0.99*axis()[3],
'Model:$ax+b$\n a = {} [eV]\n b = {} [eV]\n $\chi^2_\\nu$ = {}'.format(
    j.fmt_m_e(a[1],aerr[1]), j.fmt_m_e(a[0], aerr[0]),
    round(chisq/(len(lw)-len(a)),2)),
        horizontalalignment='left', verticalalignment='top')
#title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width FWHM vs Sample Thickness')
xlabel('Amount of Powder [mg]')
ylabel('FWHM of Absorption Line [eV]')
savefig('graphics/line_width_fit.png')
print('Measured FWHM: {} [eV]'.format(j.fmt_m_e(a[0],aerr[0])))
print('Measured Gamma: {} [eV]'.format(j.fmt_m_e(a[0]/2., aerr[0]/2.)))
print('Sigma Off: {}'.format(round((a[0]/2.-4.7e-9)/(aerr[0]/2),2)))
mE = j.weighted_mean([x.peaks_E[0] for x in lwc], [x.peaks_Ee[0] for x
    in lwc])
print('tau_1/2: {} [s]'.format(j.fmt_m_e(g.const.plancks_constant_h/g.const.electron_volt*log(2)/(2*pi*a[0]/2.),
            sqrt((g.const.plancks_constant_h/g.const.electron_volt*log(2)/(2*pi*(a[0]/2.)**2))**2*(aerr[0]/2.)**2))))

print('Measured E: {} [eV]'.format(j.fmt_m_e(*mE)))
print('Fractional Width: {}'.format(j.fmt_m_e(a[0]/mE[0],
    sqrt((1/mE[0])**2*aerr[0]**2+(a[0]/mE[0]**2)**2*mE[1]))))

# Sample Raw Data and FWHM fit
figure(figsize=(3/4*16,3/4*12))
x = lwc[4]
errorbar(x.ch, x.y, x.ye, fmt='.', ecolor='0.75', c='k')
plot(x.ch, x.yfit, c='b')
text(axis()[0], 0.99*axis()[3],
'$E$ = 14.4 + {} [eV]\n $FWHM$ = {}\n $\Gamma$ = {} [eV]\n $\chi^2_\\nu$ = {}'.format(
    j.fmt_m_e(x.peaks_E[0]-misc.E0,x.peaks_Ee[0]), j.fmt_m_e(x.peaks_fwhm_E[0],
        x.peaks_fwhm_Ee[0]), j.fmt_m_e(x.peaks_fwhm_E[0]/2.,
        x.peaks_fwhm_Ee[0]/2.), round(x.chisq/(len(x.ch)-len(x.a)),2)),
        ha='left', va='top')
[axvline(x.peaks_ch[0]+s*x.peaks_fwhm[0]/2, -10, 10, c='0.5', ls='--')
   for s in [-1,1]]
xlabel('Energy [eV]')
ylabel('Counts [1]')
savefig('graphics/fwhm_fit_line_width_sample_5.png')


'''
figure()
errorbar(d, [x.peaks_fwhm[0] for x in lwc], [x.peaks_fwhm_e[0] for x in lwc], fmt='k.')
title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width Samples')
xlabel('Amount of Powder [mg]')
ylabel('FWHM of Absorption Line [ch]')

figure()
errorbar(d, [x.peaks_ch[0] for x in lwc], [x.peaks_che[0] for x in lwc], fmt='k.')
title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width Samples')
xlabel('Amount of Powder [mg]')
ylabel('Peak of Absorption Line [ch]')
'''

# figure()
# errorbar(d/(12.), lw, lwe, fmt='k.')
# title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width Samples')
# xlabel('Average Thickness of Powder [mm]')
# ylabel('FWHM of Absorption Line [eV]')

'''
c=['r','b','g','k','y','c']
for i,x in enumerate(lwc):
    figure()
    title(str(i+1))
    errorbar(x.ch, x.y, x.ye, fmt='.', c=c[i], label=str(i+1))
    plot(x.ch, x.yfit, c=c[i], label=str(i+1))
    [axvline(x.peaks_ch[0]+s*x.peaks_fwhm[0]/2, -10, 10, c=c[i])
       for s in [-1,1]]
    legend()
    xlabel('Energy [eV]')
    ylabel('Counts [1]')
show()
'''

show()

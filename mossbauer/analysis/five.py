from __future__ import division, print_function
from abs_cal import *

make = False
if 'fit' in sys.argv:
    make = True

class Absorber(FeData):
    pass

o4 = None
o42 = None
if make:
    o4 = Absorber(['../Fe3O4/02-15-Fe3O4.csv'.format(i) for i in [1,2]],
            peaks=9, channels_to_bin=1)
    approx = j.Bundle()
    approx.peak_channel = array([342,408,645,720,957,1057,1209,1537,1900])
    approx.peak_max_count = max(o4.y)*ones(9)/9
    approx.peak_mins = array([2783,2886,2816,2843,2857,2905,2859,2753,2666])\
            - approx.peak_max_count*8
    approx.peak_fwhm = 50*ones(9)
    o4.prep_fit(approx)

    o4.fit()
    o4.extract_cal(vel)
    o4.save('storage/fe3o4.p')

    # Six Peak Fit
    o42 = Absorber(['../Fe3O4/02-15-Fe3O4.csv'.format(i) for i in [1,2]],
            peaks=6, channels_to_bin=1)
    approx = j.Bundle()
    approx.peak_channel = array([342,645,957,1209,1537,1900])
    approx.peak_max_count = max(o42.y)*ones(6)/6
    approx.peak_mins = array([2783,2816,2857,2859,2753,2666])\
            - approx.peak_max_count*8
    approx.peak_fwhm = 50*ones(6)
    o42.prep_fit(approx)

    o42.fit()
    o42.extract_cal(vel)
    o42.save('storage/fe3o4_six_peak_fit.p')

else:
    o4 = Absorber('storage/fe3o4.p')
    o42 = Absorber('storage/fe3o4_six_peak_fit.p')

figure(figsize=(3/4*16,3/4*12))
ylabel('Counts [1]')
subplot(211)
title('Fit')
#title('$Fe_3O_4$ Nine Peak Fit')
errorbar(o4.E-misc.E0, o4.y, o4.ye, fmt='.', c='0.5', ecolor='0.75')
#plot(o4.ch, o4.peaks_func(o4.ch, o4.a0))
plot(o4.E-misc.E0, o4.yfit, 'k', lw=2)
[axvline(x-misc.E0, -10, 10, c='r') for x in o4.peaks_E]
[axvline(x-misc.E0+i*xe, -10, 10, c='k', ls='--')
        for x,xe in zip(o4.peaks_E, o4.peaks_Ee) for i in [-1,1]]
text(max(o4.E-misc.E0), min(o4.y), r'$\chi_\nu^2:${}'.format(round(o4.nchisq,2)),
        ha='right')
xticks([])
subplot(212)
title('Residuals')
plot(o4.E-misc.E0, o4.y-o4.yfit, 'b.')
plot(o4.E-misc.E0, zeros(o4.E.shape), 'r')
xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
savefig('graphics/fe3o4_9_fit.png')

figure(figsize=(3/4*16,3/4*12))
ylabel('Counts [1]')
subplot(211)
title('Fit')
#title('$Fe_3O_4$ Six Peak Fit')
errorbar(o42.E-misc.E0, o42.y, o42.ye, fmt='.', c='0.5', ecolor='0.75')
#plot(o42.ch, o42.peaks_func(o42.ch, o42.a0))
plot(o42.E-misc.E0, o42.yfit, 'k', lw=2)
[axvline(x-misc.E0, -10, 10, c='r') for x in o42.peaks_E]
[axvline(x-misc.E0+i*xe, -10, 10, c='k', ls='--')
        for x,xe in zip(o42.peaks_E, o42.peaks_Ee) for i in [-1,1]]
text(max(o42.E-misc.E0), min(o42.y), r'$\chi_\nu^2:${}'.format(round(o42.nchisq,2)),
        horizontalalignment='right')
xticks([])
subplot(212)
title('Residuals')
plot(o42.E-misc.E0, o42.y-o42.yfit, 'b.')
plot(o42.E-misc.E0, zeros(o42.E.shape), 'r')
xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
savefig('graphics/fe3o4_6_fit.png')
show()

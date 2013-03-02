from __future__ import division, print_function
from abs_cal import *

make_lw = False
if 'fit' in sys.argv:
    make_lw = True

def thickness(absorb_number):
    # Absorber number -> thickness [mm]
    return j.fz(d/(12.0), d/(12.)*0.5)

d = array([25,50,75,100,125,150])

class LWAbsorber(FeData):
    pass

lw = zeros(6)
lwe = zeros(6)
lwc = []
for i,f in enumerate([27,15,27,15,26,21]):
    lwo = None
    if make_lw:
        lwo = LWAbsorber(['../line_shape/02-{}-Na4FeCN6-{}.csv'.format(f,i+1)],
                peaks=1, channels_to_bin=2)
        approx = j.Bundle()
        approx.peak_channel = array([1038])
        approx.peak_max_count = array([2800])
        approx.peak_mins = array([min(lwo.y)])
        approx.peak_fwhm = array([20])

        lwo.prep_fit(approx)
        lwo.fit()
        lwo.extract_cal(fe)
        lwo.save('storage/lw{}.p'.format(i+1))
    else:
        lwo = LWAbsorber('storage/lw{}.p'.format(i+1))
    lw[i] = lwo.peaks_fwhm_E
    lwe[i] = lwo.peaks_fwhm_Ee
    lwc.append(lwo)

figure()
errorbar(d, lw, lwe, fmt='k.')
title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width Samples')
xlabel('Amount of Powder [mg]')
ylabel('FWHM of Absorption Line [eV]')

# figure()
# errorbar(d/(12.), lw, lwe, fmt='k.')
# title(r'M$\"o$ssbauer $Na_4FeCN_6$ Line-Width Samples')
# xlabel('Average Thickness of Powder [mm]')
# ylabel('FWHM of Absorption Line [eV]')

figure()
c=['r','b','g','k','y','c']
for i,x in enumerate(lwc):
    plot(x.E, x.y, c=c[i], label=str(i+1))
    [axvline(x.peaks_E[0]+s*x.peaks_fwhm_E[0]/2, -10, 10, c=c[i]) for s in [-1,1]]
legend()
xlabel('Energy [eV]')
ylabel('Counts [1]')

show()

from __future__ import division, print_function
from abs_cal import *

make = False
if 'fit' in sys.argv:
    make = True

class Absorber(FeData):
    pass

so4 = None
so43 = None
if make:
    so4 = Absorber(['../FeSO4_Fe2SO4_3/02-19-FeSO4.csv'], peaks=2,
            channels_to_bin=1)
    approx = j.Bundle()
    approx.peak_channel = array([1008, 1335.69])
    approx.peak_max_count = max(so4.y)*ones(2)/2
    approx.peak_mins =  min(so4.y)*ones(2) - approx.peak_max_count*1
    approx.peak_fwhm = 50*ones(2)
    so4.prep_fit(approx)

    so4.fit()
    so4.extract_cal(vel)
    so4.save('storage/feso4.p')

    so43 = Absorber(['../FeSO4_Fe2SO4_3/02-27-Fe2SO4_3.csv'], peaks=1,
            channels_to_bin=1)
    approx = j.Bundle()
    approx.peak_channel = array([1098])
    approx.peak_max_count = max(so43.y)*ones(1)/1
    approx.peak_mins =  min(so43.y)*ones(1)
    approx.peak_fwhm = 80*ones(1)
    so43.prep_fit(approx)
    so43.fit()
    so43.extract_cal(vel)
    so43.save('storage/fe2so43.p')

else:
    so4 = Absorber('storage/feso4.p')
    so43 = Absorber('storage/fe2so43.p')

# errorbar(so4.ch, so4.y, so4.ye)
# plot(so4.ch, so4.yfit)
figure(figsize=(3/4*16,3/4*12))
errorbar(so43.E-misc.E0, so43.y, so43.ye, fmt='k.', ecolor='0.75')
plot(so43.E-misc.E0, so43.yfit, 'r', lw=1)
axvline(0, -10, 10, c='k', ls='--')
axvline(so43.peaks_E[0]-misc.E0, -10, 10,c='r', ls='--')
#[axvline(so43.peaks_E[0]+i*so43.peaks_Ee[0]-misc.E0, -10, 10, c='r', ls='--') for i in [-1,1]]
text(-5e-7, 3400,
r'$\chi^2_\nu$: {}'.format(round(so43.nchisq,2)),
va='bottom', ha='left')
xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
ylabel('Counts [1]')
savefig('graphics/fe2so43_fit_overview.png')

figure(figsize=(3/4*16,3/4*12))
errorbar(so43.E-misc.E0, so43.y, so43.ye, fmt='k.', ecolor='0.75')
plot(so43.E-misc.E0, so43.yfit, 'r', lw=1)
axvline(0, -10, 10, c='k', ls='--')
axvline(so43.peaks_E[0]-misc.E0, -10, 10,c='r', ls='--')
[axvline(so43.peaks_E[0]+i*so43.peaks_Ee[0]-misc.E0, -10, 10, c='b', ls='--') for i in [-1,1]]
axis([-2e-8, 5e-8,3200,4600])
shift = (so43.peaks_E[0]-misc.E0, so43.peaks_Ee[0])
# arrow(0, 4254.86, shift[0], 0, length_includes_head=True,
#        shape='full', lw=3, head_width=1e-10, arrowstype='->')
text(1.9986e-8, 4250, '$\delta$={} [eV]'.format(j.fmt_m_e(*shift)), ha='left',
va='center')
xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
ylabel('Counts [1]')
savefig('graphics/fe2so43_fit_iso.png')

show()

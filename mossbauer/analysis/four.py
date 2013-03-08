from __future__ import division, print_function
from abs_cal import *

make = False
if 'fit' in sys.argv:
    make = True

class Absorber(FeData):
    pass

o3 = None
if make:
    o3 = Absorber(['../Fe2O3/02-14-Fe2O3_{}.csv'.format(i) for i in [1,2]],
            peaks=6, channels_to_bin=1)
    approx = j.Bundle()
    approx.peak_channel = array([282, 620, 973, 1220, 1577, 1946])
    approx.peak_max_count = max(o3.y)*ones(6)/6
    approx.peak_mins =  min(o3.y)*ones(6) - approx.peak_max_count*5
    approx.peak_fwhm = 50*ones(6)
    o3.prep_fit(approx)

    o3.fit()
    o3.extract_cal(vel)
    o3.save('storage/fe2o3.p')

else:
    o3 = Absorber('storage/fe2o3.p')


ged = []
gede = []
for l,h in [(1,3), (2,4)]:
    ged.append(abs(o3.peaks_E[l]-o3.peaks_E[h]))
    gede.append(sqrt(o3.peaks_Ee[l]**2+o3.peaks_Ee[h]**2))
print('\Delta E_g:', j.fmt_m_e(*j.weighted_mean(ged,gede)))

ged = []
gede = []
for l,h in [(1,2),(3,4)]:
    ged.append(abs(o3.peaks_E[l]-o3.peaks_E[h]))
    gede.append(sqrt(o3.peaks_Ee[l]**2+o3.peaks_Ee[h]**2))
print('\Delta E_m:', j.fmt_m_e(*j.weighted_mean(ged,gede)))

print('\Delta Q:',
        j.fmt_m_e(abs(o3.peaks_E[0]+o3.peaks_E[-1]-o3.peaks_E[1]-o3.peaks_E[4])/2.,
    sqrt(o3.peaks_Ee[0]**2+o3.peaks_Ee[-1]**2+o3.peaks_Ee[1]**2+o3.peaks_Ee[4]**2)))

figure(figsize=(3/4*16,3/4*12))
errorbar(o3.E-misc.E0, o3.y, o3.ye, fmt='k.', ecolor='0.75')
plot(o3.E-misc.E0, o3.yfit, 'r', lw=2)
[axvline(x-misc.E0, -10, 10, c='k', ls='--') for x in o3.peaks_E]
text(-5.1e-7, 290, r'$\chi^2_\nu$: {}'.format(round(o3.nchisq,2)), va='top', ha='left')
xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
ylabel('Counts [1]')
savefig('graphics/fe2o3_fit.png')
show()

from __future__ import division, print_function
import sys
import os
import matplotlib
font={'family':'sans','weight':'normal','size':16}
matplotlib.rc('font', **font)
from pylab import *
import jlab as j
import cPickle
import pygsl as g; g.import_all()

if not os.path.exists('storage'):
    os.makedirs('storage')

## Adjustable Parameters
bin_cutoff = 199
make_vel = False
make_fe = False
if __name__=='__main__' and 'fit' in sys.argv:
    make_vel = True
    make_fe = True

## Create Additional Data Bundle
misc = j.Bundle()
misc.E0 = 14.4e3 #eV
misc.lam = 6.328e-7 # wavelength of laser [m]
misc.DT = 100.0e-6 # dwell time [sec]
misc.N = 4000 # passes [1]

def a_peak(ch, a):
    C0, B, CH0, FWHM = a
    return C0*(1-B/((ch-CH0)**2+(FWHM/2.)**2))

def n_peaks(ch, a, num):
    x = zeros(ch.shape)
    for i in range(num):
        x += a_peak(ch, array([a[i], a[i+num], a[i+2*num], a[i+3*num]]))
    return x

# Velocity Curve Analysis
class Vel:
    def __init__(self, data_file, misc_data=None):
        if data_file[-2:] == '.p':
            self.__dict__ = cPickle.load(open(data_file, 'rb'))
            return
        self.raw = genfromtxt(data_file, delimiter=',',
                 skip_header=17)
        if misc_data == None:
            misc_data = misc
        self.misc = misc_data
    def fit(self, a0, bin_cutoff):
        self.a0 = a0
        speed_func_ = lambda x, a: self.speed_count_func(x, a)
        self.a, self.aerr, self.chisq, self.yfit = j.levmar(
                self.raw[bin_cutoff:,0], self.raw[bin_cutoff:,2],
                sqrt(self.raw[bin_cutoff:,2]), speed_func_, self.a0,
                print_dev=True)[:-1]
        self.ch = self.raw[:,0]
        self.vel, self.vele = self.ch_to_vel(self.ch)
    def speed_count_func(self, v, a=None):
        return abs(self.vel_count_func(v, a))
    def vel_count_func(self, v, a=None):
        if a == None:
            a = self.a
        a1, min_point = a
        return a1*(v-min_point)
    def vel_count_func_error(self, ch, che):
        a1, min_point = self.a
        return sqrt(((ch-min_point)**2*self.aerr[0]**2\
                +(a1)**2*che**2+a1**2*self.aerr[1]**2))
    def ch_to_vel(self, chs, che=None):
        if che == None:
            che = zeros(chs.shape)
        return (self.vel_count_func(chs, self.a)*self.misc.lam/(2*self.misc.N*self.misc.DT),
              self.vel_count_func_error(chs, che)*self.misc.lam/(2*self.misc.N*self.misc.DT))
    def ch_to_E(self, chs, che=None):
        v = self.ch_to_vel(chs, che)
        return (misc.E0*(1+v[0]/g.const.speed_of_light),
                misc.E0*v[1]/g.const.speed_of_light)
    def save(self, filename):
        cPickle.dump(self.__dict__, open(filename, 'wb'))

class FeData:
    def __init__(self, data_files, misc_data=None, channels_to_bin=1, peaks=6,
            bin_cutoff=bin_cutoff, upper_cutoff=None):
        # data_files should be list
        if misc_data == None:
            misc_data = misc
        self.misc = misc_data
        if type(data_files) == str:
            self.__dict__ = cPickle.load(open(data_files, 'rb'))
            return
        self.raw = sum(genfromtxt(x, delimiter=',', skip_header=17) for x in
            data_files)
        self.peaks = peaks

        ## Bin Fe Data
        end = len(self.raw[:,0])-1
        if upper_cutoff:
            end = upper_cutoff
        bins = arange(bin_cutoff, end, channels_to_bin)
        digitized = np.digitize(range(len(self.raw[:,0])), bins)
        self.ch = (bins[1:]+bins[:-1])/2.
        self.y = array([self.raw[:,2][digitized == i].sum() for i in range(1, len(bins))])
        self.ye = sqrt(self.y)

        # Check that no 0 error of a point (causes problems with fit)
        assert(0 not in self.ye)

        # Check for non-even bins
        assert(False not in ((bins[1:]-bins[:-1]) == bins[2]-bins[1]))

    def prep_fit(self, approx):
        B = -(approx.peak_mins/approx.peak_max_count-1)*(approx.peak_fwhm/2)**2
        self.a0 = concatenate([approx.peak_max_count, B, approx.peak_channel,
            approx.peak_fwhm])

    def peaks_func(self, ch, a):
        return n_peaks(ch, a, self.peaks)

    def fit(self):
        peaks_func = lambda ch, a: self.peaks_func(ch, a)
        self.a, self.aerr, self.chisq, self.yfit = j.levmar(self.ch, self.y,
                self.ye, peaks_func, self.a0, print_dev=True)[:-1]
        self.nchisq = self.chisq/(len(self.ch)-len(self.a))
        self.peaks_ch = self.a[2*self.peaks:(2*self.peaks+self.peaks)]
        self.peaks_che = self.aerr[2*self.peaks:(2*self.peaks+self.peaks)]

    def extract_cal(self, vel):
        self.peaks_E, self.peaks_Ee = vel.ch_to_E(self.peaks_ch,
                self.peaks_che)
        self.peaks_fwhm = self.a[3*self.peaks:(3*self.peaks + self.peaks)]
        self.peaks_fwhm_e = self.aerr[3*self.peaks:(3*self.peaks + self.peaks)]
        self.peaks_fwhm_E = []
        self.peaks_fwhm_Ee = []
        for i in range(self.peaks):
            x,xe = vel.ch_to_E(self.peaks_ch[i] + self.peaks_fwhm[i]/2,
                    sqrt(self.peaks_che[i]**2 + self.peaks_fwhm_e[i]**2/4))
            y,ye = vel.ch_to_E(self.peaks_ch[i] - self.peaks_fwhm[i]/2,
                    sqrt(self.peaks_che[i]**2 + self.peaks_fwhm_e[i]**2/4))
            self.peaks_fwhm_E.append(x-y)
            self.peaks_fwhm_Ee.append(sqrt(xe**2+ye**2))
        self.E = vel.ch_to_E(self.ch)[0]
        self.peaks_fwhm_E = array(self.peaks_fwhm_E)
        self.peaks_fwhm_Ee = array(self.peaks_fwhm_Ee)

    def gen_cal(self, fe, peaks=None):
        if peaks == None:
            peaks = range(len(fe.peaks_E))
        self.ca,self.caerr,self.cchisq,self.cyfit = j.fitline(self.peaks_ch,
                fe.peaks_E[peaks], fe.peaks_Ee[peaks])

    def cal_ch_to_E(self, ch, che = None):
        if che == None:
            che = zeros(ch.shape)
        return (self.ca[0] + self.ca[1]*ch, sqrt((self.ca[1]*che)**2 +
            (self.caerr[0])**2 + ch**2*self.caerr[1]**2))

    def ch_to_E(self, ch, che = None):
        return self.cal_ch_to_E(ch, che)

    def save(self, filename):
        cPickle.dump(self.__dict__, open(filename, 'wb'))

## Compute Absolute Channel -> Velocity Calibration
vel = None
fe = None
fe21 = None
fe26 = None

if make_vel:
    vel = Vel('../pos_cal/02-14-V_2.csv')
    vel.fit(array([15000/800., 1000]), bin_cutoff)
    vel.save('storage/vel.p')
else:
    vel = Vel('storage/vel.p')

if make_fe:
    fe = FeData(['../pos_cal/'+x+'.csv' for x in ['02-14-6_1',
        '02-14-6_2']])

    # Manual Intervention for Approximate location of peaks
    approx = j.Bundle()
    approx.peak_channel = array([528, 742, 955, 1120, 1352, 1586])
    approx.peak_max_count = max(fe.y)*ones(6)/6
    approx.peak_mins = min(fe.y)*ones(6) - 5*int(mean(approx.peak_max_count))
    approx.peak_fwhm = array([50,50,50,50,50,50])

    fe.prep_fit(approx)
    fe.fit()
    fe.extract_cal(vel)
    fe.gen_cal(fe)
    fe.save('storage/fe.p')

    # fe21
    fe21 = FeData(['../pos_cal/02-21-6.csv'])
    fe21.prep_fit(approx)
    fe21.fit()
    fe21.gen_cal(fe)
    fe21.save('storage/fe21.p')

    # fe26
    fe26 = FeData(['../pos_cal/02-26-6.csv'])
    fe26.prep_fit(approx)
    fe26.fit()
    fe26.gen_cal(fe)
    fe26.save('storage/fe26.p')

else:
    fe = FeData('storage/fe.p')
    fe21 = FeData('storage/fe21.p')
    fe26 = FeData('storage/fe26.p')

#DE = vel.vel_per_channel[approx.peak_channel.astype(int)]/g.const.speed_of_light*misc.E0
#T = abs(vel.vel_per_channel[(approx.peak_channel+approx.peak_fwhm/2).astype(int)]-
#        vel.vel_per_channel[(approx.peak_channel-approx.peak_fwhm/2).astype(int)])*misc.E0/(2*g.const.speed_of_light)
#B = -(approx.peak_mins/approx.peak_max_count-1)*T**2
#fe.a0 = concatenate([approx.peak_max_count, B*1e22, DE*1e10, T*1e10, [misc.E0]])

if __name__ == '__main__':
    ## Figures

    # Vel Fit Figure
    figure()
    errorbar(vel.raw[:,0], vel.raw[:,2], sqrt(vel.raw[:,2]),fmt='k.')
    axvline(bin_cutoff, -10, 10, c='k')
    errorbar(vel.raw[:bin_cutoff,0], vel.raw[:bin_cutoff,2],
            sqrt(vel.raw[:bin_cutoff,2]),fmt='.', c='0.5')
    plot(vel.raw[bin_cutoff:,0], vel.yfit, 'r', lw=2)
    grid()
    #plot(vel.raw[bin_cutoff:,0], vel.vel_count_func(vel.raw[bin_cutoff:,0]), 'b')
    xlabel('Channel')
    ylabel('Counts [1]')
    text(axis()[1]-100, axis()[3]-100, r'$\chi^2$: {}'.format(round(vel.chisq/(len(vel.ch)-len(vel.a)),2)),
            va='top', ha='right')
    savefig('graphics/vel_cal.png')

    # Plot Fit Results
    print('$chi^sq$: {}'.format(fe.chisq))
    figure()
    errorbar(fe.E-misc.E0, fe.y, fe.ye, fmt='k.', ecolor='0.75')
    plot(fe.E-misc.E0, fe.yfit, 'r', lw=2)
    [axvline(x-misc.E0,-10, 10, c='k') for x in fe.peaks_E]
    xlabel('$\Delta E$ from 14.4e3[eV] in Electron Volts')
    ylabel('Counts [1]')
    savefig('graphics/fe_cal.png')

    show();exit()

    # Raw Data Figure
    figure()
    plot(range(len(fe.raw[:,2])), fe.raw[:,2],'.')
    axvline(bin_cutoff, -10, 10, c='r')
    xlabel('Channels [1]')
    ylabel('Counts [1]')


    # Plot Fit Results
    print('$chi^sq$: {}'.format(fe.chisq))
    figure()
    errorbar(fe.ch, fe.y, fe.ye, fmt='.')
    plot(fe.ch, fe.yfit, 'r')
    [axvline(x,-10, 10, c='k') for x in fe.a[12:18]]
    xlabel('Channel [1]')
    ylabel('Counts [1]')

    figure()
    errorbar(vel.ch_to_E(fe.ch)[0], fe.y, fe.ye)
    [axvline(x, -10, 10, c='k') for x in fe.peaks_E]

    x = vel.ch_to_E(fe.peaks_ch, fe.peaks_che)
    for k,v in zip(*x):
        print('DE {} [eV]'.format(j.fmt_m_e(misc.E0-k,v)))

    # Resulting Calibration
    fe.gen_cal(fe)
    figure()
    errorbar(fe.peaks_ch, fe.peaks_E, fe.peaks_Ee, c='k')
    errorbar(fe.ch, fe.cal_ch_to_E(fe.ch)[0], fe.cal_ch_to_E(fe.ch)[1], c='r')
    plot(fe.ch, vel.ch_to_E(fe.ch)[0], 'g')
    xlabel('Channel [1]')
    ylabel(r'$E$ [eV]')

    show()

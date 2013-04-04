import pylab as p
import sys; sys.path+=['../']
import jlab as j

nums = ['Two','Three','Five','Seven']
mod = [p.genfromtxt('mod{}.dat'.format(i)) for i in [2,3,4,5]]

f = lambda x,a: a[0]*(x+a[1])*p.exp(-a[2]*(x-a[3]))+a[4]
a0 = lambda x: p.array([(max(x)-min(x))/10.,0.1,0.05,0.1,x[-1]])

[p.plot(1-mod[i],label='{} Level'.format(nums[i])) for i in range(len(nums))]
p.legend(loc='lower right')
p.ylabel('Intensity')
p.xlabel('Iteration')
p.savefig('../graphics/theory_wf_fit.png')

'''
x = p.arange(0,200,1)
p.plot(x+200,1-f(x,a0(mod3)))
a,aerr,chisq,yfit,corr = j.levmar(x,mod3[200:],1e-6*p.ones(200),f,a0(mod3))
p.plot(x+200,1-yfit)
'''
p.show()

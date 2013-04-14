''' Plots all csv files in a directory '''
import pylab as p
import os
import sys

data_dir = sys.argv[1] if len(sys.argv) > 1 else '../all_data/4-11/'

for f in [x for x in os.listdir(data_dir) if 'csv' in x][::-1]:
    d = p.genfromtxt(os.path.join(data_dir,f),skip_header=2,delimiter=',')
    p.figure()
    p.title(f)
    [p.plot(d[:,0],d[:,i],label='ch%i'%(i)) for i in range(1,d.shape[1]-1) if i != 4]
    p.legend()
p.show()

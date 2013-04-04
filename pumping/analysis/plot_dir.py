import pylab as p
import os

data = '../bswitch_nf/'
for i in [x for x in os.listdir(data) if 'csv' in x or 'CSV' in x]:
    p.figure()
    x = p.genfromtxt(os.path.join(data,i), skip_header=2,
            skip_footer=19, delimiter=',')
    p.plot(x[:,0],x[:,1])
    p.title(str(i))
    p.show();exit()
p.show()

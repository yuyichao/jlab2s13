import pylab as p

norm = lambda x: (x-min(x))/max(x-min(x))
plot = lambda x,*c: p.plot(norm(x),*c)
index = p.genfromtxt('dat_index.dat', dtype=[('files','S256'),('peak','i8'),('beam','i8')])

def get_tri_range(d):
    s,e = 2*[len(d)/2]
    tmax,tmin = max(d),min(d)
    trng = 1e-2*(tmax-tmin)
    tmax -= trng
    tmin += trng
    while tmin < d[s] < tmax:
        s -= 1
    while tmin < d[e] < tmax:
        e += 1
    return (s,e)

def smooth(x,window_len=11,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    s=p.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w=p.ones(window_len,'d')
    else:
        w=eval('p.'+window+'(window_len)')
    y=p.convolve(w/w.sum(),s,mode='same')
    return y[window_len:-window_len+1]

for peak in set(index['peak']):
    lf = [index['files'][(index['peak']==peak)*(index['beam']==i)] for i in [0,1]]
    d = [[p.genfromtxt(f,skip_header=2,delimiter=',') for f in x] for x in lf]
    d = [[[x[s:e,:] for s,e in [get_tri_range(x[:,4])]][0] for x in y] for y in d]

    sc = 30
    dsr = [smooth(x[:,3],sc) for x in d[1][1:]]
    ddr = [smooth(x[:,3],sc) for x in d[0]]
    p.figure()
    p.title("peak:%i"%(peak))
    [plot(x) for x in ddr]
    dsx = [p.argmin(x[1500:]).flatten()[0] for x in dsr]
    ddx = [p.argmin(x[1500:]).flatten()[0] for x in ddr]
    dcut = min(dsx+ddx)
    ds = [smooth(x[:,2]-x[:,3],sc)[s-dcut:] for x,s in zip(d[1][1:],dsx)]
    dd = [smooth(x[:,2]-x[:,3],sc)[s-dcut:] for x,s in zip(d[0],ddx)]
    dsr = [x[s-dcut:] for x,s in zip(dsr,dsx)]
    ddr = [x[s-dcut:] for x,s in zip(ddr,ddx)]
    avg_range = range(min(map(len,ds+dd)))
    dsa = p.array([p.mean([x[i] for x in ds]) for i in avg_range])
    dda = p.array([p.mean([x[i] for x in dd]) for i in avg_range])

    [plot(x,'r') for x in ds]
    [plot(x,'b') for x in dd]
    plot(dsa)
    plot(dda)
    plot(dsa-dda)

p.show()

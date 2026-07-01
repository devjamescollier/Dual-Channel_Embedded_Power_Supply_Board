import numpy as np,sys
def load(f):
    d=np.loadtxt(f)
    t=d[:,0]; return t,d[:,1],d[:,3],d[:,5],d[:,7],d[:,9],d[:,11]
def win(t,y,a,b):
    m=(t>=a)&(t<b); return y[m],t[m]
for f in sys.argv[1:]:
    t,vo,il,vin,comp,ss,en=load(f)
    vnom=3.3 if 'v33' in f else 5.0
    ton,toff=7e-3,8.5e-3
    v,_=win(t,vo,6.5e-3,7e-3); light=v.mean(); rl=np.ptp(v)
    v,_=win(t,vo,8.2e-3,8.5e-3); heavy=v.mean(); rh=np.ptp(v)
    i,_=win(t,il,8.2e-3,8.5e-3)
    v,tt=win(t,vo,ton,ton+0.5e-3); und=v.min()
    # settling: last time outside +/-1% of heavy mean
    out=np.where(abs(v-heavy)>0.01*vnom)[0]; ts=(tt[out[-1]]-ton)*1e6 if len(out) else 0
    v,tt=win(t,vo,toff,toff+0.5e-3); ovs=v.max()
    ilpk=il[t>1e-3].max()
    v,tt=win(t,vo,0,7e-3); 
    r=np.where(v>0.9*vnom)[0]; tr=tt[r[0]]*1e3 if len(r) else float('nan')
    st=np.where(vo>0.1*vnom)[0]; t0=t[st[0]]*1e3 if len(st) else float('nan')
    vpk_start=vo[t<6.9e-3].max()
    vin_on=vin[np.argmax(ss>0.01)] if (ss>0.01).any() else float('nan')
    # switching freq at heavy load: count rising edges of IL slope sign changes ~ approximate via peaks
    g=np.loadtxt(f,usecols=(15,))[ (t>=8.0e-3)&(t<8.5e-3)]; fs=((g[1:]>0.5)&(g[:-1]<0.5)).sum()/0.5e-3/1e3
    print(f"{f:16s} Vout@0.1A={light:.4f}V rip={rl*1e3:.1f}mVpp | Vout@1.5A={heavy:.4f}V rip={rh*1e3:.1f}mVpp IL={i.mean():.3f}A ILpk(max)={ilpk:.2f}A fsw~{fs:.0f}kHz | step: under={und:.3f}V ({(und-heavy)/vnom*100:+.1f}%) settle={ts:.0f}us over={ovs:.3f}V ({(ovs-light)/vnom*100:+.1f}%) | start Vin={vin_on:.2f}V t10-90 start={t0:.2f}->{tr:.2f}ms startpk={vpk_start:.3f}V")

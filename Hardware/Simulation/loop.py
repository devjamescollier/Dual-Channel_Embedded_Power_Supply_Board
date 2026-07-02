import numpy as np
fs=570e3; gm=92e-6; Ro=8.7e6; gmps=12; L=6.8e-6
def T(f,vin,vo,io,rtop,rbot,rz,cz,cp,co,esr,se=0.5e6):
    s=2j*np.pi*f
    zc=1/(1/Ro + 1/(rz+1/(s*cz)) + s*cp)
    zo=1/(io/vo + 1/(esr+1/(s*co)))
    D=vo/vin; sn=(vin-vo)/L; mc=1+se/sn
    wn=np.pi*fs; Q=1/(np.pi*(mc*(1-D)-0.5))
    fh=1/(1+s/(wn*Q)+s**2/wn**2)
    return rbot/(rtop+rbot)*gm*zc*gmps*zo*fh
f=np.logspace(1,6,20000)
rows=[("3.3V Vin12 Co50u",12,3.3,10.2e3,3.24e3,29.4e3,1e-9,47e-12,50e-6),
      ("3.3V Vin6  Co50u",6,3.3,10.2e3,3.24e3,29.4e3,1e-9,47e-12,50e-6),
      ("3.3V Vin12 Co30u",12,3.3,10.2e3,3.24e3,29.4e3,1e-9,47e-12,30e-6),
      ("3.3V Vin12 Co80u",12,3.3,10.2e3,3.24e3,29.4e3,1e-9,47e-12,80e-6),
      ("5V   Vin12 Co36u",12,5,10e3,1.91e3,49.9e3,4.7e-9,39e-12,36e-6),
      ("5V   Vin6  Co36u",6,5,10e3,1.91e3,49.9e3,4.7e-9,39e-12,36e-6),
      ("5V   Vin12 Co25u",12,5,10e3,1.91e3,49.9e3,4.7e-9,39e-12,25e-6),
      ("5V   Vin12 Co50u",12,5,10e3,1.91e3,49.9e3,4.7e-9,39e-12,50e-6)]
for name,vin,vo,rt,rb,rz,cz,cp,co in rows:
  for io in (0.2,1.5):
    t=T(f,vin,vo,io,rt,rb,rz,cz,cp,co,1.5e-3)
    mag=20*np.log10(abs(t)); i=np.where(mag<0)[0][0]
    fc=f[i]; pm=180+np.degrees(np.angle(t[i]))
    ph=np.unwrap(np.angle(t)); j=np.where(np.degrees(ph)<-180)[0]
    gmarg=-mag[j[0]] if len(j) else float('inf')
    print(f"{name} Io={io:.1f}A  fc={fc/1e3:6.1f} kHz  PM={pm:5.1f} deg  GM={gmarg:5.1f} dB")

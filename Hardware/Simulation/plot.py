import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(3,2,figsize=(13,10))
for col,(rail,v) in enumerate([('v33',3.3),('v5',5.0)]):
    for vin,c in [(12,'#1f77b4'),(6,'#d62728')]:
        d=np.loadtxt(f'{rail}_vin{vin}.dat'); t=d[:,0]*1e3
        ax[0,col].plot(t[::20],d[::20,1],c,lw=0.8,label=f'Vin={vin} V')
        m=(t>6.9)&(t<7.4); ax[1,col].plot(t[m],d[m,1],c,lw=0.8,label=f'Vin={vin} V')
        m=(t>8.3)&(t<8.31); ax[2,col].plot((t[m]-8.3)*1e3,d[m,3],c,lw=0.8,label=f'IL, Vin={vin} V')
    ax[0,col].set_title(f'{v} V rail: startup (Vin ramps 0→Vin in 1 ms) + 0.1→1.5 A step at 7 ms'); ax[0,col].set_xlabel('ms'); ax[0,col].set_ylabel('Vout (V)')
    ax[1,col].set_title('Load step 0.1 A → 1.5 A'); ax[1,col].set_xlabel('ms'); ax[1,col].set_ylabel('Vout (V)')
    ax[2,col].set_title('Inductor current @1.5 A (steady state)'); ax[2,col].set_xlabel('µs'); ax[2,col].set_ylabel('A')
    for a in ax[:,col]: a.grid(alpha=.3); a.legend(fontsize=8)
plt.tight_layout(); plt.savefig('simulation_results.png',dpi=110)

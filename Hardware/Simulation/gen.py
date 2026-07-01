# Generates ngspice decks for a TPS54331 cycle-by-cycle peak-current-mode model.
import sys
def deck(name, vin, rtop, rbot, rz, cz, cp, cout, esr, rload_light, istep, css=10e-9,
         ren1=200e3, ren2=56e3, tstop=10e-3, tstep_on=7e-3, tstep_off=8.5e-3):
    return f"""* {name}
.option method=gear reltol=1e-3 abstol=1e-9 vntol=1e-5 itl4=200
.param fsw=570k tper={{1/fsw}}
* ---- input: battery (50 mOhm) ramps up over 1 ms ----
Vbat bat 0 PWL(0 0 1m {vin})
Rbat bat vin 0.05
Cin1 vin cin_esr 4.7u
Rin1 cin_esr 0 3m
Cin2 vin 0 0.1u
* ---- EN / UVLO divider with datasheet currents (1uA below, 4uA above threshold) ----
Ren1 vin en {ren1}
Ren2 en 0 {ren2}
Ben 0 en I = (V(en) > 1.25 ? 4u : 1u)
Ben_ok enok 0 V = (V(en) > 1.25 && V(vin) > 3.5) ? 1 : 0
* ---- slow start: 2uA into Css while enabled ----
Css ss 0 {css}
Gss 0 ss cur='V(enok) > 0.5 ? 2u : 0'
Rssd ss 0 1e9
Bnen nen 0 V = 1 - V(enok)
Sssd ss 0 nen 0 SWSS
.model SWSS SW(Vt=0.5 Vh=0.01 Ron=1 Roff=1e12)
Bref ref 0 V = min(V(ss), 0.8)
* ---- gm error amplifier: 92uA/V, +/-7uA, Ro = 8.7 MOhm ----
Gea 0 comp cur='7u*tanh(92u*(V(ref)-V(fb))/7u)'
Roea comp 0 8.7meg
Rz comp cz_n {rz}
Cz cz_n 0 {cz}
Cp comp 0 {cp}
* COMP clamps: 0.5V Eco-mode floor, ~0.87V ceiling (=> 4.6 A peak)
Vcl1 cfl 0 0.5
Dlo cfl comp DID
Vcl2 chi 0 0.87
Dhi comp chi DID
.model DID D(Is=1e-14 N=0.01)
.model DCL D(Is=1e-14)
* ---- peak current command: 12 A/V, floor 160 mA (Eco-mode) ----
Bipk ipk 0 V = 12*(V(comp)-0.487)
* ---- clock, leading-edge blanking (130ns), max duty 93% ----
Vclk clk 0 PULSE(0 1 0 1n 1n 20n {{tper}})
Vblank blk 0 PULSE(0 1 130n 1n 1n {{0.93*tper-131n}} {{tper}})
* slope compensation ramp, 0.5 A/us equivalent
Bramp ramp 0 V = 0.5e6 * (time - floor(time/tper)*tper)
Brst rst 0 V = (V(enok) < 0.5) || (V(comp) < 0.502) || (V(fb) > 0.872) || (V(blk) < 0.5 && (time - floor(time/tper)*tper) > 0.5*tper) || (V(blk) > 0.5 && (I(Vsns) + V(ramp)) > V(ipk)) ? 1 : 0
Aadc [clk rst] [dclk drst] ADC1
.model ADC1 adc_bridge(in_low=0.4 in_high=0.6)
Aone one_a ONEGEN
.model ONEGEN d_pullup
Aff one_a dclk nul drst q qb DFF1
.model DFF1 d_dff(clk_delay=1n set_delay=1n reset_delay=1n)
Anul nul ZGEN
.model ZGEN d_pulldown
Adac [q] [gate] DAC1
.model DAC1 dac_bridge(out_low=0 out_high=1)
* ---- power stage ----
Shs vin ph gate 0 SWHS
.model SWHS SW(Vt=0.5 Vh=0.05 Ron=0.1 Roff=1e8)
Dcatch 0 ph B340
.model B340 D(Is=10u N=1.2 Rs=0.03 Cjo=300p BV=40 Iave=3)
Vsns ph lx 0
L1 lx lr 6.8u
Rdcr lr out 0.09
Co out co_e {cout}
Rco co_e 0 {esr}
* ---- feedback divider (0R loop-break resistor included) ----
Rtop out fb {rtop}
Rbot fb 0 {rbot}
* ---- load: light resistive + step ----
Rl out 0 {rload_light}
Iload out 0 PWL(0 0 {tstep_on} 0 {tstep_on+1e-6} {istep} {tstep_off} {istep} {tstep_off+1e-6} 0)
.control
set noaskquit
tran 10n {tstop} 0 10n uic
wrdata {name}.dat V(out) I(Vsns) V(vin) V(comp) V(ss) V(en) V(enok) V(gate) V(ipk)
quit
.endc
.end
"""
cases = {
 # name: Vin, Rtop, Rbot, Rz, Cz, Cp, Cout_effective (DC-bias derated), ESR, Rload_light, Istep
 "v33_vin12": (12, 10.2e3, 3.24e3, 29.4e3, 1e-9, 47e-12, 50e-6, 1.5e-3, 33, 1.4),
 "v33_vin6":  (6,  10.2e3, 3.24e3, 29.4e3, 1e-9, 47e-12, 50e-6, 1.5e-3, 33, 1.4),
 "v5_vin12":  (12, 10e3, 1.91e3, 49.9e3, 4.7e-9, 39e-12, 50e-6, 1.5e-3, 50, 1.4),
 "v5_vin6":   (6,  10e3, 1.91e3, 49.9e3, 4.7e-9, 39e-12, 50e-6, 1.5e-3, 50, 1.4),
}
for n,a in cases.items():
    open(n+".cir","w").write(deck(n,*a))

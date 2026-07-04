# TPS54331 Rail Simulations (ngspice)

There is no vendor ngspice model for the TPS54331. `gen.py` builds a cycle-by-cycle
peak-current-mode model from the datasheet (SLVS839H) parameters:

| Parameter | Value used |
| --- | --- |
| Switching frequency / max duty / min on-time | 570 kHz / 93 % / 130 ns blanking |
| Error amplifier | gm = 92 µA/V, Ro = 8.7 MΩ (800 V/V), ±7 µA output |
| COMP → switch current | 12 A/V, COMP clamp 0.5 V (Eco-mode, 160 mA) to ~4.6 A |
| Reference / soft start | 0.8 V, 2 µA into Css (10 nF → 4 ms) |
| EN / UVLO | 1.25 V threshold, 1 µA / +3 µA hysteresis current |
| OVTP | high-side off above 109 % Vref |
| Power stage | 100 mΩ high side, B340 Schottky, 6.8 µH (90 mΩ DCR) |
| Output caps | DC-bias-derated effective C: 50 µF on both rails |

Run: `python3 gen.py && for f in *.cir; do ngspice -b $f; done && python3 analyze.py *.dat && python3 plot.py`
(`analyze.py`/`plot.py` need numpy and matplotlib). `loop.py` computes loop gain and phase margin
from the small-signal current-mode model, including the fs/2 sampling double pole.

## Results (from results.txt / loop_results.txt)

| Rail | Vin | Vout @0.1 A | Vout @1.5 A | Ripple @1.5 A | 0.1→1.5 A step | Crossover / PM |
| --- | --- | --- | --- | --- | --- | --- |
| 3.3 V | 12 V | 3.316 V | 3.315 V | 3.9 mVpp | −5.9 %, 55 µs to 1 % | 23.8 kHz / 60–63° |
| 3.3 V | 6 V  | 3.316 V | 3.315 V | 2.1 mVpp | −5.6 %, 54 µs | 23.8 kHz / 59–62° |
| 5 V   | 12 V | 4.984 V | 4.983 V | 4.5 mVpp | −4.0 %, 330 µs | 26.5 kHz / 66–67° |
| 5 V   | 6 V  | 4.984 V | 4.986 V | 4.3 mVpp | −5.0 %, 285 µs | ~26 kHz / >61° |

Startup is monotonic with no overshoot. The converters start at Vin ≈ 5.5 V (EN UVLO from 200 k / 56 k).
Ripple is idealized: no PCB parasitics or capacitor ESL. Expect a few times higher on the bench.

## Reverse-polarity protection (`reverse_polarity.cir`)

Q1 (AONR21357 P-FET, high side) sits between the XT60 + pin (`VBAT_IN`) and `+BATT`. R6 (100 k)
pulls the gate to GND, and D1 (12 V zener) clamps Vgs, because Q1 is rated for ±25 V and the
TPS54331 allows up to 28 V in. The model is a level-1 PMOS fitted to the datasheet
(Vth −1.7 V, Rds(on) ≈ 10 mΩ at Vgs = −4.5 V). The load is a 5 A sink, which is pessimistic.
Run with `ngspice -b reverse_polarity.cir`.

| Vbatt | Drop across Q1 | Vgs | Q1 dissipation |
| --- | --- | --- | --- |
| 4.9 V (UVLO stop) | 44 mV | −4.9 V | 0.22 W |
| 6 V | 32 mV | −6.0 V | 0.16 W |
| 12 V | 14 mV | −11.8 V | 0.07 W |
| 24–28 V | 14 mV | clamped to −12 V | 0.07 W |
| −12 V / −28 V (reversed) | blocks; about 1 nA flows | 0 V | 0 |

# [Check a converter operating point by hand](@id checking-ibr-operating-point)

**Page status:** self-checked arithmetic tutorial for one supplied RMS operating point; no network solve or physical controller validation.

A converter can satisfy its power-factor law and still violate a capability
limit. Changing Q to meet the limit can then break the law. This tutorial makes
that conflict visible in the P–Q plane, starting from voltage and current rather
than reported power. It then changes the voltage monitor without changing the
supplied phasors.

You need complex conjugation and a linear inequality. The calculation runs with
Python alone; the package-specific applicability rules remain in
[IBR control applicability](@ref ibr-pf-control-audit).

## 1. Recover power from the supplied phasors

Use a single ordered phase–neutral pair with RMS terminal voltages relative to
the same earth/frame origin:

```math
V_p=12+\mathrm j4\ \mathrm V,\qquad
V_n=3+\mathrm j4\ \mathrm V,\qquad
U=V_p-V_n=9\ \mathrm V.
```

Define I as the current injected by the converter at p, with −I injected at n.
Positive P and Q denote injection into the network. Supply

```math
I=\frac49+\mathrm j\frac13\ \mathrm A.
```

**Predict:** is the reactive injection positive or negative?

Conjugating the current gives

```math
S=U\overline I
 =9\left(\frac49-\mathrm j\frac13\right)
 =4-\mathrm j3\ \mathrm{VA}.
```

Thus P = 4 W and Q = −3 var. Call this point **A**. Its PF magnitude is
4/5. In the signed constant-PF convention used here, target f = +4/5 requires
negative Q when P is positive. Another data format may use a different sign
convention; the equation below is the definition for this exercise.

## 2. Intersect the laws; do not clip a point into compliance

Take constant target f = +4/5, generation-only minimum m = 4/5, and a lower
reactive injection bound Q ≥ −2 var. Since the complementary coefficient is
3/5, the three obligations are

```math
\begin{aligned}
\text{Constant PF:}\quad &\frac45 Q+\frac35 P=0,\\
\text{Minimum PF:}\quad &P\ge0,\quad -\frac34P\le Q\le\frac34P,\\
\text{Capability:}\quad &Q\ge-2\ \mathrm{var}.
\end{aligned}
```

![P–Q diagram showing the minimum-PF wedge, constant-PF ray and Q cap, with three candidate points.](../assets/ibr-pq-intersection.png)

*The bold segment satisfies all three declared constraints. A lies below the
Q cap; B lies off the constant-PF ray; C is their intersection. The shaded
minimum-PF wedge alone admits both signs of Q. No other capability limit or
network equation is included in this picture. The shaded wedge is truncated
at the plot edge; there is no P ≤ 5 W bound.*

At A, constant and minimum PF pass, but Q is 1 var below the lower bound.
Suppose we replace Q by −2 var while retaining P = 4 W. This gives **B**.
Its constant-PF weighted residual becomes

```math
\left|\frac45(-2)+\frac35(4)\right|=\frac45\ \mathrm{VA}.
```

B satisfies the minimum envelope and Q cap, but fails constant PF. Clipping Q
has changed which obligation fails.

To retain constant PF, follow its line Q = −3P/4 to the cap. Solving
−3P/4 = −2 gives **C**: P = 8/3 W, Q = −2 var. More generally, all points on
the bold segment satisfy these three constraints:

```math
0\le P\le\frac83\ \mathrm W,\qquad Q=-\frac34P.
```

C is the largest P in this local intersection. A feeder equation, another
device limit or an objective can change the network's admissible or selected
point. The diagram does not establish a network optimum. At the origin the
weighted laws pass, but the PF quotient is undefined.

## 3. Change the monitor, keeping the phasors fixed

A voltage-dependent controller must say which voltage it measures. For the
same terminal phasors, phase-to-neutral (PN) and phase-to-ground (PG) give

```math
U_{\mathrm{PN}}=|V_p-V_n|=9\ \mathrm V,\qquad
U_{\mathrm{PG}}=|V_p|=\sqrt{160}\ \mathrm V>12\ \mathrm V.
```

Subtracting phasors before taking the magnitude matters. Subtracting their
separate magnitudes would not give PN voltage.

![Equal-scale voltage phasor diagram showing the phase and neutral vectors and their 9 V difference.](../assets/ibr-voltage-monitor.png)

*The horizontal arrow is the phase–neutral difference. The diagonal phase
vector starts at the earth/frame origin. PN and PG are different observations
of the same supplied state, not two solutions of the circuit.*

For a separate Volt-var exercise, use the chapter's requested piecewise-linear
(PWL) graph: voltage breakpoints [8,9,11,12] V, reactive fractions [−0.6,0.44]
and branch rating 20 VA. PN is at the start of the zero band and requests
Q = 0. PG exceeds the last breakpoint and requests Q = −0.6 × 20 = −12 var.
The VI-derived injection at A is still −3 var; changing the monitor changes
the request, not that observation.

This is an alternative control example, not a PF/droop mixture. These are
requested PWL targets; the [declared smoothed model](@ref ibr-volt-var-audit)
has its own target and residual. A target alone does not show that capability,
minimum PF or the network can accommodate it.

## Run it, then change one input

From the repository root, using Python 3.11 or later:

```sh
python3 experiments/lessons/ibr_operating_point.py
python3 experiments/lessons/ibr_operating_point.py --check
python3 experiments/lessons/ibr_operating_point.py --q-min=-1
```

The default run prints A = (4,−3), B = (4,−2), C = (8/3,−2), with separate
constant-PF, generation, minimum-envelope and Q-cap residuals. Nonzero residuals
identify failures of these exact equations. The script uses rational arithmetic
and writes no files. Its seven checks also cover reference reversal, a common
terminal-voltage shift, absorption and a per-phase violation hidden by totals.

Before running the last command, predict where C moves. Then explain why A's
power is unchanged: its authored voltage and current were not changed.

**Answer:** Q ≥ −1 intersects the ray at P = 4/3 W, Q = −1 var. The admissible
segment shortens. A still has P = 4 W and Q = −3 var, so its Q-cap violation
grows to 2 var. The command changes a bound, not the supplied point or a solve.

**Transfer exercise:** now consider three per-phase minimum-PF declarations
with m = 4/5 and powers P = [1,10,10] W, Q = [3,0,0] var. Does an aggregate
PF check establish all three declarations?

**Answer:** aggregate P = 21 W and Q = 3 var give PF magnitude
``21/\sqrt{21^2+3^2}>4/5``. The first phase nevertheless has upper weighted
excess ``(4/5)3-(3/5)1=9/5`` VA. Check the declared branch scope before summing
powers. The [control chapter](@ref ibr-pf-control-audit) carries this distinction
into topology applicability, incomplete observations and finite tolerances.

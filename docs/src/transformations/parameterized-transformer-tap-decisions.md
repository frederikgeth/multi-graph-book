# [Parameterized transformer tap decisions](@id parameterized-transformer-tap-decisions)

A fixed transformer primitive is a snapshot, not a decision model. If a tap is
continuous or discrete, substituting its start value before optimization
removes feasible operating points, the decision identity, and any objective or
constraint that depends on the tap.

This chapter compiles an adjustable winding transfer into an exact
parameterized factor. It does not select a tap and does not claim that one
fixed admittance represents all positions.

## Typed tap domain

For transformer ``x`` and adjustable winding ``k``, let ``t_{xk}`` be a stable
decision identity. The compact contract declares one of

```math
\mathcal D_{xk}^{\mathrm{cont}}
=[\underline t_{xk},\overline t_{xk}],
\qquad
\mathcal D_{xk}^{\mathrm{disc}}
=\{t_{xk}^{(1)},\ldots,t_{xk}^{(m)}\}.
```

It also records the start value, but the start is initialization data—not a
replacement for the domain. Values must be finite and positive; discrete
positions must be unique and ordered. Every adjustable winding has a unique
decision identifier such as `tap/x1/winding/2`.

The first executable parameterization is a scalar ganged tap applied to all
labelled coils on one winding:

```math
a_{xkc}(t_{xk})
=t_{xk}a^0_{xkc},
\qquad c\in\mathcal C_{xk}.
```

The base coefficient ``a^0_{xkc}`` may itself be complex and need not be equal
across coils. The scalar tap parameterization is a declared model family, not
an inference from a field named `tap`. Independent per-phase controls require
distinct decision identities and a richer domain.

## A family of exact fixed-linear factors

Stack all retained decisions as ``\mathbf t_x``. The power-dual transfer from
the previous chapter becomes

```math
\mathbf B_x(\mathbf t_x)
=\mathbf T_x(\mathbf t_x)\mathbf A_x.
```

At every admissible decision ``\mathbf t_x\in\mathcal D_x``, the terminal
factor is

```math
\mathbf Y_x(\mathbf t_x)
=\mathbf B_x(\mathbf t_x)^{\mathrm H}
 \mathbf Y_x^{\mathrm{coil}}
 \mathbf B_x(\mathbf t_x)
 +\mathbf S_x^{\mathsf T}\mathbf Y_x^0\mathbf S_x
 +\mathbf Y_x^{\mathrm{ground}}.
```

The corresponding winding-side leakage current is retained as

```math
\mathbf I_x^{\mathrm{w,leak}}(\mathbf t_x)
=\mathbf T_x(\mathbf t_x)^{\mathrm H}
 \mathbf Y_x^{\mathrm{coil}}
 \mathbf T_x(\mathbf t_x)\mathbf A_x\mathbf U_x.
```

The compiler stores this parameterized relation and the decision domain. Its
evaluator accepts a complete admissible decision assignment, substitutes that
same value into the transfer, and invokes the certified fixed-linear
compilation `TR-XFMR-004`. Missing, additional, continuous out-of-range, or
unlisted discrete values return structured rejections.

## Exactness for decision problems

Let ``z`` contain network states and other controls. For constraints and an
objective that use the declared terminal and recovered component quantities,
the source feasible set has the form

```math
\mathcal F_x
=\left\{
(z,\mathbf t_x):
\mathbf t_x\in\mathcal D_x,
\quad
g_x(z,\mathbf t_x)=0,
\quad
h_x(z,\mathbf t_x)\leq0
\right\}.
```

`TR-XFMR-005` maps the decision by identity,

```math
\widehat{\mathbf t}_x=\mathbf t_x,
```

and uses the same pointwise component relations. Hence it preserves the
declared feasible set and any objective ``f(z,\mathbf t_x)`` expressed through
those interfaces. This is an exact compilation because the tap remains a
variable; it is not a claim that the resulting optimization problem is convex
or easy.

By contrast, evaluating the start value ``\mathbf t_x^0`` produces only the
slice

```math
\mathcal F_x^{\mathrm{frozen}}
=\{(z,\mathbf t_x)\in\mathcal F_x:
\mathbf t_x=\mathbf t_x^0\}.
```

Unless the domain is already a singleton or the decision is provably
irrelevant to the requested result, this is an inner restriction rather than
an exact compilation.

```@raw latex
\newpage
```

## Discrete decision witness

```@raw latex
\mbox{\strut}\par
```

The illustrative contract layers a discrete winding-2 tap
``\{0.95,1.00,1.05\}`` on the running WYE/WYE/DELTA transformer. It does not
modify the canonical fixture or claim these are nameplate settings. At a fixed
balanced boundary-voltage witness, winding 2 is at ``0.97`` of its nominal
voltage. The decision problem minimizes the maximum winding-2 leakage current
subject to the original ``2200\ \mathrm A`` winding limit.

| Tap ``t_{x_1,2}`` | Maximum winding-2 current (A) | Feasible |
|:--:|--:|:--:|
| 0.95 | 4732.320 | no |
| 1.00 | 1903.716 | yes |
| 1.05 | 1232.656 | yes |

Both the direct source evaluation and parameterized target retain feasible
positions ``\{1.00,1.05\}`` and select ``1.05``. Freezing the factor at its
``1.00`` start value gives objective ``1903.716\ \mathrm A`` rather than
``1232.656\ \mathrm A``, a gap of ``671.060\ \mathrm A``. It therefore loses
the optimal decision even though the frozen point itself is feasible.

Across all three positions, the recorded source/target terminal-admittance
difference is zero to machine precision. The largest component complex-power
residual is ``4.88\times10^{-9}\ \mathrm{VA}`` at the SI-scaled witness.

```@raw latex
\par\medskip
```

## Continuous and coordinate tests

The same compiler accepts a continuous interval. The executable test uses
``[0.94,1.06]``, evaluates an interior value ``1.013``, and rejects ``1.061``.
Reordering a winding's labelled base coefficients changes only their stored
coordinates: alignment produces the same terminal factor at the same retained
tap value.

Malformed domains are rejected before a start snapshot is constructed. The
guards cover missing or duplicate decision identities, unsupported coefficient
parameterizations, nonpositive or unsorted positions, invalid continuous
bounds, and start values outside the declared domain.

## Model boundary

The current rule covers scalar ganged magnitude taps whose fixed excitation and
internal-grounding factors do not depend on tap. Phase-angle controls,
independent phase taps, mechanically coupled devices, tap-dependent leakage,
deadbands, switching costs, operation-count limits, and automatic control logic
need additional typed relations. A solver adapter must encode the retained
continuous or discrete factor without changing its domain or current recovery
semantics.

The machine-readable result is certificate `TR-XFMR-005`. The
[transformer tap AC decision case](@ref transformer-tap-ac-decision-case) now
couples this factor to network voltage, neutral-KCL, power-balance, and
recovered-current constraints rather than holding the boundary-voltage witness
fixed.

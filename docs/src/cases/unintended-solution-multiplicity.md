# [When a model admits unintended solutions](@id unintended-solution-multiplicity)

**Page status:** self-checked exact scalar witnesses and pinned local-solver comparisons; no general AC uniqueness or dynamic-stability result.

A successful solve answers the equations and constraints that were supplied.
It does not establish that they describe the intended set of operating points,
or that the returned point is unique. This lesson separates three mechanisms:
changed admissibility, undetermined internal currents, and a lost physical
balance equation. Keep *equation roots*, *feasible operating points*, *local
optima* and *global optima* distinct throughout.

![Three mechanisms: two circuit roots distinguished by current limits, a continuous neutral-current family bounded but not selected by ratings, and a spurious zero-voltage root rejected by original KCL. Solid/dashed curves, open circles/crosses, interval endpoints and labels carry the distinctions without relying on colour.](../assets/solution-multiplicity.png)

Panel A shows two exact intersections. Its shaded strip is allowed by the
power caps but excluded by the current cap. Panel B is a current interval, not
a probability distribution; marker heights separate labels and have no physical
meaning. Panel C plots two different residual equations in their respective
per-unit coordinates; the shared axis is not an assertion that current and
power residual tolerances are interchangeable.

## Predict: which constraint describes the intended limit?

For an RMS phasor port, ``S=V\overline I``. At nonzero voltage,

```math
|S|\le S_{\max}\quad\Longleftrightarrow\quad
|I|\le \frac{S_{\max}}{|V|}.
```

Setting ``S_{\max}=V_{\rm nom}I_{\max}`` matches a current limit only at the
specified nominal voltage. Below nominal it allows more current; above nominal
it can be stricter. Neither constraint is universally a relaxation of the
other over an arbitrary voltage domain. Apparent-power ratings can be legitimate
requirements in their own right; the error is substituting one for an intended
conductor-current constraint without checking the domain and observation.
Neither simple static cap is a complete conductor-temperature model.

**Predict.** Can this substitution admit an additional operating point even
when apparent power is checked at **both** ends of a line?

## A. Same circuit roots, different admissibility

Use a real resistive two-bus circuit in consistent per-unit coordinates:

```math
E=\frac45,\qquad R=1,\qquad P=\frac3{25},\qquad
0\le V\le E.
```

Current is positive from the fixed-voltage source to the receiving bus. Retain
both equations:

```math
E-V=RI,\qquad VI=P.
```

Eliminating current gives

```math
V^2-\frac45V+\frac3{25}
=\left(V-\frac15\right)\left(V-\frac35\right)=0.
```

The factorisation exhausts the roots for this scalar model. It is not a
conclusion inferred from two solver runs. Choose ``I_{\max}=1/2`` and
``V_{\rm nom}=1``, hence the proposed constant power cap is ``S_{\max}=1/2``.
Sending power is ``EI``; receiving power magnitude is ``VI``. Their difference
is the physical resistive loss ``RI^2``.

| Quantity | Lower-voltage root | Higher-voltage root |
|:--|--:|--:|
| Receiving voltage ``V`` | 0.2 | 0.6 |
| Current ``I`` | 0.6 | 0.2 |
| Sending power ``EI`` | 0.48 | 0.16 |
| Receiving power ``VI`` | 0.12 | 0.12 |
| Resistive loss ``RI^2`` | 0.36 | 0.04 |
| Current cap 0.5 | **Fails** | Passes |
| Both-end power caps 0.5 | Passes | Passes |

Claim `LIMIT-MULTIPLICITY-001` concerns this changed admissible set. The lower
root remains a solution of the circuit equations, but violates the intended
current cap. It is not a new equation root created by a power inequality.
These deliberately depressed voltages expose the distinction; they are not a
proposal for normal service-voltage limits or a realistic feeder benchmark.

Two controls matter. Converting at the actual fixed sending voltage gives
``S_{\max}^{\rm from}=0.8\times0.5=0.4`` and excludes the lower root in this
series-only circuit. A justified receiving-voltage lower bound of 0.5 also
excludes it. Neither observation makes nominal conversion safe in general,
or justifies imposing a positive lower bound at every neutral or return.

### Feasible points, local optima and global optima

With a constant feasibility objective, both power-limited points are global
minimizers. With the objective ``\min EI``, the higher-voltage root is the unique
global minimizer among the two: 0.16 is less than 0.48. **Both isolated feasible
points are nevertheless local minimizers.** Each has a small neighbourhood
containing no other feasible point. An objective can distinguish global values
without making a local method cross between disconnected feasible components.

The pinned Ipopt observations illustrate this: starts at 0.05 and 0.2 return
the lower branch with `LOCALLY_SOLVED`, including under source-power minimization;
starts at 0.4, 0.6 and 0.75 return the higher branch. These are version- and
initialization-specific observations, not basins-of-attraction guarantees.
The global comparison above follows from exact root enumeration, not from
Ipopt's termination label.

For general positive ``E,R,P``, the discriminant is ``E^2-4RP``. A zero
discriminant gives one distinct repeated root; a negative discriminant gives
no real roots. Neither root counting nor the sign of a static equation derivative
establishes dynamic stability. A dynamic load/controller model would be needed.

## B. Ratings bound a current mode without selecting it

Two parallel ideal neutral paths have equal zero endpoint voltages and a
prescribed total through-current of 12 A. Full KCL is retained:

```math
I_1+I_2=12,\qquad (I_1,I_2)=(\alpha,12-\alpha),\quad \alpha\in\mathbb R.
```

Every terminal power is zero. Nonnegative apparent-power caps therefore impose
no restriction on ``\alpha``. This mode is a current circulation, not an arbitrary
voltage-reference shift: changing it changes the conductor currents that a rating
or measurement would observe.

Retaining ``|I_1|\le7`` A and ``|I_2|\le10`` A restricts ``\alpha`` to ``[2,7]`` A.
It bounds the admissible family but does not give a unique split. This extends
the [vanishing-impedance lesson](@ref vanishing-impedance-current-selection),
whose ratio-dependent selection is claim `PRACTICE-SHORT-001`.

| Additional model or objective | First/second current | Meaning |
|:--|:--|:--|
| Ideal paths and current caps only | ``(\alpha,12-\alpha)``, ``2\le\alpha\le7`` | Continuum remains |
| Positive resistances ``\varepsilon,2\varepsilon`` | 8 A / 4 A | Violates the first current cap |
| Positive resistances ``2\varepsilon,\varepsilon`` | 4 A / 8 A | Satisfies both caps |
| Ideal paths, caps, and ``\min(I_1^2+I_2^2)`` | 6 A / 6 A | Unique objective-selected point |

The finite-resistance comparisons keep the port **current-driven**. With one
endpoint at zero, the other has voltage ``8\varepsilon`` V when
``\varepsilon`` is expressed in ohms. This voltage tends to zero; it is not fixed
at zero for positive resistance. Keeping both endpoint voltages at zero and
requiring nonzero resistive current would be a different, inconsistent problem.

The minimum-norm selection follows from
``\alpha^2+(12-\alpha)^2=2(\alpha-6)^2+72`` and is inside the cap interval.
It is not the current-sharing law of either finite-resistance circuit. A small
positive weighting of this objective still selects 6 A / 6 A when the remaining
objective is constant along the ideal current mode. Regularization can choose
one answer without recovering the physical information removed by idealization.

## C. A root of the wrong equation

A prescribed 1 A injection feeds a 1 S resistor to ground. In normalized
coordinates its current law and original KCL are

```math
I=V,\qquad r_I=I-1=0.
```

The unique state is ``V=I=1``. Replace KCL by its power product, however, and

```math
r_S=V(I-1)=V(V-1)=0
```

also admits ``V=I=0``. At that point the original current residual is −1, although
the power residual is zero. Minimizing supplied power ``V\times1`` in the faulty
model selects this spurious root globally on ``0\le V\le2``. This is the
[zero-voltage balance boundary](@ref zero-voltage-kcl), claim
`FORMULATION-ZERO-001`; the multiconductor consequences are discussed in
Geth's versioned zero-voltage manuscript [Geth2023ZeroVoltage](@cite).

The faulty scalar equation has derivative ``2V-1=-1`` at the spurious root.
Thus the wrong model can have an isolated, nonsingular, accurately computed
solution. Jacobian rank and numerical convergence do not authenticate the
original physics. Conversely, with zero injection, ``V^2=0`` has a single
repeated root even though its derivative is zero: rank deficiency alone does
not prove a continuous family.

Adding a current cap does not restore lost KCL. For example ``|I|\le0.5`` still
admits the spurious zero-current point while excluding the physically required
1 A point. Even ``|S|\le |V|I_{\max}`` is vacuous at zero voltage. Restore the
current equation or another demonstrably equivalent relation over the full
required domain; a convenient positive voltage floor is not a universal repair.

## Diagnose the mechanism before choosing a remedy

| Mechanism | What changes or disappears? | Appropriate check | What the check does not establish |
|:--|:--|:--|:--|
| A: nominal power cap replaces a current cap | Admissible subset of the same circuit roots | Evaluate both endpoint powers and conductor currents at every enumerated root | General uniqueness or dynamic stability |
| B: parallel paths become ideal | Constitutive current-sharing relation | Parameterize the KCL family; retain member limits and compare declared finite ratios | A unique physical split from a minimum-norm objective |
| C: KCL is replaced by a power product | Original balance information at zero voltage | Recompute original current residuals, including at zero voltage | Model validity from convergence or Jacobian rank alone |

These are different interventions. Restoring a current rating repairs the stated
constraint substitution in A, only bounds the family in B, and cannot restore
the missing equation in C.

## Reproduce and challenge the result

```sh
python3 experiments/lessons/solution_multiplicity.py --check
python3 experiments/lessons/solution_multiplicity.py
python3 scripts/check_bmopf_integration.py --bmopf-root ../BMOPFTools.jl
```

The input fixture is `experiments/lessons/solution_multiplicity.json`. The exact
Python checker uses rational arithmetic and checks the committed,
source-hash-bound `experiments/generated/solution-multiplicity.json`. It includes
both-end ratings, objective comparisons, discriminant controls, reversed current,
an empty rating interval, two finite-resistance ratios and the lost-KCL residual.
It deliberately refuses irrational square roots instead of silently turning
this exact witness into an approximate general root finder.

The Julia companion runs in the existing immutable integration environment. Its
`solution-multiplicity.json` run output records all attempted solves, statuses,
starts, constraints, independent residuals, versions and source/environment hashes.
It first uses declared intervals ``[0.1,0.3]`` and ``[0.5,0.7]`` to isolate the
known roots, then records unrestricted multistart observations separately. The
current-limited lower interval is analytically infeasible; any returned iterate
is diagnostic, not an accepted operating point. Both roots of the faulty KCL
model are likewise isolated and checked against the original equation.

These are book-owned scalar models in JuMP, not new BMOPFTools device checks.
The package pin, direct-audit candidate and MCP execution surface are unchanged.
The figure can be regenerated with Matplotlib 3.10.8 using
`experiments/lessons/render_solution_multiplicity.py`; its curves illustrate the
exact artifact and do not establish completeness by sampling.

**Transfer exercise.** First change only ``I_{\max}`` from 0.5 to 0.3 while
keeping ``V_{\rm nom}=1`` and recomputing ``S_{\max}``. Do both roots still pass
the power caps? Then change only the load to ``P=4/25`` in the original branch
case. How many distinct roots remain? **Check your reasoning:** the sending-end
0.3 power cap rejects the lower branch (0.48), while the higher branch passes
(0.16); at ``P=4/25`` the quadratic has the single repeated root ``V=I=0.4``.
Do not count the repeated factor twice or infer dynamic stability from it.

Before calling a solution unintended, name the intended equations, constraints,
observations and objective. An overloaded circuit root, an ideal circulation,
a coordinate symmetry and a KCL-violating root are different findings. The
[delta-coil lesson](@ref delta-coil-current-lesson) supplies another distinction:
unchanged terminal observations can hide violated internal device laws.

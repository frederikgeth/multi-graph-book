# [When may a null mode be removed?](@id quotients-and-observations)

**Page status:** self-checked algebraic lesson with exact rational witnesses; no automatic symmetry detector or native package capability is claimed.

A matrix nullspace says which changes that matrix cannot see. It does not say
whether those changes satisfy the remaining equations, preserve a rating, or
leave the requested answer unchanged. This lesson separates three situations
that can otherwise look like the same numerical singularity. Claim
`KERNEL-OBSERVATION-001` records the scoped result.

## Start with the question being preserved

For a model with feasible set ``F`` and requested observation ``h(x)``, a proposed
identification ``x\sim y`` must be justified relative to those objects.
If ``h(x)\ne h(y)``, the observation cannot be a well-defined function of the
identified state. If feasibility or objective value differs, identifying the
states also requires more than dropping a coordinate.

For a nonempty affine solution set ``Ax=b`` and linear observation ``Hx``, two solutions
have the same observation precisely when their difference ``d`` lies in
``\ker A\cap\ker H``. Additional equations, inequalities and objectives must
still be checked. A nullspace of a component map need not be a nullspace of
the full equations. For nonlinear equations, even a Jacobian null vector may
fail to extend to a finite solution family: ``f(x)=x^2=0`` has derivative zero
at its unique real solution. We use affine relations below so that this local
versus finite distinction does not obscure the main comparison.

**Predict before reading.** Which changes preserve only the measured output,
which preserve the full model, and which are acceptable when member ratings
are part of the question?

| Proposed change | Equations initially inspected | Requested observation |
|:--|:--|:--|
| Add 5 V to both floating potentials | Resistor law and KCL | Voltage difference, current, dissipation |
| Add 1 A to one ideal parallel path and subtract it from the other | KCL and ideal zero voltage drop | Each member current and rating |
| Add 1 A to every oriented delta coil | Terminal-current map | Terminal currents **and** each coil law |

## A. A removable floating voltage reference

Take an isolated two-node resistor with conductance ``g=2`` S and balanced
injections ``(6,-6)`` A. There is no connection to a fixed earth potential,
absolute-voltage bound, or earth-referenced device law. Its equations are

```math
I=g(v_a-v_b)=6\;\mathrm A.
```

The states ``(v_a,v_b)=(3,0)`` V and ``(8,5)`` V give the same difference 3 V,
current 6 A and dissipation 18 W. More generally, adding any real constant
``c`` to both potentials leaves the equations and these observations unchanged.
Setting ``v_b=0`` chooses the unique representative
``(v_a-v_b,0)`` of each translation class. Recovery of the original absolute
offset is impossible without extra information, but it is unnecessary for the
three stated observations. An objective depending only on these observations
also has the same value throughout the class.

This is an **additive common-potential freedom in the declared floating
circuit**. It is distinct from the simultaneous phasor-angle rotation used in
other AC reference conventions. Neither is available automatically in a model
with a fixed source or an external voltage observation.

### Change the model, and the conclusion changes

Add a 1 S shunt from node ``b`` to earth held at 0 V, keeping the injections
unchanged. At ``(3,0)`` the shunt current is zero. At ``(8,5)`` it is 5 A and
node ``b`` KCL fails by 5 A. This extension breaks the proposed translation
symmetry. Shifting an earth coordinate too would be a different transformation;
the counterexample keeps that physical reference fixed.

Likewise, the absolute bounds ``0\le v_a,v_b\le4`` V admit the first state but
reject the second. The objective ``v_b^2`` takes values 0 and 25 V². Either
extension prevents a claim that arbitrary translations preserve the full
optimization problem. A coordinate convention must not silently add a physical
conducting connection, erase an earth-voltage limit, or replace its objective.

## B. Ideal circulation is observable at the members

The [multiplicity lesson](@ref unintended-solution-multiplicity) supplies two
ideal parallel paths, both endpoints at zero voltage and a total current of
12 A:

```math
I_1+I_2=12,\qquad (I_1,I_2)=(\alpha,12-\alpha)\;\mathrm A.
```

The KCL matrix ``[1\;1]`` has null vector ``(1,-1)``. This is an actual solution
direction of the stated ideal equations. Observing only total current and
terminal power cannot distinguish it: those values are always 12 A and zero.
But the member observation ``h=(I_1,I_2)`` changes. Removing this direction
would discard the very quantities required to check conductor ratings.

With caps ``|I_1|\le7`` A and ``|I_2|\le10`` A, the admissible interval is
``2\le\alpha\le7`` A. The points ``(2,10)``, ``(6,6)`` and ``(7,5)`` all pass;
``(8,4)`` fails the first cap despite identical aggregate observations.
The ratings restrict the family but do not select one physical split.

A reduced model may ask the different, existential question: **does at least
one admissible split exist?** For a general real total current ``T``, the two
symmetric member intervals project to ``|T|\le17`` A. For ``T=12`` the recovery
interval is exactly ``[2,7]`` A. That projection can preserve aggregate
feasibility if it retains this existential meaning and supplies an admissible
recovery. It cannot certify an arbitrary lifted split or recover the currents
of a particular finite-resistance source circuit.

Adding a minimum-norm objective selects ``(6,6)`` because

```math
\alpha^2+(12-\alpha)^2=2(\alpha-6)^2+72.
```

The objective has changed from being constant along the family to selecting a
member. This is a modeling choice, not a voltage-reference convention or a
recovered current-sharing law. The existing finite-resistance witnesses select
``(8,4)`` or ``(4,8)`` according to the resistance ratio.

## C. A delta terminal-map kernel is not a free device current

Use the oriented coils ``ab,bc,ca`` and real incidence

```math
C=\begin{bmatrix}1&-1&0\\0&1&-1\\-1&0&1\end{bmatrix},
\qquad u=Cv,\qquad i=C^{\mathsf T}j.
```

Here ``v,i`` are terminal coordinates and ``u,j`` are coil coordinates.
Because ``C^{\mathsf T}\mathbf1=0``, replacing ``j`` by ``j+\alpha\mathbf1``
leaves terminal currents unchanged. Total complex power is also unchanged:
``v^{\mathsf T}\overline i=u^{\mathsf T}\overline j`` and
``\mathbf1^{\mathsf T}u=0``. The argument holds for complex phasors and complex
``\alpha``; the following numbers use a real SI slice.

Fix ``v=(3,1,-1)`` V, giving ``u=(2,2,-4)`` V. Now declare the **complete coil
laws** ``j=\operatorname{diag}(1,2,3)u``, with conductances in siemens. They
uniquely give ``j=(2,4,-12)`` A. Compare the terminal-invisible perturbation
``j'=j+\mathbf1=(3,5,-11)`` A:

| Check | Declared coil solution | Perturbed current |
|:--|:--|:--|
| Terminal currents (A) | ``(14,2,-16)`` | ``(14,2,-16)`` |
| Total power (W) | 60 | 60 |
| Individual coil powers (W) | ``(4,8,48)`` | ``(6,10,44)`` |
| Residual ``j-\operatorname{diag}(1,2,3)u`` (A) | ``(0,0,0)`` | ``(1,1,1)`` |

The perturbed point is **not a second solution** of this device. It passes two
incomplete observations and fails the constitutive equations. At fixed voltage,
the terminal-current map has rank two, while stacking its rows with the coil-law
coefficient matrix adds the identity and gives rank three. No nonzero coil-current
direction survives. Different devices need their own laws; this example does
not rule out physical delta circulation in other winding or source models.

The voltage kernel ``C\mathbf1=0`` and current kernel
``C^{\mathsf T}\mathbf1=0`` also act on different spaces. At fixed terminal
voltage, the latter alone says nothing about freedom to alter the coil solution.
The [connection-map lesson](@ref load-models-and-decision-dependence) develops
the power-dual map and orientation conventions.

## Diagnose, recover, then transfer

The exact checker is independent of a solver:

```sh
python3 experiments/lessons/observation_quotients.py --check
```

It binds the input fixture, checker and shared algebra helpers into
`experiments/generated/observation-quotients.json`. It verifies original KCL,
reference recovery, the failed earth-shunt extension, ratings, objectives,
terminal/coil powers and exact row ranks. These are self-checks of the declared
models, not independent scientific review or a new BMOPFTools contract.

**Transfer 1.** Add a measurement of ``I_1`` to the ideal parallel case. Does
KCL still leave an unobserved split? No: the stacked observation rows
``[1\;1]`` and ``[1\;0]`` have rank two. A measured value must still satisfy
the ratings; measurement does not make the ideal current-sharing law unique
before the measurement is supplied.

**Transfer 2.** Measure one delta coil current in addition to terminal currents.
That also removes the terminal-map ambiguity, but agreement with the measurement
still does not validate the other device laws. For a single coil between two
terminals, the current map already has full column rank and has no circulation
kernel. Three terminal labels are not a sufficient reason to assume a cycle;
the declared coil endpoints determine the matrix.

**Transfer 3.** If only aggregate current is requested, may the ideal family be
reduced? Yes, with the projected feasible set and explicit recovery obligations.
If member currents or their particular physical provenance are requested, the
aggregate alone is insufficient. Changing the observation changes the claim.

Before removing a mode, state the full equations and domain, the proposed
identification, retained observations, constraints and objective, and what can
be recovered. Then test each obligation separately. A rank count alone cannot
make those decisions.

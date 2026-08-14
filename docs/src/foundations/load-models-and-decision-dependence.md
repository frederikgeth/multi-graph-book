# [Load models and decision dependence](@id load-models-and-decision-dependence)

**Page status:** constitutive-model reference chapter; load-model-specific
numerical certificates remain future work.

Two networks can have identical buses, edges, terminals, and ratings while
defining different decision problems because their loads obey different
voltage laws. A graph representation does not identify a load model. The
constitutive relation belongs to the factor or asset layer and must be carried
through any preservation claim.

## Five common voltage laws

Let ``v=|\Delta U|`` be the magnitude seen by one load connection and let
``v^{\mathrm{nom}}`` be its declared anchor. For active power, the standard
families can be written as

```math
\begin{aligned}
P_{\mathrm{CP}}(v)&=P^{\mathrm{nom}},\\
P_{\mathrm{CI}}(v)&=P^{\mathrm{nom}}\frac{v}{v^{\mathrm{nom}}},\\
P_{\mathrm{CZ}}(v)&=P^{\mathrm{nom}}\left(\frac{v}{v^{\mathrm{nom}}}\right)^2,\\
P_{\mathrm{ZIP}}(v)&=P^{\mathrm{nom}}\left(\alpha_Z\left(\frac{v}{v^{\mathrm{nom}}}\right)^2+\alpha_I\frac{v}{v^{\mathrm{nom}}}+\alpha_P\right),\\
P_{\mathrm{exp}}(v)&=P^{\mathrm{nom}}\left(\frac{v}{v^{\mathrm{nom}}}\right)^{\gamma_P}.
\end{aligned}
```

Reactive power may use its own coefficients or exponent. Constant power does
not need ``v^{\mathrm{nom}}``; the other laws do. ZIP is a convex combination
only when the declared coefficients are nonnegative and sum to one. Integer
exponents ``0,1,2`` make the exponential family coincide with a ZIP special
case, but arbitrary exponents do not.

At ``v=v^{\mathrm{nom}}`` the families agree by construction. Away from that
point they do not. The same topological graph can therefore produce different
currents, losses, voltage margins, active constraints, and optimal decisions.

## Why this belongs in a graph-model book

Consider a fixed two-bus graph with series impedance ``Z`` and a load at the
receiving bus. The power-flow relation is not just the graph incidence; it is

```math
U_s-U_r=ZI,\qquad S_r=U_r I^*,
```

together with a law for ``S_r`` as a function of ``U_r``. Replacing constant
power by constant impedance changes the equation graph and the feasible set
without changing the bus--branch multigraph. A transformation that preserves
only ``Y`` or connectivity has not preserved the decision problem unless it
also preserves the load relation and the observations that depend on it.

This is a useful counterweight to a common simplification: “the network graph
is unchanged, so the OPF is unchanged.” The graph is one layer of the model;
the load factor is another.

## Decision consequences

Load-model choice becomes especially visible in three regimes:

1. **voltage regulation and CVR:** constant-power loads do not reduce demand
   when voltage is lowered, while impedance loads do;
2. **hosting capacity and voltage limits:** a voltage-dependent load can
   partially relieve a binding voltage constraint, changing the reported
   capacity; and
3. **weak feeders and collapse:** constant-power demand can create a nose
   point, so a local high-voltage solution may disappear as the load scale
   increases.

The relevant preservation contract must name the load family, its anchor,
phase or connection map, and whether the decision varies load scale,
voltage, or model parameters. A numerical result that changes after a load
model swap is not necessarily a solver error; it may be the intended change in
the physical problem.

## Per-conductor and connection semantics

For a multiconductor load, ``v`` is not automatically a bus-voltage scalar.
The factor must declare whether it uses phase-to-neutral, phase-to-phase,
sequence, or another terminal combination. A delta load and a wye load can
share the same bus terminals while seeing different voltage coordinates. The
load model therefore belongs beside the terminal map, not as an unqualified
attribute of a graph vertex.

Likewise, a three-phase load may be balanced in name but still have
phase-specific ``P_p`` and ``Q_p`` values. A balanced positive-sequence view
preserves it only when the load relation, grounding, limits, controls, and
observations close under the same phase symmetry.

## Modelling checklist

Before comparing two graph views or deleting a factor, record:

- the load connection and ordered terminal map;
- the active and reactive voltage law;
- the nominal voltage anchor and units;
- phase-specific coefficients or exponents;
- whether the law changes with state, control, or time;
- the voltage and current quantities used in limits; and
- whether the study seeks feasibility, load delivery, hosting capacity,
  voltage regulation, or a different decision.

The book's existing parallel-line and transformer cases preserve their load
equations explicitly. This chapter makes the reason general: constitutive
models are part of the representation contract, even when they are invisible
in a simple graph drawing.

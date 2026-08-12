# Scope and thesis

## The problem

Much of power-system analysis starts from a bus--branch graph

```math
G=(V,E),
```

where buses are vertices and lines or transformers are edges. This is useful,
but it is not a universal physical data model.

A simple graph cannot distinguish parallel circuits. A scalar-weighted graph
cannot retain per-conductor coupling. An ordinary edge cannot directly express
a three-winding transformer, a coupled multi-circuit corridor, or a device with
several electrical and control ports. A topology graph alone does not state
which variables and constitutive relations are attached to its incidence
structure.

The limitations become consequential in decision problems. Suppose parallel
branches ``e`` have terminal relation

```math
i_e = Y_e(v_a-v_b)
```

and individual feasible current sets ``\mathcal C_e``. Their aggregate
admittance

```math
Y_{\mathrm{eq}}=\sum_e Y_e
```

preserves aggregate terminal current, but the original feasible voltage set is

```math
\left\{\Delta v:\;Y_e\Delta v\in\mathcal C_e\quad\forall e\right\}.
```

There need not be a single scalar rating on an equivalent edge that reproduces
this set. Independent switching, contingency, maintenance, and investment
variables make the loss still more apparent. Line-limit-preserving equivalents
have been studied precisely because conventional equivalents do not
automatically retain these decision constraints [Jang2013](@cite).

## The central thesis

**Proposal.** The canonical electrical model should be a typed, hierarchical
port--factor incidence structure. Physical asset facts should remain in a
linked typed property graph. Bus--branch multigraphs and simple graphs should be
treated as generated views rather than the primary source of truth.

This proposal separates three layers:

1. **Identity:** what physical or logical objects exist?
2. **Interconnection:** which typed terminals share effort variables or obey
   conservation relations?
3. **Behavior:** which constitutive, control, limit, and decision relations
   connect the port variables?

It permits a line, transformer, converter, grounding device, measurement, or
protection element to be represented by a factor with an arbitrary but typed
set of ports. Familiar graph models then arise by restricting factor arity,
discarding hierarchy, aggregating conductors, or forgetting parallel identity.

## Not one hierarchy

There is no single total order from "most expressive" to "least expressive."
The asset and electrical views can be incomparable: an asset graph can retain
ownership and construction history while omitting virtual electrical nodes; a
compiled electrical graph can contain virtual transformer buses that have no
physical asset identity.

The meaningful order is relative to a query or observation family ``Q``.
Write

```math
M_1 \succeq_Q M_2
```

when every question in ``Q`` answerable from ``M_2`` can also be answered from
``M_1`` through a declared transformation. The order can change when ``Q``
changes from power flow to protection, asset management, fault location,
optimal switching, or expansion planning.

This turns the apparent hierarchy into a **partial order of representations
relative to preservation contracts**.

## Boundaries of the initial book

The first edition should concentrate on:

- steady-state and quasi-steady electrical networks;
- multiphase and explicit-neutral distribution models;
- transmission and distribution topology processing;
- multi-terminal and multiwinding devices;
- projections used in power flow, OPF, state estimation, short-circuit and
  related studies;
- exact and approximate reductions;
- preservation of operational and decision constraints;
- typed normalization rules, provenance, and recoverability.

EMT, harmonics, thermal dynamics, communications, protection logic, and
geospatial asset systems should initially appear as boundary cases that test the
architecture. Later editions can develop them fully.

## Intended contribution

The proposed contribution is not another isolated reduction algorithm. It is a
common language for stating:

- the source and target model categories;
- whether a transformation is a projection, compilation, normalization,
  exact behavioral quotient, or approximation;
- what is preserved;
- what assumptions make the transformation valid;
- how original quantities and constraints are recovered;
- which questions become unanswerable afterward.

That language can support both a scientific theory and an implementable model
transformation system.


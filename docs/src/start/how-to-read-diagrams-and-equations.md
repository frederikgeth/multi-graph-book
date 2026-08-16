# [How to read power-network diagrams and equations](@id how-to-read-diagrams-and-equations)

**Page status:** introductory translation bridge; the examples are deliberately
small, while the terminology is used throughout the multiconductor chapters.

A power-network diagram is not a circuit equation, and a circuit equation is
not automatically a graph. Before interpreting an arrow, edge, node, or matrix
entry, ask three questions:

1. **What object is drawn?** An asset, a terminal, a port, a factor, a retained
   voltage coordinate, or an algebraic support relation?
2. **What quantity is attached to it?** A voltage, current, complex power,
   impedance, admittance, limit, state, or provenance identifier?
3. **What has already been compiled away?** Parallel-member identity, conductor
   coordinates, an internal transformer node, a neutral, or a decision state?

The same physical feeder can therefore have several faithful diagrams. The
diagram is a view with a declared semantic level, not an unqualified picture of
the network.

## The scalar circuit in one minute

For a scalar branch stored from ``i`` to ``j``, write the voltage difference

```math
\Delta v_{\ell ij}=v_i-v_j.
```

Ohm's law, or the branch constitutive relation, is

```math
i_{\ell ij}=y_\ell\Delta v_{\ell ij},
\qquad y_\ell=z_\ell^{-1}.
```

This equation says how the branch responds to its terminal voltages. It does
not say that current must flow from ``i`` to ``j`` in operation: the computed
complex current may have either sign or phase. The stored order ``\ell ij`` is
an index convention, consistent with the BMOPFTools-style notation used in
this book.

Kirchhoff's current law (KCL) is a balance at a node. With currents defined as
entering the node, one possible convention is

```math
\sum_{e\in\delta(i)} i_{e\to i}+i_i^{\mathrm{inj}}=0.
```

The signs change if the convention changes; the physical balance does not.
Kirchhoff's voltage law (KVL) says that the oriented voltage differences sum
to zero around a compatible closed circuit path. In a nodal formulation this
is usually enforced indirectly by assigning one voltage to each retained node
and deriving every branch drop from endpoint voltages. A cycle in a matrix
support graph is not automatically such a physical circuit path.

These three statements have different jobs:

| Statement | Role | What it does not define |
|:--|:--|:--|
| Ohm/constitutive law | element behaviour | asset identity or operating direction |
| KCL | balance at a junction | which graph view produced the junction |
| KVL | compatible voltage differences around a circuit loop | a cycle in every derived support graph |

## The same line with multiple conductors

For a four-wire line, the scalar voltage and current become ordered vectors:

```math
\mathbf U_i=[U_{i,a},U_{i,b},U_{i,c},U_{i,n}]^{\mathsf T},
\qquad
\mathbf I_{\ell ij}
=\mathbf Y_\ell
\left(
\mathbf U_i[\mathbf N_{\ell i}]
-
\mathbf U_j[\mathbf N_{\ell j}]
\right).
```

The matrix ``\mathbf Y_\ell`` may be dense. Its off-diagonal entries represent
mutual coupling between conductor coordinates; they are not extra physical
lines. A vector-valued edge is therefore a useful bridge phrase for a
two-terminal multiconductor factor, but it is not a new canonical graph class.
The precise source object remains a typed attributed multigraph edge with
vector terminal spaces and matrix-valued constitutive data.

When a device has three or more ports, the bridge phrase stops being adequate:
retain a typed port--factor relation. A multiwinding transformer is one factor
with several port bundles until a guarded compilation explicitly creates a
two-terminal realization.

![One four-wire factor across a vector edge, a port--factor incidence view, a block nodal operator, and scalar or realified coordinate support.](../assets/block-structure-bridge.png)

The four panels are deliberately paired. Panels A and B are the useful places
to ask *which asset or factor is present*; panel C is the natural place to write
the assembled block equation; panel D is a coordinate-level support or solver
view. The dense lines in D are algebraic coupling, not a claim that the source
contains that many physical branches. This scoped correspondence is checked by
the executable witness registered as `ARCH-BLOCK-001`.

## What a lossy edge looks like

Power engineers often draw an edge and imagine power flowing through it as one
quantity. A circuit model normally computes terminal currents first, then
complex power at each terminal, for example

```math
S_{\ell ij}=\operatorname{diag}(\mathbf U_i[\mathbf N_{\ell i}])
\mathbf I_{\ell ij}^{*}.
```

Series impedance, endpoint shunts, mutual coupling, and grounding can all make
the two terminal powers differ. Even the terminal currents need not be simple
negatives when shunts are present. A lossy edge is not a violation of graph
theory; it is a constitutive factor with nonzero dissipation or local exchange.
If a diagram shows one line with a ``\pi`` model, decide whether its shunts are
inside the factor or drawn as separate factors before comparing currents or
limits.

## Reading scalar, vector, and block notation

The following translation is safe only when the qualifiers are retained:

| Diagram or phrase | Mathematical reading | Main qualifier |
|:--|:--|:--|
| scalar edge ``i--j`` | one voltage coordinate at each endpoint | positive-sequence or single-conductor scope |
| vector-valued edge | ``\mathbf Z_\ell`` or ``\mathbf Y_\ell`` acts on ordered conductor coordinates | still a two-terminal factor |
| vector-valued node | bus ``i`` owns an ordered terminal space ``\mathbf U_i`` | terminals may be missing, permuted, or grounded |
| block nodal matrix | ``\mathbf Y^{\mathrm N}_{ij}`` maps one bus-terminal block to another | block support is not an asset multigraph |
| scalar-expanded support graph | each conductor coordinate is a vertex | cycles mean algebraic coupling, not necessarily physical loops |
| realified model | real and imaginary coordinates are stacked | doubled coordinates are not doubled assets |

The report by Geth, Claeys, and Heidari gives a practical four-wire example of
this translation: series impedances and shunts are matrices, current-injection
methods are centered on a nodal-admittance representation, and radial
backward--forward sweep uses a different impedance-oriented computational
view [GethClaeysHeidari2023](@cite). Those are alternative formulations of the
same declared circuit model, not competing definitions of what a bus or line
is.

## A diagram-reading checklist

Before using a graph in a proof, algorithm, or optimisation model, annotate it
with:

- **level:** asset, equipment/terminal, port--factor, equation, block support,
  or scalar support;
- **coordinates:** scalar, phase/neutral vector, sequence, rectangular real,
  or another declared basis;
- **orientation:** stored terminal order, sign convention, or actual control
  direction;
- **constitutive scope:** series only, nominal-``\pi``, transformer, shunt,
  grounding, nonlinear load, or an n-port relation;
- **preservation:** identities, KCL/KVL/terminal behaviour, limits, decisions,
  and provenance that remain available;
- **loss:** what has been summed, eliminated, projected, realified, or made
  implicit.

This checklist is the short route into the longer [two topology levels and the
nodal projection](@ref two-level-topology-and-nodal-projection) chapter. There
the same distinctions are stated as maps between typed objects and block
operators rather than as visual intuition alone.

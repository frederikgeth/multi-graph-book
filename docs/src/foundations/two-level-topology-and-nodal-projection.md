# [Two topology levels and the nodal projection](@id two-level-topology-and-nodal-projection)

**Page status:** literature-backed definitional synthesis and proposed source-
retention contract; general inverse recovery from a nodal operator is
intentionally rejected.

## The missing middle between a one-line diagram and ``\mathbf Y^{\mathrm N}``

Power engineers routinely move between a bus--branch diagram, a
multiconductor circuit, and a nodal admittance matrix. Those three objects are
related, but they do not have the same vertices, edges, or cycles. Calling all
three *the network graph* hides two distinct topology levels and a many-to-one
algebraic projection:

1. the **asset/terminal topology** records identified equipment and its
   high-level attachments;
2. the **conductor/port--factor topology** records the electrical terminals,
   junctions, conductor coordinates, and constitutive factors;
3. the **nodal-operator support graph** records which retained voltage
   coordinates are coupled by the assembled matrix.

The first two are retained source structure in this book. The third is a
derived computational view. The asset/dependency model remains an orthogonal
companion to both: ownership, protection, common-mode failure, and maintenance
are not entries of a nodal admittance matrix.

![Two source topology levels and their many-to-one nodal-admittance projection.](../assets/topology-projection-layers.png)

The figure uses parallel lines because they expose the loss immediately. Both
identified factors attach to the same electrical junction coordinates, and
their matrix contributions occupy the same nodal block. The assembly preserves
their combined linear boundary relation but forgets how that contribution was
split between assets.

## Level 1: identified assets and high-level attachments

For the two-terminal subset of a network, let

```math
G_{\mathrm A}=(\mathcal B,\mathcal L,\partial),
\qquad
\partial(\ell)=\{i,j\}.
```

This is an identified multigraph: ``\ell_1`` and ``\ell_2`` remain distinct
when ``\partial(\ell_1)=\partial(\ell_2)``. A stored reference orientation is
written ``\ell ij`` and does not make the physical line a directed edge. The
element-intrinsic impedance or primitive matrix keeps the symmetric element
index ``\mathbf Z_\ell`` or ``\mathbf Y_\ell``; terminal observations use
``\ell ij`` and ``\ell ji``.

The multigraph is only a high-level skeleton. A transformer ``x`` with winding
set ``\mathcal K_x`` is naturally multi-terminal, and a jointly coupled line
group may own more than two port bundles. Such objects belong in an
asset--port incidence structure or hypergraph, not in ``G_{\mathrm A}`` unless
an explicit two-terminal compilation has been selected. Consequently,
*radial at asset level* must name both the selected object class and any
multi-terminal compilation used to obtain an ordinary graph.

At this level, parallelism means repeated high-level attachment. It says
nothing yet about terminal order, phase availability, grounding, mutual
coupling, state, or whether currents may be added in a common coordinate
space.

## Level 2: conductor junctions and electrical factors

The canonical electrical model is the hierarchical port--factor object
``\mathfrak P`` defined in [Formal representation frameworks](@ref formal-representation-frameworks).
For the present discussion, its important incidence maps are

```math
j:\mathcal Q\rightarrow\mathcal J,
\qquad
f:\mathcal Q\rightarrow\Phi,
```

where ``j`` attaches a typed port to an electrical junction and ``f`` assigns
the port to its owning factor. A junction may represent a scalar conductor
coordinate such as ``i/a`` or a typed bundle such as ``i/[a,b,c,n]``. The
factor relation retains the full conductor coupling, terminal maps, internal
variables, limits, state, and decisions.

Two distinct ports may attach to the same junction; indeed, that is how KCL
composes several devices. More generally, a source construction may contain
several physical conductors or sub-conductors connected to one electrical
terminal. The attachment relation must therefore not be assumed injective.
An importer or line-constant tool may choose a narrower schema. For example,
the current BMOPFTools line-geometry compiler checks one geometry conductor
per terminal label. That is a useful implementation guard for its present
primitive, not a theorem that the general electrical model forbids bundled or
multiply attached conductor structure. Such a source must remain expanded or
pass through a declared bundle-compilation rule before entering that adapter.

This level has its own notions of parallelism:

- factors can be parallel because all of their boundary port spaces and
  attachment maps coincide;
- physical conductors can be parallel inside one factor while sharing an
  electrical terminal at one or both ends;
- two factors can share high-level buses but fail to be terminal-parallel
  because their phase sets, neutral connections, or terminal maps differ;
- mutual coupling can place two nominal assets in one joint factor, so they
  are not independent edges even when the asset inventory lists them
  separately.

The high- and low-level decompositions are therefore related by an explicit
lineage/refinement relation, not by an assumed one-edge-to-one-wire rule.

## From factors to a compound nodal operator

Stack the retained junction-voltage coordinates into ``\mathbf U``. For each
linear factor ``\phi``, let ``\mathbf A_\phi`` select, permute, and sign its
ordered terminal voltages, so

```math
\mathbf u_\phi=\mathbf A_\phi\mathbf U,
\qquad
\mathbf i_\phi=\mathbf Y_\phi\mathbf u_\phi.
```

After mapping terminal currents back to the junction coordinates, linear
assembly has the form

```math
\mathbf Y^{\mathrm N}
=
\sum_{\phi\in\Phi_{\mathrm{lin}}}
\mathbf A_\phi^{\mathsf T}
\mathbf Y_\phi
\mathbf A_\phi.
```

The factor primitive ``\mathbf Y_\phi`` may already contain series, shunt,
ideal-connection, transformer, or multiport structure. Incidence-matrix
assembly of compound polyphase networks is developed by Kettner and Paolone
[KettnerPaolone2019](@cite); nested primitive, winding, and connection maps for
general multiphase transformers provide a particularly clear device-level
example [Coppo2017](@cite).

The equation is an **assembly identity**, not a unique factorization of
``\mathbf Y^{\mathrm N}``. For two electrically aligned parallel factors
``\ell_1ij`` and ``\ell_2ij``, the same off-diagonal nodal block contains

```math
\mathbf Y^{\mathrm N}_{ij}
=
\mathbf Y_{\ell_1,ij}
+
\mathbf Y_{\ell_2,ij}
+
\sum_{\phi\notin\{\ell_1,\ell_2\}}
\mathbf Y_{\phi,ij}.
```

Even when the last sum is empty, ``\mathbf Y^{\mathrm N}_{ij}`` does not
identify its two summands. In the scalar case, every decomposition
``y_{ij}=y_1+y_2`` produces the same nodal coefficient. Ratings, outage states,
investment variables, owners, and the two-edge line-identity cycle are absent
unless they are retained separately.

## Is nodal admittance a simple-graph concept?

Not in the physical sense. A nodal admittance matrix is a linear operator on
a chosen ordered voltage space. From it one can derive simple support graphs
at several granularities.

**Definition (block support).** Given bus blocks
``\mathbf Y^{\mathrm N}_{ij}``, define

```math
G_Y^{\mathrm{blk}}=(\mathcal B,E_Y^{\mathrm{blk}}),
\qquad
\{i,j\}\in E_Y^{\mathrm{blk}}
\Longleftrightarrow
\mathbf Y^{\mathrm N}_{ij}\ne\mathbf 0.
```

**Definition (scalar support).** Given retained coordinates
``\mathcal C=\{(i,p)\}``, define

```math
G_Y^{\mathrm{sc}}=(\mathcal C,E_Y^{\mathrm{sc}}),
\qquad
\{(i,p),(j,q)\}\in E_Y^{\mathrm{sc}}
\Longleftrightarrow
Y^{\mathrm N}_{(i,p),(j,q)}\ne0.
```

These support graphs are simple by construction: a matrix position is either
zero or nonzero. But that does not make the source network a simple graph.
Several factor stamps sum into one position, and their decomposition is not
encoded in matrix support. If an algorithm needs the decomposition, it can use
a **stamp multigraph** whose identified members are the separate
``\mathbf A_\phi^{\mathsf T}\mathbf Y_\phi\mathbf A_\phi`` contributions.
That multigraph is extra data; it cannot generally be recovered from the sum.

The support relation also requires qualifications:

- a dense off-diagonal block can be produced by mutual conductor coupling
  inside one physical line;
- several contributions can occupy one block, including parallel factors and
  multi-terminal compilations;
- exact cancellation can make a matrix entry zero even though source factors
  touch both coordinates;
- a diagonal block combines incident series terms, local shunts, grounding,
  and possibly several compiled factors;
- changing coordinates can change scalar support without changing the
  underlying external relation.

Thus ``G_Y^{\mathrm{blk}}`` is often an excellent sparsity and decomposition
view, while ``G_Y^{\mathrm{sc}}`` exposes within-block coupling. Neither is an
asset register.

## Why a radial network can acquire cycles

Gan and Low show that a multiphase radial network can be represented as an
equivalent scalar network that is radial at the macro level but has a clique
associated with each line [GanLowChordal2014](@cite). Their companion
multiphase BIM/BFM work similarly treats each bus--phase pair as a coordinate
of an equivalent scalar circuit [GanLowMultiphase2014](@cite). The observation
is valuable here because it makes the level distinction impossible to ignore.

![A bus-level tree and the cyclic scalar support induced by dense multiconductor line stamps.](../assets/radial-clique-projection.png)

For an ``m``-conductor two-terminal factor with a dense ``2m\times2m``
terminal stamp, its scalar support can contain a clique on the ``2m`` endpoint
coordinates. A triangle or larger cycle inside that clique is an algebraic
coupling cycle. It is not evidence that operators can open an alternative
physical route, that power is circulating, or that the bus-level feeder is
meshed. If some primitive entries are structurally zero, the clique loses the
corresponding support edges; the matrix pattern, not the word
*multiconductor*, decides the scalar support.

This produces several useful apparent paradoxes:

| Statement | Resolution |
|:--|:--|
| a radial feeder has cycles | asset topology can be a tree while conductor-expanded matrix support contains cliques |
| two parallel lines become one edge | their stamps add in one block-support edge; asset identity has been projected away |
| one line becomes many edges | one dense multiconductor factor produces many scalar nonzeros |
| a transformer creates a triangle | a clique compilation of one multi-terminal factor creates a support cycle, not three transformer assets |
| a new edge appears after reduction | Kron fill-in is an equivalent boundary coefficient, not a discovered line |
| no matrix edge means no physical relation | cancellation, coordinate choice, or eliminated variables can hide the relation |

These are not contradictions. Each sentence changes the graph without saying
so.

## Three cycle questions, not one

The [cycles and radiality chapter](@ref cycles-parallelism-radiality) defines
the corresponding graph objects in detail. The practical crosswalk is:

| Cycle question | Graph or incidence object | What it can support |
|:--|:--|:--|
| Is there an alternative route through identified two-terminal members? | asset/bus multigraph | switching, outages, member radiality, line-identity cycle bases |
| Is there repeated incidence through conductor junctions and factors? | conductor/port--factor graph or a declared compilation | terminal connectivity, factor decomposition, conductor-resolved equations |
| Does the assembled or reduced operator have cyclic sparsity? | block or scalar matrix-support graph | chordal decomposition, ordering, fill, sparse numerical algorithms |

A cycle basis computed in one row is not automatically a basis for another.
In particular, a parallel pair gives a two-member cycle in the identified
multigraph but one edge in block support, while a dense line stamp can give
many scalar-support cycles without any asset-level cycle.

## Kron reduction adds a fourth source of apparent adjacency

Partition retained boundary coordinates ``B`` and eliminated internal
coordinates ``I``. When ``\mathbf Y_{II}`` is invertible, Kron reduction gives

```math
\widehat{\mathbf Y}_{BB}
=
\mathbf Y_{BB}
-
\mathbf Y_{BI}\mathbf Y_{II}^{-1}\mathbf Y_{IB}.
```

The Schur-complement term can introduce a nonzero retained block between two
boundary nodes that shared no source factor. This fill edge belongs to the
reduced operator support. It does not belong retrospectively to the source
asset or conductor topology. Dörfler and Bullo characterize this graph effect
for electrical-network Kron reduction [DorflerBullo2013](@cite), while the
compound polyphase setting requires the relevant block-rank conditions
[KettnerPaolone2019](@cite).

Any eliminated current, voltage, or limit that still matters to a decision
problem must be evaluated through a recovery map. This includes neutral-
conductor current limits: the disappearance of the neutral coordinate from
the retained operator does not remove the conductor's thermal constraint.

## Maintain the decomposition; do not promise inversion

The canonical record should retain at least:

- stable asset and factor identities;
- ordered ports, junction attachments, and conductor/terminal maps;
- factor class and full primitive relation or a reproducible construction
  record;
- active-state, rating, grounding, control, and decision ownership;
- each assembly, compilation, coordinate, and reduction map;
- provenance from every matrix block or generated object back to its source
  factors;
- recovery maps for eliminated quantities that remain observable or
  constrained.

For a supplied nodal operator and claimed source decomposition, the basic
round-trip certificate is

```math
\left\|
\mathbf Y^{\mathrm N}
-
\sum_{\phi}
\mathbf A_\phi^{\mathsf T}\mathbf Y_\phi\mathbf A_\phi
\right\|
\le \varepsilon_{\mathrm{asm}},
```

together with checks of coordinate order, units, states, and factor types.
This verifies a proposed decomposition. It does **not** prove that the
decomposition is unique.

Recovery from ``\mathbf Y^{\mathrm N}`` alone is an inverse problem and is
generally non-identifiable. Additional catalog constraints, construction
priors, measurements, switch states, or asset records can narrow the candidate
set, but an estimator must report ambiguity rather than inventing line
identity. The safe engineering objective is therefore:

> preserve the two-level source structure through compilation, and validate
> every derived nodal operator against it; attempt recovery only as a
> separately scoped inference problem.

That direction supports both rigorous proofs and practical data
standardisation. Power engineers can work with familiar bus blocks and line
triples, while the retained maps make clear which topology, constraints, and
physical meanings survive each transformation.

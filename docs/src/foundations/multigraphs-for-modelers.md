# [Multigraphs for expert modelers](@id multigraphs-for-modelers)

**Page status:** normative mathematical conventions and literature-backed
reference; core matrix identities have an executable finite witness; electrical
adequacy remains representation- and query-dependent.

## Purpose

This chapter fixes the graph-theoretic object used when the identities of
several two-terminal members must survive. It is written for readers who know
ordinary graph theory but need to determine which generalizations remain valid
for power-system models.

Three habits organize the chapter:

1. declare the graph object before asking a graph question;
2. qualify every overloaded quantity—especially *degree*, *loop*, *parallel*,
   and *Laplacian*—by its convention; and
3. describe simplification by a map and its fibres, not by saying that duplicate
   edges were removed.

The conventions are compatible with standard graph and matrix treatments, but
not every text chooses the same definition for loops, adjacency diagonals, or
paths. We therefore state the convention used here rather than appealing to a
supposed universal one [Diestel2025, GrossYellenAnderson2019, Bapat2014](@cite).
The [representation-framework chapter](@ref formal-representation-frameworks)
locates this object among the book's other models. The
[cycles chapter](@ref cycles-parallelism-radiality) develops the engineering
consequences; it does not replace the definitions below.

## The finite undirected multigraph

### Edge-end definition

An **undirected multigraph with loops** is a tuple

```math
G=(V,E,\mathcal F,s,p),
```

where ``V`` is a finite vertex set, ``E`` is a finite set of identified edges,
``\mathcal F`` is a finite set of edge ends or **flags**, and

```math
s:\mathcal F\rightarrow V,
\qquad
p:\mathcal F\rightarrow E,
\qquad
|p^{-1}(e)|=2\quad(e\in E).
```

Each edge therefore owns two distinct flags. If the two flags of ``e`` map
under ``s`` to different vertices, ``e`` is a non-loop edge. If both map to the
same vertex, ``e`` is a **graph loop**. Distinct edges may have the same two
endpoint vertices; their identity in ``E`` makes them parallel members rather
than one edge with an unexplained multiplicity.

The edge-end definition is slightly more elaborate than an endpoint pair, but
it prevents two common ambiguities. A loop has two incident ends even though it
has one endpoint vertex, and a later port model can map the two ends to distinct
terminals owned by the same component. It also separates incidence from edge
attributes.

For compact notation define the endpoint multiset

```math
\partial(e)=\{\!\{s(h):h\in p^{-1}(e)\}\!\}
\in \operatorname{Sym}^{2}(V).
```

For a non-loop edge this is the unordered pair ``\{u,v\}``; for a loop it is
the repeated multiset ``\{\!\{v,v\}\!\}``. The endpoint map is derived from
the flag model. It is not a substitute when individual ends or terminals
matter.

An **attributed multigraph** adds declared maps such as

```math
\alpha_V:V\rightarrow\mathcal A_V,
\qquad
\alpha_E:E\rightarrow\mathcal A_E,
\qquad
\alpha_{\mathcal F}:\mathcal F\rightarrow\mathcal A_{\mathcal F}.
```

Names, impedances, ratings, phases, switch states, owners, provenance, and
decision variables belong to these typed maps or to linked models. They are not
encoded merely by drawing an edge.

This adopted source-object convention is registered as `GRAPH-MULTI-001`.

### Orientation is additional structure

An orientation chooses, for each non-loop edge, one flag as tail and the other
as head. A graph loop may also have its two flags ordered, but its tail and head
vertex coincide. Orientation is a coordinate convention. It does not assert
the sign of current, power, or causality in an operating solution.

Reorienting one edge negates the corresponding signed-incidence column and any
edge-coordinate written in that orientation. It does not change connectivity,
cycle rank, or the underlying physical member.

### The word degree is insufficient

For ``v\in V`` define the **incidence degree**

```math
d_{\mathrm{inc}}(v)=|s^{-1}(v)|.
```

A graph loop contributes two because it has two flags at ``v``. This is the
degree used by the handshake identity

```math
\sum_{v\in V}d_{\mathrm{inc}}(v)=2|E|.
```

Other useful counts are different:

- the **non-loop incidence count** counts flags at ``v`` belonging to edges
  with two different endpoint vertices;
- the **distinct-neighbour degree** counts vertices ``u\ne v`` joined to ``v``
  by at least one edge and ignores multiplicity;
- the **member count** counts identified incident non-loop equipment, so
  parallel members count separately;
- a **terminal count** belongs to a terminal or port model and need not equal
  any graph degree; and
- a matrix row nonzero count belongs to a compiled sparsity graph and can
  include diagonal terms or couplings that are not bus--branch edges.

Consequently, statements such as “remove degree-two buses” are incomplete.
They must say which representation supplies the vertices, which degree is
used, whether loops and open members count, and what electrical conditions make
the proposed elimination valid.

## Matrix conventions

Let ``n=|V|`` and ``m=|E|``. Fix an ordering of vertices and edges and an
orientation of every non-loop edge.

### Signed incidence matrix

The signed incidence matrix ``B\in\{-1,0,1\}^{n\times m}`` has a ``-1`` at
the tail and ``+1`` at the head of each non-loop edge. A graph-loop column is
zero because its two signed incidences occur at the same vertex and cancel.
Changing all signs in a column is an equivalent orientation convention.

This zero column does **not** say that a physical self-connected or grounded
device has no effect. It says only that an ordinary graph loop contributes
nothing to the signed boundary operator.

### Multiplicity adjacency and degree matrices

Let ``\mu(u,v)`` be the number of edges with distinct endpoints ``u`` and
``v``, and let ``\lambda(v)`` be the number of graph loops at ``v``. This book
uses the multiplicity adjacency matrix

```math
A_{uv}=\mu(u,v)\quad(u\ne v),
\qquad
A_{vv}=2\lambda(v).
```

With ``D=\operatorname{diag}(d_{\mathrm{inc}}(v))``, the row sums of ``A``
equal the incidence degrees and

```math
L=D-A=BB^{\mathsf T}.
```

The graph loops cancel between ``D`` and ``A``. Some authors instead place
``\lambda(v)`` or zero on the adjacency diagonal and modify associated degree
or Laplacian definitions. Those are legitimate conventions, but identities
must not be moved between them without adjustment [Bapat2014,
Bollobas1998](@cite).

For diagonal nonnegative edge weights ``W``, the weighted series Laplacian is

```math
L_W=BWB^{\mathsf T}.
```

Ordinary graph-loop weights again vanish because the loop columns of ``B`` are
zero. Complex branch stamps, ideal transformer ratios, mutual coupling, phase
coordinates, and controlled factors generally require a richer assembly than
this scalar expression. A power-system nodal admittance matrix is therefore
not, without qualification, “the graph Laplacian.”

### Graph loops are not shunts

Four objects that are often drawn similarly must remain distinct:

| Object | Formal location | Incidence/Laplacian effect |
|:--|:--|:--|
| graph loop | an edge whose two flags map to one graph vertex | zero signed-incidence column; cancels from ``D-A`` under this convention |
| shunt to reference | a one-terminal constitutive relation, or an edge to an explicit reference vertex before grounding | contributes a grounded diagonal or primitive stamp |
| contraction-created loop | an ordinary edge whose endpoints become identified under a quotient | records information created by contraction; may later be deleted only by a declared map |
| diagonal dependency | a diagonal term in an operator or sparsity pattern | algebraic self-dependence; not automatically an asset edge |

For a scalar grounded network one may write

```math
Q=BWB^{\mathsf T}+Y_{\mathrm{sh}},
```

where ``Y_{\mathrm{sh}}`` is a declared grounded diagonal contribution. Calling
the second term a graph loop and then applying the zero-column convention would
erase precisely the grounding effect being modeled.

The compatible incidence/adjacency/Laplacian identity and the graph-loop versus
grounded-shunt distinction are registered as `GRAPH-MATRIX-001`.

### Self-loops, circuit branches, and collapsed two-port factors

The word *loop* changes meaning at the boundary between graph theory and
circuit theory. A graph self-loop is one identified edge whose two flags map to
one vertex. An electrical loop or mesh is a closed branch path used by a
particular circuit formulation. A graph self-loop may be a one-edge circuit in
the graphic-matroid sense, but it is not thereby an ordinary circuit branch
between two distinct retained nodes.

Many incidence-based network texts use loopless graphs as their circuit
specialization: every ordinary branch has a distinct source and sink node, and
the incidence column records the difference of the two node potentials
[SeshuReed1961](@cite). This is a useful specialization, not a universal
definition of every graph used in electrical modeling. Network-reduction
literature also uses *loopy Laplacian* for diagonal grounded terms, including
positive or negative differential conductances; that usage is a matrix-level
abstraction and must not be silently identified with the graph-loop convention
above [DorflerBullo2013, SongHillLiu2017](@cite).

The book therefore uses the following boundary:

| Situation | Retain in the source model | Possible compiled view |
|:--|:--|:--|
| ordinary two-terminal branch with distinct retained terminals | identified factor and both terminal maps | loopless bus--branch edge or terminal relation |
| graph self-loop in the multigraph | edge identity, flags, state, and provenance | omitted from distinct-node connectivity, or retained as a declared degenerate factor |
| one-terminal shunt or grounded load | constitutive relation and attachment map | diagonal nodal stamp or explicit reference edge |
| two-terminal factor after terminal identification | original factor, its two ports, and the quotient map | a compiled one-terminal relation only after the factor equation is assembled |

Thus a self-loop produced by node contraction is not automatically deleted and
not automatically called a shunt. The safe order is:

1. retain the source factor and its terminal maps;
2. apply the topology-state quotient to those maps;
3. compile the factor in the declared equation target; and
4. simplify only after checking the requested observations, limits, controls,
   and recovery map.

This order matters because graph projection and constitutive compilation need
not commute. A loopless connectivity view may omit the self-loop while the
compiled factor still contributes a diagonal term or a constraint.

#### Exact collapse of a fixed linear π section

Let a fixed two-port π factor have series admittance ``Y_s`` and terminal
shunt admittances ``Y_a`` and ``Y_b``. Its terminal admittance relation is

```math
\mathbf i_\pi=Y_\pi\mathbf v_\pi,
\qquad
Y_\pi=
\begin{bmatrix}
Y_a+Y_s & -Y_s\\
-Y_s & Y_b+Y_s
\end{bmatrix}.
```

For retained node-voltage coordinates ``\mathbf u``, let ``T_\pi`` map
retained voltages to the two terminal voltages. The nodal contribution is the
standard terminal-map assembly

```math
Y^{\mathrm N}_\pi=T_\pi^{\mathsf T}Y_\pi T_\pi.
```

If topology processing identifies both terminals with the same retained
coordinate and there is no transformer or coordinate conversion, then
``T_\pi=[1\;1]^{\mathsf T}`` and

```math
Y^{\mathrm N}_\pi
=\begin{bmatrix}1&1\end{bmatrix}Y_\pi
  \begin{bmatrix}1\\1\end{bmatrix}
=Y_a+Y_b.
```

The series term cancels because its terminal voltage difference is zero. The
two shunts remain and combine into one constant-admittance, equivalently
constant-impedance, one-terminal nodal contribution. This is consistent with
power-system π models, where the line is a two-port and shunt terms enter the
nodal diagonal rather than the off-diagonal bus coupling [OpenDSSLine,
SeshuReed1961](@cite).

This identity does **not** license a universal “self-loop deletion” rule. It
does not preserve a branch-current observation, member rating, loss
allocation, switching decision, or source provenance. It also does not apply
without further analysis when the factor contains an ideal voltage source,
zero-impedance constraint, nontrivial transformer ratio, mutual coupling,
dependent source, control law, dynamic state, or incompatible terminal
coordinates. Such factors belong in modified nodal, tableau, or port--factor
formulations until an exact elimination and recovery map has been established
[HoRuehliBrennan1975, OpenDSSSolutionTechniques](@cite).

The loopless circuit specialization, the literature distinction between graph
self-loops and loopy diagonal terms, and the guarded π-collapse identity are
registered as `GRAPH-SELF-LOOP-001`, `GRAPH-LOOPY-001`, and
`GRAPH-PI-COLLAPSE-001`.

## Connectivity and cycles

Graph loops do not connect distinct vertices. Connected components are
therefore determined by non-loop edges. If ``c`` is the number of components,
then over any field of characteristic zero

```math
\operatorname{rank}B=|V|-c,
\qquad
\dim\ker B=|E|-|V|+c.
```

Each graph loop contributes one zero column and hence one cycle-space
dimension. Each additional edge in a parallel class contributes another
dimension after the first member needed for connectivity. Thus multigraph
cycles include:

- a one-edge circuit formed by a graph loop;
- a two-edge circuit formed by two parallel non-loop edges; and
- the familiar longer circuits.

Over ``\mathbb F_2``, a cycle is often represented by an even-degree edge set
and orientation signs disappear. Over ``\mathbb R`` or ``\mathbb C``, cycle
coordinates retain signed coefficients. The dimension formula agrees, but the
coefficient field and intended use must be stated.

The inclusion-minimal supports of nonzero vectors in ``\ker B`` are the
circuits of the graphic matroid. This definition handles loops and parallel
members without adding exceptions [Oxley2011, VanLintWilson2001](@cite). It
also explains why a cycle basis is not unique: it is a vector-space basis, not
a canonical set of physical loops.

The classical connection between incidence matrices, cut spaces, cycle spaces,
and electrical network equations is developed in network-matrix texts such as
[SeshuReed1961](@cite). Electrical interpretation still requires constitutive
laws: a topological circuit does not prove that a circulating current exists at
a particular operating point.

## Simple projection is a quotient

Let

```math
E^{\circ}=\{e\in E:\partial(e)=\{u,v\},\ u\ne v\}
```

be the non-loop edges. The loopless underlying simple graph is

```math
\overline G=(V,\overline E),
\qquad
\overline E=\bigl\{\{u,v\}:e\in E^{\circ},\ \partial(e)=\{u,v\}\bigr\}.
```

Its quotient map

```math
q:E^{\circ}\rightarrow\overline E,
\qquad
q(e)=\partial(e)
```

has fibres ``q^{-1}(\{u,v\})`` containing all identified members between the
same endpoint vertices. Constructing ``\overline G`` therefore performs two
operations: graph loops are omitted, and every non-loop parallel class is
replaced by one adjacency. Neither operation is invertible without retained
fibre and loop records.

This is not a data-cleaning rule. Two records with the same endpoints may be
two valid circuits, while two records with different bus identifiers may become
parallel only after topology processing identifies their terminal nodes.

### What the projection preserves

Preservation is query-dependent. For the unweighted loopless simple projection
above:

| Query or object | Status under simple projection | Qualification |
|:--|:--|:--|
| vertex set and connected components | preserved | loops and multiplicity do not join new vertex pairs |
| adjacency and distinct-neighbour sets | preserved by definition | edge identity is not preserved |
| unweighted vertex-to-vertex distance | preserved | edge-level routes and member choices are not |
| articulation vertices | preserved | use the conventional vertex-deletion query on the underlying loopless graph |
| vertex properties defined on the underlying simple graph, such as treewidth | preserved by definition | this says nothing about member-level constraints |
| edge count, incidence degree, and cycle-space dimension | not preserved | loops and excess parallel members change all three |
| bridges and edge connectivity | not preserved | a parallel pair contains no bridge, while its image may be a bridge |
| spanning-tree count and Eulerian parity | not preserved | multiplicity changes member choices and degrees |
| line graph and edge-disjoint routing | not preserved | both depend on identified edges |
| member outages, ratings, losses, controls, provenance, and decisions | not preserved | these live on source members or linked factors |

The structural preservation boundary of this quotient is registered as
`TR-GRAPH-SIMPLIFY-001`.

Weighted aggregation adds a second transformation whose rule depends on the
query. Under suitable independence and coordinate assumptions, parallel scalar
admittances add, capacities add for a maximum-flow query, shortest-path lengths
take a minimum, and independent component reliabilities combine as
``1-\prod_k(1-r_k)``. None of those operations is a universal edge merge, and
none preserves member identity, individual limits, switching decisions, or
coupling. The [preservation-contract chapter](@ref preservation-contracts)
provides the required transformation vocabulary.

### Worked parallel fibre: four queries, four rules

Take two identified members ``e_1,e_2`` between ``u`` and ``v``. Give them
scalar admittances ``y=(10,1)\,\mathrm S``, current limits
``\bar i=(100,100)\,\mathrm A``, route lengths ``\ell=(10,1)``, and independent
availability probabilities ``r=(0.9,0.8)``. The simple projection records only
the adjacency ``\{u,v\}``. A useful weighted image depends on the question:

| Query | Image value | What remains outside the image |
|:--|:--|:--|
| unconstrained linear terminal current | ``y_{\mathrm{eq}}=10+1=11\,\mathrm S`` | member currents, ratings, losses, identity |
| endpoint maximum-flow capacity | ``c_{\mathrm{eq}}=100+100=200\,\mathrm A`` | the electrical sharing law and member constraints |
| shortest route | ``\ell_{\mathrm{eq}}=\min(10,1)=1`` | the nonselected route and route identity |
| at-least-one-member availability | ``r_{\mathrm{eq}}=1-(1-0.9)(1-0.8)=0.98`` | common-cause dependence, repair states, member provenance |

The capacity image is not an exact electrical-limit image. At a common voltage
difference of ``15\,\mathrm V``, the member currents are ``(150,15)\,\mathrm
A``. Their sum ``165\,\mathrm A`` satisfies the aggregate ``200\,\mathrm A``
bound while ``e_1`` violates its own ``100\,\mathrm A`` bound. The same fibre
therefore admits a sum, a minimum, a probability product, or no adequate scalar
replacement depending on the exactness object.

This example is intentionally elementary. Matrix admittances require compatible
terminal coordinates, capacity addition requires the declared flow model, and
the reliability expression requires independent member availability. The
numbers make the operation visible; they do not broaden its assumptions.

## Deletion, contraction, and matroid structure

For ``e\in E``, deletion removes ``e`` and its two flags. Contraction of a
non-loop edge identifies its two endpoint vertices and removes the contracted
edge. Other edges incident to those vertices are carried through the quotient.
That operation can create parallel edges and graph loops even when the input
was simple.

The category of multigraphs is therefore the natural working space for repeated
deletion and contraction. Insisting that every intermediate object remain
simple silently inserts a further simplification after each contraction and can
destroy information needed by later queries.

### Worked deletion and contraction

Let ``e_1,e_2`` be parallel edges between ``u`` and ``v`` and let ``e_3`` join
``v`` to ``w`` while ``e_4`` joins ``w`` to ``u``. The connected multigraph has
three vertices, four edges, and cycle rank two.

- Deleting ``e_1`` leaves ``e_2`` between ``u`` and ``v``; connectivity is
  unchanged and the cycle rank falls to one.
- Contracting ``e_1`` identifies ``u`` and ``v`` as ``x`` and removes
  ``e_1``. The image of ``e_2`` is a graph loop at ``x``; the images of
  ``e_3`` and ``e_4`` are parallel between ``x`` and ``w``. The contracted
  multigraph has two vertices, three edges, and cycle rank two.
- Simplifying that contracted graph deletes the loop and retains one of the
  two ``x``--``w`` members. The result has cycle rank zero.

The first two operations have standard edge-level meanings. The third is a
separate quotient that loses both circuits. This is why algorithms based on
minors naturally permit loops and parallel classes even when their input and
final presentation are simple.

The graphic matroid ``M(G)`` has ground set ``E`` and circuits given by the
minimal cycle supports. In this language:

- a graph loop is a matroid loop;
- two parallel non-loop edges form a two-element circuit;
- a bridge is a coloop and belongs to every spanning forest basis; and
- matroid simplification deletes loops and retains one representative from each
  parallel class.

This language is especially useful when the query concerns independence,
bases, cuts, or cycle supports rather than endpoint geometry. It does not carry
terminal coordinates, impedances, controls, or power-flow equations by itself.
Matroid equivalence is consequently not electrical equivalence.

Topology processing illustrates the distinction. Closing a zero-impedance
switch may cause a node-identification contraction; opening a branch is closer
to deletion; and bus--branch assembly may subsequently project parallel
identified devices into one adjacency. Each step has a different map and a
different recovery obligation. The [topology-processing chapter](@ref
node-breaker-topology) develops the state semantics.

## Power-system specialization

### Same endpoints do not settle electrical parallelism

Two identified branches are graph-parallel when their endpoint vertices agree
in the declared multigraph. They are electrically parallel for a particular
formulation only if they also act on compatible retained terminal coordinates.
Different phase sets, terminal permutations, transformer connections, mutual
coupling, controls, or internal states can invalidate scalar parallel formulas
even though the bus endpoints agree.

Conversely, elements can contribute to the same reduced nodal block only after
terminal identification or coordinate lowering. Their shared matrix support is
a fact about that compiled operator, not proof that the source assets were one
edge.

### Loads and generators: source role versus compiled placement

Whether a load or generator “belongs to the graph” has no context-free answer.
In this book, typed loads and generators belong to the canonical source model
and attach through nodal or terminal maps. A selected graph view may represent
them as factor vertices, terminal relations, one-terminal elements, edges to an
explicit reference, or no graph edges at all.

A constant-admittance load can be compiled into a nodal-admittance matrix. A
constant-power load generally remains a nonlinear current-injection or power
constraint. A solution method may also place a linearized or constant-impedance
component in the matrix and retain a compensation current outside it. OpenDSS,
for example, uses primitive admittances and compensation currents in its
current-injection solution architecture, with study-mode-specific equations
[OpenDSSSolutionTechniques, OpenDSSPowerConversionElements,
OpenDSSFaultStudyEquations](@cite).

These alternatives can produce different legitimate nodal matrices for the
same source system, operating point, initialization, or study. Therefore:

1. matrix membership does not determine source ontology;
2. the nodal matrix must be labelled by formulation, study mode, state, and
   linearization point where applicable; and
3. moving a typed element into a matrix stamp must not discard its identity,
   model class, limits, provenance, or recovery map.

The [load-model chapter](@ref load-models-and-decision-dependence) gives the
full engineering treatment. The [circuit-formulation chapter](@ref
circuit-formulations-and-lowering) distinguishes source factors from solver
assembly.

### Beyond multigraphs

A multigraph edge has exactly two flags. An n-port device, shared magnetic
relation, protection dependency, or multiway constraint may not have a faithful
two-terminal edge representation. Three common alternatives are:

- a bipartite incidence graph with explicit factor vertices;
- a hypergraph or incidence structure whose relation can own more than two
  flags; and
- a hierarchical port--factor model retaining typed coordinates and internal
  variables.

Replacing an n-port relation by a clique or star is a compilation choice. It
can create graph cycles or auxiliary vertices that are absent from the source
relation, so its preservation contract must identify which observations and
constraints survive. The multigraph remains essential for identified
two-terminal members, but it is not the universal source ontology.

### Incidence structures and typed n-port relations

The flag construction generalizes without forcing pairwise edges. Define a
finite incidence structure

```math
\mathcal I=(X,R,\mathcal F,s,p),
\qquad
s:\mathcal F\to X,
\qquad
p:\mathcal F\to R,
```

where ``X`` is a set of junction or object vertices and ``R`` is a set of
identified relations. Unlike a multigraph, the fibre ``p^{-1}(r)`` may have
any declared finite cardinality. A two-uniform incidence structure, in which
every relation owns exactly two flags, recovers the multigraph object. A
relation with three flags is natively ternary rather than three unexplained
pairwise edges.

For mathematical modeling, incidence alone is usually insufficient. Give each
flag ``f`` a typed variable space ``\mathcal X_f``, give each relation an
ordering or role map ``\omega_r`` on ``p^{-1}(r)``, and attach a constitutive
or constraint relation

```math
\mathcal R_r\subseteq
\prod_{f\in p^{-1}(r)}\mathcal X_f.
```

This is the flat core of the book's hierarchical port--factor object. The
hierarchy additionally records ownership, internal variables, subsystem
boundaries, and source provenance. A bare hypergraph records the multiway
incidence set; a bipartite incidence graph represents each ``r\in R`` as a
factor vertex adjacent to its incident flags or junctions; the typed
port--factor model retains the relation spaces and roles. These are related
representations, not synonyms.

This arbitrary-arity incidence and typed-relation boundary is registered as
`GRAPH-NPORT-001`.

For example, a three-winding transformer relation with ports ``h,m,l`` is one
arity-three factor. A star lowering introduces an internal vertex and three
two-terminal branches. Eliminating the star vertex can produce a three-edge
terminal clique. The incidence graph is acyclic locally, the star is acyclic,
and the clique has cycle rank one, yet all three can encode views of one device.
The cycle-rank change belongs to the compilation, not to the physical
transformer inventory.

## Declaration checklist

Before using a graph-derived result, record:

1. **Vertices:** buses, connectivity nodes, terminals, conductors, factors,
   equations, variables, or another declared object?
2. **Edges:** identified assets, closed-state members, terminal incidences,
   nonzero matrix blocks, or dependencies?
3. **Multiplicity and loops:** allowed, omitted, or produced by a quotient?
4. **Orientation:** which endpoint order is stored, and which quantities change
   sign under reorientation?
5. **Degree:** incidence, member, distinct-neighbour, terminal, or sparsity
   degree?
6. **Matrix convention:** how are loop and diagonal terms represented?
7. **State and study:** which switch state, formulation, mode, and operating or
   linearization point apply?
8. **Map:** what source-to-view transformation was applied, and what are its
   fibres?
9. **Query:** connectivity, cycle support, flow, feasibility, reliability,
   optimization, or another objective?
10. **Recovery:** which source identities, constraints, and results remain
    recoverable?

If these entries are absent, a mathematically correct theorem about the chosen
graph can still yield an engineering conclusion about the wrong object.

## Evidence boundary

The definitions and elementary matrix identities above are adopted conventions;
the repository checks them on a finite loop-and-parallel-edge witness in
`experiments/test/multigraph_conventions.jl`. The cited books establish the
general graph, matrix, and matroid background. The power-system sections are a
representation synthesis linked to this book's executable cases and specialist
chapters.

This chapter does not claim that every power-system device should be encoded as
an edge, that every nodal matrix is a Laplacian, that endpoint-parallel members
can always be aggregated, or that graph/matroid preservation implies electrical
or decision preservation. Those are precisely the shortcuts the declared maps
are intended to prevent.

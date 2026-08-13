# [Cycles, parallelism, and radial structure](@id cycles-parallelism-radiality)

## Why these words need a representation

Power-system discussions often say that a network has a cycle, a parallel line,
or a radial end as if these were properties of the physical system alone. They
are first properties of a declared mathematical representation. A simple
topology graph, an identified line multigraph, a junction--factor incidence
graph, and a compiled equation graph can give different answers while all
being legitimate views of the same network.

This chapter fixes the book's terminology. The electrical and decision meaning
of a topological statement is a second question: constitutive equations,
limits, states, and observations must still be attached.

## Simple cycles and line-identity cycles

Let ``G_{\mathrm s}=(\mathcal B,E)`` be a loopless undirected simple graph.
A simple cycle is a closed walk with at least three distinct vertices and no
repeated edge or internal vertex. Its cycle-space dimension is

```math
\mu_{\mathrm s}=|E|-|\mathcal B|+c,
```

where ``c`` is the number of connected components. The equation counts a
vector-space dimension; it does not select a unique cycle basis.

For an identified bus--branch multigraph, write

```math
G_{\mathrm M}=(\mathcal B,\mathcal L,\partial),
\qquad
\partial:\mathcal L\rightarrow\binom{\mathcal B}{2}.
```

Choose an arbitrary stored orientation for each line and let ``A`` be its
oriented incidence matrix. We use the following representation-aware
definition.

**Definition.** A **line-identity cycle** is a nonzero vector
``z\in\ker A`` whose support is inclusion-minimal among nonzero vectors in
``\ker A``. A cycle basis is any basis of ``\ker A``. Reorienting a line
negates one incidence column and changes the coordinates of ``z`` but not the
underlying cycle or its dimension.

This is the circuit definition of the graphic matroid written in incidence
coordinates. It includes the two-edge cycle made by parallel lines. If
``\ell_1ij`` and ``\ell_2ij`` have the same unordered endpoints, their two
incidence columns are equal up to sign, so a vector supported on
``\{\ell_1,\ell_2\}`` lies in ``\ker A``. The cycle does not require three
distinct buses.

For a loopless multigraph with ``c`` connected components,

```math
\mu_{\mathrm M}=|\mathcal L|-|\mathcal B|+c.
```

If ``\pi:\mathcal L\rightarrow E`` forgets line identity and retains the
unordered endpoint pair, then

```math
\mu_{\mathrm M}-\mu_{\mathrm s}
=
\sum_{e\in E}\bigl(|\pi^{-1}(e)|-1\bigr).
```

Thus each additional identified member in a parallel fibre contributes one
line-identity cycle dimension, even though the simple graph sees only one
adjacency. The five-bus example makes this loss explicit: its source rank is
three and its simple projection rank is two because the ``q``--``r`` fibre
contains two lines.

The cycle vector is a topological object. A nonzero cycle coordinate in a
branch-current parameterization is not automatically a circulating current,
and a topological cycle does not imply that power is flowing around it at a
particular operating point.

!!! warning "Graph-theory trap"
    Do not use *cycle*, *cycle-basis coordinate*, and *loop flow* as synonyms.
    The first two are properties or coordinates of a declared graph; the last
    is an operating statement requiring electrical variables and equations.

## Parallelism has levels

The phrase **parallel lines** is underspecified. The book distinguishes the
following tests, from weakest to strongest:

| Level | Condition | Where it can be decided |
|:--|:--|:--|
| topological parallelism | same unordered bus pair ``\partial(\ell_1)=\partial(\ell_2)`` | identified multigraph |
| terminal parallelism | endpoint terminal spaces and terminal maps align, up to declared coordinate actions | terminal-connectivity or port model |
| electrical parallelism | both factors see the same boundary voltage variables and their currents can be summed | port--factor or equation model |
| operational parallelism | both members are active in the declared switch, outage, investment, and state scenario | asset/state and decision model |
| homogeneous parallelism | construction, grounding, parameter, and constraint guards support a physical merge | asset plus electrical model |

Only topological parallelism is visible in a bare multigraph. In a simple graph
it is not an internal relation at all: it survives only as the fibre

```math
\pi^{-1}(\{i,j\})\subseteq\mathcal L
```

of the multigraph-to-simple-graph quotient. In a port--factor model, the two
lines remain separate factors attached to the same junction variables. That
representation can test whether a phase permutation, neutral connection,
grounding scope, control, and limit really align.

Electrical parallelism permits a terminal relation such as

```math
\mathbf I_{ij}^{\mathrm{total}}
=\sum_{\ell\in\pi^{-1}(\{i,j\})}\mathbf I_{\ell ij},
```

but it does not permit replacing member constraints by a summed constraint.
That replacement needs an explicit implication or lifting certificate. A
parallel pair can be electrically aggregable for an unconstrained nodal
admittance and still be operationally non-aggregable because its members have
different ratings, outages, owners, or investment decisions.

## Degree, leaves, bridges, and radial ends

For a bus ``i``, define the simple and multigraph degrees by

```math
d_{\mathrm s}(i)
=|\{j:\{i,j\}\in E\}|,
\qquad
d_{\mathrm M}(i)
=\sum_{e\in E:\,i\in e}|\pi^{-1}(e)|.
```

These are different measurements. A bus joined to one neighbour by two
parallel lines has ``d_{\mathrm s}(i)=1`` but ``d_{\mathrm M}(i)=2``. Calling
it a leaf without naming the graph is therefore ambiguous.

We use these precise terms:

- a **simple leaf bus** has ``d_{\mathrm s}(i)=1``;
- a **multigraph leaf bus** has ``d_{\mathrm M}(i)=1``;
- a **pendant line** is a bridge incident to a leaf in the declared graph;
- a **radial tail** is a maximal path of bridges ending at a leaf, with any
  internal buses of the path having degree two in that graph;
- a **pendant subnetwork** is a region attached through one articulation bus;
  it need not itself be radial.

An edge is a **bridge** if deleting that identified edge increases the number
of connected components. A simple edge ``e`` represents a parallel fibre
``\pi^{-1}(e)`` in the multigraph.

**Proposition.** For a line ``\ell`` in a loopless identified multigraph,
``\ell`` is a bridge if and only if ``\pi(\ell)`` is a bridge in the simple
projection and ``|\pi^{-1}(\pi(\ell))|=1``.

**Proof.** If another line shares the same endpoint pair, deleting ``\ell``
leaves that pair connected, so ``\ell`` cannot be a bridge. Conversely, suppose
the fibre of ``e=\pi(\ell)`` is a singleton but ``\ell`` is not a bridge. Then
there is a multigraph path between the two sides after deleting ``\ell``.
Projecting that path and removing repeated vertices gives a walk, hence a path,
in the simple graph with ``e`` deleted. This contradicts that ``e`` is a
simple-graph bridge. Therefore a singleton fibre over a simple bridge is a
multigraph bridge, and the two conditions are equivalent.

**Corollary.** The identified multigraph is a forest if and only if its simple
projection is a forest and every nonempty edge fibre is a singleton.

This gives two useful but different radiality predicates:

```math
\begin{aligned}
\text{adjacency-radial}&:\Longleftrightarrow G_{\mathrm s}\text{ is a forest},\\
\text{member-radial}&:\Longleftrightarrow G_{\mathrm M}\text{ is a forest}.
\end{aligned}
```

Adjacency-radial does not imply member-radial. A feeder with two parallel
circuits can have a tree-shaped simple projection and still contain a
line-identity two-cycle. Conversely, a simple graph can be meshed even when a
particular operating state opens enough members to make the active
multigraph radial.

!!! warning "Power-system shorthand"
    *Radial feeder* is incomplete unless it names both the graph and the active
    state. In particular, a tree-shaped simple projection can hide parallel
    member cycles.

“Radial end” should therefore be replaced in technical writing by the graph,
state, and object being tested: for example, “the ``m`` end is a pendant
bridge in the active identified multigraph” or “the simple bus projection has
a leaf at ``m``.”

## Multi-terminal factors change the question

A multiwinding transformer represented as one factor is not an ordinary graph
edge. Its natural incidence structure is bipartite:

```text
bus i  --  factor x  --  bus j
                    \--  bus k
```

This junction--factor incidence graph is a tree. A clique projection onto bus
vertices creates the triangle ``ij,jk,ki``; a star compilation through a
virtual junction remains a tree. The apparent cycle can therefore be created
by the representation rather than by an alternative physical transfer path.

The same warning applies to hyperedges, grounding factors, shared controls,
and equation graphs. A cycle in a factor-incidence graph means repeated
incidence through factors and junctions. A cycle in a nodal-admittance
sparsity graph means algebraic coupling. Neither should be silently called a
physical power-transfer loop.

## Consequences for decisions and reductions

The graph predicates above do not authorize a transformation by themselves:

- a bridge may carry a load, generator, measurement, grounding relation,
  protection boundary, or investment decision;
- a leaf may be the boundary of a nontrivial factor or a retained observation;
- a radial tail may be reducible for one boundary relation and indispensable
  for another;
- a parallel pair may provide outage redundancy even when its simple projection
  contains only one bridge;
- opening a chord is a topology decision, not a coordinate change;
- summing parallel admittances can preserve ``Y``-bus behavior while changing
  member-level feasible sets.

For a declared graph transformation, the preservation contract should record
at least:

1. the graph whose cycles, degrees, bridges, or forests are being tested;
2. whether members are identified, aggregated, or merely projected;
3. the active state and admissible future states;
4. the boundary quantities and source constraints that must be recovered;
5. the provenance fibre for every quotient edge or compiled factor.

The scope rule is simple:

> A cycle, parallel relation, bridge, leaf, or radiality claim must name its
> representation. None of these graph properties, alone, authorizes an
> electrical reduction.

## Executable active-state certificate

The package-independent witness in
`experiments/generated/active-radiality-witness.json` compares a four-member
inventory with an active state in which one of two parallel members is open.
The inventory's simple projection is radial, but its identified multigraph is
not: the parallel fibre contributes a line-identity cycle. After the outage,
the active identified multigraph is a tree, so both active radiality predicates
agree. This is the small counterexample needed before using radiality as a
guard for a conductor-coordinate or phase-to-phase reduction.

Run it with:

```sh
julia --project=experiments experiments/run_active_radiality.jl
```

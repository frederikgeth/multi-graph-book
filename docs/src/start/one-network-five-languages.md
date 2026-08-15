# [One network, five languages](@id one-network-five-languages)

**Page status:** explanatory cross-community vocabulary bridge; not a standards crosswalk.

The communities that work on power networks often use the same word for
different objects, and different words for nearly the same object. This is
more than a stylistic inconvenience. If *edge*, *state*, *flow*, or
*equivalent* changes meaning halfway through an argument, a correct statement
about one representation can become a false statement about another.

This book therefore uses a **bridge vocabulary**. It does not ask readers to
abandon familiar language. It asks them to qualify a familiar term when that
term carries mathematical, physical, software, or decision meaning.

![Five communities approach the same source model through different vocabularies; the bridge records the object, qualifier, and unsafe inference.](../assets/vocabulary-bridge-five-languages.png)

## The running network in five dialects

Consider the same multiconductor network with parallel circuits, explicit
neutral and grounding, phase-selective switches, limits, and a multiwinding
transformer. Each community has a useful description of it:

- **Power engineering:** buses, feeders, lines, transformers, radial operation,
  and power flow support physical interpretation and operating practice. The
  graph, terminal sign, device boundary, and active state may remain implicit.
- **Power-system software and data:** equipment records, terminals,
  connectivity nodes, statuses, profiles, and compiled buses support exchange,
  topology processing, and provenance. A record may represent a physical
  asset, generated object, or equation object.
- **Mathematical modelling and optimization:** variables, constraints,
  parameters, feasible sets, objectives, and relaxations support decision
  semantics and formal comparison. Source identity and physical recovery may
  be outside the formulation.
- **Mathematical graph theory:** vertices, edges, arcs, multigraphs,
  incidence, cycles, quotients, and minors support structural theorems and
  algorithms. The physical referent and load-bearing attributes must be added.
- **Graph machine learning:** heterogeneous nodes and edges, features, message
  passing, pooling, embeddings, and hidden states support learned computation.
  Parallel identity, n-port structure, limits, and physical state survive only
  when the compiled graph and feature maps retain them.

None of these descriptions is the universal one. The bridge is the typed map
from a community's phrase to the object and query meant in this book.

## Translation is not word substitution

For each community term, the relation to the book's term should be classified
before it is reused:

- **Exact alias:** interchangeable under the declared scope. For example,
  `Ybus` can be an alias for the declared nodal operator after its coordinate
  order and model class are fixed.
- **Scoped alias:** conventional shorthand that is safe only with a qualifier.
  *Branch direction* may mean the stored orientation ``\ell ij``.
- **Broader or narrower term:** one term contains distinctions omitted by the
  other. A physical line can contain several homogeneous model sections.
- **Representation-dependent term:** its referent changes with the selected
  view. *Node*, *edge*, *cycle*, and *radial* are the leading examples.
- **False friend:** the words coincide but the concepts do not. Electrical
  loss is not an ML loss; a GNN message is not a conserved power flow.

These labels are deliberately asymmetric. A term can be acceptable when
reading a source and still be too weak to use in a preservation claim.

## The collision set to learn first

### Objects

**Bus, node, vertex, junction, terminal, and port** must not be collapsed into
one noun. A bus may mean a busbar section, a connectivity node, a
state-dependent topological node, a group of nodal variables, or a reporting
aggregate. A graph vertex is whatever the declared graph makes a vertex. A
port is a typed component interface; a junction supplies interconnection and
conservation semantics.

Likewise, **line, branch, edge, arc, relation, and matrix nonzero** do not share
one identity. A line ``\ell`` owns intrinsic equipment or model data. The
oriented triple ``\ell ij`` orders its terminals. An edge in a support graph
records algebraic coupling and may have no one-to-one physical asset.

An especially important collision is **factor**. Here it means a typed
constitutive, control, measurement, limit, or decision relation over ports. It
does not mean power factor or matrix factorization, although the same factor
may become a node in a factor graph.

### Structure and state

**Graph, topology, adjacency, parallel, cycle, tree, and radial** require a
named representation and usually an active state. A simple bus projection, an
identified asset multigraph, a conductor-coordinate support graph, and a GNN
message graph can give different answers for the same source network.

**State** is also overloaded. It can mean continuous electrical state
variables, discrete equipment status, an operating scenario, an estimator
state, or an ML hidden representation. The book uses a modifier whenever two
of these meanings are in scope.

### Quantities and computation

**Direction** may mean stored orientation, terminal-current sign, observed
power transfer, rooted-tree order, causal dependence, one-way admissibility,
or message direction. None implies the others.

**Flow** may mean a conserved commodity variable, internal series current,
terminal current, terminal complex power, an operating transfer, or a learned
message. A lossy AC device generally exposes a tuple of terminal powers rather
than one antisymmetric edge-flow scalar.

**Limit, rating, and constraint** occupy different layers. A rating is an
equipment or operational datum; a mathematical constraint is a particular
encoding of admissibility; whether that constraint binds belongs to an
operating point or solution.

### Transformations and evidence

**Projection, compilation, lowering, elimination, aggregation, reduction,
coarsening, and pooling** are not interchangeable ways of saying *make the
graph smaller*. Compilation can make a graph larger. Elimination can create
fill. Pooling can erase member identities required by a decision problem.

**Equivalent, exact, and structure preserving** are incomplete until their
object is named. The relevant claim may concern an algebraic identity,
boundary behaviour, topology, feasible decisions, objective value, limits,
measurements, numerical sparsity, or provenance.

Two cross-community false friends deserve permanent warnings:

- **normalization** can mean per-unit conversion, conductor-coordinate
  canonicalization, schema normalization, or ML feature scaling;
- **loss** can mean electrical dissipation, information discarded by a map,
  or an ML training objective.

## House policy: familiar words with explicit qualifiers

The book uses three vocabulary statuses:

1. A **preferred house term** is used in definitions, claims, contracts, and
   executable artifacts.
2. An **accepted qualified shorthand** is retained when it helps a community
   read naturally and its scope is stated nearby.
3. An **unsafe unqualified term** is accompanied by the missing
   representation, quantity, state, or preservation object.

For example, *radial feeder* remains useful prose. A load-bearing statement is
written as *the active simple bus projection is a tree in state ``\sigma``*.
Similarly, *power flow on line ``\ell``* is replaced in an equation or limit
claim by the relevant terminal observation ``\mathbf S_{\ell ij}`` or
``\mathbf S_{\ell ji}`` and its sign convention.

## Two worked translations

> **Community phrase:** Power flows downstream on each edge of the radial
> feeder.

A testable translation names (i) the active bus-level graph, state, and root
that define the parent relation; (ii) the oriented terminal at which active
power is measured; and (iii) the fact that its sign is an operating result.
It does not infer member-radiality, losslessness, or permanent upstream and
downstream asset labels.

> **Community phrase:** Pool the parallel edges and run message passing on the
> network graph.

A testable translation names the computational graph and pooling map, then
asks whether line identity, outage state, member limits, conductor
coordinates, and recovery are inputs to the downstream query. If they are,
the pooled graph needs side information or is not a sufficient representation
for that task.

## Where to go next

The [Translation traps](@ref translation-traps) chapter develops the most
dangerous false inferences. [Representation taxonomy](@ref
representation-taxonomy) defines the graph families, [Notation and modelling
conventions](@ref) fixes semantic ownership and indices, and the maintained
[Terminology](@ref) page provides the compact lookup vocabulary. The later
preservation-contract chapters turn these linguistic qualifications into
mathematical obligations.

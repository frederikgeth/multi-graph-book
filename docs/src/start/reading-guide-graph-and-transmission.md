# [Reading guide: from simple graphs and transmission models to multiconductor networks](@id reading-guide-graph-and-transmission)

**Page status:** audience-specific onboarding guide; the formal definitions and
the executable evidence remain in the linked foundation and case chapters.

This book has two especially common starting points. Some readers know graph
theory and expect vertices, edges, incidence, cycles, and sparsity. Others know
power-system analysis and expect a balanced bus--branch model, often in
positive-sequence form. Both are strong foundations. Neither is the whole
multiconductor power-network model.

Use the route that matches your background, then join the shared path at the
four-wire relation and the first decision counterexample.

## Two routes into one language

| Starting point | Familiar starting model | First surprise | New question to ask |
|:--|:--|:--|:--|
| Simple graph theory | vertices, edges, paths, cycles, incidence, quotients | an electrical edge can be a vector-valued factor, and a matrix-support cycle need not be a physical loop | which graph, which coordinates, and which identities are retained? |
| Balanced transmission modelling | one complex relation per bus pair, often positive sequence | a line can have phase and neutral coordinates, dense coupling, endpoint shunts, and distinct terminal observations | which specialization was made, and which constraints or ports were collapsed? |

The shared destination is not a larger drawing. It is a typed model in which
identities, terminals, factors, equations, constraints, decisions, and
provenance can be related without silently treating one view as another.

## If you come from simple graph theory

### 1. Replace “edge” by “terminal relation”

A graph edge records incidence. A power-network factor also has a constitutive
relation. In the scalar case this may be

```math
i_{ell ij}=y_ell(v_i-v_j).
```

In a four-wire case the same idea is a map between ordered terminal spaces:

```math
\mathbf I_{ell ij}
=\mathbf Y_ell
\left(
\mathbf U_i[\mathbf N_{ell i}]
-\mathbf U_j[\mathbf N_{ell j}]
\right).
```

The edge identity ``\ell`` and the attachment triple ``\ell ij`` remain
separate from the matrix coordinates inside ``\mathbf Y_\ell``.

### 2. Replace scalar vertices by terminal spaces

A bus may own ``a``, ``b``, ``c``, and ``n`` terminals, or a different ordered
subset. Thus one bus can correspond to a block of variables rather than one
scalar vertex. A dense block says that conductor coordinates are coupled; it
does not create one physical asset per nonzero entry.

### 3. Keep the multigraph fibre

Two lines with the same endpoint pair are parallel in the simple projection but
remain distinct in the identified asset multigraph. Their separate ratings,
states, owners, and outage decisions may matter even when their unconstrained
terminal admittances add exactly.

### 4. Separate physical and algebraic cycles

The incidence nullspace of an identified line multigraph, the cycle space of a
simple quotient, the cycle structure of a port--factor graph, and cycles in a
scalar support graph are different objects. A dense conductor block can make a
support graph cyclic while the bus-level equipment graph remains a tree.

### 5. Treat n-port devices as factors

A three-winding transformer is naturally one factor with three typed port
bundles. A star, clique, or ordinary-edge realization is a derived target and
needs a declared lowering map and provenance fibre.

The main graph-theory route is therefore:

1. [Five-bus cycle spaces](@ref five-bus-cycle-spaces);
2. [Five buses through a multi-port lowering](@ref
   five-bus-transformer-lowering);
3. [Two topology levels and the nodal projection](@ref
   two-level-topology-and-nodal-projection);
4. [Circuit formulations and the lowering boundary](@ref
   circuit-formulations-and-lowering).

## If you come from balanced transmission modelling

### 1. Treat positive sequence as a specialization

The positive-sequence bus--branch model is often exactly the right model for a
declared balanced transmission study. In this book it is a derived
specialization, not the universal meaning of a bus, line, or edge. The question
is not whether the specialization is legitimate, but what assumptions make it
legitimate for the study at hand.

### 2. Expand one edge before expanding the whole network

Start with the familiar scalar relation and add structure in a controlled order:

```math
\text{scalar edge}
\;\longrightarrow\;
\text{four-wire matrix edge}
\;\longrightarrow\;
\text{port--factor relation}
\;\longrightarrow\;
\text{block nodal operator}.
```

At each arrow, ask what was added: conductor coordinates, mutual coupling,
terminal maps, shunts, grounding, internal ports, or decision variables.

### 3. Relearn “flow” at the edge boundary

Power engineers often speak of power flowing through a line as though one
antisymmetric scalar lived on the edge. A lossy AC factor instead has terminal
currents and terminal powers. Endpoint shunts, grounding, and series loss can
make the two terminal observations different. The stored orientation fixes a
sign convention; it does not predict the operating direction.

### 4. Keep the neutral when reducing it

Kron reduction may preserve a boundary voltage relation while eliminating an
internal neutral coordinate. The recovered neutral current, grounding path,
protection rule, and current limit still belong to the source decision problem.
This is why a reduced Y-bus is not automatically a complete feasible-set model.

### 5. Promote transformers from “branches” to multi-port factors

Two-winding transformer notation is a useful special case. Multiwinding devices,
connection maps, internal grounding, and controls need typed ports and factors.
An ordinary-edge expansion is optional and guarded; direct factor stamping or a
tableau/MNA formulation may be the faithful target.

### 6. Requalify radial language

“Upstream” and “downstream” are properties of a selected active rooted tree,
not permanent properties of a meshed asset. Switching can change the tree,
parallel members can make member-radiality differ from adjacency-radiality, and
phase-selective switching can break a scalar feeder interpretation.

The main transmission route is therefore:

1. [When the general model collapses](@ref positive-sequence-collapse);
2. [From conductor geometry to impedance fidelity](@ref
   impedance-fidelity-ladder);
3. [Four-wire impedance-model ladder](@ref four-wire-impedance-model-ladder);
4. [A first failure: heterogeneous parallel branches](@ref
   first-failure-parallel-branches);
5. [Kron, Ward, and optimized network equivalents](@ref
   kron-ward-opti-kron).

## The shared convergence point

Both routes should meet at the same question:

> What does this representation preserve for the observation, constraint, and
> decision I care about?

The first failure is deliberately small. Two identified parallel branches can
have an exactly summed terminal admittance and still have a different feasible
set when their individual current limits matter. The example is the bridge from
graph structure or transmission equations to the book's central preservation
contract.

From there, read the [preservation contracts](@ref preservation-contracts),
then use [Translation traps](@ref translation-traps) whenever a familiar word
such as *edge*, *flow*, *radial*, or *equivalent* appears without a qualifier.

## A compact checklist

Before importing a theorem, software formulation, or engineering shorthand,
write down:

- **objects:** assets, buses, terminals, ports, factors, or matrix coordinates;
- **index meaning:** semantic label, endpoint triple, conductor slot, or storage
  position;
- **coordinates:** scalar, phase/neutral vector, sequence, complex block, or
  realified array;
- **graph:** simple quotient, identified multigraph, port--factor incidence,
  equation graph, or support graph;
- **orientation:** stored order, current sign, operating transfer, or rooted-tree
  parent relation;
- **preservation target:** terminal behaviour, limits, decisions, objectives,
  recovery, or provenance.

If those fields are explicit, the two starting communities can use the same
mathematical language without pretending that their familiar starting graphs
already contain the full multiconductor model.

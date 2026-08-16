# Terminology

**Page status:** maintained glossary and translation aid.

This page records the preferred vocabulary used in definitions, claims, and
certificates. Readers approaching from power engineering, software and data,
mathematical modelling, graph theory, or graph machine learning should begin
with [One network, five languages](@ref one-network-five-languages).

The canonical editorial policy and its three usage statuses are defined in
[House policy: familiar words with explicit qualifiers](@ref
vocabulary-house-policy). This page applies that policy as a lookup surface.
Community terms are not declared synonyms merely because they occupy the same
row: the vocabulary relation and the permitted editorial usage are separate
classifications. For the exhaustive generated views, use the
[community-to-book and book-to-community indexes](@ref vocabulary-indexes).
Those indexes are generated from the controlled registry; this page remains the
maintained definition surface.

## Cross-community collision index

| Familiar term or cluster | Required question in this book | Common unsafe inference |
| --- | --- | --- |
| [bus, node, vertex, junction, terminal, port](@ref terminology-bus) | What object type and representation? | every node is one physical bus |
| [line, branch, edge, arc, relation, nonzero](@ref terminology-line) | What owns identity and what records attachment or coupling? | every graph edge is one physical branch |
| factor | Behavioural relation, factor-graph node, power factor, or matrix factor? | these uses are interchangeable |
| graph, topology, adjacency | Asset, active-connectivity, factor-incidence, equation, support, or message graph? | one topology answers every query |
| [directed, oriented, upstream, downstream](@ref terminology-directed) | Stored order, operating sign, rooted-tree relation, causality, or admissibility? | an arrow predicts physical transfer |
| [flow, current, power, message](@ref terminology-flow) | Which terminal or internal quantity and which conservation law? | one antisymmetric scalar lives on every edge |
| parallel | Same endpoints, same terminals, shared corridor, homogeneous equipment, or parallel computation? | members can be merged without a contract |
| cycle, loop, mesh, radial | In which graph and active state? | a graph cycle is a circulating physical flow |
| state | Electrical variables, equipment status, scenario, estimator state, or ML hidden state? | one state object contains all of them |
| rating, limit, constraint | Source datum, operational policy, or mathematical encoding? | one scalar constraint reproduces the equipment limit |
| [equivalent, exact, preserving](@ref terminology-equivalent) | Which interface and preservation object? | equal terminal equations imply equal decisions |
| projection, compilation, elimination, aggregation, reduction, pooling | Which objects are changed, forgotten, solved, or recoverable? | every operation merely makes a graph smaller |
| normalization | Per-unit, coordinate, schema, physical-model, or feature normalization? | all normalizations preserve the same semantics |
| loss | Electrical dissipation, information loss, or training objective? | a shared word implies a shared quantity |
| [ground, neutral, reference](@ref terminology-ground-neutral-reference) | Physical earth, conductor, impedance, or gauge choice? | all are one zero-voltage node |
| [phase, conductor, sequence, coordinate](@ref terminology-phase-conductor-coordinate) | Asset label, physical path, terminal slot, phase-domain quantity, or transformed coordinate? | one label fixes every coordinate and transformation |

The sections below give the compact house definitions. Detailed counterexamples
belong to [Translation traps](@ref translation-traps); rigorous graph objects
belong to [Representation frameworks](@ref formal-representation-frameworks).

| Term | Meaning in this book | Definition or route |
| --- | --- | --- |
| Asset | A physical or organizational entity with stable identity and lifecycle facts | [Frameworks](@ref formal-representation-frameworks) |
| Port | A typed interface at which variables interact with a component or subsystem | [Frameworks](@ref formal-representation-frameworks) |
| Junction | An interconnection object imposing equality/conservation structure | [Frameworks](@ref formal-representation-frameworks) |
| Factor | A constitutive, control, limit, measurement, or decision relation over ports | [Frameworks](@ref formal-representation-frameworks) |
| Hierarchy | Explicit containment with declared subsystem boundary ports | [Frameworks](@ref formal-representation-frameworks) |
| Projection | A map that forgets distinctions without solving governing equations | [Transformation register](@ref transformation-semantics-register) |
| Compilation | Replacement of a high-level component by a realization in a target vocabulary | [Transformation register](@ref transformation-semantics-register) |
| Normalization | A semantics-preserving rewrite into a selected canonical physical/model form | [Transformation register](@ref transformation-semantics-register) |
| Behavioral reduction | Elimination of hidden variables preserving a declared external relation | [Projection, compilation, and reduction](@ref) |
| Approximate reduction | Reduction with a stated observation domain, metric and error | [Projection, compilation, and reduction](@ref) |
| Preservation contract | Precise statement of retained observations, constraints, assumptions and recovery | [Contracts](@ref preservation-contracts) |
| Recovery map | Map from retained/reduced variables to eliminated source quantities | [Contracts](@ref preservation-contracts) |
| Provenance | Traceable correspondence among source, generated and reduced objects | [Source architecture](@ref source-to-canonical-model) |
| Morphism | A map preserving the declared structure within one representation framework | [Representation maps](@ref representation-maps) |
| Isomorphism | A reversible morphism; a change of names or coordinates rather than a quotient or compilation | [Representation maps](@ref representation-maps) |
| Query factorization | Evidence that a source query can be answered from a target because it factors through the declared transformation | [Contracts](@ref preservation-contracts) |
| Computational dependency graph | A graph whose vertices and edges encode declared variables, equations, operations, or dependencies rather than physical equipment | [Frameworks](@ref formal-representation-frameworks) |
| Message graph | The compiled graph on which a graph-learning architecture exchanges messages; its nodes and edges need not be physical buses and branches | [Vocabulary bridge](@ref one-network-five-languages) |
| Feature | An attribute supplied to a statistical or learned model; physical meaning exists only through its source map, units, coordinate convention, and state association | [Vocabulary bridge](@ref one-network-five-languages) |
| Pooling | A many-to-one learned or algorithmic aggregation whose sufficiency is relative to a downstream query and retained side information | [Transformation register](@ref transformation-semantics-register) |
| Electrical state | The declared continuous electrical variables at an operating point, distinct from equipment status, scenario labels, estimator metadata, and learned hidden state | [Load models](@ref load-models-and-decision-dependence) |
| Equipment state | A discrete or continuous device condition such as switch status or tap position, with source identity and admissible transitions retained | [Topology processing](@ref node-breaker-topology) |
| Neutral conductor | An explicit conductor with voltage, current, connectivity, ratings, and provenance rather than a synonym for earth or reference | [Earth and neutral](@ref earth-ground-models) |
| Voltage reference | A gauge choice used to select a voltage representative; not automatically physical earth or a neutral conductor | [Earth and neutral](@ref earth-ground-models) |
| Terminal coordinate | One ordered component of a declared terminal interface vector | [Notation and modelling conventions](@ref) |
| Sequence coordinate | A transformed combination of phase-domain coordinates under a declared basis | [General-model collapse](@ref positive-sequence-collapse) |
| Asset/terminal topology | Identified high-level equipment and its port or bus attachments; a multigraph only for the genuinely two-terminal subset | [Frameworks](@ref formal-representation-frameworks) |
| Conductor/port--factor topology | Electrical conductor junctions, typed ports, and constitutive factors, with terminal maps and coupling retained | [Frameworks](@ref formal-representation-frameworks) |
| Block-support graph | Simple graph with one vertex per retained nodal block and an edge for each nonzero off-diagonal block of an assembled operator | [Two-level topology](@ref two-level-topology-and-nodal-projection) |
| Scalar-support graph | Simple graph on retained scalar coordinates, with edges determined by nonzero matrix entries rather than asset identity | [Two-level topology](@ref two-level-topology-and-nodal-projection) |
| Stamp multigraph | Derived decomposition that retains one identified member for each separate factor stamp contributing to an assembled matrix | [Two-level topology](@ref two-level-topology-and-nodal-projection) |
| Simple cycle | A closed cycle of at least three distinct vertices in a loopless simple graph | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Line-identity cycle | A minimal-support nonzero vector in the incidence nullspace of an identified multigraph | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Parallel fibre | The set of identified elements mapped to one unordered endpoint pair by the simple quotient | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Bridge | An identified edge whose deletion increases the number of connected components in the declared graph | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Radial tail | A maximal bridge path ending at a leaf in a specified graph and active state | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Adjacency-radial | Forest property of the simple topology projection | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Member-radial | Forest property of the identified line multigraph | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Terminal power | Complex-power injection at one declared device terminal; generally one member of a two-end or multiport observation tuple | [Orientation and power](@ref orientation-terminal-power) |
| Energized | Connected through the declared active device states to an admissible source under the study's electrical semantics | [Earth and neutral](@ref earth-ground-models) |
| Complex symmetric | Matrix satisfying ``\mathbf A^{\mathsf T}=\mathbf A``; not synonymous with Hermitian | [Translation traps](@ref translation-traps) |
| Physical merge | Rewrite asserting that source assets are subdivisions or representations of one target asset | [Transformation register](@ref transformation-semantics-register) |
| Composite equivalent | Behavioral object representing several source components without claiming homogeneous physical identity | [Transformation register](@ref transformation-semantics-register) |
| Closure | Property that a model class remains in the same class under a transformation | [Transformation register](@ref transformation-semantics-register) |
| Confluence | Property that different valid rewrite orders reach equivalent normal forms | [Transformation register](@ref transformation-semantics-register) |
| Structure-preserving transformation | A typed bijective map or coordinate action that commutes with the declared incidence and relation structure | [Transformation register](@ref transformation-semantics-register) |
| Decision-preserving transformation | A transformation whose mapped feasible decisions, objective and declared source constraints agree under the stated contract | [Contracts](@ref preservation-contracts) |
| Composite factor | A target factor that preserves a declared relation for several source assets without claiming they are one homogeneous physical asset | [Transformation register](@ref transformation-semantics-register) |
| Type-safe composition | Composition accepted only when ports, factor classes, units, states and constraint ownership satisfy a declared rule | [Transformation register](@ref transformation-semantics-register) |
| Anti-pattern | A tempting rewrite that is algebraically suggestive but violates a type, preservation or observation precondition | [Translation traps](@ref translation-traps) |
| Rooted active-tree view | A state- and root-dependent parent/child orientation of a radial active graph used by an algorithm or feeder recursion | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Parent edge | The unique active-tree edge connecting a non-root node to its predecessor on the selected root path | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Chord | An active member omitted from a selected spanning forest; it closes a cycle and is not intrinsically upstream or downstream | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Upstream/downstream | A qualified hierarchy label relative to a declared root, active state and tree; never an unqualified property of a passive asset | [Cycles and radiality](@ref cycles-parallelism-radiality) |
| Source-distance | A graph metric or path relation from a designated source, which may remain meaningful in a mesh even when parenthood is not unique | [Cycles and radiality](@ref cycles-parallelism-radiality) |

## Terms to use carefully

### [Structure preserving](@id terminology-structure-preserving)

Always qualify the structure: Laplacian, sparsity, radiality, phase
connectivity, port-Hamiltonian form, equipment class, asset correspondence,
limits, or dynamic equations. The unqualified phrase is too ambiguous.

### [Equivalent](@id terminology-equivalent)

Always state the interface, operating/model domain, observations, constraints,
and whether the claim is exact, conservative, relaxed, or approximate.

### [Bus](@id terminology-bus)

Distinguish at least:

- physical busbar or busbar section;
- connectivity node;
- state-dependent topological node;
- mathematical nodal variable group;
- reporting or planning bus.

### Nodal-admittance graph

State whether this means block support, scalar conductor-coordinate support,
or a retained stamp decomposition. The first two are simple support graphs of
an operator. They do not recover the identified asset multigraph that was
assembled into that operator.

### [Line](@id terminology-line)

Distinguish:

- physical circuit or cable system;
- homogeneous construction segment;
- model section introduced by discretization;
- mathematical two-port branch;
- behavioral equivalent with no single physical counterpart.

### [Flow](@id terminology-flow)

Distinguish a commodity-flow variable, an internal series current, a terminal
current, a terminal complex power, and an observed operating-point transfer.
A lossy AC branch generally has a pair of terminal powers rather than one
conserved edge-flow scalar.

### [Directed](@id terminology-directed)

State whether direction means stored orientation, terminal-current sign,
positive power reference, observed operating transfer, causal dependency, or
one-way admissibility. These meanings do not imply one another.

### Connected and energized

Graph connectivity is a structural predicate. Energization additionally
depends on active state, admissible sources, terminal connectivity, and the
electrical semantics of the study.

### [Ground, neutral, and reference](@id terminology-ground-neutral-reference)

Distinguish physical earth or an earth-return model, a neutral conductor, a
grounding impedance or connection, and a voltage reference used to remove
gauge freedom. A neutral voltage may be eliminated from a reduced coordinate
system while its recovered current, rating, grounding path, and protection
meaning remain part of the source feasible set.

### [Phase, conductor, sequence, and coordinate](@id terminology-phase-conductor-coordinate)

State whether *phase* names an asset label, a physical conductor, a bus
terminal, a phase-domain component, or a reporting aggregate. A terminal
coordinate is an ordered interface slot; a sequence component is a transformed
coordinate. Conductor permutations, phase discontinuities, and sequence
transforms therefore require declared maps rather than matching labels alone.

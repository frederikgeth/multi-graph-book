# Representation taxonomy

The phrase *power-network graph* covers several mathematical and data structures that retain
different facts. This taxonomy prevents a physical asset graph, an equation graph, and a solver
sparsity graph from being treated as interchangeable merely because all have vertices and edges.

## Five questions before naming a graph

For a representation ``M``, ask:

1. **Identity:** which physical, logical, and generated objects remain distinguishable?
2. **Interconnection:** what counts as a terminal, junction, edge, hyperedge, or port?
3. **Behaviour:** where do constitutive equations, controls, limits, and uncertainty live?
4. **State:** which topology and equipment states are fixed, variable, or omitted?
5. **Purpose:** which observations, analyses, and decisions is the representation intended to
   support?

Two structures with identical unlabelled topology can answer these questions differently.

## Representation families

### Asset and property models

Vertices represent physical or organizational entities; typed relations record containment,
ownership, construction, location, protection, measurement, and provenance. Such a model may retain
two electrically equivalent parallel assets as distinct while omitting the internal variables of a
compiled electrical equivalent.

### Terminal-connectivity models

Objects expose ordered terminals or conductor bundles. Junctions express equality and conservation
without yet requiring every device to be an ordinary edge. This family is the natural baseline for
explicit phases, neutrals, grounding, phase discontinuities, and switchgear.

### Node--breaker and bus--branch models

A node--breaker model retains switching equipment and detailed connectivity. A state-resolved bus
model quotients nodes connected by closed ideal switches. A bus--branch multigraph adds identified
two-terminal branches; a simple graph additionally forgets parallel identity.

These are different representations, not interchangeable names for resolution levels.

### Port, factor, and hypergraph models

A behavioural factor relates variables on an arbitrary ordered set of ports. Ordinary branches are
arity-two special cases. Multiwinding transformers, converters, mutual couplings, shared controls,
and measurement relations need not be decomposed into artificial pairwise edges.

### Algebraic and equation models

Incidence, admittance, Laplacian, Jacobian, KKT, and constraint matrices induce graphs from their
nonzero structure. Their vertices may represent variables, equations, blocks, or matrix rows rather
than physical objects. They are indispensable for analysis and computation, but their edges do not
automatically carry physical meaning.

### Study-specific compiled models

A power-flow, OPF, state-estimation, fault, or decomposition model selects variables and relations
for a task. Compilation may create virtual buses and branches, eliminate explicit currents, fix
states, relax constraints, or introduce auxiliary variables. Graph size alone therefore says
nothing reliable about physical or decision expressiveness.

## Comparison by retained meaning

| Family | Primary objects | Strongest use | Characteristic omission |
| --- | --- | --- | --- |
| Asset/property | equipment, owners, locations, records | identity and lifecycle | electrical state equations |
| Terminal connectivity | terminals, junctions, switches | conductor-aware interconnection | device behaviour unless linked |
| Bus--branch multigraph | buses and identified branches | conventional network algorithms | internal device and conductor structure |
| Simple weighted graph | vertices and aggregated edges | visualization and generic graph methods | parallel identity, controls, limits |
| Port--factor/hypergraph | ports and behavioural relations | multi-terminal composition | asset meaning unless linked |
| Equation/sparsity graph | variables, equations, nonzeros | numerical solution and decomposition | most physical identity |

No row is globally maximal. An asset graph and a compiled equation graph may retain incomparable
information.

## Comparison by decision support

| Required question | Representation obligation | Common failure |
| --- | --- | --- |
| Which asset is out of service? | stable element identity and state | aggregated edge has no member state |
| Is every conductor within its rating? | terminal/conductor currents and limits | scalar branch rating replaces several limits |
| May a switch be operated? | switch identity, admissible states, control ownership | closed-switch quotient discards the choice |
| Is grounding represented correctly? | neutral, earth, reference, and impedance semantics | neutral and ground are conflated |
| Is an OPF decision equivalent? | feasible-set, objective, and decision maps | terminal voltages agree but active constraints change |
| Can source results be reconstructed? | recovery map and provenance | virtual or eliminated objects have no source correspondence |

## Axes, not one ladder

Representations should be located along several independent axes:

- physical identity retained or forgotten;
- conductor and terminal resolution;
- factor arity and device vocabulary;
- hierarchy and subsystem boundaries;
- fixed versus variable topology state;
- equations only versus equations plus feasible sets and decisions;
- exact versus approximate behaviour;
- source provenance and recoverability;
- physical versus computational interpretation.

A representation can be simpler on one axis and richer on another. Compiling a transformer into a
loss network may increase the number of vertices while reducing the device vocabulary. Eliminating
internal buses may reduce the vertex count while creating dense coupling and more complicated
constraints.

## The general multiconductor baseline

The book begins with arbitrary ordered terminal sets and full conductor coupling. A transmission
bus--branch model appears when additional conditions justify several collapses, for example:

- the retained buses have compatible phase sets and ordering;
- the system is sufficiently balanced for the declared observations;
- sequence domains decouple under the element models used;
- neutral and grounding behaviour is absent, externally fixed, or validly reduced;
- equipment can be represented as identified two-terminal branches;
- per-conductor and device-internal constraints do not affect the decisions of interest;
- parallel aggregation retains all relevant member states and all nonredundant
  limits, with any removed constraint certified as implied, or those
  distinctions are outside the contract.

This explains why many transmission studies can use compact graphs successfully without treating
their assumptions as universal power-network semantics.

## Proposed linked reference architecture

The working hypothesis of this book is that two linked structures provide a useful source from
which the major representation families can be generated:

1. a typed asset/property model for stable physical and organizational identity;
2. a typed hierarchical port--factor model for electrical interconnection, behaviour, limits, and
   decisions.

This is a proposal to test. Evidence must include faithful mappings of multiconductor lines,
multiwinding transformers, switchgear, grounding, parallel assets, controls, and study-specific
models—not only an abstract claim of generality.

## A representation card

Every representation chapter and knowledge-base entry should record:

| Field | Question |
| --- | --- |
| Object types | What becomes a vertex, edge, port, factor, or attribute? |
| Identity | Which objects remain distinguishable? |
| Coordinates | How are terminals, conductors, orientation, units, and bases declared? |
| Behaviour | Which equations and inequalities are native? |
| State | Which continuous and discrete states are represented? |
| Purpose | Which analyses or decisions motivate the view? |
| Loss | What cannot be answered from this view alone? |
| Recovery | Can source quantities or objects be reconstructed? |
| Provenance | How are generated objects related to source objects? |
| Evidence | Is the mapping proved, tested, standardized, observed in practice, or proposed? |

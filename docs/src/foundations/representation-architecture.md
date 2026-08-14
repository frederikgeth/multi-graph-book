# Representation architecture

**Page status:** proposed architecture; adequacy remains an open research question.

## Two proposed, linked structures

The working reference architecture links an asset/property model to an electrical port--factor
model. It is intended to generate useful views without requiring every view to share one graph
class. Its adequacy is a hypothesis to test, particularly for multiconductor networks,
multiwinding devices, and decision constraints.

### Asset/property model

The asset model records physical and organizational identity. Relevant object
types include equipment, spans, conductors, joints, structures, windings,
terminals, protection zones, measurements, owners, construction standards, and
locations. Edges express typed relations such as `contains`, `connected_to`,
`protected_by`, `measured_by`, `derived_from`, and `located_at`.

This model must permit two electrically equivalent objects to remain distinct.
It is the authoritative source for questions about lifecycle, maintenance,
outages, construction, geography, and provenance.

### Electrical port--factor model

Let ``\mathcal Q`` be a set of typed ports, ``\mathcal J`` a set of junctions, and
``\Phi`` a set of behavioural factors. Incidence maps connect ports to junctions
and factors. A factor ``\phi\in\Phi`` carries a relation

```math
\mathcal R_\phi(z_{\mathcal Q_\phi},u_\phi,\theta_\phi)=0,
```

possibly together with inequalities, discrete states, dynamics, or stochastic
parameters. Here ``\mathcal Q_\phi`` is the ordered set of ports belonging to the factor. These
symbols avoid conflicting with the phase, terminal, and configuration sets in the book's
[Notation and modelling conventions](@ref).

This subsumes ordinary edges: a two-port line is a factor of arity two. It also
supports:

- a multiwinding transformer as one factor with one port bundle per winding;
- a delta winding through terminal-to-terminal voltage relations;
- a multiconductor line through matrix-valued constitutive relations;
- mutual coupling among nominally separate assets through a joint factor;
- converters, protection and controls through electrical and information
  ports;
- grounding as an explicit connection or impedance factor rather than a bus
  annotation with ambiguous semantics.

Port-based network modeling is well developed in compositional circuit and
port-Hamiltonian theory [BaezFong2018, vanderSchaftMaschke2013](@cite). The
power-system-specific challenge is to connect that mathematical compositionality
to asset identity, phase semantics, operational limits, and optimization
decisions.

## Hierarchy and bi-level structure

Multiconductor networks motivate at least two scales:

1. an equipment- or bus-level topology;
2. conductor or terminal connectivity within each high-level object.

This is naturally represented by hierarchy rather than by forcing every object
into a flat graph. Hierarchical factors can be expanded when an algorithm needs
conductor variables and collapsed when an admissible summary exists. The
boundary ports of a subsystem provide its composition interface.

Hierarchy is not merely visual grouping. It establishes:

- ownership of internal variables;
- a boundary across which a behavioral equivalent may be defined;
- provenance between physical and compiled objects;
- a scope for local consistency checks and rewrite rules.

### Conductor-terminal lift on the running fixture

The generated `experiments/generated/conductor-terminal-lift-witness.json`
instantiates this hierarchy on the versioned running network. Its junctions
are bus--terminal pairs such as ``i_1/a`` and ``i_5/n``; line factors have two
ordered four-conductor ports; the ``x_1`` transformer is one factor with three
winding ports of arity four, four, and three; and ``w_0`` is a two-port factor
with an explicit ``open``/``closed``/``unknown`` state domain. Every port
retains its terminal order and maps back to a source asset.

For the closed switch, the contraction map is per conductor,
``i_0/c\mapsto i_1/c`` (and analogously for ``a,b,n``). For an open switch the
map is empty; for an unknown switch it is deliberately undefined until a
state realization is selected. This is a refinement map, not an assertion
that the bus quotient and the conductor-terminal factor graph are the same
object.

### Checked hierarchy and open-system boundaries

The companion artifact
`experiments/generated/hierarchy-boundary-witness.json` makes the remaining
composition vocabulary explicit. It declares containers for the running
network, parallel corridor, and transformer bay; typed source and target
boundary spaces; a partial refinement map from selected conductor terminals to
bus ports; and gluing records for shared subsystem interfaces. The map is
partial because a factor's internal terminals need not all be exposed at a
chosen boundary.

The witness also evaluates the switch boundary in three states. A closed
switch supplies a per-conductor contraction, an open switch supplies no
contraction, and an unknown switch leaves the boundary map undefined until a
state realization is selected. This is the minimum state-space discipline
needed before claiming that two subsystem views compose: identity, port order,
variable space, and state domain must agree at the shared boundary.

The generated checks now verify the parent chain itself (not merely the absence
of self-parenting), require every glued port to be declared in the target
boundary, and enumerate the finite ``open/closed/unknown`` state domain. This
is a checked hierarchy and gluing witness for the running fixture, not yet a
general categorical composition theorem.

### Public transformation API boundary

The executable evidence already contains reusable transformation code, but a
research notebook is not automatically a stable software interface. The first
package boundary is therefore deliberately small. The facade in
`experiments/src/GraphModelsForPowerNetworks.jl` exports only dependency-light
multigraph primitives, typed linear Kron operations, typed state-space/unit
declarations, and certificate contracts: identified edges, incidence and
cycle-space queries, simple projection, block reduction, coordinate/recovery
maps, unit conversion, boundary projections, and structural certificate
validation. Their inputs and outputs are explicit and are tested independently
of the solver-backed case studies.

The generated `experiments/generated/public-api-manifest.json` is the checked
record of this boundary. Solver-backed AC decision cases, generated figures,
benchmark witnesses, literature-specific adapters, and BMOPFTools integration
adapters remain runnable evidence, but are intentionally experimental rather
than promises of the package API. Promotion to a standalone package should
wait until the reusable state-space/unit types and their conversion contracts
are versioned; otherwise a seemingly harmless representation change could
silently change the meaning of a reduction.

Coverage is tracked separately from API existence. The generated
`experiments/generated/fixture-coverage-matrix.json` distinguishes direct
fixture evidence from related evidence and explicit ``not_yet_tested`` rows for
the running network, five-bus cycle-space example, and multiwinding transformer.
This prevents a certificate tested on a synthetic fixture from being silently
read as validation on a canonical network fixture.

The first typed layer is now explicit. A `UnitSpec` names a unit family and
scale, while a `UnitSystem` records the bases used for per-unit conversion. A
`VariableSpec` carries an identifier, role (`state`, `decision`, `parameter`, or
`constraint`), owner, domain, and unit. `BoundarySpec` names the variables
exposed at a subsystem interface and may reference a finite `StateDomain`, such
as ``\{\text{open},\text{closed},\text{unknown}\}``. A `StateSpaceSpec` bundles
these declarations and rejects duplicate or dangling identifiers at
construction time. This is intentionally a typed declaration layer, not yet a
full nonlinear state manifold or solver-variable container.

The checked
`experiments/generated/state-space-unit-witness.json` instantiates the layer
with voltage, current, power, and per-unit quantities; a discrete transformer
tap; and a three-state switch boundary. It provides the conversion and
boundary-projection contract needed by later transformation certificates. The
`typed_interfaces` attachment on each generated certificate records how its
certificate-local variable/unit/boundary labels map into this vocabulary; an
unresolved label is retained explicitly rather than silently assigned a unit.

## Required derived views

The linked source structures should generate, at minimum:

| View | Purpose | Characteristic loss |
| --- | --- | --- |
| Connectivity-node graph | switchgear and topology processing | constitutive behavior |
| Conductor-resolved factor graph | full multiphase equations | some asset semantics unless linked |
| Oriented bus--branch multigraph | conventional power-flow algorithms | terminal internals and some coupling |
| Simple topology or weighted graph | connectivity algorithms and visualization | parallel identity and constraints |
| Sparsity/incidence graph | numerical ordering and decomposition | most physical interpretation |

These are purpose-specific products, not a ladder ordered only by graph size.
Their mathematical definitions and the maps among them are collected in
[Formal representation frameworks](@ref formal-representation-frameworks).

## Evidence from current software practice

The distinction already appears in existing tools, although not as a unified
theory.

PowerModelsDistribution separates an engineering model from a mathematical
model. Its engineering representation includes arbitrary bus terminals,
explicit grounding impedances, conductor matrices, line codes, and
multiwinding transformers [PMDEngineering](@cite). Its compiler can turn lossy
grounding into shunts, lossy switches into ideal switches plus virtual branches,
and an ``N``-winding transformer into two-winding transformers and an internal
loss network [PMDConversion](@cite). The compiled graph can therefore contain
more vertices and edges while using a less expressive component vocabulary.

Substation topology processing provides a different projection. Connectivity
nodes connected by closed switches are quotiented into topological nodes. CIM
defines this quotient as state dependent [CIMTopologicalNode](@cite), and
PowSyBl exposes node/breaker, bus/breaker and bus views [PowsyblTopology](@cite).
The simpler view is useful, but cannot reconstruct the omitted switchgear if the
source model is discarded.

## Minimal object vocabulary

The architecture itself can remain small if richness is carried by types,
ports, relations and hierarchy. A plausible kernel is:

- `Entity`: stable identity and metadata;
- `Container`: hierarchy and subsystem boundary;
- `Port`: typed interface carrying variables and orientation;
- `Junction`: equality and conservation structure;
- `Factor`: constitutive, limit, control, measurement, or decision relation;
- `Transformation`: source/target provenance and certificate.

Lines, transformers, switches, loads, generators and converters need not be
kernel graph categories. They are typed factor schemas built on the kernel.
This avoids continually expanding the graph formalism whenever a new physical
device appears.

# Representation architecture

## Two canonical, linked structures

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

Let ``P`` be a set of typed ports, ``N`` a set of connectivity objects, and
``F`` a set of behavioral factors. Incidence maps connect ports to connectivity
objects and to factors. A factor ``f\in F`` carries a relation

```math
\mathcal R_f(x_{P_f},u_f,\theta_f)=0,
```

possibly together with inequalities, discrete states, dynamics, or stochastic
parameters. Here ``P_f`` is the ordered set of ports belonging to the factor.

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

## Required derived views

The canonical structures should generate, at minimum:

| View | Purpose | Characteristic loss |
| --- | --- | --- |
| Connectivity-node graph | switchgear and topology processing | constitutive behavior |
| Conductor-resolved factor graph | full multiphase equations | some asset semantics unless linked |
| Bus--branch multigraph | conventional power-flow algorithms | terminal internals and some coupling |
| Simple weighted graph | graph algorithms and visualization | parallel identity and constraints |
| Sparsity/incidence graph | numerical ordering and decomposition | most physical interpretation |

These are products, not competing canonical schemas.

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


# Book plan

## Working identity

**Working title:** *Structure-Preserving Graph Models for Power Networks*

**Form:** a scientific reference monograph with tutorial entry points and an executable
knowledge base.

**Primary audience:** power-system modellers, optimization researchers, advanced practitioners,
and software or data specialists who need to know what a network representation preserves.
Graph and formal-methods researchers are an important secondary audience; graph theory beyond the
basics is introduced as needed.

**Assumed background:** linear algebra, phasors, elementary circuit modelling, and basic power
flow. The book does not assume that the reader already knows category theory, graph rewriting,
multiconductor OPF, CIM, or a particular software package.

## Scope

The first edition concerns **electrical power networks**, with the general multiconductor case as
the baseline. A source model may have:

- arbitrary ordered terminal sets at buses;
- explicit phase, neutral, and ground semantics;
- full series and shunt coupling matrices;
- parallel assets with distinct identity and constraints;
- multi-terminal and multiwinding devices;
- switch, tap, outage, control, and investment states;
- measurements, limits, objectives, and other decision relations;
- hierarchy and provenance between physical and generated objects.

Balanced positive-sequence transmission models are important derived cases. The book will explain
the symmetry, transposition, grounding, equipment, and decision assumptions under which the
general model collapses to them. It will not take that collapse as the universal starting point.

The first edition emphasizes steady-state and quasi-steady models used in power flow, optimal
power flow, topology processing, state estimation, selected fault studies, and planning. Dynamics,
EMT, harmonics, protection logic, communications, markets, geographic graphs, and graph learning
are boundary cases unless a result directly tests the proposed framework.

## Central claim

There is no universally correct graph of a power network. A representation is adequate relative
to declared observations, constraints, and decisions. A nontrivial transformation must therefore
state a **preservation contract** that identifies:

1. its source and target model categories;
2. its structural, physical, and operating assumptions;
3. the observations, feasible sets, constraints, and decisions it preserves;
4. the distinctions and questions it forgets;
5. its source-to-target provenance;
6. recovery or lifting maps for eliminated quantities;
7. an error domain and bound when the transformation is approximate.

The linked asset/property and hierarchical port--factor models are a **proposed reference
architecture**, not an assumed universal truth. The book must test their coverage, compositionality,
and ability to generate useful study-specific views.

## Reader promise

After reading the core route, a reader should be able to:

- distinguish physical, connectivity, behavioural, mathematical, and computational graphs;
- choose a representation for a declared study instead of asking for the smallest graph in the
  abstract;
- identify when a familiar simplification is exact, conservative, relaxed, or approximate;
- carry element limits and decision variables through a transformation;
- specify recovery and provenance rather than treating eliminated objects as nonexistent;
- construct minimal counterexamples when a preservation claim is too strong;
- implement and test a transformation certificate independently of a particular solver.

## Linear book structure

The HTML knowledge base is the primary product and provides generated indexes by claim type,
verification state, chapter, artifact, and unresolved issue. The PDF is a secondary, curated
serialization with a shorter argument-shaped route; it reuses the same Markdown sources but does
not attempt to reproduce the knowledge-base indexes as a linear chapter sequence.

### Start here — one network, many graphs

1. **One network, many graphs**
   - Render the running network as an asset graph, terminal-connectivity model, multigraph,
     port--factor model, equation graph, and sparsity graph.
   - Show that these views answer different questions.
2. **Fit for purpose and preservation**
   - Identity, interconnection, behaviour, constraints, decisions, provenance, and recovery.
3. **A first failure: heterogeneous parallel branches**
   - Preserve terminal admittance while changing the OPF feasible set and available decisions.
4. **Reading paths and scope**
   - Routes for power engineers, optimization researchers, software/data practitioners, and
     graph/formal-methods readers.
5. **From source data to a canonical network model**
   - Semantic projection, validation gates, inference, unsupported fields, and provenance before
     any graph view is derived.

### Part I — Representation landscape

5. **Formal representation frameworks**
   - Simple topology quotient, oriented attributed multigraph, hierarchical
     port--factor incidence model, asset/dependency relation model, and
     equation/sparsity graphs.
6. **Maps between representation frameworks**
   - Morphisms and isomorphisms within each framework; typed quotients,
     compilers, reductions, provenance relations, and query factorization
     between frameworks.
7. **Translation traps: graphs, circuits, and power-system language**
   - Controlled replacements for ambiguous arrows, flows, conservation,
     cycles, parallelism, radiality, buses, equivalents, and matrix language.
8. **Cycles, parallelism, and radial structure**
   - Simple cycles, line-identity cycles, parallel fibres, graph degrees,
     bridges, leaves, radial tails, active-state forests, and multi-terminal
     factor incidence.
9. **Physical assets and dependency relations**
10. **Terminals, conductors, connectivity, and ground**
   - Reference, neutral, earth-return, and asset-aware grounding classes;
     scope contracts for neutral and earth reductions.
11. **Orientation, terminal signs, and operating-point power transfer**
   - Undirected physical incidence, the terminal-arc double cover, arbitrary
     reference orientation, two-end current and power observations, losses,
     nominal-``\pi`` shunts, and genuinely directed relations.
   - Rooted active-tree views, parent/child labels, source-relative distance,
     meshed chords, and switching-state recomputation.
12. **Node--breaker, bus--breaker, and oriented bus--branch models**
   - State-conditioned connectivity, switch contraction, topological nodes,
     and recovery of switching/protection identity.
13. **Simple topology quotients and weighted graphs**
14. **Multi-terminal and multiwinding devices**
15. **Port, factor, and hypergraph models**
16. **Circuit matrices, equation graphs, and sparsity graphs**
17. **Hierarchy, zones, and subsystem boundaries**
18. **Numerical consequences of representation and reduction**
   - Per-unit and coordinate scaling, conditioning, residual/backward-error
     reporting, Jacobian dependency structure, Schur-complement fill-in,
     ordering, recovery cost, and decision margins.
19. **Study-specific and algorithmic graphs**
20. **Comparing representation families**
   - Crosswalks to CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER.
21. **When the general model collapses**
    - Balanced operation, transposition, sequence decoupling, neutral elimination, identical
      terminal sets, two-terminal equipment, and transmission-style models.
22. **Load models and decision dependence**
    - Constant-power, current, impedance, ZIP, and exponential laws as constitutive relations
      that change feasible sets without changing topology.
23. **From conductor geometry to impedance fidelity**
    - Geometry, earth return, mutual matrices, conditioning, sequence coordinates, and the
      physical provenance of scalar transmission edges.

24. **Transformation semantics, closure, and anti-patterns**
    - Structure, behaviour, decisions and provenance; target-library closure;
      typed composition; and warnings for line/transformer, grounding/
      transformer and unguarded series merges.

### Part II — A common language for transformations

22. **Source, target, and observation contracts**
23. **Projection and forgetting**
24. **Compilation and realization**
25. **Normalization within a model family**
26. **Circuit coordinate transformations**
    - Phase-to-neutral and phase-to-phase maps, common-mode quotients,
      neutral recovery, grounding and shunt guards, and active-member
      radiality conditions.
27. **Exact behavioural reduction and linear Kron elimination**
28. **Ward and extended-Ward external-system equivalents**
29. **Structure-constrained and optimized reduction**
    - Opti-KRON, voltage-observation metrics, phase/connectivity guards, and
      radiality restoration.
30. **Approximate but certified reduction**
31. **Transformation certificates and recovery maps**
32. **Composition, critical pairs, and purpose-specific normal forms**

### Part III — Guarded transformation patterns

33. **Conductor coordinates, terminal maps, and orientation**
34. **Switch contraction and state-resolved topology**
35. **Series elimination and physical line concatenation**
36. **Parallel recognition, aggregation, and constraint lifting**
37. **Grounding and explicit neutrals**
38. **Multiwinding transformer compilation**
39. **Star--mesh and related circuit transformations**
40. **Constraint and decision recovery**
   - Rating and limit semantics: duration, ambient, quantity, ownership, and
     uncertainty domains.

### Part IV — Consequences for decisions

40. **Power flow and optimal power flow**
41. **Topology processing and switching**
42. **State estimation and measurement structure**
43. **Fault, grounding, and protection boundaries**
44. **Planning, contingencies, and reliability**
45. **Feeder reduction and operating envelopes**

These chapters evaluate more than state error. Their comparison criteria include feasibility,
active limits, continuous and discrete controls, objective value, optimal decisions, contingency
outcomes, and recoverability of source quantities.

### Part V — Worked cases

46. **The running multiconductor network, end to end**
47. **Heterogeneous parallel-line OPF**
48. **Four-wire grounding-aware estimation**
49. **Multiwinding transformer realization**
50. **Distribution-model cleaning**
51. **Certified feeder reduction**

### Reference

- notation and modelling conventions;
- terminology and controlled vocabulary;
- representation comparison tables;
- transformation-certificate schema;
- software and information-model crosswalks;
- literature synthesis and verified bibliography;
- open questions and research agenda.

## Chapter forms

### Representation chapter

1. Objects and relations.
2. Mathematical definition.
3. Questions it answers well.
4. Information it omits.
5. Common applications and implementations.
6. Maps to neighbouring representations.
7. The running example in this representation.
8. Failure modes and unresolved questions.

### Transformation chapter

1. Motivating decision context.
2. Source and target model categories.
3. Rule or construction.
4. Preconditions and negative application conditions.
5. Preservation contract.
6. Proof, derivation, or error definition.
7. Recovery, constraint, and provenance maps.
8. Positive example and minimal counterexample.
9. Implementation, executable tests, and literature comparison.

### Application chapter

1. Analysis or decision task.
2. Required observations, controls, and constraints.
3. Candidate representations.
4. Consequences of information loss.
5. Benchmark or worked study.
6. Recommendations and validity boundary.

### Reference entry

A compact card records definition, aliases, source and target types, preserved properties,
characteristic losses, recovery, citations, implementation status, and related entries.

## Mathematical and software policy

- The notation in the BMOPFTools model specification is the house style and the initial source for
  the notation contract.
- An oriented two-terminal attachment uses an element--bus--bus triple such as `\ell i j`.
- The orientation in `\ell i j` is a reference and terminal-order convention,
  not an assertion of physical power-transfer direction.
- Element-intrinsic symmetric data use only the element index, for example `\mathbf Z_\ell`.
- End-specific quantities retain the oriented index, for example
  `\mathbf I_{\ell ij}` or `\mathbf Y^{\mathrm{sh}}_{\ell ij}`.
- Genuinely multi-terminal devices retain a device identity and winding/port indices; they are not
  forced into artificial arcs until an explicit compilation step.
- Foundational equations use dimensional quantities. Per-unit scaling is a declared coordinate
  transformation, not implicit ontology.
- Colour may aid reading but never carries meaning that is unavailable in monochrome.
- Prose and definitions remain package-independent. BMOPFTools may provide notation, fixtures,
  executable examples, OPF experiments, and implementation case studies where suitable.
- Reproducible results record the BMOPFTools commit and complete environment.

## Running-example policy

The book uses one synthetic, engine-neutral reference network with ordered bus terminals, explicit
grounding, heterogeneous parallel branches, a genuinely multiwinding transformer, operational
limits, continuous controls, and discrete states for representation comparisons and end-to-end
case studies. Each derived view must provide a stable mapping back to source identities. Isolated
minimal or analytic cases may use smaller bespoke fixtures when that makes one guard or
counterexample independently checkable; they are not presented as additional running networks.

The specification is maintained in `docs/src/cases/running-network.md`. Numerical data and
BMOPFTools fixtures will be added only after its semantic contract is reviewed.

## Editorial and research separation

- `BOOK_PLAN.md` defines the reader-facing architecture and editorial contract.
- `ROADMAP.md` tracks the scientific and implementation programme.
- `QUALITY_CONTROL.md` defines evidence and review policy.
- `claims/claims.toml` records claim-level type, legacy status, evidence, and verification state.
- A future software roadmap will track executable transformations without controlling the order of
  the book.

## First drafting cycle

The first complete internal milestone is not the full planned book. It is a coherent vertical slice:

1. one network, many graphs;
2. notation and representation taxonomy;
3. preservation contracts and transformation taxonomy;
4. series and parallel counterexamples;
5. the running-network specification;
6. one executable decision-preservation study;
7. audited sources for every claim in that slice.

This milestone should be reviewable as a short monograph while later chapters remain planned.

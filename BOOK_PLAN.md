# Book plan

## Working identity

**Working title:** *What Power-Network Models Preserve*

**Subtitle:** *Graphs, reductions, and decision boundaries*

**Form:** a scientific reference monograph with tutorial entry points and an executable
knowledge base.

**Primary audience:** power-system modellers, optimization researchers, advanced practitioners,
and software or data specialists who need to know what a network representation preserves.
Graph and formal-methods researchers are an important secondary audience; graph theory beyond the
basics is introduced as needed.

**Assumed background:** linear algebra, phasors, elementary circuit modelling, and basic power
flow. The book does not assume that the reader already knows category theory, graph rewriting,
multiconductor OPF, CIM, or a particular software package.

**Editorial status labels:** `[core argument]` chapters carry the problem-first thesis; `[reference
card]` chapters provide definitions, crosswalks, or compact lookup material; `[worked case]`
chapters demonstrate the thesis on a declared fixture; `[research record]` chapters report
literature, implementation, or open-work status; `[future application]` chapters are planned
inventory, not completed evidence in the current release candidate.

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

The current release candidate is not a completed general transformation calculus and does not
claim complete coverage of state estimation, protection, planning, contingency analysis, or
feeder reduction. Those application areas remain explicit future boundaries unless a chapter's
claims ledger and executable evidence say otherwise.

## The problem before the tools

Power-network workflows routinely move between physical assets, terminal connections, circuit
factors, nodal matrices, optimization models, and visual or data views. Each move can be useful,
but it can also forget distinctions that matter to the study: conductor identity, grounding,
limits, controls, switching states, measurements, decisions, or provenance. A smaller graph may
therefore preserve one equation while changing the feasible set or the decision problem.

The book is organized to establish this problem first. Its typed architecture, transformations,
and certificates are responses to the problem, not the premise that a single preferred graph can
represent every purpose.

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

The long-form monograph is the argument-shaped product and follows:

**problem and counterexample → representation obligations → canonical model → valid collapses and
failure modes → preservation contracts → transformations and recovery → cases and consequences.**

The HTML knowledge base is the exhaustive retrieval product and provides generated indexes by claim type,
verification state, chapter, artifact, and unresolved issue. The PDF is a secondary, curated
serialization of the same Markdown sources. It follows the argument sequence without shortening the
underlying chapter content and does not attempt to reproduce the knowledge-base indexes as a linear
chapter sequence.

### Start here — one network, many graphs

1. **[core argument] One network, many graphs**
   - Render the running network as an asset graph, terminal-connectivity model, multigraph,
     port--factor model, equation graph, and sparsity graph.
   - Show that these views answer different questions.
2. **[core argument] Fit for purpose and preservation**
   - Identity, interconnection, behaviour, constraints, decisions, provenance, and recovery.
3. **[worked case] A first failure: heterogeneous parallel branches**
   - Preserve terminal admittance while changing the OPF feasible set and available decisions.
4. **[core argument] Reading paths and scope**
   - Routes for power engineers, optimization researchers, software/data practitioners, and
     graph/formal-methods readers.
5. **[core argument] From source data to a canonical network model**
   - Semantic projection, validation gates, inference, unsupported fields, and provenance before
     any graph view is derived.

### Part I — Representation landscape

6. **[core argument] Formal representation frameworks**
   - Simple topology quotient, oriented attributed multigraph, hierarchical
     port--factor incidence model, asset/dependency relation model, and
     equation/sparsity graphs.
7. **[reference card] Maps between representation frameworks**
   - Morphisms and isomorphisms within each framework; typed quotients,
     compilers, reductions, provenance relations, and query factorization
     between frameworks.
8. **[core argument] Translation traps: graphs, circuits, and power-system language**
   - Controlled replacements for ambiguous arrows, flows, conservation,
     cycles, parallelism, radiality, buses, equivalents, and matrix language.
9. **[core argument] Two topology levels and the nodal projection**
   - Identified asset/terminal topology, conductor/port--factor topology, and
     block/scalar nodal-operator support.
   - Parallelism and cycles at each level; factor-stamp assembly,
     non-identifiability, source retention, and radial macro-topology with
     cyclic conductor-expanded support.
10. **[core argument] Cycles, parallelism, and radial structure**
   - Simple cycles, line-identity cycles, parallel fibres, graph degrees,
     bridges, leaves, radial tails, active-state forests, and multi-terminal
     factor incidence.
11. **[reference card] Physical assets and dependency relations**
12. **[reference card] Terminals, conductors, connectivity, and ground**
   - Reference, neutral, earth-return, and asset-aware grounding classes;
     scope contracts for neutral and earth reductions.
13. **[core argument] Orientation, terminal signs, and operating-point power transfer**
   - Undirected physical incidence, the terminal-arc double cover, arbitrary
     reference orientation, two-end current and power observations, losses,
     nominal-``\pi`` shunts, and genuinely directed relations.
   - Rooted active-tree views, parent/child labels, source-relative distance,
     meshed chords, and switching-state recomputation.
14. **[reference card] Node--breaker, bus--breaker, and oriented bus--branch models**
   - State-conditioned connectivity, switch contraction, topological nodes,
     and recovery of switching/protection identity.
15. **[reference card] Simple topology quotients and weighted graphs**
16. **[reference card] Multi-terminal and multiwinding devices**
17. **[reference card] Port, factor, and hypergraph models**
18. **[reference card] Circuit matrices, equation graphs, and sparsity graphs**
19. **[reference card] Hierarchy, zones, and subsystem boundaries**
20. **[core argument] Numerical consequences of representation and reduction**
   - Per-unit and coordinate scaling, conditioning, residual/backward-error
     reporting, Jacobian dependency structure, Schur-complement fill-in,
     ordering, recovery cost, and decision margins.
21. **[reference card] Study-specific and algorithmic graphs**
22. **[research record] Comparing representation families**
   - Literature-facing landscape of graph, circuit, equation, and information
     models; selected source, derived view, equivalent alternative, scope
     collapse, and orthogonal companion; crosswalks to CIM/CGMES,
     PowerModelsDistribution, OpenDSS, and MATPOWER.
   - Canonicality is argued as a scoped design choice, not universal uniqueness.
23. **[core argument] Circuit formulations and the lowering boundary**
   - Nodal admittance, modified/sparse tableau, branch-current, hybrid,
     port/factor, and constraint formulations.
   - Nodal admittance as a powerful representation for an important class of
     reduced linear networks, but not a universal representation of general
     *power networks* when identity, switching, controls, limits, grounding,
     multi-terminal behaviour, or decisions matter.
   - Exact nodal-stamping conditions, singular or unavailable ``Y`` cases,
     direct factor stamping, and provenance-aware compiler targets.
24. **[core argument] When the general model collapses**
    - Balanced operation, transposition, sequence decoupling, neutral elimination, identical
      terminal sets, two-terminal equipment, and transmission-style models.
25. **[core argument] Load models and decision dependence**
    - Constant-power, current, impedance, ZIP, and exponential laws as constitutive relations
      that change feasible sets without changing topology.
26. **[reference card] From conductor geometry to impedance fidelity**
    - Geometry, earth return, mutual matrices, conditioning, sequence coordinates, and the
      physical provenance of scalar transmission edges.

27. **[core argument] Transformation semantics, closure, and anti-patterns**
    - Structure, behaviour, decisions and provenance; target-library closure;
      typed composition; and warnings for line/transformer, grounding/
      transformer and unguarded series merges.

### Part II — A common language for transformations

28. **[core argument] Source, target, and observation contracts**
29. **[core argument] Projection and forgetting**
30. **[core argument] Compilation and realization**
31. **[core argument] Normalization within a model family**
32. **[core argument] Circuit coordinate transformations**
    - Phase-to-neutral and phase-to-phase maps, common-mode quotients,
      neutral recovery, grounding and shunt guards, and active-member
      radiality conditions.
33. **[core argument] Exact behavioural reduction and linear Kron elimination**
34. **[core argument] Ward and extended-Ward external-system equivalents**
35. **[core argument] Structure-constrained and optimized reduction**
    - Opti-KRON, voltage-observation metrics, phase/connectivity guards, and
      radiality restoration.
36. **[core argument] Approximate but certified reduction**
37. **[core argument] Transformation certificates and recovery maps**
38. **[core argument] Composition, critical pairs, and purpose-specific normal forms**

### Part III — Guarded transformation patterns

39. **[core argument] Conductor coordinates, terminal maps, and orientation**
40. **[core argument] Switch contraction and state-resolved topology**
41. **[core argument] Series elimination and physical line concatenation**
42. **[core argument] Parallel recognition, aggregation, and constraint lifting**
43. **[core argument] Grounding and explicit neutrals**
44. **[core argument] Multiwinding transformer compilation**
45. **[reference card] Star--mesh and related circuit transformations**
46. **[core argument] Constraint and decision recovery**
   - Rating and limit semantics: duration, ambient, quantity, ownership, and
     uncertainty domains.

### Part IV — Consequences for decisions

47. **[future application] Power flow and optimal power flow**
48. **[future application] Topology processing and switching**
49. **[future application] State estimation and measurement structure**
50. **[future application] Fault, grounding, and protection boundaries**
51. **[future application] Planning, contingencies, and reliability**
52. **[future application] Feeder reduction and operating envelopes**

These chapters evaluate more than state error. Their comparison criteria include feasibility,
active limits, continuous and discrete controls, objective value, optimal decisions, contingency
outcomes, and recoverability of source quantities.

In the current release candidate, Part IV is a future-application inventory rather than a claim
that all of these study families are complete. The repository contains scoped power-flow, OPF,
topology, grounding, transformer-control, and reduction witnesses, but it does not yet establish
general state-estimation, protection, planning, contingency, or feeder-reduction results. New
chapters in these areas should enter as research records or bounded worked cases until their
source model, evidence, recovery, and review status are explicit.

### Part V — Worked cases

53. **[worked case] The running multiconductor network, end to end**
54. **[worked case] Heterogeneous parallel-line OPF**
55. **[worked case] Coupled multi-voltage corridor and equivalent lattice**
56. **[future application] Four-wire grounding-aware estimation**
57. **[worked case] Multiwinding transformer realization**
58. **[future application] Distribution-model cleaning**
59. **[future application] Certified feeder reduction**

### Reference

- **[reference card]** notation and modelling conventions;
- **[reference card]** terminology and controlled vocabulary;
- **[reference card]** representation comparison tables;
- **[reference card]** transformation-certificate schema;
- **[reference card]** software and information-model crosswalks;
- **[research record]** literature synthesis and verified bibliography;
- **[research record]** open questions and research agenda.

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

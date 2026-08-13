# Work plan and roadmap

This file tracks the scientific and implementation programme. The reader-facing argument, target
table of contents, chapter forms, and first drafting milestone are maintained separately in
[`BOOK_PLAN.md`](BOOK_PLAN.md).

## Guiding outcome

Produce a citable, open scientific book and executable knowledge base that
explains power-network graph model categories and provides verified,
provenance-aware transformations among them.

The roadmap separates **publication infrastructure**, **knowledge synthesis**,
**formal results**, and **software/experiments** so that progress in one does
not masquerade as completion of the others.

## Phase 0 — Repository and editorial foundation

**Target:** first two weeks.

- Choose the final title, repository name, license and citation metadata.
- Establish Documenter HTML and PDF builds in CI.
- Add issue templates for claim verification, new transformations and source
  reviews.
- Implement the claims ledger and bibliography-verification table.
- Define style rules for equations, diagrams, terminology and epistemic labels.
- Freeze a versioned glossary for the first drafting cycle.

**Exit criterion:** clean local/CI builds; every existing scientific claim is
either cited, labeled as a proposal, or entered as unresolved.

## Phase 1 — Systematic scoping review

**Target:** months 1--2.

Run reproducible searches across:

- circuit/network theory and inverse electrical networks;
- Kron, Ward, REI and dynamic equivalents;
- distribution feeder reduction and aggregation;
- topology processing, CIM/CGMES and utility model management;
- graph rewriting and model-driven engineering;
- port-Hamiltonian, bond-graph and compositional systems;
- network sparsification and Schur-complement approximations;
- optimization-preserving and constraint-aware reduction;
- protection-, grounding- and asset-aware simplification.

Code each source by source/target model, physical detail, exactness,
observations, retained constraints, phase/neutral treatment, provenance, and
implementation availability.

**Exit criterion:** publishable literature matrix, explicit search protocol,
and a gap analysis stronger than the current provisional assessment.

## Phase 2 — Foundations and taxonomy

**Target:** months 2--4.

- Define asset graph and hierarchical port--factor semantics.
- Separate undirected physical incidence, reference orientation, terminal-arc
  signs, operating-point power transfer, and genuinely directed relations.
- Define simple topology, oriented multigraph, port--factor, asset/dependency,
  and equation/sparsity frameworks as distinct mathematical objects.
- Define relative expressiveness by query families.
- Formalize projection, compilation, normalization, exact behavioral reduction
  and approximation.
- Define preservation certificates and transformation composition.
- Map CIM, PowerModelsDistribution, OpenDSS and other representative tools into
  the framework.

**Exit criterion:** internally consistent Part I draft reviewed by experts from
at least graph/formal methods and power-system modeling.

## Current foundation refactor

The next reader-facing milestone is a rigorous separation of representation
frameworks and network-equivalent families.

### Stage A — first formal definitions

- [x] define the simple topology quotient and its lost parallel-cycle rank;
- [x] define the oriented attributed multigraph and incidence convention;
- [x] define a first hierarchical port--factor incidence object and external
  behaviour;
- [x] define the typed asset/dependency relation model and its nonfunctional
  link to electrical objects;
- [x] distinguish topology graphs from equation and matrix-sparsity graphs;
- [x] separate physical incidence, reference orientation, terminal signs,
  operating-point transfer, and causal direction;
- [x] state series and nominal-``\pi`` two-end current and power balances.

### Stage B — network equivalents

- [x] state linear and affine Kron elimination with recovery;
- [x] separate the Ward realization question from the Schur complement;
- [x] classify Opti-KRON as optimized structural selection plus a Kron-based
  relation and scenario observation metric;
- [x] audit primary sources for conventional, extended, and operating-point
  Ward formulations;
- [x] prove a typed multiconductor Kron result with terminal maps;
- [ ] characterize realizability of reduced multiports in selected line,
  shunt, transformer, and general-factor libraries;
  - an initial exact full-matrix reciprocal line--shunt construction and its
    passivity boundary are now stated; restricted line and transformer
    libraries still require executable tests;
- [ ] build an executable Kron--Ward--scenario comparison with voltage,
  internal-current, constraint, and decision observations.

### Stage C — stronger mathematical structure

- [x] define first morphisms, isomorphisms, and coordinate actions for every
  representation framework;
- [ ] formalize hierarchy, open-system composition, and boundary gluing;
- [ ] replace prose state-space and unit interfaces with checked objects;
- [ ] test every map on the running multiconductor network, its five-bus
  line-identity example, and the multiwinding transformer;
- [ ] obtain independent review from both graph/formal-methods and
  power-system-modeling perspectives.

### Stage D — graph invariants with representation scope

- [x] define simple cycles and line-identity cycles through simple cycles and
  incidence-nullspace circuits;
- [x] define topological, terminal, electrical, operational, and homogeneous
  parallelism as distinct predicates;
- [x] distinguish simple and multigraph degree, leaves, pendant lines, bridges,
  radial tails, and pendant subnetworks;
- [x] state bridge and forest characterizations for simple projections and
  identified parallel fibres;
- [x] distinguish adjacency-radial from member-radial active states;
- [x] explain why multi-terminal factor incidence and clique/star compilation
  can create different apparent cycles;
- [ ] lift these invariants to conductor-terminal incidence and
  state-conditioned topology decisions;
- [ ] lift the active-state radiality witness to the running network and its
  switch/outage variants.

### Stage E — translation traps and controlled shorthand

- [x] add an early synthesis chapter separating graph-theory, circuit-theory,
  power-system-practice, and decision-model statements;
- [x] define the four recurring callouts: graph-theory trap, circuit-theory
  trap, power-system shorthand, and decision-model consequence;
- [x] prioritize arrows versus operating flow, terminal power pairs, KCL,
  cycles versus loop flow, parallelism, radiality, bus meanings, and
  decision-relative equivalence;
- [x] seed callouts in the formal-framework, orientation, cycle, preservation,
  Kron/Ward, and series-elimination chapters;
- [x] complete the first terminology audit of the foundations, starting
  chapters, and transformation chapters; the remaining pass is a style and
  consistency sweep rather than an unscoped search-and-replace;
- [x] add minimal executable witnesses for connectivity versus energization,
  complex symmetry versus Hermitian structure, and terminal-specific ratings;
- [x] add an active-state radiality witness that reports simple-projection and
  identified-member forests separately;
- [x] add a circuit-coordinate transformation chapter synthesizing the
  phase-to-neutral and phase-to-phase reductions and their exactness guards;
- [ ] make the controlled callout vocabulary machine-checkable without
  requiring every chapter to contain a callout.

## Phase 3 — Verified local transformations

**Target:** months 4--8.

Develop complete chapters and executable tests for:

1. conductor-coordinate normalization;
2. ideal-switch contraction and state-resolved topology;
3. degree-two series elimination;
4. homogeneous physical line merging;
5. parallel-bundle representation and constraint recovery;
6. grounding extraction;
7. multiwinding transformer compilation;
8. selected `Y`--`Δ` and star-mesh relations with explicit scope.

**Exit criterion:** each rule has guards, proof/derivation, provenance model,
positive and negative examples, and source-feasibility recovery tests.

## Phase 4 — Decision-preserving case studies

**Target:** months 7--12.

Prioritize:

- heterogeneous parallel-line OPF;
- four-wire grounding-aware state estimation;
- topology cleaning of real distribution models;
- multiwinding transformer realization;
- feeder reduction for hosting capacity or dynamic operating envelopes.

Compare transformations by both state error and decision error: feasibility,
active limits, discrete choices, objective value, and contingency outcomes.

**Exit criterion:** open benchmark cases and at least one journal-quality study
showing a consequential failure of conventional reduction plus a certified
alternative.

## Phase 5 — General theory and formalization

**Target:** year 2.

- Establish closure and non-closure results for important device classes.
- Study rewrite termination and critical pairs.
- Formalize linear core results and selected rewrite proofs in Lean.
- Develop exact, inner, outer and scenario-approximate constraint projection
  theory.
- Connect compositional black-box semantics to nonlinear and discrete
  power-system factors.

**Exit criterion:** one or more theorem-led papers and mechanically checked core
results.

## Phase 6 — Reference implementation and community release

**Target:** year 2 onward.

- Release a Julia transformation library independent of a specific optimizer.
- Provide CIM/CGMES, OpenDSS and PowerModelsDistribution adapters.
- Integrate generated model views with PowerOptLab/BMOPFTools experiments where
  appropriate, without defining the research agenda around those packages.
- Establish a versioned transformation registry and community review process.
- Publish tagged book editions with archived source, PDF and bibliography.

## Immediate next sprint

The first executable vertical slice is complete:

1. every seed BibTeX record has a dated audit entry, with final publications
   substituted where found;
2. the systematic scoping-review protocol, search strings, and evidence-matrix
   schema are versioned;
3. fixture version 0.1.0 has been reproduced at a clean pinned BMOPFTools
   commit without changing the user's development checkout;
4. all six illustrated views have complete, hash-bound source maps; a later
   foundation pass added the seventh simple-topology quotient map;
5. the degree-two rewrite returns a certified exact behavioural composite or a
   structured guard rejection, with positive and adversarial tests;
6. CI checks claims, bibliography coverage, local links, generated artifacts,
   source maps, and the package-independent series rule.
7. conductor-coordinate normalization is an independently certified exact
   rule and composes explicitly with series elimination;
8. the two-bus parallel decision case compares source, naïve aggregate, and
   exact lifted formulations, with respective optima 110, 200, and 110 MW;
9. all transformation artifacts use the version 1.1.0 JSON certificate schema,
   including six typed interfaces, and repository checks validate structure
   and claim registration.
10. the coordinate action now applies to typed grounded-wye and delta winding
    factors while preserving stable coil coordinates and limits;
11. a coupled two-conductor AC decision case gives source, naïve, and exact
    lifted optima of 0.6138908, 1.0630833, and 0.6138908 p.u., with an
    independent closed-form check.
12. complete pairwise multiwinding short-circuit data compile into a full
    reference impedance matrix with an exact recovery map; the three-winding
    star/T form is treated as a special case and a non-diagonal four-winding
    round trip is tested.
13. the multiwinding compiler accepts any declared winding reference, rebases
    source short-circuit data explicitly, and verifies that all reference
    choices give the same external winding admittance.
14. labelled winding connection factors compose with the leakage relation into
    an exact 11-terminal factor for the running WYE/WYE/DELTA transformer,
    retaining a lifted coil-current map and the original winding limits.
15. a versioned transformer-completion contract now composes fixed power-dual
    voltage transfers, a labelled excitation shunt, and transformer-internal
    grounding with that leakage factor; adjustable transfers are rejected by
    the static compiler and retain their decision identities for a later
    parameterized target.
16. positive scalar winding taps now compile into exact parameterized
   continuous or discrete decision factors. A discrete witness retains the
   same feasible positions and 1.05 optimum as direct source evaluation,
   while freezing the 1.00 start value worsens the current-stress objective by
   671.060 A.
17. the retained discrete tap factor is now embedded in a solver-backed,
   full 11-terminal WYE/WYE/DELTA AC network case. Direct source and
   parameterized target formulations agree at all positions and select 0.95
   with served fraction 1.2305865; freezing 1.00 loses 0.090169 MW.
18. a separate LinearAlgebra-only damped Newton, continuation, and bisection
   engine reproduces all three tap-conditioned high-voltage branch boundaries
   to within 3.14e-10 served fraction of JuMP/Ipopt and selects the same tap;
   truncated and infeasible searches return structured rejections.
19. Molzahn's scalar AC parallel-line redundancy certificate is now separated
   explicitly from asset aggregation. The proportional multiconductor case
   includes an exact-pruned formulation that removes only the implied
   member-2 current limits and retains the source optimum of 0.6138908.
20. a package-independent multiconductor checker now realifies fixed complex
   terminal-current maps and certifies pairwise limit implication by a PSD
   difference test. It checks every aligned conductor at both ends and has
   non-proportional positive, reverse-implication, singular, and one-end-only
   negative tests.
21. a reciprocal non-proportional three-phase four-wire AC case now certifies
   candidate limits jointly from all component discs of a nonsingular retained
   member. Source and exact-pruned objectives agree at 1.1274329, while a
   same-size summed-limit target reaches 1.8058181 by violating a member limit;
   an independent Newton continuation reproduces the boundary and BMOPFTools
   cross-checks both line primitives.
22. the joint-disc kernel now accepts any invertible fixed terminal-current
   map. A non-proportional four-wire nominal-pi case stacks all ij/ji currents,
   includes distinct end shunts, prunes eight certified limits, and preserves
   the 1.1286205 source objective; independent continuation and BMOPFTools
   primitive reconstruction cross-check the result.
23. a corrected five-bus worked example now separates line-identity cycle
   space, simple-graph projection, electrical aggregation, guarded reduction,
   and spanning-tree coordinates. The seven-line source multigraph has cycle
   rank three, its simple projection has rank two, and the executable
   line-indexed basis agrees with BMOPFTools' parallel-aware extra-edge count.
   Three generated small-multiple figures expose the lost parallel cycle,
   typed transformation semantics, and equal-`Ybus`/unequal-feasible-set
   counterexample; a hash manifest binds them to the analysis artifact.
24. the five principal representation frameworks now have explicit
    within-framework morphisms and isomorphisms, while quotients, compilers,
    sparsity extraction, behavioural reduction, and the asset/electrical link
    remain separately typed cross-framework maps. Query factorization gives a
    precise, purpose-relative expressiveness test;
25. the running-network provenance artifact includes a checked simple-topology
    quotient: the `i1--i2` adjacency maps to both `l1` and `l2`, while the
    three-winding transformer is explicitly outside the quotient until a
    compilation is selected;
26. Ward's original constant-current boundary construction, the 1979
    operating-state extended Ward method, and the Ward--PV construction now
    have audited primary sources and distinct model contracts;
27. typed multiconductor Kron reduction is proved coordinate covariant under
    power-dual terminal actions. A first realizability proposition separates
    an exact general multiport from direct reciprocal line--shunt realization,
    passivity, and recovery of original constraints.
28. cycles, parallelism, bridges, leaves, and radiality now have
    representation-scoped definitions. The chapter distinguishes simple cycle
    rank from line-identity cycle rank, records the levels of parallelism, and
    proves the bridge and forest conditions for simple projections with
    parallel fibres.
29. an early translation-traps chapter now distinguishes mathematical errors
    from context-dependent engineering shorthand. Controlled callouts connect
    the ten highest-priority misconceptions to their rigorous foundation and
    decision consequences.

The next sprint should:

1. implement a typed multiconductor Kron fixture that tests coordinate
   covariance, internal-state recovery, original limits, and direct
   line--shunt realizability;
2. define hierarchy, open-system boundary gluing, and refinement maps, then
   test them on the running network's grounding, switch, and transformer;
3. compare exact Kron, an operating-point Ward equivalent, and an
   Opti-KRON-style scenario approximation on common voltage, current,
   constraint, and decision observations;
4. execute and archive the first database searches, then populate the evidence
   matrix with double-coded seed results;
5. obtain independent reviews of the parallel, coordinate, series, and winding
   transformation claims, prioritizing `TR-PAR-004` and `TR-XFMR-001`;
6. extend the retained transformer-control domain to phase-angle,
   independent-phase, mechanically coupled, automatic, and tap-dependent-loss
   controls, and reproduce a case with an independently assembled primitive;
7. extend the completed nominal-pi case to singular shunted maps, limits
   implied by several retained members, and state-conditioned topology and
   controls; add a global bound where required;
8. replace prose interface entries with checked state-space and unit objects,
   then strengthen composition beyond its current identity meeting check;
9. add scheduled external-link checking without making ordinary builds depend
   on publisher availability.
10. lift the five-bus incidence and cycle-space objects to conductor-terminal
   connectivity, compiled multi-terminal factors, and state-conditioned
   radial-topology decisions.
11. lift the active-state radiality certificate to the running network and
    its switch/outage variants, reporting both adjacency-radial and
    member-radial status.
12. audit the remaining draft for the controlled shorthand vocabulary and add
    executable counterexamples for connectivity versus energization, matrix
    symmetry, and terminal-rating semantics.
13. add typed four-wire phase-to-neutral and three-wire phase-to-phase
    certificates, with explicit shunt, grounding, mesh, and recovery guards.

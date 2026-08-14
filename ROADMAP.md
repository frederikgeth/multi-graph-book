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

## Current status and active plan (2026-08-15)

The review-response foundation pass is implemented and retained as an internal
archival record. The HTML-first knowledge base, curated PDF route, claims
ledger, generated indexes, running fixture, graph-invariant witnesses,
multiconductor parallel cases, transformer compilers, positive-sequence
collapse witness, certified-approximation chain, and argument-diagram
portfolio are implemented and locally validated. The remaining work is
optional external validation and broader research scope, not a prerequisite
for using the knowledge base.
The historical dispositions are archived in
[`review/archive/`](review/archive/).

The checklists below preserve the scientific record of that pass. They are not
the active task queue. The active queue is the four milestones at the end of
this file, ordered by dependency:

1. integrity and reproducibility release;
2. certified reduction and approximation evidence;
3. graph architecture, route structure, and argument diagrams;
4. external validation and dissemination.

The first two milestones are the publication gate for stronger decision-case
claims. General formalization, broad adapters, and paper extraction remain
deliberate follow-on work rather than prerequisites for the knowledge base.

**Latest verification (2026-08-14):** the aggregate experiment suite passes
through the standalone `GraphModelsForPowerNetworks` package boundary using the
isolated-plus-user Julia depot configuration. The evidence-matrix, artifact,
claim-mention, controlled-callout, figure, and whitespace audits also pass.
The remaining release gates are substantive rather than local-test failures:
independent review of the four highest-risk theorem claims, evidence-matrix
double-coding, the scoped global nonlinear-bound extensions, and external
package/API publication.

The BMOPFTools documentation review has added a focused editorial tranche:
source-to-canonical semantic projection and validation gates, constitutive load
models as decision semantics, and the physical geometry-to-impedance fidelity
ladder. These are adapted to the book's graph-and-preservation story rather
than copied as package tutorials.

- [x] add the source-to-canonical semantic-projection and validation-gate
  chapter;
- [x] add the load-model decision-dependence chapter;
- [x] add the conductor-geometry-to-impedance fidelity ladder;
- [x] extend the grounding taxonomy with a study-specific comparative case;
- [x] add executable numerical witnesses for the load-model and grounding
  comparisons before treating them as empirical claims.

The next editorial tranche is now explicit:

- [x] define the four preservation layers (structure, behaviour, decision,
  provenance) and a first reader-facing transformation register;
- [x] add anti-patterns for heterogeneous series merges, line--transformer
  flattening, and absorption of external grounding;
- [x] add a BIM/BFM parallel-line expressiveness case using ``\ell i j``
  branch identity and total-terminal-current semantics;
- [x] define rooted active-tree views separately from stored orientation,
  operating transfer direction, and meshed graph structure;
- [x] add executable negative witnesses for the anti-patterns and formulation
  changes, then bind them to the certificate/evidence matrix.

The impedance-standardisation tranche is now added as a bridge from the book's
taxonomy to implementable data and transformation workflows:

- [x] define a canonical impedance-data contract that retains geometry or
  linecode provenance, ordered ``\ell i j`` terminals, series/shunt blocks,
  units, grounding assumptions, limits, and derived-view lineage;
- [x] represent the four-wire impedance ladder as a risk-aware transformation
  path, separating guarded neutral/phase reductions and exact coordinate maps
  from shunt deletion, sequence decoupling, balancing, and positive-sequence
  approximations;
- [x] add a deterministic package-independent four-wire ladder fixture with
  neutral-current and phase-to-neutral recovery checks, visible sequence
  mixing, and explicit per-edge risk tags;
- [x] promote the reader-facing impedance contract to a versioned interchange
  schema with machine-readable finding codes and source/derived/inferred field
  status, limits, and grounding assumptions;
- [ ] reproduce the authored overhead-line and underground-cable cases with
  balanced/unbalanced load rows, grounding variants, voltage/loss observations,
  and geometry or linecode provenance;
- [x] cross-check the authored cases against OpenDSS, BMOPFTools, and a
  separately assembled LinearAlgebra reference solve, with explicit line-loss
  versus grounding-reactor-loss accounting;
- [x] add path-level composition checks that carry the weakest preservation
  status and the union of unresolved guards through a sequence of maps.

The available Australian source data is now audited and reproduced as a
bounded case study:

- [x] lift the Pluto overhead and UGHV 185 Al PILC construction fields from
  the `ImpedanceModels.jl` line-library history into a project-local input
  record;
- [x] regenerate Carson series/capacitance primitives with BMOPFTools and
  solve the resulting four-wire cases through OpenDSSDirect with
  `vminpu=0`, `vmaxpu=2`;
- [x] compare the regenerated matrices against the Australian overhead and
  CS1035 files without using those matrices as model inputs, and record solve
  diagnostics and provenance in a generated artifact;
- [x] separate the Australian overhead mismatch into frequency and conductor
  ordering: a 60 Hz probe with source order `[4,1,2,3]` reproduces the stored
  matrix to approximately `4.3e-5 Ohm/km`;
- [x] add a machine-readable source-audit register that distinguishes lifted
  construction, derived reference, inferred alignment, and unresolved mapping
  status (including the OpenDSS underground-height caveat);
- [x] bind the generated neutral conductor to the explicit grounding terminal
  and decompose OpenDSS line losses from separately modelled grounding losses;
- [x] add low- and high-grounding-impedance rows with independent voltage and
  line-loss cross-checks;
- [ ] recover an explicit source declaration for the overhead reference
  frequency/order, and the raw cable construction mapping for CS1035;
- [ ] only claim a faithful reproduction of those reference cases after the
  preceding provenance mappings are available.

The two-level topology and nodal-projection tranche is now part of the active
graph-architecture work:

- [x] distinguish identified asset/terminal topology, conductor/port--factor
  topology, and block/scalar nodal-operator support;
- [x] define the factor-stamping map and explain why a nodal operator is not a
  unique factorization or an asset multigraph;
- [x] separate asset, conductor-incidence, and matrix-support cycles, including
  the radial-macro/clique-support example from the multiphase OPF literature;
- [x] add audited diagrams for the two-level projection and the radial-to-
  cyclic-support apparent paradox;
- [x] state a source-retention and assembly round-trip contract, including the
  non-injective conductor-to-terminal case outside narrower adapters;
- [x] add a generated factor-stamp witness that computes block/scalar support,
  parallel-stamp aggregation, and decomposition provenance on the running
  multiconductor fixture;
- [x] investigate source recovery as a separately scoped inverse problem with
  explicit identifiable, set-identifiable, and non-identifiable classes; add
  a recovery contract and finite executable witnesses without presenting
  ``\mathbf Y^{\mathrm N}`` inversion as a canonical import path;
- [x] add a guarded-observation tranche showing bounded catalog ambiguity,
  member-current lifting, grounding declarations, and state-conditioned
  transformer recovery;
- [x] add the scoped multiconductor observation-rank witness: full-rank
  voltage excitation with complete currents, single-snapshot ambiguity, and
  phase-selective partial-observation ambiguity;
- [x] add a deterministic noisy-multiconductor recovery bound and a
  conditioning witness contrasting well-conditioned and nearly dependent
  voltage snapshots;
- [x] add a local nonlinear-grounding derivative certificate comparing the
  frozen nominal bond coefficient with the recomputed real Jacobian;
- [ ] extend the guarded classification to noisy partial observations,
  global nonlinear grounding, full transformer controls, and experimental
  design, with independent evidence before treating those extensions as
  general results.

The 2026-08-15 technical review of that tranche adds the following ordered
repair plan. Two reviewer formulations are deliberately qualified: passivity
alone gives a convex, not necessarily bounded, parallel-split ambiguity set;
and nodal-operator singularity is conditional on connectivity, grounding,
shunts, and component hypotheses rather than universal.

- [x] state and illustrate the positive chordal counterpart to conductor
  expansion: under dense two-terminal ``m``-conductor stamps on a bus-level
  tree, leaf-block elimination is a perfect elimination order with zero fill;
- [x] define injectivity of the restricted assembly map by its kernel on the
  admissible model class, then give a support-separated two-terminal
  sufficient condition and the three principal failure mechanisms;
- [x] characterize the aligned parallel-factor ambiguity as an affine family,
  intersect it with passivity and parameter guards without claiming
  boundedness absent coercive bounds, and cite recoverable-network theory;
- [x] state the conditional rank/nullspace alternatives for an unreferenced
  versus sufficiently grounded compound nodal operator;
- [x] say explicitly that the nodal operator assembles only the declared
  linear unconstrained factor subset and therefore omits loads, controls,
  limits, objectives, and discrete decision semantics;
- [x] replace the absolute assembly residual with a named normwise backward
  error and distinguish consistency from source attribution;
- [x] separate the always-many-to-one port attachment ``j`` from a possibly
  non-injective physical-conductor realization map ``c`` and move the
  BMOPFTools restriction into an implementation note;
- [x] make ``\mathbf Y^{\mathrm N}`` the typed compound-nodal notation, retain
  ``\mathbf Y_{\mathrm{bus}}``/`Ybus` as a declared conventional alias, and
  explain why the transpose is correct only for real assembly maps;
- [x] register the chapter's claim-shaped results and add executable witnesses
  for parallel-split non-identifiability/certificate blindness and the
  radial-clique perfect elimination order;
- [x] make this chapter the single source of the block/scalar support-graph
  definitions and reduce neighbouring chapters to linked summaries.

## Phase 0 — Repository and editorial foundation

**Target:** first two weeks.

**Status:** local infrastructure, claims, generated indexes, HTML, and PDF
are in place; CI/release verification remains in M1.

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

**Status:** protocol, search strings, audit schema, and seed bibliography are
versioned; executing and double-coding the searches remains in M4.

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

**Status:** the core representation and translation foundations are drafted;
independent review, checked composition, and broader topology witnesses remain
in M1--M3.

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

## Review-response foundation pass

This completed pass established a rigorous separation of representation
frameworks and network-equivalent families. Its unchecked boxes record open
scientific boundaries, not a replacement task queue; use the active milestones
below for prioritization.

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
- [x] characterize realizability of reduced multiports in selected line,
  shunt, transformer, and general-factor libraries;
  - an initial exact full-matrix reciprocal line--shunt construction and its
    passivity boundary are now stated; the typed witness also includes
    positive and negative closure tests for a conductor-diagonal transformer
    library. These are structural library tests, not parameter-identification
    or physical-realization guarantees;
- [x] build an executable Kron--Ward--scenario comparison with voltage,
  internal-current, constraint, and decision observations; the generated
  witness now carries a shared observation contract and an explicit selected
  candidate ledger.

### Stage C — stronger mathematical structure

- [x] define first morphisms, isomorphisms, and coordinate actions for every
  representation framework;
- [x] formalize a finite hierarchy, open-system composition, and boundary
  gluing witness; parent-chain acyclicity, declared shared ports, and the
  finite switch state domain are now checked explicitly. A general categorical
  composition theorem remains deliberately out of scope;
- [x] replace prose state-space and unit interfaces with checked typed
  declarations for variables, units, boundaries, and finite state domains;
- [ ] test every map on the running multiconductor network, its five-bus
  line-identity example, and the multiwinding transformer;
- [x] add a generated fixture-coverage matrix that distinguishes direct,
  related, not-yet-tested, and not-applicable evidence for those three
  canonical fixtures; the five-bus port--factor lift is now direct evidence,
  and its scalar conductor-terminal lift is now direct evidence as well,
  together with direct inventory/active radiality checks on the five-bus case,
  and a direct scalar typed-Kron check for its pendant bus ``m``,
  extended with a non-pendant ``l`` elimination that records retained
  Schur-complement fill edges and an exactly recovered but deliberately
  violated ``x``-branch limit,
  while remaining direct-coverage rows stay open rather than being implied
  by synthetic witnesses;
  - the running fixture now has direct line-identity cycle evidence: its
    scalar line projection retains the ``\ell_1/\ell_2`` parallel cycle while
    the simple projection is acyclic; multi-terminal assets remain outside
    this scalar cycle calculation;
  - the serialized three-winding transformer contract now has direct
    conductor-terminal lift evidence, preserving ordered WYE/DELTA ports and
    keeping grounding and excitation observations separate;
  - the same contract now has direct typed-Kron precondition evidence: its
    ungrounded DELTA terminal block is singular, so elimination is refused
    without a pseudoinverse and the winding-limit observation stays explicit;
  - the same contract now has direct cycle-view evidence: native factor--port
    incidence is acyclic while a named three-port clique compilation has rank
    one; active radiality remains explicitly open for the isolated contract;
  - the fixture matrix now also records direct running-network typed
    state-space/unit evidence and direct ``x1`` winding-normalization evidence,
    while related and not-applicable combinations remain explicit;
  - parameterized transformer control is now a separate fixture family in the
    matrix: direct on the running network through the retained-tap AC decision
    certificate, not applicable to the five-bus cycle-space fixture, and related
    (rather than direct) to the fixed ``x1`` multiwinding contract;
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
- [x] lift these invariants to conductor-terminal incidence and
  state-conditioned topology decisions on the running network, while keeping
  multi-terminal factor compilation as a separate view;
- [x] lift the active-state radiality witness to the running network and its
  switch/outage variants, with explicit active member inventories and
  transformer-winding provenance.

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
- [x] make the controlled callout vocabulary machine-checkable without
  requiring every chapter to contain a callout; the audit rejects unknown
  labels and requires each of the four labels to appear somewhere in the book.

### Stage F — expert-review response (2026-08-13)

The external review is retained as an internal historical record of the
integrity pass. Its response and qualifications are archived in
[`review/archive/`](review/archive/); they are not formal publication
requirements for the current knowledge-base release.

#### F0 — repair claims, contracts, and internal consistency first

- [x] correct the typed-Kron covariance and reciprocity statements before
  treating `TR-KRON-001` as established;
- [x] repair the defective bridge proof, quantify preservation contracts over
  all admissible observations and inputs, and weaken the line--shunt
  realization proposition to its actual stamping claim;
- [x] split claim **type** from verification **status**, render both in the
  book, and revise the README's independent-reproduction wording;
- [x] fix the six-versus-eight-variable count, running-fixture/spec drift,
  tap-witness explanation, running-example policy, and chapter-count statement;
- [x] make the compiled-star convention explicit in the generated multiview
  figure and its caption text; remaining figure-family audits stay open;
- [x] reconcile the taxonomy tables by making the four principal levels and
  their orthogonal companions explicit; the formal-framework chapter now owns
  the rigorous definitions while the taxonomy chapter owns the reader-facing map;
- [x] complete the remaining figure-family monochrome audit;
- [x] remove reader-facing drafting-process notes from chapters and move them
  to the roadmap/contributing material.

#### F1 — make the mathematical and numerical evidence auditable

- [x] add the side-by-side Schur-complement versus phase-to-neutral reduction
  witness, with explicit grounding and invertibility assumptions;
- [x] add condition numbers, backward-error estimates, and decision margins to
  redundancy certificates; reject numerically ambiguous certificates;
- [x] instantiate a minimal executable `𝔓` and `Λ` port--factor case on the
  running network; the structural witness validates typed incidence, a
  three-port transformer, grounding, and many-to-many asset linkage.

#### F2 — add the missing positive theory and physical scope

- [x] add **When the general model collapses**, deriving a balanced,
  positive-sequence transmission-style model from declared transposition,
  grounding, symmetry, and decision assumptions;
- [x] add the earth/ground model taxonomy (ideal reference, reduced earth
  return, explicit earth conductor) and scope every result accordingly;
- [x] add a balanced three-bus nominal-``\pi`` transmission witness that
  solves the phase-domain and positive-sequence network views independently,
  checks voltage and branch-current recovery, and keeps the decision-equivalence
  boundary explicit;
- [x] reproduce that balanced witness with an independent standard-library
  complex solver and bind the comparison to the artifact checks;
- [x] independently reproduce the CP/CI/CZ load-model decision witness with a
  separate damped fixed-point implementation and retain its scope boundary;
- [x] extend that scalar witness with a normalized active-power ZIP row while
  keeping multiconductor connection maps explicitly out of scope;
- [x] give the ZIP row separate normalized active- and reactive-power
  coefficients, and reproduce both coefficient maps independently;
- [x] independently reproduce the running four-conductor Kron neutral-current
  recovery and retained limit violation;
- [x] add a linear midpoint neutral-to-reference shunt probe with retained KCL,
  neutral-current recovery, and an independently reproduced limit check;
- [x] add an explicit-earth five-conductor Kron probe with separate neutral and
  earth KCL recovery, a retained neutral-current limit, and an independent
  standard-library reproduction; keep standards-aligned grounding, protection,
  and nonlinear earth-return extensions explicitly open;
- [x] extend that probe to a three-segment chain with two explicit grounding
  points, separately recovered bond currents, and independent KCL checks;
- [x] add a finite grounding-impedance sweep with a fixed neutral limit and an
  independent reproduction, separating structural/KCL preservation from
  parameter-dependent feasible-set preservation;
- [x] add a local state-dependent neutral--earth bond probe with shifted-state
  recomputation, a frozen-map failure residual, and an independent Newton
  reproduction; retain global nonlinear grounding and continuation as open;
- [x] extend the local state-dependent probe to two interacting grounding
  points, checking frozen-map failure and recomputed-chain recovery with an
  independent Newton reproduction;
- [x] add a finite five-state endpoint continuation of the two-point nonlinear
  grounding chain, with per-state neutral-limit margins and independent row
  reproduction; keep adaptive/global continuation explicitly open;
- [x] add a local real-Jacobian grounding certificate that quantifies frozen
  map error versus recomputed-map linearisation error;
- [x] extend the three-member four-wire AC joint-pruning witness to a finite
  four-state admittance envelope, including a phase-selective unbalanced state,
  rebuilding source/pruned formulations and independent boundaries at each
  state;
- [x] independently reproduce all four three-member state-envelope boundaries
  with a separate standard-library Newton/bisection implementation;
- [x] state explicitly which state-estimation, protection, contingency, and
  data-exchange promises are current content and which remain future work.

#### F3 — connect the framework to practice

- [x] add the node--breaker/topology-processing crosswalk;
- [x] add a data-model crosswalk for CIM/CGMES, PowerModelsDistribution,
  OpenDSS, and MATPOWER, with versioned source references;
- [x] define rating semantics (continuous/emergency, ambient adjustment,
  conductor/terminal equipment, current/apparent-power/thermal/CT/relay
  limits) before extending decision-preservation claims.

#### F4 — expose computational consequences and communication quality

- [x] add conditioning, per-unit scaling, Jacobian structure, fill-in, and
  solver-behaviour consequences to the transformation chapters;
- [x] restructure **Start here** around one running network, the five-bus
  failure, the first positive collapse, and scope; move longer worked cases
  out of the orientation path;
- [x] consolidate repeated parallel-flow messaging and add a generated
  structural constraint-variable/Jacobian/fill-in witness.
- [x] extend the witness to a pinned solver-exported passive/linearized
  `Ybus` and realified current-Jacobian view.
- [x] add a finite-difference nonlinear source/aggregate decision Jacobian and
  symbolic KKT fill comparison under explicit orderings.
- [ ] connect it to nonlinear OPF KKT/Jacobian exports and actual
  ordering-dependent factorization diagnostics across reduced views.
  The current structural crosswalk now binds the five-bus typed-Kron fill and
  recovered branch-limit observation to the declared Jacobian dependency
  witness; solver-private ordering and factorization exports remain open.

#### F5 — publication and figure track

- [x] add the figure set prioritised in the response document (map of maps,
  Kron fill-in, provenance lineage, and active radiality panels);
- [x] add a generated preservation-contract card with monochrome-safe labels;
- [x] add a generated earth/neutral model-class ladder with explicit study
  boundaries and monochrome-safe labels;
- [x] add a generated three-winding transformer anatomy card with explicit
  port bundles, auxiliary factors, recovery, and grounding scope;
- [x] add a generated scalar parallel feasible-set geometry card showing the
  outer aggregate relaxation and exact lifted interval;
- [x] prepare and audit the three paper-sized extraction tracks, beginning with
  the multiconductor parallel-limit result; `scripts/check_paper_tracks.py`
  verifies their claim IDs, local links, and shared boundary protocol. These
  remain dissemination cuts, not alternate scientific claims.

#### F6 — HTML-first knowledge-base structure

- [x] make the HTML site the primary product and give the PDF a separate,
  curated navigation route over the same Markdown sources;
- [x] generate claim, verification, artifact, unresolved-issue, and chapter
  status indexes from `claims/claims.toml` and `experiments/generated/`;
- [x] move drafting-order language in the reviewed foundations into reader-
  facing scope/open-boundary language;
- [x] add chapter-level status metadata to every untracked explanatory page,
  and render it in the generated status index;
- [x] generate provisional representation/transformation/study/software facet
  indexes from stable claim IDs and chapter paths; replace these with explicit
  claim facets when the schema is normalized;
- [x] agree and check an initial public API boundary in
  `experiments/src/GraphModelsForPowerNetworks.jl`, with a generated manifest
  separating stable primitives from experimental evidence;
- [x] stage the facade and selected transformations as the dependency-light
  `package/GraphModelsForPowerNetworks` candidate, with versioned state-space /
  unit objects and conversion contracts;
- [ ] publish/tag that package after external review of its API and
  compatibility policy;
- [x] review the stale `power-network-graph-models/` snapshot and retain it as
  an explicitly archived historical seed; its README and handover prohibit new
  chapters or generated artifacts, while the repository root is authoritative.

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

## Completed baseline (archived vertical slice)

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

The numbered record above documents the completed first vertical slice. New
work should be added to the active milestones below, not appended to this
archive.

## Active milestones

### M1 — Integrity and reproducibility release

**Priority:** immediate publication gate.

**Progress:** the local/CI preparation is complete. The first repair pass for
the two dark-background PNGs, the clipped numerical figure, and the
chapter-status output is complete, and the claims, artifacts, figures, HTML,
PDF, and aggregate tests agree. Independent review of selected claims is
optional future validation rather than a release gate.

- [x] add or normalize page-status metadata for every reader-facing page and
  make the generated chapter-status index agree with it;
- [x] complete the monochrome and print audit for the remaining figure family;
- [x] configure and locally verify the HTML and PDF workflows, including DejaVu font
  availability and the native-Tectonic fallback documentation;
- [x] add explicit white backgrounds to generated SVG assets and regenerate the
  preservation-contract and transformer PNGs;
- [x] make the chapter-status parser line-safe and regenerate the status/index
  pages without prose or Markdown tables in status cells;
- [x] repair the clipped structural/Jacobian witness layout and its overprinted
  labels;
- [x] audit every ledger claim for a reader-facing mention in its chapter;
  `ARCH-PORT-001` is now surfaced in the formal-framework chapter, and the
  repository-wide audit is enforced by `scripts/check_claim_mentions.py`;
- [x] align the numerical certificate field proposal with schema v1.2 (or
  explicitly label the proposal as non-normative);
- [ ] optionally obtain independent reviews of the highest-risk claims,
  prioritizing `TR-KRON-001`, `TR-PAR-004`, `TR-SER-001`, and `TR-XFMR-001`;
- [x] prepare and archive a reproducible reviewer packet with claim-specific
  artifacts, commands, assumptions, and an explicit reviewer record;
- [x] make claim type, verification state, artifact, and unresolved issue
  cross-checks fail closed in the local and CI checks.

**Exit criterion:** a clean local release candidate whose claims, chapter
statuses, figures, HTML, PDF, and generated artifacts agree. Independent
review remains useful future validation but is not required for this release.

### M2 — Reduction evidence

**Priority:** next scientific tranche.

- [x] implement a typed multiconductor Kron fixture covering coordinate
  covariance, internal-state recovery, original limits, and direct
  line--shunt realizability;
- [x] add direct running-network coverage for a four-conductor series-line
  midpoint elimination, with terminal/order provenance and exact recovery of
  the original line primitive; the witness also retains and evaluates the
  eliminated neutral-current limit after recovery;
- [x] compare exact Kron, an operating-point Ward equivalent, and an
  Opti-KRON-style scenario approximation on common voltage, current,
  constraint, and decision observations;
- [x] write the first certified-approximation chain: parameter/model residual →
  state error → constraint margin → decision margin, using the Ward scenario
  fixture and the book's certified/ambiguous/violated classification;
- [x] construct an extended-Ward fixture with explicit boundary support
  injections, while retaining the base-state Ward target as a separate
  operating-point comparison;
- [x] add a scoped nonlinear constant-power Ward probe with a damped-Newton
  reference solve and an explicitly local inverse-Jacobian decision bound;
- [x] add guarded witnesses for singular full terminal maps, jointly retained
  support bounds, and state-conditioned recovery maps;
- [x] add a scoped transformer-control family witness covering phase-angle,
  independent-phase, mechanically coupled, automatic-deadband, and
  tap-dependent-loss maps;
- [ ] extend the nominal-``\pi`` and parallel-limit cases to singular maps,
  jointly implied limits, and state/control-dependent models at full AC scale,
  adding global bounds where required;
  - nominal-``\pi`` singular and singular-shunted refusal probes are now
    executable, together with a voltage-dependent shunt recomputation guard.
    A series-only singular fixture now also demonstrates exact recovery in the
    endpoint-voltage-drop coordinate while retaining the zero-neutral invariant;
    exact singular shunted reductions and global AC bounds remain open. The
    state-conditioned shunt-map probe rejects frozen off-state maps and
    requires recomputation at the shifted state. The companion full-AC
    decision probe solves base and shifted shunt states, and rechecks exact
    pruning after rebuilding the shifted map; global control-policy guarantees
    remain open. A finite three-state shunt envelope now rebuilds the map and
    re-solves source/pruned AC formulations at each declared state;
  - a three-member four-wire AC probe now crosses the jointly retained
    fixed-map support certificate into a local nonlinear decision solve:
    member 3 is recovered from members 1 and 2, and its limits are deleted
    only after the recorded support bound fits inside the candidate rating.
    An independent finite-difference continuation and bisection reproduces
    the source boundary as a branch-level numerical check. This closes the
    local several-retained-member example while leaving global nonlinear and
    state/control-dependent guarantees open;
- [x] compose the BMOPFTools Ybus/Jacobian and nonlinear KKT witnesses in a
  package-level crosswalk with shared node/order provenance and explicit
  ordering-dependent symbolic fill;
- [x] exercise BMOPFTools' public checked-KKT factorization callback on a
  staged OPF context, including a regular acceptance and near-singular
  rejection probe;
- [x] wire that callback through DiffOpt on a minimal parameterized OPF and
  compare the forward sensitivity with a central finite difference;
- [x] capture the solver-provided KKT matrix passed through the DiffOpt
  callback, recording dimensions and sparsity while retaining the row-label,
  scaling, ordering, and active-set caveats;
- [x] bind the captured KKT dimension to ordered JuMP variable and constraint
  metadata, while explicitly marking the row-label mapping as an adapter
  convention rather than a solver-native export;
- [x] compare a two-member parallel-line source with its scalar equivalent
  through DiffOpt, preserving the tested voltage sensitivity while exposing
  changed KKT dimensions and sparsity;
- [x] attach BMOPFTools differentiability and active-set diagnostics to the
  DiffOpt witness, retaining qualifications and explicit limits on what
  `ready` means;
- [x] connect the crosswalk to a native JuMP/MOI nonlinear Jacobian structure
  export, while retaining the explicit boundary around Ipopt-private KKT and
  factorization diagnostics;
- [ ] connect the crosswalk to BMOPFTools/solver-exported KKT rows and
  ordering-dependent factorization diagnostics if that public boundary becomes
  available;
- [x] add scoped JuMP/Ipopt feasibility probes for phase-angle,
  independent-phase, mechanically coupled, automatic, and tap-dependent-loss
  control maps, while keeping the full network-level extension open;
- [x] cross the phase-angle and tap-dependent-loss probes into a two-bus AC
  served-current network fixture, retaining the explicit non-OPF scope;
- [x] cross independent-phase and mechanically coupled maps into a three-phase
  uncoupled AC fixture, retaining phase-specific control provenance;
- [x] add a neutral-coupled four-wire fixture with mutual impedance, neutral
  displacement, and explicit return-current KCL;
- [x] add a two-scenario 11-terminal tap ledger that enumerates all finite tap
  pairs, applies an explicit switching cost, and records finite-domain branch
  completeness;
- [x] sweep the declared switching cost over a finite range and record the
  selected-pair stability region alongside the complete branch ledger;
- [x] record positive affine branch-objective intersections so switching-cost
  policy breakpoints are explicit rather than inferred from sampled costs;
- [x] extend the finite tap-pair ledger to a phase-selective unbalanced
  second scenario on the 11-terminal WYE/WYE/DELTA case, retaining explicit
  phase directions and nine-pair branch completeness;
- [x] extend the finite phase-selective tap ledger to a three-scenario,
  27-branch tap path with consecutive movement cost and explicit phase scales;
- [x] add an explicit at-most-one tap-movement policy over that full 27-branch
  domain, retaining 15 admissible branches and an independent reproduction;
- [ ] extend the switching-cost and branch-completeness contract to richer
  unbalanced multiwinding network decisions and continuous/global guarantees.

**Exit criterion:** a reproducible comparison showing when each reduction is
exact, conservative, relaxed, or scenario-approximate for declared decision
observations.

### M3 — Graph architecture and topology

**Priority:** after the first reduction comparison, with selected items able
to proceed in parallel.

- [x] formalize a first hierarchy/refinement/open-system boundary witness with
  checked typed interfaces and state-conditioned switch maps;
- [x] introduce reusable state-space and unit objects for the initial public
  facade, with a generated running-network witness;
- [x] add a generated node--breaker fixture with open, closed, and unknown
  switch states;
- [x] lift the five-bus cycle and radiality architecture to conductor-terminal
  connectivity, compiled multi-terminal factors, and state-conditioned switch
  maps on the running fixture;
- [x] lift active-state radiality to the running network and switch/outage
  variants, reporting adjacency-radial and member-radial status;
- [x] agree the initial public API boundary before package promotion, and bind
  it to `experiments/generated/public-api-manifest.json`;
- [x] attach typed declarations directly in every public certificate generator
  and run a package-level matrix over all sixteen certificate artifacts.
- [x] complete a release-oriented package test matrix that binds the typed
  declarations to every transformation's semantic evaluator and test path,
  not only its serialized certificate.
- [x] run that matrix from a clean, separately instantiated package checkout
  and retain the pinned result in `experiments/generated/clean-package-matrix.json`;
- [x] stage a dependency-light standalone package candidate under
  `package/GraphModelsForPowerNetworks`, route the experiment facade through
  it, and add a package-native test gate.
- [x] bind the conductor-terminal, running-network radiality, and hierarchy
  boundary witnesses to the aggregate experiment test suite and documentation
  CI, alongside the dependency-light package test.
- [x] add the two-level topology/nodal-projection chapter, support-graph
  definitions, and radial-macro versus clique-support diagrams;
- [x] add the generated factor-stamp and support-graph witness described in the
  topology-projection tranche;
- [x] add the scoped source-recovery vocabulary and executable witnesses for
  support-separated, multiplicity, elimination, and over-parameterized
  classes;
- [x] add guarded-recovery witnesses for catalog bounds, member-current
  observations, grounding declarations, and declared transformer state;
- [x] add the multiconductor observation-rank and phase-selective
  partial-observation witness;
- [x] add the bounded-noise multiconductor recovery and conditioning witness;
- [ ] extend guarded recovery to noisy partial observations, nonlinear
  grounding, full transformer controls, and experimental design before
  claiming general inverse-import guarantees;
- [ ] optionally publish/tag the standalone package after API and
  compatibility-policy review.

**Exit criterion:** the proposed representation architecture has checked maps
and topology witnesses on the running network, not only prose definitions.

### M4 — External validation and dissemination

**Priority:** parallel track; not a gate on M1--M3 unless a result is used to
support a stronger claim.

- [ ] execute and archive the planned database searches and populate the
  evidence matrix with double-coded seed results;
  - a 2026-08-14 web seed batch is archived in
    `review/search-runs/2026-08-14-seed-batch.md` and adds three scoped
    single-coded records; database exports and second-coder review remain open;
- [x] add a fail-closed evidence-matrix validator for schema, controlled
  vocabulary, exclusion logic, and coding-status checks; it intentionally
  leaves the existing single-coded seed row below the double-coding gate;
- [x] add scheduled external-link checking without making ordinary builds
  depend on publisher availability; `.github/workflows/external-links.yml`
  runs independently on a weekly schedule, manually, and for documentation
  changes in pull requests;
- [x] add a version-pinned running-fixture contract crosswalk for CIM/CGMES,
  OpenDSS, PowerModelsDistribution, and MATPOWER; external package imports and
  file-level round-trip adapters remain open;
- [x] complete the map-of-maps, Kron fill-in, provenance-lineage, and active
  radiality figure set;
- [x] prepare the three paper-sized extraction tracks after M1 corrections;
- [x] review the stale `power-network-graph-models/` snapshot and archive it
  in place once its historical status is confirmed.

**Exit criterion:** external sources, adapters, figures, and paper extracts
are traceable to the same claims and artifacts as the book.

#### M4a — Argument diagrams and route structure

The 2026-08-14 review identifies a portfolio problem rather than a shortage of
plots: most existing figures show that a computation happened, while the
book's arguments remain in dense prose. New figures must carry one claim,
share a documented visual grammar, remain legible in monochrome, and be linked
from the chapter that uses them. Every generated figure needs a source fixture
or deterministic generator, an SVG/PNG pair when the PDF route needs it, alt
text/caption prose, and a figure-audit entry.

**First argument batch (highest leverage):**

- [x] draw the four exactness classes as observed-set containment, including
  the scalar parallel-line outer witness;
- [x] draw the recovery-map loop, with the missing recovery arrow producing an
  outer relaxation;
- [x] draw the argument spine showing the current premise/counterexample/tool/
  consequence position;
- [x] add a thin chapter-header band with the current spine stage highlighted;
- [x] draw partial orders under two query families to make incomparability
  visible;

**Second explanatory batch:**

- [x] turn the five worked parallel cases into a case-escalation grid, and do
  the same for the transformer chain;
- [x] add a reading-route map for the HTML/PDF spine and the four audiences;
- [x] add sequence-subspace geometry for the positive-sequence collapse;
- [x] add a four-overlay “what does bus mean?” figure for node--breaker and
  compiled bus--branch views;
- [x] draw certificate composition and the guarded-rule gate once for Part III;
- [x] add an orientation-versus-power-transfer panel and a cycles/parallelism/
  radial-tail panel if the existing argument figures do not cover them;

**Consolidation and acceptance:**

- [x] merge the duplicate scalar feasible-set cards and replace the survivor
  with the promised complex-plane disc/ellipse geometry;
- [x] split the overloaded numerical-structure witness into one fill-in
  argument and one Jacobian-dependency argument;
- [x] re-curate `PAGES_PDF` on argument value, restore `translation-traps`,
  and avoid using the PDF route as a mirror of the HTML index;
- [x] shorten `index.md` to a route paragraph and delegate retrieval to the
  generated knowledge-base index;
- [x] split Part I into representations versus physical/computational
  reference, and consolidate the four overlapping framework chapters into one
  core chapter plus reference cards;
- [x] apply the figure grammar and audit to every new asset before marking the
  visual track complete.

**Exit criterion:** each load-bearing argument has a compact explanatory
diagram, the HTML route remains the primary product, and the PDF route is a
curated serialization whose diagrams and captions survive print and
monochrome rendering.

## Deliberately deferred

Lean formalization, broad category-theoretic claims, a full explicit-earth and
protection implementation, and a general optimizer-independent release remain
Phase 5--6 work. They should not expand the M1--M4 scope until the reduction
evidence and independent review gates are met.

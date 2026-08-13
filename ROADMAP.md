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

## Current status and active plan (2026-08-13)

The review-response foundation pass is substantially complete. The HTML-first
knowledge base, curated PDF route, claims ledger, generated indexes, running
fixture, graph-invariant witnesses, multiconductor parallel cases, transformer
compilers, and positive-sequence collapse witness are implemented and locally
validated. The native Tectonic fallback and PDF-safe diagram assets are also in
place.

The checklists below preserve the scientific record of that pass. They are not
the active task queue. The active queue is the four milestones at the end of
this file, ordered by dependency:

1. integrity and reproducibility release;
2. reduction evidence;
3. graph architecture and topology;
4. external validation and dissemination.

The first two milestones are the publication gate for stronger decision-case
claims. General formalization, broad adapters, and paper extraction remain
deliberate follow-on work rather than prerequisites for the knowledge base.

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

### Stage F — expert-review response (2026-08-13)

The external review is accepted as the governing integrity pass for the next
milestone.  The response, including qualifications and acceptance criteria, is
recorded in [`review/expert-review-response-2026-08-13.md`](review/expert-review-response-2026-08-13.md).

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
- [ ] complete the remaining figure-family monochrome audit;
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

#### F5 — publication and figure track

- [ ] add the figure set prioritised in the response document (map of maps,
  Kron fill-in, provenance lineage, and active radiality panels);
- [x] add a generated preservation-contract card with monochrome-safe labels;
- [x] add a generated earth/neutral model-class ladder with explicit study
  boundaries and monochrome-safe labels;
- [x] add a generated three-winding transformer anatomy card with explicit
  port bundles, auxiliary factors, recovery, and grounding scope;
- [x] add a generated scalar parallel feasible-set geometry card showing the
  outer aggregate relaxation and exact lifted interval;
- [ ] prepare the three paper-sized extraction tracks, beginning with the
  multiconductor parallel-limit result; these are parallel dissemination
  work, not a prerequisite for the book's integrity fixes.

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
- [ ] promote `experiments/transformations/` to a standalone package after
  its public API boundary is agreed;
- [ ] review the stale `power-network-graph-models/` snapshot and remove it or
  archive it after confirming it is not an intentional historical artifact.

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

- [ ] add or normalize page-status metadata for every reader-facing page and
  make the generated chapter-status index agree with it;
- [ ] complete the monochrome and print audit for the remaining figure family;
- [ ] verify the HTML and PDF workflows in CI, including DejaVu font
  availability and the native-Tectonic fallback documentation;
- [ ] obtain independent reviews of the highest-risk claims, prioritizing
  `TR-KRON-001`, `TR-PAR-004`, `TR-SER-001`, and `TR-XFMR-001`;
- [ ] make claim type, verification state, artifact, and unresolved issue
  cross-checks fail closed in the local and CI checks.

**Exit criterion:** a clean release candidate whose claims, chapter statuses,
figures, HTML, PDF, and generated artifacts agree and whose core theorem
claims have an independent review record.

### M2 — Reduction evidence

**Priority:** next scientific tranche.

- [ ] implement a typed multiconductor Kron fixture covering coordinate
  covariance, internal-state recovery, original limits, and direct
  line--shunt realizability;
- [ ] compare exact Kron, an operating-point Ward equivalent, and an
  Opti-KRON-style scenario approximation on common voltage, current,
  constraint, and decision observations;
- [ ] extend the nominal-``\pi`` and parallel-limit cases to singular maps,
  jointly implied limits, and state/control-dependent models, adding global
  bounds where required;
- [ ] connect the numerical witnesses to BMOPFTools solver-exported
  Jacobian/KKT and ordering-dependent factorization diagnostics;
- [ ] extend transformer-control evidence to phase-angle, independent-phase,
  mechanically coupled, automatic, and tap-dependent-loss controls.

**Exit criterion:** a reproducible comparison showing when each reduction is
exact, conservative, relaxed, or scenario-approximate for declared decision
observations.

### M3 — Graph architecture and topology

**Priority:** after the first reduction comparison, with selected items able
to proceed in parallel.

- [ ] formalize hierarchy, refinement, open-system composition, and boundary
  gluing, replacing prose interfaces with checked state-space and unit objects;
- [ ] add a generated node--breaker fixture with open, closed, and unknown
  switch states;
- [ ] lift the five-bus cycle and radiality witnesses to conductor-terminal
  connectivity, compiled multi-terminal factors, and state-conditioned
  topology decisions;
- [ ] lift active-state radiality to the running network and switch/outage
  variants, reporting adjacency-radial and member-radial status;
- [ ] agree the public API boundary before promoting
  `experiments/transformations/` to a standalone package.

**Exit criterion:** the proposed representation architecture has checked maps
and topology witnesses on the running network, not only prose definitions.

### M4 — External validation and dissemination

**Priority:** parallel track; not a gate on M1--M3 unless a result is used to
support a stronger claim.

- [ ] execute and archive the planned database searches and populate the
  evidence matrix with double-coded seed results;
- [ ] add scheduled external-link checking without making ordinary builds
  depend on publisher availability;
- [ ] add selected version-pinned CIM/CGMES, OpenDSS, and
  PowerModelsDistribution crosswalk tests;
- [ ] complete the map-of-maps, Kron fill-in, provenance-lineage, and active
  radiality figure set;
- [ ] prepare the three paper-sized extraction tracks after M1 corrections;
- [ ] review the stale `power-network-graph-models/` snapshot and remove or
  archive it once its historical status is confirmed.

**Exit criterion:** external sources, adapters, figures, and paper extracts
are traceable to the same claims and artifacts as the book.

## Deliberately deferred

Lean formalization, broad category-theoretic claims, a full explicit-earth and
protection implementation, and a general optimizer-independent release remain
Phase 5--6 work. They should not expand the M1--M4 scope until the reduction
evidence and independent review gates are met.

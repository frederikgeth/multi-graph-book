# Work plan and roadmap

This file tracks the scientific and implementation programme. The reader-facing argument, target
table of contents, chapter forms, and first drafting milestone are maintained separately in
[`BOOK_PLAN.md`](BOOK_PLAN.md).

## Guiding outcome

Produce a citable, open, problem-first scientific book and executable companion
knowledge base that explains what power-network representations preserve and
lose, when familiar simplifications fail, and how transformations can make
their preservation obligations explicit.

The book's primary contribution is methodological and diagnostic: it establishes
representation problems, semantic failure modes, and evidence boundaries. The
typed architecture, transformation rules, and certificates are the proposed
tools for addressing those problems. They must not be presented as a completed
general transformation calculus when the evidence is only fixture-level or
scope-specific.

The roadmap separates **publication infrastructure**, **knowledge synthesis**,
**formal results**, and **software/experiments** so that progress in one does
not masquerade as completion of the others.

## Current status and active plan (2026-08-17)

The repository is an internally validated HTML-first release candidate. The
curated PDF is a secondary serialization of the same Markdown sources. The
current checks cover 96 registered claims, 66 audited SVG/PNG pairs, 562 local
links, the aggregate experiment suite, rendered-output smoke checks, the HTML
build, and a 349-page PDF.
The high-risk 2026-08-15 review findings, the 2026-08-16 vocabulary and
multi-port-lowering reviews, and the canonical-model section review have been
repaired. Those automated and supplied
reviews remain technical evidence, not external human peer review.

The remaining work is a refactor and review-readiness programme, not a content
shortening programme. The full long-form material remains in scope. The active
question is how to make the book, knowledge base, evidence record, and external
review packet tell the same story.

### Federated executable-knowledge scale-out inventory (2026-08-26)

`ARCHITECTURE.md` remains the authority for what belongs in this repository and
what belongs in BMOPFTools. This inventory is the prioritized promotion queue:
it identifies topics where the book already has a scientific basis and where a
package check, fixture, or existing diagnostic can provide complementary
case-specific evidence. A row is not a promise that every topic needs one large
contract; promotion still requires a scoped PSK, explicit refusal semantics,
and a minimized negative witness.

| Priority | Topic | Book-owned basis | BMOPFTools complement | Status / intended class |
|---:|---|---|---|---|
| 1 | Parallel member limits | `TR-PAR-001..003`; parallel-rating misconception | source/aggregate interval witness | Implemented as `PSK-000001` |
| 2 | Neutral, ground, and reference identity | `GROUND-SCOPE-001..002`; grounding misconception | mapped representation relations | Implemented as `PSK-000002` |
| 3 | Solver status versus validated result | `NUMERICAL-001`, `NUMERICAL-004` | independent result profiling | Implemented as `PSK-000003` |
| 4 | WYE/DELTA load nominal-voltage coordinate | `LOAD-BASE-001`, `LOAD-CONNECTION-001` | propagated-base declaration check | Implemented as `PSK-000004` |
| 5 | Adjustable transformer tap domain | `TR-XFMR-005..006`; tap-decision certificates | mapped continuous interval comparison | Implemented as `PSK-000005` |
| 6 | Transformer winding coil bases, ratio, and orientation | `TR-XFMR-001..004`; winding-normalization evidence | existing ratio/base/orientation diagnostics plus a mapped convention contract | Implemented as `PSK-000006` |
| 7 | Terminal equivalence versus decision equivalence | preservation-contract definitions and multiple transformation witnesses | transformation manifest with constraints, objective, and recovery obligations | Implemented as `PSK-000007` |
| 8 | Kron boundary exactness and internal recovery | `PRESERVE-001`, `TR-KRON-*`; Kron misconception | source/target boundary and recovery-map checks | Implemented as `PSK-000008` |
| 9 | Positive-sequence collapse applicability | `COLLAPSE-001..002`; sequence misconception | symmetry, grounding, terminal, and decision-domain guards | Implemented as `PSK-000009` |
| 10 | Fixed versus state-dependent equivalents | formulation split, Ward/Kron, and load-dependence claims | detect frozen parameters and missing state/update provenance | Implemented as `PSK-000010` |
| 11 | Floating references and singularity | grounding/reference and numerical-consequence claims | existing reference, connectivity, and singularity diagnostics | Implemented as `PSK-000011` |
| 12 | Terminal/conductor ordering and permutation | typed terminal-map and coordinate-action claims | metamorphic relabelling/permutation invariance | Implemented as `PSK-000012` |
| 13 | Complete solved-network feasibility | numerical validation boundary | equation, KCL, power-balance, device-limit, and recovery residuals | Implemented as `PSK-000013`; residual-witness gate |
| 14 | Unit/base and serialization invariance | normalization, coordinate, and provenance claims | round-trip and unit/base metamorphic tests | Implemented as `PSK-000014`; metadata/payload binding |

The first scale-out milestone is now complete and extended: fourteen stable PSK paths cover a
transformation constraint, model semantics, numerical inference, connection
coordinates, an adjustable decision domain, typed transformer-winding
conventions, the terminal-to-decision evidence boundary, and Kron boundary/recovery
conditions, positive-sequence domain closure, state/update provenance,
reference/rank validation, terminal/conductor permutation invariance,
solved-network feasibility, and unit/base serialization. Remaining promotion is
evidence-gated rather than quota-driven.

### Executable interface and recipe tranche (in progress, 2026-08-30)

The first two scientific transport slices are implemented for `PSK-000001` and
`PSK-000002`. BMOPFTools owns a versioned JSON execution response, a curated
`check-contract` CLI/API adapter registry, and CI-tested
`parallel_member_limits` and `neutral_ground_reference` recipes that reuse the
minimized fixtures. A third, non-contract `analyze-case` route now parses one
BMOPF JSON case and returns the package's complete standard analysis/validation
report. Its `completed` operation status remains separate from Finding severity,
and its tutorial-derived `analyze_case` recipe explicitly rejects the shortcut
that a completed report means a clean or solver-ready case. Tests exercise
successful, failing, inapplicable, indeterminate, request-error, and completed-
with-Findings outcomes. The federated pair manifest pins both PSK-linked recipes
and the package-only analysis recipe; book context packets surface the linked
scientific examples while keeping ordinary package operations separate.

A fourth, package-only `verify-solution` route now profiles a supplied result
without invoking a solver. Its tutorial-derived `verify_solution` recipe uses a
minimized claimed-feasible counterexample: solver termination is
`LOCALLY_SOLVED`, execution is `completed`, and the independent report still
contains `E.SOL.VOLT_VIOLATION`. This makes solver termination, execution
status, Finding severity, and scientific-contract status explicit rather than
collapsing them into one success flag. The pair manifest pins this operation
recipe without injecting it into a PSK context packet.

A fifth, package-only `explain-finding` route now performs deterministic offline
lookup over a generated registry of all 341 Finding codes documented by
BMOPFTools. Its `explain_finding` recipe distinguishes a canonical code meaning
from one case-specific observation and refuses to infer causes, repairs, or PSK
links. External PowerIO diagnostic namespaces remain outside the package
registry. The pair manifest pins the recipe and registry provenance without
turning the lookup into a book scientific claim.

A sixth, package-only `parse-case` route now exposes the distinct intake
boundary already implemented by `parse_bmopf`: JSON decoding, supported
forward migration, and terminal normalization, but no schema/domain validation
or analysis. Its tutorial-derived recipe deliberately parses and migrates an
incomplete document while a separate schema assertion still requires
`E.SCHEMA.REQUIRED`. This settles the parse-only decision without collapsing
successful intake into solver readiness or scientific validity. The pair
manifest pins the hash-bound inventory recipe without inventing a PSK link.

The core execution and recipe surface is now settled. Remaining work in this
tranche is evidence-gated contract promotion plus the optional thin MCP or
PowerMCP adapter, which must expose the existing response model rather than
define a competing one. Solver invocation remains outside the current
transport slice.

### Product identity and editorial stance

The project has two deliberate products:

1. a long-form scientific monograph whose argument is problem-first; and
2. an HTML knowledge base that provides exhaustive retrieval, claims, artifacts,
   literature records, and unresolved boundaries.

The PDF may remain long. Refactoring means improving order, authority chains,
cross-references, duplicated explanations, and evidence labels while retaining
the detailed chapters and research agenda.

The working title is now **What Power-Network Models Preserve: Graphs, reductions,
and decision boundaries**. It signals that the book is about the limits and
preservation of power-network models, not only about constructing a preferred
graph or solving reduction problems. The repository and PDF filenames retain
their historical identifiers for compatibility.

### Active programme — problem-first refactor and external-review readiness

This is the current implementation queue. It supersedes older “Next” labels
when they conflict with the sequence below. Completed historical tranches remain
below for provenance; they are not re-opened by this programme.

#### R0 — Establish one source of truth for status and evidence

- [x] regenerate the evidence-map prose from the claims ledger so its claim and
  verification counts agree with the generated knowledge-base index (currently
  the prose and generated verification graphic report different totals);
- [x] add a consistency check for generated claim counts, verification counts,
  chapter-status hashes, and evidence-map text so this drift fails in CI;
- [x] audit every reader-facing status line for the distinction between
  theorem, definition, proposal, empirical witness, independent numerical
  reproduction, and external review;
- [x] add a compact, reusable chapter evidence banner with fields for scope,
  evidence type, numerical optimality status, and unresolved boundary;
- [x] correct the running-fixture earth classification: an explicit neutral and
  finite neutral-to-earth relation without an explicit earth conductor is not
  “partly E₂”; classify it as the applicable reduced-earth class plus explicit
  neutral/grounding factors;
- [x] rerun the complete local validation suite and archive the resulting status
  snapshot.

**R0 exit criterion:** generated counts and prose agree; every load-bearing
claim visibly states what kind of evidence supports it; no numerical witness is
described as external review or global optimality.

#### R1 — Refactor the long-form argument without shortening the content

- [x] rewrite the README, home page, and book-plan opening so the central
  problem is stated as representation loss and preservation, with transformations
  presented as the response rather than the premise;
- [x] preserve the complete chapter inventory, but mark each chapter as core
  argument, reference card, worked case, research record, or future application;
- [x] revise the curated PDF route around the argument sequence:
  problem and counterexample → representation obligations → canonical model →
  valid collapses and failure modes → preservation contracts → transformations
  and recovery → cases and consequences;
- [x] move repeated navigation and status explanation to the knowledge-base
  indexes, replacing duplicated prose in argument chapters with authoritative
  cross-references rather than deleting substantive material;
- [x] align `BOOK_PLAN.md` with the actual evidence boundary so promised state
  estimation, protection, planning, and feeder-reduction chapters are visibly
  either current content, scoped future content, or research agenda material;
- [x] decide the public title and subtitle after the route refactor, using the
  test that the title must communicate limits, meaning, and preservation of
  power-network models;
- [x] add a short “how to use this book” page explaining the relationship between
  the long-form monograph and the exhaustive HTML knowledge base.

**R1 exit criterion:** the full content remains available, but a new reader can
follow one problem-first argument without mistaking the knowledge-base index,
research agenda, or proposed architecture for established theory.

#### R2 — Complete the engineering and scientific readiness audit

- [x] perform a formula-level audit of the positive-sequence, phase-to-neutral,
  phase-to-phase, Kron, Ward, and nominal-π chapters, checking coordinate duals,
  grounding assumptions, invertibility, reciprocity, and shunt placement;
- [x] make the positive-sequence chapter cite the original symmetrical-component
  literature and state explicitly that transposition alone is not an exact
  reduction without the required sequence-invariance conditions;
- [x] require every exactness claim to name its exactness object using the
  controlled vocabulary: equation identity, boundary behaviour, feasible set,
  connectivity view, representation definition, observation sample, or
  `not_applicable`;
- [x] extend certificate evidence fields with solver status, local/global
  optimality status, residual and tolerance, conditioning/backward error, and
  uncertainty status where applicable;
- [x] add permutation, randomized, and near-degenerate tests to the highest-risk
  algebraic rules, especially coordinate actions, series composition, Kron
  covariance, and parallel-limit implication;
- [x] distinguish source-faithful external model validation from independent
  reimplementation of the same synthetic fixture;
- [x] keep state estimation, protection, contingency, and full adapter claims
  explicitly scoped until a solved, versioned, independently checked case exists.

**R2 exit criterion:** an external technical reviewer can identify, for every
high-consequence result, the mathematical scope, numerical evidence, solver
limitations, recovery obligations, and known failure cases without inferring
them from surrounding prose.

#### R3 — Strengthen the literature record and citation practice

- [x] add primary literature anchors for symmetrical components, ground-return
  impedance, EMS topology processing, unbalanced power-flow modelling, and
  provenance/model transformation semantics;
- [x] add a chapter-level literature-position table recording what the literature
  establishes, what the book synthesizes, what the repository demonstrates, and
  what remains open;
- [x] audit every broad literature statement in the rendered literature map for
  a directly supporting source,
  especially claims about prevalence, maturity, industrial deployment, and
  “structure-preserving” terminology;
- [x] distinguish standards, peer-reviewed primary papers, official software
  documentation, author-derived results, and project proposals in the rendered
  literature map;
- [ ] execute and archive the planned database exports, backward/forward citation
  chasing, duplicate resolution, and independent human double-coding before
  using systematic-review or PRISMA-style language;
- [x] retain the current single-coded seed snapshot as historical evidence rather
  than silently replacing it with a later coding state.

**R3 exit criterion:** every major foundation chapter has a defensible literature
anchor set and an explicit boundary between prior work, synthesis, and project
contribution; the review record is either genuinely double-coded or clearly
labelled as a seed review.

#### R4 — Prepare the external-review packet

- [x] assemble separate review tracks for graph/formal methods, circuit and
  multiconductor modelling, optimization/decision preservation, and utility/data
  practice/visual language;
- [x] give each reviewer a bounded packet containing the relevant chapters,
  claims, certificates, source fixtures, reproduction commands, assumptions,
  and specific questions rather than asking for an undifferentiated review;
- [x] create a reviewer response ledger that records finding, severity,
  affected claim/chapter, disposition, evidence, and whether the change is
  mathematical, engineering, editorial, or scope-only;
- [x] define the external-review release gate: no claim is promoted to
  externally reviewed without a named reviewer, date, scope, and recorded
  response;
- [x] add a consolidated internal release gate that records validator results,
  observed output counts, and hashes for the source, artifacts, HTML, and PDF;
- [ ] freeze a review candidate commit, bibliography snapshot, generated
  artifacts, and PDF only after R0--R3 pass;
- [ ] contact external reviewers after the packet and release candidate have
  passed the preceding gates.

**R4 exit criterion:** reviewers can reproduce the selected results, understand
  the unresolved boundaries, and return structured feedback against stable
  artifacts and claims.

#### R5 — Build a versioned LLM-accessibility layer

- [x] define a model-independent claim-bundle corpus generated from canonical
  chapters, the claims ledger, the vocabulary registry, and the release identity;
- [x] register high-consequence misconceptions with mandatory qualifications,
  evidence, counterexamples, and operational consequences;
- [x] add audience-parallel evaluation cases for students, software engineers,
  and power engineers without maintaining separate scientific facts;
- [x] make stale corpus records, hashes, release identity, and evidence links
  fail the consolidated release gate;
- [x] implement a model-independent lexical baseline over the generated corpus,
  reporting raw ranking separately from guarded contract expansion;
- [x] implement a structured context-packet builder and validator that binds
  mandatory claims, qualifications, failure consequences, source anchors, and
  release identity;
- [x] evaluate required-claim, qualification, counterexample, routing, and
  audience-parallel coverage on the initial 27-case benchmark;
- [x] add a reproducible character n-gram TF-IDF surface-semantic proxy and
  rank-fused hybrid baseline, comparing it with the committed lexical baseline;
- [x] add an optional neural-embedding adapter with immutable-revision checks,
  local artifact hashing, runtime provenance, neural search integration, and a
  standalone benchmark contract;
- [x] execute and record a pinned neural-retrieval comparison plus a generic
  cross-encoder reranking experiment, with both candidates rejected by the
  held-out quality gates because they underperform the hybrid baseline;
- [x] expose deterministic answer packets with source-hash validation,
  conservative abstention, stable Markdown/JSON and HTTP routes, and an MCP
  stdio adapter over the same service behavior;
- [x] add benchmark-only provenance-graph retrieval and adversarial/metamorphic
  checks for terminology variants, misleading shorthand, and unsupported
  questions;
- [x] report held-out contract-router firing, zero-recall cases, and the
  nine-target clustering explicitly, with a provisional 2/3 routing regression
  floor rather than treating the benchmark as independent evidence;
- [x] distinguish `under_retrieved` related-material packets from genuine
  `unsupported` abstention so downstream answer renderers cannot silently
  promote relevance to book-supported evidence;
- [x] trigger the accessibility reproduction check when canonical chapters,
  claims, or vocabulary sources change, and record the generated-page exclusion
  rule in the corpus manifest;
- [x] bind high-precision canonical prose numbers to generated artifacts or
  explicit hash-bound derivation records;
- [x] require stable H1 `@id` anchors for every HTML-routed page and inventory
  generated experiment artifacts without replacing their semantic validators;
- [ ] select, adapt, or train a domain-appropriate retriever/reranker that
  passes the required-claim, qualification, and counterexample gates;
- [ ] promote graph retrieval beyond its explicit diagnostic/opt-in route only
  after broader and independently calibrated evaluation;
- [ ] calibrate answer-quality and audience-consistency evaluation against a
  human-reviewed sample before presenting the interface as reliable.

**R5 exit criterion:** an AI client can identify the corpus edition, retrieve
the mandatory scope and counterexample for dangerous-shortcut questions, render
one scientific answer in each target audience's language, cite stable book
sources, and abstain when the resource does not support an answer.

#### R6 — Develop the multigraph reference for expert modelers

This tranche absorbs and extends the graph-theoretic material reviewed from
Appendix A. It is a refactor-and-expansion tranche: the existing representation,
cycle, topology-processing, and nodal-projection chapters remain authoritative
for their subjects, while a new reference chapter supplies the common formal
object and convention layer that those chapters can cite.

- [x] create a dedicated development branch from the squashed public snapshot;
- [x] define the finite undirected multigraph using edge ends (flags), so loops,
  parallel members, endpoint multiplicity, and later port generalizations are
  unambiguous;
- [x] separate incidence degree, distinct-neighbour degree, terminal count, and
  model-specific engineering counts rather than using an unqualified degree;
- [x] state compatible incidence, adjacency, degree, Laplacian, and cycle-space
  conventions, including the treatment of graph loops;
- [x] distinguish graph loops, shunts to reference, contraction-created loops,
  diagonal matrix terms, and self-dependencies;
- [x] define simple projection as a quotient with explicit edge fibres and give
  a query-indexed preservation table for simplification;
- [x] connect deletion, contraction, graphic matroids, parallel classes, and
  minimal cycle supports to topology processing and network-model reduction;
- [x] add graph-theory, algebraic graph theory, matroid, and classical
  network-matrix textbook anchors, with conventions attributed rather than
  presented as universal;
- [x] add an executable convention witness covering loop degree, Laplacian
  cancellation, parallel-cycle rank, simple projection, and shunt distinction;
- [x] refactor overlapping chapters to cite the new normative definitions and
  remove competing notation without shortening their application-specific
  explanations;
- [x] add worked examples for deletion/contraction, weighted parallel
  aggregation under different queries, and topology-processor state changes;
- [x] extend the treatment from two-terminal multigraphs to declared
  hypergraph/incidence and port--factor alternatives for n-port equipment;
- [x] register the high-consequence convention and simplification claims in the
  claims ledger and accessibility corpus after the prose stabilizes;
- [ ] commission expert review of graph/matroid terminology and the boundary
  between combinatorial and electrical statements as part of R4.

**R6 exit criterion:** an expert mathematical modeler can identify the exact
graph object, loop and multiplicity convention, matrix construction, and
information-losing quotient behind every graph-derived statement; a power
engineer can determine which assets or nodal elements are represented by that
object; and the core identities are covered by executable witnesses and stable
literature anchors.

#### R7 — Clarify self-loops, loopless circuit graphs, and collapsed two-port factors

This tranche closes the remaining ambiguity between a graph-theoretic
self-loop, an electrical circuit loop, a grounded shunt, and a two-terminal
factor whose terminals become identified during topology processing. It extends
R6 without changing the adopted multigraph object or treating a nodal matrix
as the canonical source model.

- [x] review graph-incidence, loopy-Laplacian, network-reduction, and
  power-system π-model precedents;
- [x] state the loopless bus--branch circuit specialization and distinguish
  graph self-loops from electrical loops, meshes, and diagonal self-admittance;
- [x] document that literature uses “loopy Laplacian” for some grounded or
  differential-conductance diagonal terms, and keep that convention separate
  from this book's zero-incidence graph-loop convention;
- [x] derive the terminal-map compilation of a fixed linear π section after
  both terminals are identified, including the exact constant-admittance
  shunt result;
- [x] state refusal conditions for ideal sources, transformers, coupling,
  controls, nonmatching coordinates, and member-level observations;
- [x] integrate the rule with node--breaker contraction, nodal lowering, and
  load/generator placement without deleting source-factor identity;
- [x] add literature-anchored claims, an executable π-collapse witness, and
  synchronized accessibility/release artifacts;
- [ ] commission expert review of the circuit-graph boundary and the use of
  “self-loop” across graph-theory and power-system communities as part of R4.

**R7 exit criterion:** a reader can decide whether a self-loop is a source
graph object, a contraction artifact, a grounded one-port abstraction, or a
compiled two-port result; can reproduce the exact π-section collapse under its
assumptions; and can identify when the collapse is invalid or insufficient for
the requested electrical query.

#### Implementation order

Work in this order: **R0 → R1 → R2 → R3 → R4** for the external-review
candidate. R5 may proceed after R0--R3 because it compiles and tests the same
evidence boundary; it must not silently promote verification states or delay a
stable reviewer snapshot. Do not expand the general transformation theory or add broad application claims before R0--R2 are complete.
New content is welcome when it closes a named evidence or reader-inference gap;
otherwise it belongs in the research agenda rather than the active queue.
R6 may proceed as a self-contained reference tranche. Its definitions must be
integrated before its claims are promoted, and its externally reviewed status
remains subject to R4.
R7 may proceed as a focused pre-review clarification of R6. Its π-collapse
identity is a formulation-scoped assembly result, not a universal rule for
all self-loops, circuit elements, or power-system study modes.

### Latest Part I review tranche (complete)

- [x] correct the nonlinear witness prose so primal-variable counts are not
  confused with KKT dimensions (7 source variables versus 5 aggregate
  variables; 13 is the source KKT dimension);
- [x] report rank-aware effective condition estimates for the singular Ybus
  witness, while retaining the ordinary estimates only as diagnostic signals;
- [x] state explicitly that complex transpose symmetry need not survive the
  realified coordinate embedding, and bind that distinction to the generated
  witness and `NUMERICAL-002` claim;
- [x] remove the rating-record notation collision by using ``\chi`` for
  scenario validity and ``\omega`` for provenance/protection ownership;
- [x] remove duplicate Roman-part labels from the HTML navigation and promote
  rating semantics and the data-model crosswalk into the curated PDF route;
- [x] add the translation table from limit dispositions to preservation
  contracts, with a record-by-record qualification.

**Exit criterion:** the Part I reference and numerical chapters agree with the
executed witness fields, use unambiguous notation, and are present in both
reader-facing serialisations.

### Transformation-language review tranche (complete)

- [x] repair the neutral-rating admonition indentation and bare ``\leq``
  command, and make the callout and math hygiene checks gate these failures;
- [x] split the long Kron witness by fixture and question, with one scope table
  covering the running-network, earth/grounding, state-dependent, and five-bus
  claims;
- [x] register definition claims for observation-indexed preservation
  contracts and the four-layer transformation semantics register;
- [x] mark the v1.2-only `error_bound` field at the table row where it is
  proposed rather than current-schema-required;
- [x] place the guarded-rule gate figure at the first executable series rule;
- [x] extend the math lint from isolated ``ell``/``Pi`` checks to a controlled
  set of commonly mistyped bare TeX command names.

**Exit criterion:** transformation chapters have auditable callouts, explicit
scope boundaries, definition-level ledger coverage, and a visible guarded-rule
template before the later transformation cases.

### Guarded-patterns review tranche (complete)

- [x] distinguish terminal-column permutations ``P_{xk}`` from coil-row
  permutations ``Q_{xk}`` in the adjacent transformer chapters;
- [x] replace the catalogue's duplicated series-elimination derivation with a
  coordinate-aware pointer to the dedicated executable rule;
- [x] give the guarded-normalization catalogue a stable anchor and a scoped
  catalogue claim;
- [x] promote transformer-winding normalization and the guarded catalogue into
  the PDF route alongside the dependent multiwinding assembly chapters;
- [x] write the dual current relation as explicit equations and add a
  maintainable row-versus-column action figure.

**Exit criterion:** the guarded-pattern section has one authoritative series
rule, unambiguous transformer coordinate actions, complete HTML/PDF coverage,
and a visual bridge for the two permutation types.

Deferred follow-ups from this review: replace the remaining chapter-local raw
LaTeX pagination hacks with a template-level float policy, and either wire the
legacy `five-bus-feasible-sets`/`numerical-structure-witness` raster assets into
reader-facing chapters or retire them after checking historical references.

### Research-record review tranche (complete)

- [x] publish a generated review-protocol/evidence-status chapter with
  protocol version, snapshot date, checksums, database coverage, search runs,
  screening counts, coding status, and the explicit single-coded boundary;
- [x] add scoped status lines to every research-agenda candidate result;
- [x] give the research agenda a stable anchor and include it in the PDF route;
- [x] add a literature-attention/gap-map figure linked to the current
  assessment table;
- [x] replace hand-maintained literature-map counts with a link to the
  generated status page;
- [x] refresh the review snapshot manifest after its bibliography-input hash
  drift and verify the snapshot checker passes.

Deferred: apply the second-coding recommendations to the canonical matrix only
after independent human review and recorded conflict resolution; add a
PRISMA-style flow figure once the full screening pipeline has published stable
counts.

### Reference-section review tranche (complete)

- [x] expand the notation table with the high-use Greek symbols ``\sigma``,
  ``\pi``, ``\alpha``, ``\Lambda``, ``\rho``, ``\kappa``, ``\Theta``, and
  ``\eta``, including their competing scopes and qualifiers;
- [x] make the evidence-map prose name the empty measurement, state,
  numerical-structure, and external-review regions rather than leaving the
  reader to infer gaps from pixels;
- [x] add stable anchors to notation, terminology, and references;
- [x] clarify the retrieval roles of the knowledge-base and vocabulary indexes;
- [x] add limit dispositions and observed-set preservation classes to the
  maintained terminology surface.

### PDF table-of-contents refinement (complete)

- [x] expose internal subsection entries for the reader-facing start,
  foundations, transformations, and worked-case chapters;
- [x] keep generated indexes, literature records, references, and archived
  search runs at chapter level so the TOC remains a reading aid;
- [x] retain linked search-run content in the PDF while suppressing its
  artificial child-page entries.

### Rendered-output validation tranche (complete)

- [x] add a PDF TOC-policy check for the selected subsection chapters and the
  intentionally chapter-level reference/search-run pages;
- [x] check expected HTML page inventory, nonempty titles, image alt text, and
  empty-link regressions;
- [x] check PDF text extraction, page count, compiler-log markers, and a
  cover-page raster smoke test;
- [x] wire the rendered-output check into the README validation recipe and the
  documentation workflow.

Visual comparison against stored page snapshots and human assessment of
mathematical correctness, pedagogy, and typography remain separate review
activities rather than pretending to be machine proofs.

M1 (integrity and reproducibility) is complete. M2 (reduction evidence) and M3
(graph architecture) satisfy their scoped book claims; their remaining broad
items are research extensions, not publication blockers. M4 (systematic
literature work and external validation) remains open. Historical review
dispositions are retained in [`review/archive/`](review/archive/).

### Now — formulation equivalence and the nodal-admittance boundary (complete)

- [x] add the precise nodal rank/nonsingularity guard and its
  Kettner--Paolone scope, making clear that a declared ground or reference does
  not alone prove the required rank;
- [x] define current signs and MNA right-hand-side terms, consolidate the
  nodal-stamping guards, and state that ``\Phi_{\mathrm{lin}}`` excludes
  unfixed decision-carrying factors;
- [x] separate branch-current, branch-flow/BFM, chain/ABCD, hybrid, and
  scattering formulations, including the singular-partition caveat;
- [x] define formulation equivalence relative to a declared observation family
  and preservation contract;
- [x] make the formulation chapter authoritative for assembly and formulation
  guards, remove its duplicated parallel-line derivation, and register the
  lowering architecture as a proposal claim. The formulation-lattice figure is
  already complete.

**Exit criterion:** the book can state exactly when a nodal-admittance target
exists, when another circuit formulation is required, and what “equivalent
formulations” preserve for the declared study.

### Next — general multi-port lowering (complete)

- [x] extend the composed transformer witness to an evaluated four-winding
  factor with a full non-diagonal reference matrix, connection-specific
  shunts, grounding, controls, and retained decision observations;
- [x] state and test the realizability boundary for direct factor stamping,
  generated edge models, and terminal support without implying that every
  ``n``-port has a source-faithful ordinary-edge realization;
- [x] test the layer--lens matrix against concrete power-system data,
  optimization, sparse-matrix, and graph-learning APIs without assigning an
  entire package to one stage.

**Exit criterion:** the three-winding example is demonstrably a pedagogical
special case of an architecture that remains valid for a nontrivial
four-winding model.

### Parallel editorial tranche — diagram and equation bridge (complete)

- [x] add a Start Here bridge explaining how to read diagram levels, stored
  orientation, KCL, KVL, Ohm/constitutive laws, lossy edges, and scalar versus
  matrix-valued branch relations;
- [x] qualify *vector-valued multigraph* as a useful two-terminal bridge phrase
  while retaining typed port--factor incidence as the canonical n-port model;
- [x] expand the two-level topology chapter with block nodal structure,
  scalar-expanded support, Schur fill, and complex-to-realified coordinates;
- [x] add the PowerModelsDistribution four-wire current-injection report as a
  traceable literature bridge;
- [x] add the paired four-panel diagram (asset/vector edge, port--factor,
  block nodal matrix, scalar/realified support);
- [x] add an executable block-structure witness before registering a stronger
  block-support claim.

**Exit criterion:** a reader can translate one scalar line diagram into a
matrix-valued multiconductor equation and a block nodal operator, then explain
which graph cycles, identities, and coordinates are introduced or forgotten by
each view.

### Label-before-coordinate pedagogy (complete)

- [x] state in the opening equation-reading chapter that semantic labels and
  storage coordinates are different objects;
- [x] show an explicit enumeration map from named buses to ordinary array
  positions, including the scalar/block distinction for ``Y_{ij}``;
- [x] apply the same labelled-index principle to the signed incidence and
  edge--cycle matrices in the five-bus example;
- [x] add a maintainable semantic-label-to-storage-coordinate diagram;
- [x] add a short vocabulary-bridge entry for “label-indexed relation,”
  “enumeration,” and “array position” to the reference terminology page;
- [x] audit the remaining opening-route chapters for equations that use
  integer-looking subscripts without declaring whether they are labels,
  coordinates, or phases; qualify member, winding-pair, and generic graph
  indices where needed.

**Exit criterion:** a new reader can read ``Y^{\mathrm N}_{ij}`` as a labelled
block relation, understand how it becomes an integer-indexed array, and see
that reordering storage cannot change the underlying network semantics.

### Audience-specific reading guide (complete)

- [x] add parallel onboarding routes for simple-graph readers and balanced
  transmission readers;
- [x] name the conceptual leaps: terminal factors, vector-valued buses,
  multigraph identity, support cycles, n-port devices, lossy terminal
  quantities, neutral recovery, and formulation boundaries;
- [x] converge both routes on the first decision counterexample and the
  preservation-contract language;
- [x] link the guide from the Start Here navigation and home reading route.

**Exit criterion:** a reader can enter from either simple graph theory or
balanced transmission modelling, identify what must be expanded or qualified,
and reach the same multiconductor decision semantics without treating either
starting model as the universal ontology.

### Start Here review repair tranche (complete)

- [x] repair the graph/transmission guide's BMOPFTools-style ``\ell`` notation;
- [x] align the block-structure figure with the ``ARCH-BLOCK-001`` 8×8 witness,
  including the two-port/four-conductor distinction and all 64 scalar supports;
- [x] shorten the guide to a routing page rather than a duplicate teaching
  chapter, and place the vocabulary bridge before it in HTML and PDF navigation;
- [x] add a maintainable two-route convergence figure and register its SVG/PNG
  pair in the figure audit;
- [x] add math-hygiene validation for bare ``ell``/``Pi``, orphan ``\mathbf``,
  and unbalanced inline math delimiters, and run it from artifact checks.

**Exit criterion:** the Start Here route is concise, the visual claims agree
with their executable witnesses, navigation follows the intended onboarding
order, and the notation slips called out by review fail the validation gate.

### Canonical-model section review tranche (complete)

- [x] repair doubled-backslash inline math, add stable anchors for both running
  fixture chapters, and use those anchors in source and generated references;
- [x] include the executable running-network evidence in the PDF route;
- [x] standardize the Fortescue transform as ``\mathbf F`` while retaining
  ``\mathbf A`` for incidence, and document ``C_+``/``E_+`` and the restricted
  observation factorization;
- [x] register the source-adapter and impedance-data publication contracts as
  scoped practice claims and check their required fields;
- [x] add the load-model divergence/continuation figure, source validation
  pipeline, and impedance-fidelity ladder figure to the maintained audit.

**Exit criterion:** the canonical-model section has no fragile fixture links,
its paired reduction chapters use one transform vocabulary, the PDF carries
the executable evidence, and the three central “same graph, different model”
arguments have maintainable visual summaries.

### Parallel AC evidence-section review tranche (in progress)

- [x] include the three parallel AC decision chapters in the curated PDF route;
- [x] state the nominal-``\pi`` conditioning and relative-margin thresholds;
- [x] separate singular-map, jointly retained, and state-conditioned evidence
  in the nominal-``\pi`` chapter and repair the ``\ell`` indices;
- [x] report relative non-proportionality and distinguish absolute p.u.
  currents from rating fractions in the four-wire tables;
- [x] register the source-backed Australian Carson/OpenDSS reproduction as a
  scoped empirical claim, retaining the unresolved CS1035 boundary;
- [x] add and audit a maintained certificate-geometry/decision-gap figure;
- [x] independently re-derive the generated series-elimination certificate with
  an explicit cross-coupling witness and expose the element-pair model field
  that a junction-only representation cannot carry;
- [x] formulate a separate exact rule for eliminating a complete mutually
  coupled section pair, with an explicit four-term impedance identity,
  pair-keyed coupling guards, recovery/constraint maps, executable tests, and
  certificate evidence; independent mathematical review remains open.

**Exit criterion:** the parallel case chapters expose their numerical guards,
units, evidence boundaries, and PDF route, while coupled-section elimination
is a separately scoped, self-checked rule rather than an implicit extension;
named independent mathematical review remains an external validation item.

### Then — literature and external validation

- [x] reconcile the claims ledger and canonical evidence matrix, add the
  Gan--Low and practical feeder/transmission records, and encode the shared
  CGMES/PowSyBl topology transformation without treating the sources as
  duplicates;
- [x] exercise genuine ``exclude`` screening decisions and resolve
  automated-versus-human reviewer metadata; the current matrix has one
  explicit exclusion and machine-readable review bases.
- [ ] execute and archive database exports and complete an independent human
  double-coding pass before using *systematic* or PRISMA-style language.

The following work is **externally blocked or conditional**, so it is not part
of the unchecked active queue: recovering missing Australian source
frequency/order and cable-construction provenance; solver-native
BMOPFTools/KKT row and factorization exports; external terminology and
technical review; and publishing/tagging the standalone package after that API
review. No stronger claim should be made while its stated gate remains open.

The following work is **later research scope**: global nonlinear recovery,
noisy partial inverse problems, general singular AC reductions, richer
continuous multiwinding controls, full optimizer-independent guarantees, and
formal categorical composition. Conditional chapter splits, extra figures,
and vocabulary additions should be undertaken only when retrieval tests,
evidence, or a concrete false inference justifies them.

### How to read the remainder

The sections below preserve the scientific and editorial history. Completed
checkboxes document delivered work. Remaining ambitions are labelled
**Next**, **Later**, **External**, **Conditional**, or **Gate** and point back
to the queue above; they are not a second active task list.

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

The subsequent editorial tranche is complete:

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

The narrow-circuit transformation tranche makes commonly used star--delta and
shunt-placement manipulations explicit instead of leaving them implicit in
equipment models:

- [x] add a reader-facing register entry and guarded scalar formulas for
  floating star--delta / delta--star conversion, including the distinction
  between fixed linear terminal equivalence and preservation of grounding,
  branch limits, switching, and asset identities;
- [x] state why the scalar formulas do not automatically lift to arbitrary
  coupled multiconductor blocks, and route those cases through typed Schur
  complements or port--factor relations;
- [x] document endpoint shunts as two independently placed terms, including
  capacitor banks, neutral-ground points, and magnetizing branches, and state
  explicitly that unequal endpoint diagonals do not imply non-reciprocity;
- [x] add the adapter rule for tools with only one shared line-shunt field:
  retain an explicit shunt or generic endpoint-augmented factor and report the
  loss of semantics rather than silently averaging from/to shunts;
- [x] add executable witnesses for scalar Y--Delta conversion, rejection of a
  grounded-star case, and asymmetric-shunt adapter diagnostics before adding
  these transformations to the stronger claim ledger.

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
- [x] reproduce the available authored overhead-line and underground-cable
  construction cases as bounded local studies with load, grounding,
  voltage/loss, and available geometry/linecode provenance; reserve *faithful
  source reproduction* for the provenance gate below;
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
- **External:** recover an explicit source declaration for the overhead
  reference frequency/order and the raw cable construction mapping for CS1035.
- **Gate:** claim a faithful reproduction of those reference cases only after
  the preceding provenance mappings are available.

The two-level topology and nodal-projection tranche is part of the completed
graph-architecture record:

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
- **Later:** extend the guarded classification to noisy partial observations,
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
- **Coverage rule:** use the generated fixture-coverage matrix to expose
  specific direct-evidence gaps; do not require every map to apply to every
  fixture when the combination is explicitly not applicable;
- [x] add a generated fixture-coverage matrix that distinguishes direct,
  related, not-yet-tested, and not-applicable evidence for those three
  canonical fixtures; the five-bus port--factor lift is now direct evidence,
  and its scalar conductor-terminal lift is now direct evidence as well,
  together with direct inventory/active radiality checks on the five-bus case,
  and a direct scalar typed-Kron check for its pendant bus ``m``,
  extended with a non-pendant ``l`` elimination that records retained
  Schur-complement fill edges and an exactly recovered but deliberately
  violated ``u``-branch limit,
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
- **External:** obtain independent review from both graph/formal-methods and
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
- [x] connect the structural crosswalk to public JuMP/MOI nonlinear Jacobian
  structure and a captured KKT callback with explicit row/order caveats. The
  remaining solver-native row identities and factorization diagnostics are
  recorded once as an external boundary under M2.

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
- **External:** publish/tag that package after external review of its API and
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
work belongs in the current dashboard, not in this archive.

## Milestone record

### M1 — Integrity and reproducibility release

**Status:** scoped internal milestone complete; external review is the next
release gate for the externally validated book and package, not an optional
replacement for the internal checks.

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
- **External:** obtain independent reviews of the highest-risk claims,
  prioritizing `TR-KRON-001`, `TR-PAR-004`, `TR-SER-001`, and `TR-XFMR-001`,
  after the active R0--R4 readiness programme has produced a stable packet;
- [x] prepare and archive a reproducible reviewer packet with claim-specific
  artifacts, commands, assumptions, and an explicit reviewer record;
- [x] make claim type, verification state, artifact, and unresolved issue
  cross-checks fail closed in the local and CI checks.

**Exit criterion:** a clean internal release candidate whose claims, chapter
statuses, figures, HTML, PDF, and generated artifacts agree. External review is
not required for this internal milestone, but it is required before describing
the book as externally validated or publishing a reviewer-backed release.

### M2 — Reduction evidence

**Status:** scoped milestone complete; unresolved global and richer-control
extensions are later research rather than blockers.

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
- **Later:** extend the nominal-``\pi`` and parallel-limit cases to singular maps,
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
- **External:** connect the crosswalk to BMOPFTools/solver-exported KKT rows and
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
- **Later:** extend the switching-cost and branch-completeness contract to richer
  unbalanced multiwinding network decisions and continuous/global guarantees.

**Exit criterion:** a reproducible comparison showing when each reduction is
exact, conservative, relaxed, or scenario-approximate for declared decision
observations.

### M3 — Graph architecture and topology

**Status:** core scoped milestone complete; the general multi-port extension is
also complete for the current evaluated, package-independent scope.

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
The completed graph-architecture tranche was scoped around **identity,
visualisation, lowering, and surgery**. The chapters define identified
equipment, port--factor structure, state-conditioned topology, and provenance;
the tranche made their relationship explicit and added diagnostics for when a
power-system drawing or algorithm silently changes the object set. The
identity-agnostic high-level graph is treated as a
quotient view with source fibres, not as a competing canonical model. Likewise,
ordinary-edge expansion is a lowering target, not permission to discard
n-port, grounding, switch, or asset semantics.

- [x] define an identity-bearing source graph contract with equipment/factor
  identities, terminal and port sets, n-port objects (including multiwinding
  transformers), and explicit quotient maps to identity-agnostic views;
- [x] define a typed visualisation registry for single-line, multi-line,
  port--factor, node--breaker, nodal-support, and reduced/Kron views, recording
  preserved and forgotten semantics, port multiplicity, grounding, switch
  state, identity fibres, and whether a reverse map is available;
- [x] add explicit source-to-view map records with reverse-map status and a
  reader-facing “one source, four views, three surgeries” diagram;
- [x] specify a compiler-like lowering contract from the typed source graph
  through canonical port--factor form and ordinary-edge incidence form to
  numeric operators/Jacobians, with provenance and omitted-semantics records
  at every boundary;
- [x] add state-conditioned graph-surgery semantics for galvanic zones,
  open-all-switches, energized subgraphs, active radiality, switch elimination,
  and component families, returning state-indexed graphs plus diagnostics
  rather than one silently selected graph;
- [x] define separate two-terminal and n-terminal surgery rules while
  preserving phase, neutral, earth, and grounding-coordinate identity;
- [x] add degeneracy and under-determination diagnostics for duplicate ideal
  switches in parallel, duplicate factor/terminal sets, phase-only switching
  in multi-grounded neutral networks, missing references/grounding, and
  singular active-state maps; these are model-quality findings, not reasons
  for an algorithm to invent physical intent;
- [x] add executable witnesses for (i) a multiwinding transformer lowered to
  ordinary edges with a retained factor/provenance fibre, (ii) parallel ideal
  switches with an ambiguity certificate, (iii) phase-only switching whose
  phase and neutral connectivity/radiality queries disagree, and (iv)
  open-switch/galvanic-zone surgery that returns a family of active graphs;
- [x] extend the witness with port-selective n-terminal surgery and explicit
  missing-reference and singular-active-map diagnostics;
- [x] add reader-facing claims and a compact “source graph to views and
  surgery” chapter, then cross-link it to the formal-representation,
  node--breaker, cycles/radiality, and transformation-register chapters;
- [x] keep the lowering/surgery claims scoped to declared state and model
  classes; broad category-theoretic or optimizer-independent guarantees stay
  deferred until independent evidence exists.

The 2026-08-15 expert review of this tranche adds the following repair plan.
The review's central corrections are accepted: realizability conditions must be
carried with any n-port-to-edge lowering, direct factor stamping is the default
path, duplicate ideal switches are an asset-attribution ambiguity rather than
an electrical degeneracy, and unknown-state families need a scalable summary.

- [x] repair the chapter's Markdown math fences and inline math delimiters;
- [x] reconcile the chapter's shorthand source tuple with the canonical
  ``\mathfrak P`` notation and make direct stamping versus optional lowering
  explicit;
- [x] condition edge-only three-port realization on
  ``\mathbf Y_\phi\mathbf 1=0`` and point to the line--shunt realizability
  proposition when residual shunts are required;
- [x] classify duplicate ideal switches as asset-attribution ambiguity and
  retain the well-defined electrical quotient;
- [x] state the ``2^n`` enumeration bound and add a three-valued
  certainly-connected/certainly-separated/undetermined summary;
- [x] cite the typed graph-transformation, CIM/PowSyBl, and nanopass compiler
  precedents, while explicitly scoping the book's DPO relationship as a
  vocabulary/roadmap rather than a completed rewrite calculus;
- [x] reconcile the compact figure with the six-entry registry, repair its
  arrow routing, and correct the six-case description;
- [x] reclassify normative architecture statements as ``proposal`` claims;
- [x] make the node--breaker, representation-taxonomy, and compiled-views
  chapters defer to one authoritative definition each, retaining only
  cross-links and application-specific qualifications;
- **Next:** add independent review or executable evidence for the full
  n-port-to-edge realizability conditions beyond the scoped witness.

**Exit criterion:** the proposed representation architecture has checked maps
and topology witnesses on the running network, not only prose definitions.

### Representation-landscape and circuit-formulation tranche

This tranche distinguished literature context from the book's adopted
formalism and made the lowering boundary honest about cases where an exact
nodal-admittance operator does not exist or is not the right target. Its
remaining formulation details are now owned by the **Now** dashboard.

- [x] add a reader-facing representation-landscape section (or chapter) that
  surveys simple, multi-, directed/oriented, hypergraph, incidence/factor,
  port-Hamiltonian/bond-graph, asset/dependency, equation, sparsity, and
  tableau/MNA families;
- [x] classify each family as selected source, derived view, equivalent
  alternative, scope-specific collapse, or orthogonal companion, with a
  preservation/omission matrix and explicit canonicality status;
- [x] justify the book's chosen source pair as sufficiently canonical for the
  stated multiconductor, multi-terminal, and decision-problem scope without
  claiming universal uniqueness or community-wide standardisation;
- [x] expand the literature map with primary references, a dated seed search
  protocol, and coded evidence-matrix rows for graph-model and
  circuit-formulation precedents (not only network-reduction papers);
- [x] add an operational coding guide, DOI/title deduplication register, and
  citation-chasing records for official information-model and software sources;
- [x] add a hash-checked review snapshot manifest that joins matrix rows to
  deduplication records and explicitly records the single-coded status;
- **Gate:** do not call the literature review systematic until the M4 database
  exports, deduplication, citation chasing, and independent double-coding are
  complete;
- [x] add a circuit-formulation chapter covering nodal admittance, modified or
  sparse tableau, branch-current, hybrid, and general port/factor relations.
  State precisely that nodal admittance is powerful for an important class of
  reduced linear networks, but is not a universal representation of general
  *power networks*: asset identity, switching, controls, limits, grounding,
  multi-terminal behaviour, and decision semantics may be absent even when a
  numerical ``\mathbf Y`` can be assembled;
- [x] document the conditions under which exact nodal stamping is unavailable,
  singular, or semantically lossy, and when a tableau/factor target is the
  faithful lowering result;
- [x] revise the compiled-view lowering contract so its numeric target is a
  general declared equation/constraint operator, with nodal admittance as an
  optional target guarded by formulation and device assumptions;
- [x] add a minimal witness with a general circuit element that is representable
  in tableau/factor form but not as an exact ordinary nodal-admittance graph,
  and record the resulting lowering diagnostic and provenance boundary;
- [x] cross-link the landscape, formal-framework, two-level-topology,
  compiled-view, numerical-consequences, and positive-sequence chapters, then
  update the reader routes and chapter-status index.

**Exit criterion:** a reader can see which graph/circuit frameworks exist, why
the book selects its source pair, what collapses for the declared scope, and
why the lowering pipeline may terminate in a tableau or factor operator rather
than an exact ``\mathbf Y`` matrix, even when some reduced numerical nodal
equation could be formed.

### Urgent review-repair tranche — 2026-08-15

This tranche reconciles three distinct review streams without conflating their
status:

1. the expert review of the circuit-formulation and lowering chapter;
2. the automated independent technical review in
   [`review/independent-technical-review-2026-08-15.md`](review/independent-technical-review-2026-08-15.md);
3. the automated literature second-coding log in
   [`review/second-coding-2026-08-15.md`](review/second-coding-2026-08-15.md),
   whose working snapshot is
   [`review/snapshots/evidence-matrix-second-coding-2026-08-15.csv`](review/snapshots/evidence-matrix-second-coding-2026-08-15.csv).

Both automated passes are valuable reproducible audits, but neither is human
peer review. They must not populate metadata in a way that implies external
human validation. The second-coder snapshot remains non-canonical until each
conflict below is resolved and recorded.

#### A. Circuit-formulation and lowering chapter

The details in this subsection were the formulation milestone in the current
dashboard; the completed entries are retained here to preserve their review
provenance.

- [x] add explicit MNA/tableau structural-solvability diagnostics for ideal
  voltage-source loops and ideal current-source cutsets, distinguishing
  redundant consistent constraints from contradictory constraints; do not
  make a general DAE-index claim without a precise supporting source;
- [x] add the nodal-admittance rank/nonsingularity guard, with the relevant
  Kettner--Paolone result, and state that merely declaring grounding or a
  reference does not by itself establish the required rank;
- [x] merge overlapping nodal-admittance guards, define the current sign
  convention and MNA right-hand-side terms, and state explicitly that
  ``\Phi_{\mathrm{lin}}`` excludes decision-carrying factors;
- [x] add chain/ABCD formulations, separate branch-current formulations from
  branch-flow/BFM formulations, and note scattering variables as a possible
  remedy when a chosen hybrid partition is singular;
- [x] define equivalence between formulations relative to a declared
  observation family ``H`` and its preservation contract, rather than treating
  algebraic interconvertibility as semantic equivalence;
- [x] make the circuit-formulation chapter authoritative for assembly
  identities and formulation guards, while the two-level-topology chapter owns
  topology, support, projection, and non-identifiability;
- [x] compress the duplicated parallel-line witness, cross-reference its
  authoritative claim/case, and register the lowering architecture as a
  proposal claim. The formulation-lattice argument figure is complete.

#### B. High-risk technical claims and certificates

- [x] **Resolve the `TR-SER-001` publication hold.** State that both factors must be
  series-only and that there is no mutual coupling either with other elements
  or between the two eliminated sections. For cross-coupled sections, document
  the exact composite
  ``Z_1 + Z_{12}P + P^{\mathsf T}Z_{21} + P^{\mathsf T}Z_2P`` rather than
  ``Z_1 + P^{\mathsf T}Z_2P``;
- [x] redesign the series-elimination data contract so mutual coupling is an
  element-pair property that the guard can inspect, not junction free text;
  add a negative executable witness reproducing the reported 11.65% relative
  error before releasing the hold. The repaired rule and adjacent coordinate
  normalization now fail closed on declared pair coupling, the focused tests
  pass 22/22 in each suite, and the aggregate and clean-package suites pass;
- [x] revise `TR-KRON-001` to separate the mathematical requirement that the
  coordinate action respect the retained/internal partition from the stronger
  modelling choice of per-port block diagonality; add the load-bearing
  assumption that internal current injections are fixed data independent of
  internal voltage, plus a voltage-dependent-injection counterexample. The
  typed witness now exercises dense within-partition actions and records the
  fixed-injection scope probe;
- [x] sharpen the Kron reciprocity discussion by separating physical Kron
  reduction from complex power-dual coordinate action, and record numerical
  conditioning in the witnesses;
- [x] repair the `TR-XFMR-001` certificate with the terminal-current dual map
  ``\widehat i=Pi``, terminal- versus coil-indexed limit semantics, and a
  complex-power-invariance check; remove the unfalsifiable
  `all_declared_source_semantics` entry and populate `evidence.checks` from the
  executable assertions;
- [x] record `TR-PAR-004` as mathematically reproduced by the automated audit,
  while adding the high-voltage-branch/local-solve caveat and the exact-
  proportionality scope of the pruning result; do not label it human-reviewed;
- [x] refresh the independent-review packet: `running_network_typed_kron` is
  13/13 rather than 7/7, and its scope note must acknowledge the existing
  neutral-shunt witness. The refreshed 2026-08-15 packet preserves the stale
  2026-08-14 snapshot as archival history.

#### C. Evidence-matrix reconciliation and coverage

- [x] reconcile the six controlled-field conflicts from the non-canonical
  snapshot, apply the recorded decisions to the canonical matrix, and retain
  `single_coded` status pending a genuine independent second pass; the
  field-by-field decisions are recorded in
  [`review/evidence-matrix-reconciliation-2026-08-15.md`](review/evidence-matrix-reconciliation-2026-08-15.md);
- [x] repair the `provenance_map` slot errors in `EV-0007`, `EV-0010`, and
  `EV-0012`, moving limitation prose to `limitations`, and soften the
  over-reading of MNA multi-terminal scope in `EV-0005`;
- [x] add a controlled `exactness_object` field to the schema, coding guide,
  validator, and canonical matrix so equation identity, connectivity quotient,
  boundary behaviour, feasible-set preservation, and observation-sample
  agreement are not aggregated as though they were the same object;
- [x] expand the evidence matrix beyond the initial 14/35 bibliography seed
  coverage with the classical Ward family and the priority
  `DorflerBullo2013`, `Jang2013`, `CurtisMorrow2000`, and
  `KettnerPaolone2019` records; the controlled scope and exactness-object
  decisions are recorded in the reconciliation note;
- [x] add the Gan--Low formulation records and practical feeder/transmission
  reductions, then reassess whether any source needs split rows; the targeted
  2026-08-16 pass retained one scoped row per source and documented why no split
  was required yet;
- [x] exercise the screening protocol with a genuine `exclude / wrong_domain`
  record (`EV-0029`) and retain the explicit limitation that one screened seed
  is not a corpus-flow count or a PRISMA-style review;
- [x] resolve the reviewer/date consistency rule, and distinguish automated
  agreement, human double-coding, and external technical review explicitly in
  the metadata; the new `review_basis` field and fail-closed validator keep all
  29 current rows as `single_coded` until a genuine human second pass occurs;
- [x] record that the CGMES and PowSyBl rows describe the same underlying
  connectivity-node-to-topological-node transformation without treating the
  sources as duplicates, then regenerate and validate the canonical snapshot.

**Exit criterion:** no blocking claim is labelled established while a required
assumption is absent or unrepresentable; the transformer and Kron certificates
state their complete typed maps; the formulation chapter has symmetric
solvability and equivalence guards; and all evidence-matrix conflicts are
resolved without presenting automated audits as human review.

### M4 — External validation and dissemination

**Status:** open external gate. It is not required to keep developing the
scoped M1--M3 material, but it is required before systematic-review language,
external-validation claims, a reviewer-backed book release, or a package
release. The active R0--R4 programme above defines the preparation sequence;
M4 begins when the stable packet is sent to external reviewers.

- **External:** execute and archive the planned database searches and populate the
  evidence matrix with double-coded seed results;
  - a 2026-08-14 web seed batch is archived in
    `review/search-runs/2026-08-14-seed-batch.md` and adds three scoped
    single-coded records; database exports and second-coder review remain open;
- [x] generate a current blank second-coding worksheet from the canonical matrix;
  it contains all 29 records and does not promote any row or count as human
  review;
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

The new identity/lowering tranche adds a semantic requirement to this visual
grammar: every diagram must declare whether it is an identified source view,
a quotient, a lowered algorithmic view, or a lossy reduced view. The registry
should make the forward map and any recoverable source fibre visible in the
caption or companion metadata; a visually neat single-line diagram is not
evidence that n-port, grounding, switch-state, or member-identity semantics
survived.

#### Guarded-case evidence-plate tranche — 2026-08-16

The next-section review identifies an evidence-distribution problem: the
numerical-consequences chapter held most of the figures while the executed
case chapters had none. The immediate repair is to make the book's own audit
method visible at the point where a reader evaluates a reproduction. A
generated result plate is a summary of an artifact, not a replacement for its
certificate; it must expose claim identity, classification, source scope,
discharged guards, residual, cross-check, and open item.

- [x] add a reusable artifact-derived guarded-result plate and link it from
  the Australian Carson case;
- [x] add the four-wire transformation-ladder plate: green edge-local checks,
  a red endpoint, and accumulated unresolved guards;
- [x] add the overhead Carson reconciliation plate with frequency and
  conductor-order probes shown as diagnostic knobs;
- [x] add the CS1035 unresolved-data plate, retaining the failed probe as a
  credibility result rather than relabelling it a reproduction;
- [x] instantiate decision/evidence plates for the transformer-tap and
  parallel-line cases, and add the BIM/BFM member-signature capability plate;
  each plate states whether it is artifact-backed or notation-only;
- [x] reuse `transformer-anatomy.png` in the multiwinding terminal-leakage
  case; decide later whether conductor-coordinate normalization deserves its
  own plate or belongs inside the impedance ladder;
- [x] move conceptual numerical-fill-in and Jacobian-dependency figures to
  the core formulation/lowering chapter, leaving only executed witness figures
  in the numerical-consequences chapter;
- **Conditional:** revisit whether the overloaded guarded-case section should become a
  separate Part after the case-plate tranche is stable.

**Exit criterion:** every executed case has either an artifact-derived result
plate or a documented reason that its evidence is not yet expressible in the
shared template; unresolved source mappings remain visibly unresolved.

#### Reference-section navigation and evidence tranche — 2026-08-16

The reference review correctly treats this section as queried infrastructure,
not a miniature narrative. The generated knowledge-base index should remain
complete and machine-readable; the repair is to add compact navigational and
relational views that cannot drift from `claims/claims.toml`.

- [x] add generated symbol anatomy showing element identity, relation role,
  oriented attachment, and coordinate slots;
- [x] add a terminology distinction map for bus, transformation, exactness,
  state, and flow clusters;
- [x] add a claims-derived evidence map with visible empty cells and an
  explicit warning that facet counts are retrieval aids, not literature
  completeness claims;
- [x] add a claims-derived verification summary showing the current
  self-checked, independently-implemented, and externally-reviewed states;
- [x] include the evidence map and verification summary in both HTML and the
  curated PDF route;
- [x] add explicit preservation-dimension fields to the claims schema and use
  the controlled dimensions to drive the evidence map (the remaining
  transformation-family × dimension synthesis is a later literature task);
- **Then:** reconcile the claims ledger with the second-coded literature matrix and
  display classical Kron/Ward coverage as a separate evidence-matrix view,
  without treating frequent citation as a coded record;
- **Conditional:** reduce generated-index verbosity only if retrieval tests show a concrete
  failure; do not replace the complete index with a hand-curated summary.

**Exit criterion:** a reader can decode notation, resolve a terminology
collision, inspect evidence coverage, and see verification state without
reading the 20,000-word generated index; the HTML and PDF summaries are
generated from the same source ledger.

#### Structural-section diagram review — 2026-08-15

The next-section review changes the figure test from surprise to reuse: formal
objects should have canonical glyphs, distinctions should be shown side by
side with numbers, and each transformation family should have a stable visual
card. The following tranche is now implemented:

- [x] place the existing map-of-maps and query-partial-orders plates in the
  PDF-facing formal-representation-frameworks chapter;
- [x] draw the canonical ``\mathfrak P`` port--factor object with explicit
  ports, junction bars, separate ``j``/``f`` incidence arrows, containment,
  and the many-to-many ``\Lambda`` asset relation;
- [x] add the numerical three-route impedance plate from
  ``IMPEDANCE-LADDER-001``; explicitly show that the phase-to-phase quotient
  is 2×2 rather than mislabelling it as a 3×3 matrix;
- [x] add the projection/normalization/compilation/behavioural-reduction
  size-inversion plate, marked as schematic rather than a new numerical
  witness;
- [x] strengthen the topology-projection figure's port-incidence legend;
- [x] design the reusable translation-trap card and typed transformation
  register glyph plate after the structural source vocabulary is reviewed;
- **Conditional:** revisit chapter splitting for the overloaded Kron/Ward/Opti-KRON and
  two-level-topology chapters rather than adding more figures to them.

The review's claim that the topology-projection panel had no ports was stale:
the current panel already contains factor-boundary port nodes. The repair makes
the ``j``/``f`` distinction explicit instead of redrawing the object.

#### Start-here hook tranche — 2026-08-15 review

The start-here review correctly identifies a missing pedagogical layer: the
opening figures must create a numerical surprise and immediately name the
semantic distinction that resolves it. The first high-value hooks are now
implemented:

- [x] draw the reusable running-network source layout and use it as the
  reference drawing for later views;
- [x] draw the radial-bus/tree versus conductor-expanded support/clique
  contrast, with the resolution **which graph?**;
- [x] draw the same-``Y``-bus/different-dispatch counterexample, with the
  resolution **which observations and constraints?**;
- [x] draw the neutral-recovery hook, with ``43.0\ \mathrm{A}`` against a
  ``42.6\ \mathrm{A}`` limit and the resolution **what must be recovered?**;
- [x] add a source-bound negative-star-arm panel and promote its positive-
  semidefinite matrix guard as reader-facing evidence (the guard is
  ``\operatorname{Im}(Z_B)\succeq 0``, not componentwise arm positivity);
- **Conditional:** add the paired “eight constraints deleted” panel only after the exact
  redundancy and naïve aggregate objectives are bound to a dedicated,
  source-traceable witness rather than review prose.

The generated SVG/PNG assets are registered in `figure-audit.json`, and the
three opening chapters now state the belief, numerical failure, and resolving
semantic word in their captions and surrounding prose.

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
- [x] add a reading-route map for the HTML/PDF spine and revise it for the five
  target communities;
- [x] add sequence-subspace geometry for the positive-sequence collapse;
- [x] add a four-overlay “what does bus mean?” figure for node--breaker and
  compiled bus--branch views;
- [x] draw certificate composition and the guarded-rule gate once for Part III;
- [x] add an orientation-versus-power-transfer panel and a cycles/parallelism/
  radial-tail panel if the existing argument figures do not cover them;
- [x] add the formulation-lattice argument figure showing the faithful
  equation/constraint boundary and the guarded nodal-admittance branch;

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

#### Cross-community vocabulary bridge — 2026-08-16

The same terms carry different object, state, and preservation semantics in
power engineering, software and network data, mathematical modelling, graph
theory, and graph machine learning. The bridge should retain familiar language
while preventing word-level translation from substituting for a typed map.

- [x] add a short illustrated Start Here chapter describing one source network
  in the five community vocabularies;
- [x] distinguish exact aliases, scoped aliases, broader/narrower terms,
  representation-dependent terms, and false friends;
- [x] adopt the three editorial statuses: preferred house term, accepted
  qualified shorthand, and unsafe unqualified term;
- [x] add the first cross-community collision index to the maintained
  terminology page;
- [x] connect the bridge to the opening route, representation introduction,
  translation traps, HTML navigation, and curated PDF route;
- [x] revise the audience-route diagram so graph theory and graph machine
  learning are explicit rather than implicit audiences;
- [x] stabilize the manual collision set, promote its 17 initial concepts to a
  structured registry, and generate community-to-book and book-to-community
  HTML indexes for the five audience routes plus shared circuit vocabulary;
- [x] complete the first targeted bridge-card audit: computational graph
  identity, electrical/equipment/hidden state, coarsening and pooling,
  normalization, and the three meanings of loss now appear at their
  load-bearing chapters;
- **Conditional:** continue the chapter audit only where a concrete cross-community false
  inference remains, prioritizing factor, direction/flow, and software object
  identity rather than repeating the bridge mechanically;
- **External:** seek separate terminology review from representatives of the five
  communities; do not treat internal consistency as evidence that the bridge
  matches every community's practice.
- **Gate:** after community review, add or revise registry entries only with a
  recorded usage witness; do not imply that the controlled book vocabulary is
  a descriptive standard for any community.

##### Vocabulary-bridge review repair — 2026-08-16

The first focused review accepted the chapter and its placement but found one
blocking repository gate and several semantic/navigation weaknesses. The
agreed repair is complete:

- [x] collapse five ad-hoc admonition titles into the single controlled
  **Vocabulary bridge** callout and update the checker and declared callout
  vocabulary together;
- [x] qualify the `Ybus` exact-alias example as an operator alias, not an alias
  for the network or its assembly decomposition, and make the scoped branch-
  orientation example state its required qualifier;
- [x] explain why circuit theory is shared target/technical vocabulary rather
  than a sixth audience route;
- [x] promote ground/earth/neutral/reference and
  phase/conductor/sequence/coordinate into the Start Here collision set and
  add a third worked neutral-elimination translation;
- [x] state explicitly that vocabulary-relation classes and editorial-usage
  statuses are orthogonal, with the house policy owned by the Start Here
  chapter rather than duplicated in the glossary;
- [x] make the collision index link to its detailed expansions and add a
  definition/route column to the house-definition table;
- [x] redraw the vocabulary figure so the solid bridge path blocks the unsafe
  inference and a dashed *if untranslated* path bypasses it;
- [x] add the auditable `VOCAB-BRIDGE-001` engineering-practice claim and bind
  it to the controlled callout checker.

**Exit criterion:** a reader can start from a familiar community term, locate
the book's object and required qualifier, identify the unsafe inference, and
reach the rigorous defining chapter without learning a second disconnected
glossary.

#### Multi-port lowering pedagogy — 2026-08-16

The transformer discussion exposed a missing connection between the clean
five-bus topology example, the canonical port--factor model, optional
ordinary-edge realizations, equation/operator targets, and support graphs. The
repair treats construction stage and semantic lens as orthogonal axes and
makes structure loss visible at every lowering boundary.

- [x] preserve the original five-bus line-induced graph as the stable topology
  kernel rather than changing its incidence and cycle-space derivation;
- [x] add a companion five-bus structural extension with one three-port
  transformer attached at ``j``, ``l``, and ``m``;
- [x] add a hash-bound executable witness comparing local and embedded
  factor-incidence, generated-star, terminal-clique, member, and simple graph
  cycle ranks;
- [x] define the source-asset, canonical port--factor, optional edge,
  equation/operator, and support stages together with the interface carried at
  each stage;
- [x] add generated transformer-unpacking, five-bus-lowering, and layer--lens
  diagrams with explicit loss ledgers and monochrome-safe companions;
- [x] state that direct factor stamping is the default branch and that an
  ordinary-edge realization is a guarded compatibility target;
- [x] separate the three-winding star/T special case from the generally full
  ``(n-1)\times(n-1)`` reference impedance of the arbitrary-winding case;
- [x] split the short Start Here argument route from the longer canonical-model
  construction and running-case material in HTML and PDF navigation;
- [x] independently review the proposed layer-interface ledger and the
  interpretation of factor-incidence versus terminal-support cycle counts;
- [x] close the 2026-08-16 review corrections: remove the five-bus line/
  transformer ``x`` collision by renaming the pendant line ``u``; distinguish
  equal cycle ranks from equal semantics; show the parallel pair in the
  flagship figure; state that full ``K_3`` terminal support is generic; and
  compose the numerical negative-star-arm guard into the witness;
- [x] type ``\pi_\sigma`` as a state-conditioned edge-contraction quotient,
  add it to the principal map table with reciprocal topology-processing links,
  and distinguish exact query factorization from inner, outer, and
  scenario-approximate sufficiency;
- [x] require a boundary reduction to declare its internal-injection model
  rather than hiding that load-bearing assumption under admissible inputs;
- [x] extend the composed witness to an evaluated four-winding factor with a
  non-diagonal reference matrix and to connection-specific shunts, grounding,
  controls, and decision-preserving pointwise equation operators;
- [x] state the direct-factor, pointwise equation-operator, support-projection,
  and ordinary-edge realizability boundary in the evaluated witness; do not
  infer an edge realization from a terminal operator;
- [x] test the layer--lens matrix against concrete APIs from power-system data,
  optimization, sparse-matrix, and graph-learning software without assigning
  an entire package to one representation stage.

**Exit criterion:** a reader can follow one transformer from source identity to
several valid target graphs, name the interface at each boundary, and explain
why a tree-to-clique change does not create a physical loop or authorize new
asset decisions.

### Representation-landscape review tranche (complete)

- [x] make `formal-representation-frameworks.md` the sole normative authority
  for the linked architecture and disambiguate ``\mathfrak B(\mathfrak P)``
  from the bus set ``\mathcal B``;
- [x] add a four-level taxonomy diagram with orthogonal asset and
  computational companions;
- [x] retire the orphan architecture chapter, preserving its implementation
  and fixture-coverage material in the research record;
- [x] register the implementation-status contract as `PRACTICE-ARCH-001`;
- [x] add and run a PDF ``@ref`` reachability gate, and include the normative
  target chapters needed by the curated route;
- [x] retain the expanded PDF route after the TOC audit: reader-facing start,
  foundations, transformations, and worked-case chapters expose their
  subsections, while generated indexes, literature records, references, and
  archived search runs remain chapter-level. The resulting 335-page PDF is
  intentionally a navigable secondary serialization, not the primary
  retrieval surface.

**Exit criterion:** the representation landscape has one authority chain, one
maintained classification figure, no orphan architecture chapter, and no
dangling cross-reference in the curated PDF.

### Standards-aware visual-language tranche (in progress)

The book now has a typed view registry, but its visual conventions are still
distributed across individual figures. This tranche makes the visual language
explicit without claiming that IEC/IEEE symbol standards define the book's
lowering semantics.

- [x] record the standards boundary: IEC 60617 for graphical symbols, IEC
  61082 for document presentation, IEC 61970-453/CGMES for identity-linked
  diagram layout exchange, IEC 61850-6 for substation configuration exchange,
  and IEEE C57.12.70 for transformer terminal and connection conventions;
- [x] add a visual contract declaring object level, identity fibre, preserved
  semantics, omitted semantics, map type, and reverse-map status;
- [x] add a reader-facing legend that distinguishes asset, terminal,
  conductor, factor, compiled-equation, and operational overlays;
- [x] add the first maintainable equipment plate covering line, three-winding
  transformer, regulator, switch, and single-line/multi-line/factor views;
- [x] extend the plate family to explicit neutral grounding, nominal-``\pi``
  shunts, phase-selective switching, and an n-winding leakage-factor graph;
- [ ] independently review the visual grammar with power-system engineering
  and diagramming practitioners.

**Exit criterion:** every maintained equipment figure identifies its semantic
level and source-object mapping, and a reader can distinguish a physical
asset, a factor decomposition, and a compiled graph without relying on symbol
shape alone.

### Practitioner visual-review repair tranche (in progress)

The first independent review found unsafe inferences in the original
equipment plate and several cross-figure consistency gaps. The repair gate is
now explicit:

- [x] redraw the single-line panel with buses/terminals as vertices and real
  branch or multi-terminal equipment glyphs, including a three-terminal X1;
- [x] remove sibling-factor arrows that falsely asserted lowering maps and add
  exactness/reverse-map labels to the source/view surgery figure;
- [x] make nominal-``\pi`` asymmetry visible with unequal shunt glyphs and both
  terminal-current equations;
- [x] reconcile the X1 winding count, make the phase-only regulator choice
  explicit, and flag an open neutral as a potentially floating/hazardous state;
- [x] repair leakage-factor label collisions and add one shared legend for the
  reviewer packet;
- [x] add the missing neutral bus and an orientation disclaimer to the
  label-to-coordinate bridge;
- [x] replace the declared-only monochrome flag with a dependency-free rendered
  PNG grayscale contrast sample in the figure audit;
- [ ] obtain a three-reviewer practitioner pass (power/protection, CIM or
  network software, and graph/optimization) using the shared packet and record
  findings by semantic risk rather than symbol preference.

**Exit criterion:** no maintained figure encourages a reader to treat a bus as
equipment, a factor as an asset, a per-pole state as scalar, or a support edge
as a physical circuit without an explicit warning and map contract.

## Deliberately deferred

Lean formalization, broad category-theoretic claims, a full explicit-earth and
protection implementation, and a general optimizer-independent release remain
Phase 5--6 work. They should not expand the M1--M4 scope until the reduction
evidence and independent review gates are met.

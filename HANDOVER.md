# Codex handover

## Purpose

Continue developing this repository as a high-quality scientific book,
knowledge base, and eventual executable theory of graph transformations for
power networks.

## Core decisions already made

1. Do not search for one universally correct graph class.
2. Test a linked asset/property model and typed hierarchical port--factor electrical model as a
   proposed reference architecture.
3. Treat bus--branch multigraphs, simple graphs and sparsity graphs as derived
   views.
4. Define expressiveness relative to supported queries or observations, giving
   a partial rather than total order.
5. Distinguish projection, compilation, normalization, exact behavioral
   reduction and approximate reduction.
6. Require every nontrivial transformation to state assumptions, preservation,
   information loss, provenance, constraint maps and recoverability.
7. Distinguish an exact terminal equivalent from a valid physical equipment
   normalization.

## Most important technical insight so far

For a zero-injection degree-two junction between series-only multiconductor
elements, terminal equivalence gives ``Z_eq = Z_1 + Z_2`` after conductor
coordinates are aligned. Equal construction codes are not required for that
behavioral identity. They are required—along with additional guards—to claim
that the result is one longer homogeneous physical line.

A neutral grounding, shunt, measurement, protection boundary, mutual coupling,
control, or independently meaningful constraint can invalidate the physical
merge. Schur elimination may remain possible but can produce a general two-port
outside the source line family.

Parallel admittance aggregation similarly preserves aggregate terminal current
but not generally the feasible set induced by individual ratings, switching,
contingencies or investments.

## Current state of files

- The reader-facing architecture and target contents are fixed in `BOOK_PLAN.md`.
- The thesis now starts from general multiconductor, multi-terminal networks and treats balanced
  transmission graphs as derived cases.
- The proposed port--factor model is explicitly a reference-architecture hypothesis, not an assumed
  canonical truth.
- A BMOPFTools-aligned notation contract fixes element, oriented-arc, terminal-map, and winding
  indices.
- A semantic running network with explicit neutral grounding, heterogeneous parallel branches,
  phase discontinuity, switchgear, and a three-winding transformer is specified.
- Fixture version 0.1.0 realizes that network in BMOPF, passes schema/conformance checks, and
  solves continuous PF and OPF cases. Its normal provenance records the dirty local BMOPFTools
  state, while a separate isolated run establishes a clean pinned reproduction.
- Six representation views are generated from the fixture, and the scalar parallel-line failure
  has an executable machine-readable certificate.
- The initial claims ledger and CI checker are present.
- Every bibliography entry has a dated audit record; the Sistermanns final
  conference paper and the final Opti-KRON journal article replace inaccurate
  preprint-only metadata.
- A versioned scoping-review protocol, search strategy, and evidence schema are present; systematic
  searching and screening have not yet begun.
- Fixture version 0.1.0 also passes in an isolated clean clone of BMOPFTools commit
  `b7aa9a1bb48bcc8b790d3bcf5417d6a32036352a`; its fixture is byte-identical to the canonical one.
- The six generated views now have complete source maps bound to fixture and figure hashes.
- Degree-two series elimination is an executable package-independent rule with conductor
  permutation, constraint/recovery maps, structured rejections, and adversarial tests.
- Conductor-coordinate normalization is now its own exact, invertible rule;
  its certificate composes explicitly with degree-two series elimination.
- Five transformation artifacts share the version 1.0.0 JSON certificate
  schema and are validated against registered claim IDs.
- A solved two-bus maximum-served-load comparison records 110 MW for the
  source, 200 MW for the naïve summed-rating aggregate, and 110 MW for the
  exact lifted formulation.
- An initial representation taxonomy separates physical, connectivity, behavioural, study, and
  computational graphs.
- A preservation-contract schema is proposed.
- Transformation categories are separated.
- Candidate guarded rules are drafted.
- A provisional literature map and research agenda are included.
- DocumenterCitations and HTML/PDF build scaffolding are present.
- The bibliography is still a seed for literature coverage. Its metadata has a
  dated first-party/DOI audit, but the nearby technical claims still require
  source-by-source review.

## Do not assume

- that the literature review is systematic yet;
- that `structure preserving` has one accepted meaning;
- that a smaller graph is less expressive;
- that an exact boundary equivalent preserves optimization constraints;
- that software practice constitutes a theorem;
- that the initial factor-graph vocabulary is final;
- that an audit date makes living documentation metadata permanently current or
  proves that a source supports every nearby interpretation.

## Recommended next actions

### 1. Execute the scoping review

Run and archive the first database searches under `review/protocol.md`, then
populate the evidence matrix. Double-code the most consequential sources first.

### 2. Independent claim review

Obtain independent reviews for the parallel and series claims before promoting
the vertical slice beyond an internal research draft.

### 3. Extend executable reproducibility

Add a second solver reproduction where practical and decide whether the pinned
BMOPFTools commit should be replaced by a tagged release once available.

### 4. Formal definitions

Define the port--factor object, morphisms, hierarchy, boundary/interface,
asset linkage, observation functor, and transformation certificate. Test the
definitions on the specified running network and its parallel-line, grounding,
permutation, switch, and multiwinding variants before making them more abstract.

### 5. Extend executable rules

Generalize conductor-coordinate normalization to typed factors and transformer
windings. Enrich certificate composition with typed state, unit, objective,
and decision interfaces, then test critical pairs with switch and grounding
rules.

Use BMOPFTools where its model fits, but keep the book-level transformation contracts independent
of its schema. Record the exact BMOPFTools commit for every executable result.

### 6. First counterexample paper

Extend the solved two-bus linear decision example to the smallest credible
multiconductor AC OPF instance. Compare the source and lifted formulations'
size and solution behaviour, and reproduce the result with an independent
solver.

## Questions to keep open

- Should the mathematical foundation use decorated cospans/corelations,
  attributed typed hypergraphs, or a simpler engineering schema first?
- Is a factor a graph node, a hyperedge, or an abstract relation independent of
  serialization?
- Which transformations should be called normalization rather than compilation?
- What is the smallest useful preservation-contract language?
- Can important rewrite subsets be confluent, or should canonicalization use
  explicit priorities and cost functions?
- How should scenario-dependent and uncertain ratings appear in exact versus
  conservative reductions?
- How far should the first edition extend into short circuit, harmonics, EMT,
  protection, communications and thermal dynamics?

## Suggested working principle

Keep the agenda broader than any existing personal software project. Use
PowerModelsDistribution, OpenDSS, CIM, PowerOptLab and BMOPFTools as case studies
and integration targets, not as the conceptual boundary of the book.

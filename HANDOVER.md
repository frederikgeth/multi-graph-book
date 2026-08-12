# Codex handover

## Purpose

Continue developing this repository as a high-quality scientific book,
knowledge base, and eventual executable theory of graph transformations for
power networks.

## Core decisions already made

1. Do not search for one universally correct graph class.
2. Use a linked asset/property model and typed hierarchical port--factor
   electrical model as the canonical architecture.
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

- The initial thesis and architecture are drafted.
- A preservation-contract schema is proposed.
- Transformation categories are separated.
- Candidate guarded rules are drafted.
- A provisional literature map and research agenda are included.
- DocumenterCitations and HTML/PDF build scaffolding are present.
- The bibliography is a seed and must be independently checked.

## Do not assume

- that the literature review is systematic yet;
- that `structure preserving` has one accepted meaning;
- that a smaller graph is less expressive;
- that an exact boundary equivalent preserves optimization constraints;
- that software practice constitutes a theorem;
- that the initial factor-graph vocabulary is final;
- that all BibTeX metadata are correct.

## Recommended next actions

### 1. Bibliographic audit

Verify each entry from the publisher, DOI registration, standard body, or
official project. Check whether the Sistermanns and Mokhtari preprints have
final publications and cite both only when useful.

### 2. Systematic review protocol

Create `review/protocol.md`, `review/search-strings.md`, and a CSV/JSON evidence
matrix. Include backward and forward citation chasing. Record exclusion reasons.

### 3. Formal definitions

Define the port--factor object, morphisms, hierarchy, boundary/interface,
asset linkage, observation functor, and transformation certificate. Test the
definitions on parallel lines, four-wire grounding and a three-winding
transformer before making them more abstract.

### 4. First executable rules

Implement pure Julia prototypes for conductor permutation and degree-two
series elimination. The prototype should return either a transformed model plus
certificate or a structured rejection with failed guards.

### 5. First counterexample paper

Build the smallest parallel-line OPF examples demonstrating that an aggregate
edge with a conventional rating changes the feasible region or optimum. Then
identify the exact lifted constraint representation and its computational
cost.

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

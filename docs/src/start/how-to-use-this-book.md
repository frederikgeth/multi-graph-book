# [How to use this book](@id how-to-use-this-book)

**Page status:** reading guide for the long-form monograph and the exhaustive HTML knowledge base.

This project has two complementary reading surfaces. They share Markdown sources, claims,
citations, generated artifacts, and evidence boundaries, but they answer different reader needs.

## Follow the monograph argument

The long-form route is organized around a problem rather than a catalogue of graph types:

1. **Problem and counterexample:** see why a plausible simplification can change the question being
   answered, beginning with [One network, many graphs](@ref one-network-many-graphs) and [A first
   failure: heterogeneous parallel branches](@ref first-failure-parallel-branches).
2. **Representation obligations:** identify which physical objects, equations, observations,
   constraints, decisions, and provenance a study requires.
3. **Canonical model:** establish the source data and semantic projection before deriving a graph or
   matrix view.
4. **Collapses and failure modes:** study when balanced, nodal, radial, series, parallel, or
   reduced views are valid and when they discard needed meaning.
5. **Preservation contracts:** state the exact object being preserved, the guards, the recovery map,
   and the evidence boundary.
6. **Transformations and recovery:** read the executable rules and certificates only after the
   contract is clear.
7. **Cases and consequences:** compare feasible sets, active limits, objectives, decisions, and
   recovery—not only state or terminal-equation error.

The curated PDF route follows this sequence. It remains a long-form draft and retains detailed
reference and case material; the route is refactored, not shortened.

## Use the HTML knowledge base for retrieval

Use the generated [knowledge-base indexes](@ref knowledge-base-index) to find claims by type,
chapter, verification state, unresolved issue, or generated artifact. Use the [chapter-status
table](@ref chapter-status) to see what each page establishes and what remains open. Use the
[evidence map](@ref reference-evidence-map) for coverage gaps, the [vocabulary indexes](@ref
vocabulary-indexes) for cross-community terminology, and the [references](@ref reference-bibliography)
page for the bibliography.

The knowledge base is intentionally more exhaustive than the monograph. Its presence does not
promote a proposal into a theorem, a local numerical witness into a global result, or an
independent numerical reimplementation into external peer review.

## Read the evidence labels correctly

- **Definition / proposal:** the book's vocabulary or architecture; not a claim that the field has
  adopted it.
- **Theorem / established result:** a mathematical or literature claim whose scope and assumptions
  must be read with its citation or derivation.
- **Empirical witness:** a result recorded for a declared fixture, solver, state, and tolerance.
- **Independently implemented:** a separate numerical path for the declared case; it may still
  share source fixtures, matrices, or model assembly.
- **Externally reviewed:** human review recorded with reviewer, date, scope, and response. The
  current ledger has no claims in this category.

For every transformation, ask four questions: what is the source model, what is the target model,
what is preserved for the declared observation or decision, and how are forgotten quantities and
constraints recovered or bounded?

## Choose a route by background

- Power engineers: begin with [One network, five languages](@ref one-network-five-languages), the
  [reading guide](@ref reading-guide-graph-and-transmission), and the parallel or grounding cases.
- Optimization researchers: begin with [Load models and decision dependence](@ref
  load-models-and-decision-dependence), [Preservation contracts](@ref preservation-contracts), and
  the decision certificates.
- Software and data practitioners: begin with [From source data to a canonical network model](@ref
  source-to-canonical-model), [Data-model crosswalk](@ref data-model-crosswalk), and the generated
  indexes.
- Graph and formal-methods readers: begin with [Formal representation frameworks](@ref
  formal-representation-frameworks), [Maps between representation frameworks](@ref
  representation-maps), and [Transformation semantics](@ref transformation-semantics-register).

# Structure-Preserving Graph Models for Power Networks

Power-network studies routinely speak of *the network graph*. In fact, several
different structures are being conflated:

1. physical assets and their identities;
2. terminals and conductor connectivity;
3. constitutive relations among terminal variables;
4. operational state, including switch positions;
5. limits, controls, protection, measurements, and decisions;
6. simplified graphs compiled for particular algorithms.

This distinction matters. Two parallel lines can have the same endpoints but
different impedances, ratings, outage states, ownership, protection, and
investment decisions. Combining them into one edge may preserve aggregate
terminal admittance while changing the feasible set of an optimal power-flow or
security problem. Similar issues arise from explicit neutrals, grounding,
multiwinding transformers, mutual coupling, switchgear, and internal equipment
states.

The thesis of this book is:

> A graph transformation for a power network is meaningful only relative to an
> explicit preservation contract. Canonical data should retain typed physical
> and terminal structure; simpler graphs should be derived, traceable views.

The minimum architecture proposed here is:

- a **typed asset/property graph** for physical identity and lifecycle facts;
- a **typed hierarchical port--factor incidence model** for electrical
  interconnection and constitutive behavior;
- generated conductor-level, bus--branch multigraph, and simple-graph views;
- explicit transformation records containing assumptions, provenance,
  transformed constraints, recovery maps, and approximation error where
  relevant.

This is not merely a data-format question. It joins circuit theory, graph
transformation, model compilation, mathematical optimization, protection,
state estimation, and scientific reproducibility.

## Reading path

Begin with [Scope and thesis](@ref), followed by
[Representation architecture](@ref) and [Preservation contracts](@ref).
[Projection, compilation, and reduction](@ref) separates transformations that
are often incorrectly grouped together. [Guarded normalization rules](@ref)
develops the degree-two line example and related rewrite rules. The
[Literature map](@ref) and [Research agenda](@ref) record what appears mature,
fragmented, and genuinely open.

## Status labels

The text uses five epistemic labels:

- **Definition**: terminology adopted consistently in this book.
- **Established result**: supported by a proof or authoritative primary source.
- **Engineering practice**: implemented or standardized practice, not
  necessarily accompanied by a general preservation theorem.
- **Proposal**: a design choice advanced by this book.
- **Open question**: an unresolved claim, boundary, or research opportunity.

The quality-control process is specified in the repository-level
`QUALITY_CONTROL.md`.

## Publication formats

This knowledge base is generated from the same Markdown sources in two formats:

- the navigable HTML site;
- a [single-file PDF](GraphModelsForPowerSystems.pdf).

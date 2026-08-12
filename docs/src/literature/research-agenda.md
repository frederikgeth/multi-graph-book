# Research agenda

## Research objective

Develop a theory, reference architecture, and executable toolkit for
**typed, asset-, constraint-, and provenance-preserving transformations of
multiconductor power-network models**.

The agenda should deliberately connect formal results to utility-relevant
applications. A transformation is valuable when it enables faster or more
reliable computation without silently invalidating the decisions being made.

## Workstream A: model categories and semantics

1. Define the typed hierarchical port--factor category.
2. Define linked asset/property semantics and stable identities.
3. Specify conductor, phase, neutral, ground, orientation and reference-frame
   types.
4. Formalize observation contracts and relative expressiveness
   ``\succeq_Q``.
5. Separate physical equivalence, terminal behavioral equivalence, feasible-set
   equivalence, and approximation.

**Candidate result A1.** A representation theorem showing that ordinary
bus--branch multigraphs, conductor-expanded graphs, hypergraphs/factor graphs,
and common component compilations embed into the port--factor kernel.

**Candidate result A2.** Conditions under which a projection between model
categories is faithful, conservative, or admits a reconstruction functor on a
restricted subcategory.

## Workstream B: normalization calculus

1. Specify typed rewrite rules and negative application conditions.
2. Prove semantic preservation of conductor permutation, ideal-switch
   contraction, homogeneous line concatenation, grounding extraction, and
   transformer compilation.
3. Characterize critical pairs among rules.
4. Determine whether useful subsets terminate and are confluent up to typed
   isomorphism.
5. Define normal forms by purpose rather than one universal form.

**Candidate result B1.** Necessary and sufficient conditions for degree-two
multiconductor bus elimination to remain inside a selected line model class.

**Candidate result B2.** A closure classification for series composition of
series-only, nominal-``\pi``, exact distributed-parameter, frequency-dependent,
and thermally coupled line models.

**Candidate result B3.** A non-existence result showing that no single simple
edge with conventional scalar or per-conductor limits can exactly represent
the feasible set of general heterogeneous parallel branches.

## Workstream C: decision-preserving reduction

1. Treat equations and feasible sets together.
2. Develop recovery maps for internal voltages, currents, losses and thermal
   states.
3. Classify exact, inner, outer and scenario-approximate constraint maps.
4. Study preservation for OPF, security-constrained OPF, reconfiguration,
   expansion planning, dynamic operating envelopes and state estimation.
5. Quantify when reduced models change optimal decisions rather than merely
   state-variable errors.

**Candidate result C1.** A general lifting theorem: if eliminated variables are
uniquely recoverable and all source constraints are composed with that recovery
map, optimization over boundary variables is exactly equivalent.

**Candidate result C2.** Complexity or representability bounds for projecting
branch-wise thermal constraints onto boundary variables.

## Workstream D: approximate but certified models

1. Define application-specific observation norms.
2. Develop scenario and uncertainty-domain error certificates.
3. Preserve radiality, phase availability, grounding modes and selected physical
   corridors.
4. Compare Kron, clustering, aggregation, sparsification and learned surrogates
   under the same contract.
5. Measure errors in feasibility, optimal objective, active constraints and
   decisions—not voltage alone.

## Workstream E: implementation and interoperability

Develop a Julia reference implementation with:

- immutable source identities and explicit generated-object identities;
- typed ports, factors and hierarchy;
- a transformation registry with machine-readable certificates;
- rule tracing and reversible provenance;
- adapters for CIM/CGMES, OpenDSS, PowerModelsDistribution and selected Julia
  optimization models;
- generated multigraph, simple-graph and sparse-matrix views;
- property-based tests and adversarial counterexamples.

Graph representation should be independent of any one solver. Mathematical
models should consume generated views and expose the mapping back to canonical
entities.

## Workstream F: empirical corpus

Build a deliberately difficult test corpus containing:

- heterogeneous parallel lines with distinct ratings and decisions;
- four-wire feeders with multi-grounded and impedance-grounded neutrals;
- phase discontinuities and conductor permutations;
- same-code and mixed-code degree-two line chains;
- nominal-``\pi`` versus distributed line concatenation;
- mutually coupled parallel circuits;
- multiwinding and autotransformer/regulator models;
- lossy and controllable switches;
- measurements and protection zones at otherwise eliminable nodes.

Each case should include an expected preservation/failure certificate. Small
symbolic cases are as important as large benchmarks because they expose exact
semantic errors.

## High-value applications

The first demonstrations should target decisions for which structural loss has
obvious consequences:

1. **Parallel-line OPF and contingency analysis:** show incorrect feasible
   regions from naïve aggregation.
2. **Four-wire state estimation:** show the effect of grounding-aware versus
   topology-only normalization.
3. **Distribution model cleaning:** safely merge genuine line subdivisions
   while retaining construction and provenance.
4. **Multiwinding transformer compilation:** prove terminal equivalence and
   source-level constraint recovery.
5. **Feeder reduction for hosting capacity or operating envelopes:** compare
   voltage accuracy with decision accuracy.

## Longer-term formalization

A formal methods track could encode the core semantics and selected rewrite
proofs in Lean. The initial targets should be finite-dimensional linear
relations, incidence conservation, conductor permutations, series composition,
parallel feasible sets, and Schur-complement recovery. This should follow a
stable mathematical specification rather than precede it.


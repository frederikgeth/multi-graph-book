# [Research agenda](@id research-agenda)

**Page status:** proposal and open-work register.

The current paper-sized dissemination cuts are recorded in the repository's
review track. They reuse this agenda's claim and evidence boundaries rather than
creating a second roadmap.

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

**Status:** partial — `ARCH-BLOCK-001`, `ARCH-LOWER-001`, `ARCH-PORT-001`, and
the representation taxonomy establish finite typed embeddings and lowering
examples; a general representation theorem remains open.

**Candidate result A2.** Conditions under which a projection between model
categories is faithful, conservative, or admits a reconstruction functor on a
restricted subcategory.

**Status:** partial — `ARCH-LENS-001`, `ARCH-RECOVERY-002`, and the
representation-map query-sufficiency analysis classify scoped faithful,
set-identifiable, and non-identifiable cases; a general reconstruction result
is open.

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

**Status:** partial — `TR-SER-001` and `TR-SER-002` discharge the guarded
uncoupled behavioural rule and show why homogeneous line-class closure is
separate; `TR-SER-003` now gives a distinct exact rule for a complete mutually
coupled section pair, while necessary-and-sufficient closure conditions for
broader line libraries remain open.

**Candidate result B2.** A closure classification for series composition of
series-only, nominal-``\pi``, exact distributed-parameter, frequency-dependent,
and thermally coupled line models.

**Status:** partial — the guarded-normalization catalogue and the degree-two
series chapter cover series-only, nominal-``\pi``, and distributed-parameter
warnings; frequency-dependent and thermally coupled closure are open.

**Candidate result B3.** A non-existence result showing that no single simple
edge with conventional scalar or per-conductor limits can exactly represent
the feasible set of general heterogeneous parallel branches.

**Status:** partial — the parallel decision cases and `TR-PAR-001`/`TR-PAR-002`
give scalar counterexamples and explicit outer-relaxation witnesses; a formal
non-existence theorem for the general heterogeneous multiconductor class is
open.

**Candidate result B4.** Necessary and sufficient redundancy certificates for
multiconductor parallel-member constraint sets, extending scalar quadratic
containment to coupled phase, neutral, ground, and terminal-direction models,
with explicit guards for topology and control states.

**Current partial result.** Claim `TR-PAR-005` gives a necessary-and-sufficient
PSD test for each individual centered linear-current norm implication and a
two-end componentwise certificate. Claim `TR-PAR-006` adds an exact complex
polydisc row-norm test when all component limits of one nonsingular series
member jointly imply another member's limits, and exercises it in a reciprocal
non-proportional four-wire AC decision case. Claim `TR-PAR-007` generalizes the
same support-function argument to an invertible stacked terminal-current map
and exercises distinct from/to shunts in a nominal-``\pi`` case. Singular
shunted maps, implication by several different members, non-Euclidean regions,
and state-conditioned models remain open parts of B4.

## Workstream C: decision-preserving reduction

1. Treat equations and feasible sets together.
2. Develop recovery maps for internal voltages, currents, losses and thermal
   states.
3. Classify exact, inner, outer and scenario-approximate constraint maps.
4. Treat certified removal of implied constraints as exact presolve, retaining
   the asset laws, identities, recovery maps, and all nonredundant constraints.
5. Study preservation for OPF, security-constrained OPF, reconfiguration,
   expansion planning, dynamic operating envelopes and state estimation.
6. Quantify when reduced models change optimal decisions rather than merely
   state-variable errors.

**Candidate result C1.** A general lifting theorem: if eliminated variables are
uniquely recoverable and all source constraints are composed with that recovery
map, optimization over boundary variables is exactly equivalent.

**Status:** partial — `PRESERVE-001`, the recovery-map chapter, and the Kron,
parallel, and transformer certificates establish the statement for declared
finite linear and decision cases; a general theorem over nonlinear and mixed
discrete models remains open.

**Candidate result C2.** Complexity or representability bounds for projecting
branch-wise thermal constraints onto boundary variables.

**Status:** open — current work provides exact recovery and support-function
certificates, but no general complexity or representability bound.

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
models should consume generated views and expose the mapping back to stable
source entities.

## Workstream F: empirical corpus

Build a deliberately difficult test corpus containing:

- heterogeneous parallel lines with distinct ratings and decisions;
- four-wire feeders with multi-grounded and impedance-grounded neutrals;
- phase discontinuities and conductor permutations;
- same-code and mixed-code degree-two line chains;
- nominal-``\pi`` versus distributed line concatenation;
- physically parallel and endpoint-parallel circuits with full, sequence-only,
  partial-overlap, different-voltage, open, and grounded coupling states;
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

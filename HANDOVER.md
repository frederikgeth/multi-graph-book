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
- Six illustrated representation views and a seventh simple-topology quotient
  map are generated from the fixture, and the scalar parallel-line failure
  has an executable machine-readable certificate.
- The initial claims ledger and CI checker are present.
- Every bibliography entry has a dated audit record; the Sistermanns final
  conference paper and the final Opti-KRON journal article replace inaccurate
  preprint-only metadata.
- A versioned scoping-review protocol, search strategy, and evidence schema are present; systematic
  searching and screening have not yet begun.
- Fixture version 0.1.0 also passes in an isolated clean clone of BMOPFTools commit
  `b7aa9a1bb48bcc8b790d3bcf5417d6a32036352a`; its fixture is byte-identical to the canonical one.
- The generated views now have complete source maps bound to fixture and
  figure hashes. The simple edge `i1--i2` retains a provenance fibre to both
  parallel source lines; the multiwinding transformer is explicitly outside
  that quotient until compilation.
- Degree-two series elimination is an executable package-independent rule with conductor
  permutation, constraint/recovery maps, structured rejections, and adversarial tests.
- Conductor-coordinate normalization is now its own exact, invertible rule;
  its certificate composes explicitly with degree-two series elimination.
- Thirteen transformation artifacts share the version 1.1.0 JSON certificate
  schema, declare six typed interfaces, and are validated against registered
  claim IDs.
- A solved two-bus maximum-served-load comparison records 110 MW for the
  source, 200 MW for the naïve summed-rating aggregate, and 110 MW for the
  exact lifted formulation.
- The common coordinate action now normalizes a full transformer-winding
  terminal-to-coil relation; delta and grounded-wye round trips are tested.
- Complete pairwise multiwinding leakage data now compile exactly to the full
  reference-coordinate impedance matrix and external winding admittance. The
  tests cover the fixture, an admissible negative three-winding arm, a non-PSD
  rejection, incomplete data, and a non-diagonal four-winding round trip.
- The leakage compiler now distinguishes the source short-circuit-impedance
  base from the selected internal reference. All winding-reference choices are
  tested, and the running transformer preserves its external admittance to a
  maximum entrywise difference of `2.84e-14` S.
- The running transformer's WYE/WYE/DELTA connection-incidence factors now
  compose with the leakage factor into an exact 11-terminal admittance plus a
  retained 9-by-11 coil-current map. Terminal permutations, coil-row
  permutations, leakage-reference changes, complex-power consistency, and
  inconsistent-limit rejections are tested.
- A versioned compact completion contract composes that leakage block with
  fixed power-dual voltage transfers, a labelled winding-2 excitation shunt,
  and transformer-internal neutral grounding. Component-current and power
  identities are tested, and the result matches BMOPFTools' independent
  n-winding primitive to `2.96e-17` S after removing the separately retained
  grounding contribution. Static compilation rejects adjustable transfers
  rather than freezing their decision values.
- Continuous and discrete scalar winding taps now compile into a parameterized
  factor with identity decision recovery and pointwise fixed-linear evaluation.
  The discrete witness retains feasible taps 1.00 and 1.05 and selects 1.05;
  the frozen 1.00 snapshot increases the winding-current objective from
  1232.656 A to 1903.716 A.
- The full 11-terminal WYE/WYE/DELTA factor now participates in a solver-backed
  AC network decision with winding-2 phase power balance, explicit neutral KCL,
  open-delta tertiary KCL and gauge separation, voltage bounds, and all nine
  recovered leakage-current limits. Exact finite enumeration selects tap 0.95
  with served fraction 1.2305865; freezing 1.00 loses 0.090169 MW.
- A separate LinearAlgebra-only finite-difference Newton, continuation, and
  bisection engine reproduces the three tap-conditioned high-voltage branch
  boundaries to within 3.14e-10 served fraction of JuMP/Ipopt and selects the
  same tap. It shares the certified factor matrices but no optimization engine;
  missing brackets and infeasible scans are structured rejections.
- A coupled phase-neutral AC decision case records objectives 0.6138908,
  1.0630833, and 0.6138908 for source, naïve, and exact lifted formulations.
  A closed-form loop-impedance derivation independently checks the numerical
  source and naïve optima.
- Molzahn's parallel-line result is now coded in the literature evidence
  matrix as exact scalar AC constraint pruning rather than asset aggregation.
  In the proportional phase-neutral case, the member-2 current map is exactly
  0.1 times member 1, so an exact-pruned formulation drops only the implied
  member-2 limits and reproduces the 0.6138908 source optimum with 5 variables
  and 9 constraints.
- A package-independent containment kernel now converts arbitrary fixed linear
  complex current maps into normalized real quadratic forms. A candidate limit
  is pairwise implied exactly when the retained form minus the candidate form
  is PSD. The member checker requires every aligned conductor at both ends;
  tests include singular cylinders, a non-proportional positive case, and
  reverse and one-end-only failures.
- A solved reciprocal non-proportional three-phase four-wire parallel case now
  uses the exact complex-polydisc row norm to prove all member-2 component
  limits jointly implied by member 1. The exact-pruned and source objectives
  agree at 1.1274329 with explicit neutral voltage, while a same-size naive
  aggregate reaches 1.8058181 and loads the binding member conductor to 168%.
  A LinearAlgebra-only Newton continuation reproduces the boundary to 1.4e-8,
  and BMOPFTools `line_yprim` independently reconstructs both line primitives.
- The joint-disc theorem now acts on a general invertible terminal-current map.
  A second four-wire case stacks the full nominal-pi ij/ji primitive with
  unequal end shunts, certifies and removes all eight member-2 terminal limits,
  and preserves the 1.1286205 source objective. The same-size naive target
  reaches 1.8077114; BMOPFTools reconstructs both full primitives and an
  independent Newton continuation reproduces the source boundary to 1.4e-8.
- The supplied five-bus graph notes have been corrected and exposed as a
  worked line-identity cycle-space chapter. The package-independent prototype
  constructs the 5-by-7 incidence matrix, a three-column fundamental basis,
  bridge set, simple projection, and equal scalar source/projected nodal
  admittances. It records the lost parallel two-cycle under projection, retains
  every chord in spanning-tree coordinates, reproduces the parallel-limit
  counterexample, and cross-checks cycle rank three with BMOPFTools. Three
  generated pedagogical figures replace the former monolithic sketch; their
  manifest binds the cycle-basis, typed-transformation, and feasible-set views
  to the current executable analysis by SHA-256.
- The representation landscape now has a first rigorous definition pass for
  the simple topology quotient, oriented attributed multigraph, hierarchical
  port--factor incidence model, typed asset/dependency relations, and compiled
  equation/sparsity graphs. These are linked by typed maps rather than treated
  as one detail ladder.
- A dedicated direction chapter separates undirected physical incidence,
  arbitrary reference orientation, terminal-current signs, operating-point
  power transfer, and genuinely directed causal or admissible relations. It
  derives the two-end loss balance and explains why nominal-pi terminal
  currents cease to be negatives when shunts remain internal to the line
  factor.
- A dedicated graph-invariants chapter now defines simple cycles,
  line-identity cycles, topological/terminal/electrical/operational/homogeneous
  parallelism, simple versus multigraph degree, bridges, leaves, radial tails,
  and adjacency- versus member-radiality. It also explains why
  multi-terminal factor incidence and clique/star compilation can create
  different apparent cycles.
- A first network-equivalent chapter states exact linear/affine Kron
  elimination and recovery, proves typed multiconductor coordinate covariance,
  distinguishes reduced multiport behavior from line--shunt realization and
  passivity, and classifies Opti-KRON as optimized structural selection with a
  scenario-defined observation metric.
- Ward's original construction, the operating-state extended Ward method, and
  Ward--PV now have audited primary sources and distinct source/target
  interpretations rather than being treated as one fixed reduction.
- A dedicated maps chapter defines within-framework morphisms and
  isomorphisms, orientation reversal, the principal cross-framework maps, and
  query factorization as a precise fit-for-purpose test.
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

Build on the first morphisms and coordinate actions by defining hierarchy,
boundary/interface composition, refinement, observation functors, and
machine-checkable data correspondence. Test every map on the specified running
network and its grounding, permutation, switch, and multiwinding variants.
Add executable Kron realizability and recovery tests before extending the
network-equivalent comparison to nonlinear and decision observations.

### 5. Graph invariants and active topology

The representation-scoped definitions are now written. Add executable
certificates for active-state adjacency-radiality and member-radiality, then
lift the incidence and cycle objects to conductor-terminal connectivity and
state-conditioned topology decisions.

### 6. Translation traps and community language

The early synthesis chapter and controlled callout vocabulary are in place.
The first terminology audit has been applied to the foundations, starting
chapters, and transformation chapters. Three package-independent executable
witnesses now cover connectivity versus energization, complex symmetry versus
Hermitian structure, and terminal-specific nominal-pi ratings. Continue the
style sweep in later case and reference chapters, preserving useful
power-system shorthand while pairing consequential uses with their precise
representation, terminal quantity, active state, and decision meaning.

An active-state radiality witness now reports simple-projection and
identified-member forests separately. The circuit-coordinate chapter
synthesizes the attached four-wire phase-to-neutral and three-wire
phase-to-phase reductions, including their grounding, shunt, mesh, and
recovery guards.

### 7. Extend executable rules

Extend the retained transformer-control domain to phase-angle,
independent-phase, mechanically coupled, automatic, and tap-dependent-loss
controls, and reproduce a case with an independently assembled primitive.
Extend the parallel-line containment results beyond the completed pairwise,
series, and nonsingular nominal-pi tests: handle singular shunted maps, limits
implied by several different retained members, and state-conditioned
certificates for switching, outage, tap, and investment decisions. Add a
global bound where conclusions require more than the traced high-voltage AC
branch.
Lift the five-bus incidence and fundamental-cycle implementation from scalar
bus--branch edges to conductor-terminal graphs and compiled multi-terminal
factors. Use the identified-line cycle space, rather than deduplicated
adjacency, when formulating state-conditioned radiality decisions.
Replace the certificate's prose interface
entries with checked state-space and unit objects, then test critical pairs
with switch and grounding rules.

Use BMOPFTools where its model fits, but keep the book-level transformation contracts independent
of its schema. Record the exact BMOPFTools commit for every executable result.

### 8. First counterexample paper

Extend the coupled two-conductor AC case to non-proportional three-phase
four-wire members. Compare active constraints and decision recovery in a
larger BMOPFTools case and reproduce it with an independent numerical solver.

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

# Executable vertical slice

This directory turns the book's semantic running-network specification into a
versioned BMOPF fixture and a small set of reproducible checks. It deliberately
keeps the documentation environment independent of the numerical environment.

The local development setup expects `BMOPFTools.jl` to be a sibling of this
repository. From the repository root:

```sh
julia --project=experiments -e 'using Pkg; Pkg.instantiate()'
julia --project=experiments experiments/run_vertical_slice.jl
julia --project=experiments experiments/test/runtests.jl
python3 experiments/generate_views.py
julia --project=experiments experiments/run_series_elimination.jl
julia --project=experiments experiments/run_coordinate_series_composition.jl
julia --project=experiments experiments/run_parallel_decision_comparison.jl
julia --project=experiments experiments/run_transformer_winding_normalization.jl
julia --project=experiments experiments/run_multiwinding_leakage_compilation.jl
julia --project=experiments experiments/run_multiwinding_terminal_assembly.jl
julia --project=experiments experiments/run_multiwinding_terminal_lift.jl
julia --project=experiments experiments/run_multiwinding_typed_kron.jl
julia --project=experiments experiments/run_transformer_factor_completion.jl
julia --project=experiments experiments/run_transformer_tap_decision_compilation.jl
julia --project=experiments experiments/run_transformer_tap_ac_decision.jl
julia --project=experiments experiments/run_transformer_tap_ac_independent_reproduction.jl
julia --project=experiments experiments/run_multiconductor_parallel_ac.jl
julia --project=experiments experiments/run_four_wire_parallel_ac.jl
julia --project=experiments experiments/run_pi_four_wire_parallel_ac.jl
julia --project=experiments experiments/run_five_bus_cycle_space.jl
julia --project=experiments experiments/run_running_network_cycle_space.jl
julia --project=experiments experiments/run_translation_traps.jl
julia --project=experiments experiments/run_active_radiality.jl
julia --project=experiments experiments/test/typed_kron.jl
julia --project=experiments experiments/run_typed_kron.jl
julia --project=experiments experiments/test/public_api.jl
julia --project=experiments experiments/run_public_api_manifest.jl
julia --project=experiments experiments/test/state_space_units.jl
julia --project=experiments experiments/run_state_space_units.jl
julia --project=experiments experiments/test/certificate_api_matrix.jl
julia --project=experiments experiments/test/kron_ward_scenario.jl
julia --project=experiments experiments/run_kron_ward_scenario.jl
julia --project=experiments experiments/test/certified_approximation.jl
julia --project=experiments experiments/run_certified_approximation.jl
python3 experiments/generate_five_bus_cycle_figure.py
python3 experiments/generate_numerical_structure_views.py
python3 experiments/render_argument_diagrams.py
julia --project=experiments experiments/run_ybus_jacobian_witness.jl
python3 experiments/render_ybus_jacobian_view.py
julia --project=experiments experiments/run_nonlinear_kkt_witness.jl
python3 experiments/render_nonlinear_kkt_view.py
python3 scripts/attach_typed_certificate_interfaces.py
python3 scripts/generate_semantic_evaluator_matrix.py
python3 scripts/generate_knowledge_base_indexes.py
bash scripts/reproduce_clean_package_matrix.sh
python3 scripts/check_artifacts.py
```

The figure renderers require Pillow. Their generated PNGs are committed, so
Pillow is not required to build the book unless the figures are being
regenerated. The five-bus renderer reads the Julia-generated analysis rather
than duplicating graph or witness data in the drawing code.

`run_vertical_slice.jl` writes:

- `data/running-network/v0.1.0.json`: the canonical generated BMOPF fixture;
- `experiments/generated/summary.json`: validation and solve results;
- `experiments/generated/parallel-branch-certificate.json`: the first
  decision-preservation counterexample;
- `experiments/generated/provenance.json`: package versions and the exact local
  BMOPFTools repository state used for generation.
- `experiments/generated/view-source-maps.json`: complete source maps for the
  six rendered representations, bound to fixture and figure hashes;
- `experiments/generated/port-factor-architecture.json`: the checked minimal
  ``(𝔓, Λ)`` structural witness for the running network;
- `experiments/generated/five-bus-port-factor-witness.json`: a direct
  structural port--factor lift of the seven identified scalar lines on the
  five-bus multigraph, retaining bus junctions, line orientation, and member
  identity without claiming a numerical factor evaluator;
- `experiments/generated/positive-sequence-collapse-witness.json`: the
  positive-sequence diagonalization witness and non-circulant rejection;
- `experiments/generated/certified-approximation-witness.json`: a declared
  residual-to-state-to-constraint-to-decision margin chain for the Ward
  scenario fixture, including feasible, ambiguous, and violated cases;
- `experiments/generated/degree-two-series-certificate.json`: the first
  executable guarded series-elimination rule.
- `experiments/generated/coordinate-normalization-certificate.json`: an exact,
  invertible conductor-coordinate rewrite;
- `experiments/generated/coordinate-series-composition-certificate.json`: the
  explicit normalization-then-elimination composition trace;
- `experiments/generated/parallel-opf-comparison.json`: source, naïve aggregate,
  and exact lifted solutions for the two-bus decision example.
- `experiments/generated/transformer-winding-normalization-certificate.json`:
  an exact delta-winding terminal-coordinate action derived from fixture `x1`;
- `experiments/generated/multiwinding-leakage-compilation-certificate.json`:
  an exact pairwise-test to full reference-impedance compilation for fixture
  `x1`, including invariance across all three winding-reference choices;
- `experiments/generated/multiwinding-terminal-assembly-certificate.json`:
  exact WYE/WYE/DELTA connection-factor assembly with a terminal admittance
  and retained coil-current constraint map;
- `experiments/generated/transformer-factor-completion-certificate.json`:
  exact fixed-linear composition of leakage, typed voltage transfers,
  winding-2 excitation, and transformer-internal grounding, with component
  recovery maps and an independent BMOPFTools primitive cross-check;
- `experiments/generated/transformer-tap-decision-certificate.json`: exact
  continuous/discrete tap-domain retention plus a discrete decision witness
  showing why freezing the start value is not decision preserving;
- `experiments/generated/transformer-tap-ac-decision-certificate.json`: the
  full 11-terminal transformer factor embedded in nonlinear voltage, KCL,
  power-balance, voltage-limit, and recovered-current constraints, with exact
  finite tap enumeration;
- `experiments/generated/transformer-tap-ac-independent-certificate.json`: a
  separate finite-difference Newton, continuation, and bisection reproduction
  of all tap-conditioned boundaries and the selected tap, including explicit
  failed-bracket guards;
- `experiments/generated/multiconductor-parallel-ac-certificate.json`: source,
  naïve aggregate, exact lifted, and certified exact-pruned results for the
  coupled phase-neutral AC case, including the proportional member-current
  cross-check and a general two-end quadratic-containment certificate.

`experiments/transformations/MulticonductorFlowLimitRedundancy.jl` implements
the package-independent containment kernel for fixed linear complex current
maps. Its tests include singular quadratic forms, a non-proportional
multiconductor positive case, reverse implication failure, and a candidate
that passes at `ij` but fails at `ji`.

- `experiments/generated/four-wire-parallel-ac-certificate.json`: a reciprocal,
  non-proportional three-phase four-wire AC decision case. It contains the
  exact joint component-disc certificate, source/lifted/pruned/naive solutions,
  and an independent finite-difference Newton continuation and bisection
  reproduction; tests also cross-check both line primitives with BMOPFTools.
- `experiments/generated/pi-four-wire-parallel-ac-certificate.json`: the full
  nominal-pi extension with distinct from/to shunts, eight both-end current
  limits, exact joint-disc pruning, source/lifted/pruned/naive AC solutions,
  independent continuation, BMOPFTools primitive cross-checks, and a finite
  three-state shunt envelope that rebuilds the map and re-solves each state.
- `experiments/generated/three-member-four-wire-parallel-ac-certificate.json`:
  a scoped three-member full-AC joint-pruning probe.  Member 3 is bounded by a
  fixed linear recovery map from members 1 and 2; the recorded support bound
  certifies deletion of member-3 limits for this local fixed-map witness only.
  It also carries an independent finite-difference continuation and bisection
  reproduction of the source boundary.
- `experiments/generated/five-bus-cycle-space-analysis.json`: a line-identity
  incidence and cycle-space analysis of the five-bus multigraph. It records a
  three-dimensional source cycle space, the two-dimensional simple projection,
  an exact scalar `Ybus` aggregation check, the parallel-limit decision
  witness, and BMOPFTools' parallel-aware extra-edge count.
- `experiments/generated/running-network-cycle-space-witness.json`: direct
  line-identity cycle evidence for the running fixture. It retains the
  parallel ``l_1/l_2`` fibre, records one multigraph cycle and zero cycles in
  the simple projection, and explicitly excludes the switch and multi-terminal
  transformer from this scalar line view.
- `experiments/generated/five-bus-figure-manifest.json`: hashes binding the
  verified five-bus analysis to the generated cycle-basis, transformation-map,
  and feasible-set figures used in the chapter.
- `experiments/generated/translation-trap-witnesses.json`: three small
  package-independent witnesses for connectivity versus energization, complex
  symmetry versus Hermitian structure, and terminal-specific nominal-pi
  currents and ratings.
- `experiments/generated/active-radiality-witness.json`: an inventory-versus-
  active-state certificate reporting simple-projection and identified-member
  radiality, including a hidden parallel-member cycle.
- `experiments/generated/five-bus-active-radiality-witness.json`: direct
  inventory and declared-spanning-tree radiality checks for the five-bus
  multigraph at both member and simple-projection levels;
- `experiments/generated/numerical-structure-witness.json`: a structural
  five-bus witness separating member edges, simple-projection edges, one
  Schur-elimination fill edge, and a declared equation-variable dependency
  pattern. Its fill-in and Jacobian-dependency companion SVGs are generated
  from the same artifact source, with a crosswalk to the direct five-bus
  typed-Kron fill and recovered branch-limit observation.
- `experiments/generated/ybus-jacobian-witness.json`: a pinned BMOPFTools
  passive/constant-Z linearized Ybus export for the running fixture, together
  with its realified current-voltage matrix, condition estimates, and checks.
- `experiments/generated/nonlinear-kkt-witness.json`: a finite-difference
  nonlinear parallel-member/aggregate decision Jacobian and symbolic KKT
  fill comparison under two elimination orders.
- `experiments/generated/typed-kron-witness.json`: a package-independent
  multiconductor Kron fixture covering coordinate covariance, affine boundary
  recovery, source-current limits, and positive/negative line--shunt library
  realizability cases.
- `experiments/generated/five-bus-typed-kron-witness.json`: direct scalar
  five-bus Kron evidence eliminating the pendant bus ``m`` through line ``x``
  and matching the retained boundary ``Y``-bus to direct leaf deletion. The
  same witness eliminates non-pendant bus ``l`` and records the resulting
  ``j-m`` and ``k-m`` Schur-complement fill edges;
- `experiments/generated/typed-kron-certificate.json`: the version 1.1.0
  preservation certificate for that typed Kron fixture.
- `experiments/generated/kron-ward-scenario-comparison.json`: a shared
  observation comparison of exact Kron, a base-state Ward-style equivalent,
  an explicit-support extended Ward target, and a sparsity-penalized
  scenario-selected target. The extended target is exact only for the
  declared fixed-current linear fixture because its boundary support
  injection is supplied explicitly.
- `experiments/generated/nonlinear-ward-witness.json`: a scoped scalar
  constant-power probe that compares a damped-Newton nonlinear solve with a
  base-state Ward target and reports a local inverse-Jacobian decision bound.
  It is exploratory evidence, not a global AC certificate.
- `experiments/generated/solver-diagnostics-crosswalk.json`: a package-level
  crosswalk binding the BMOPFTools Ybus/Jacobian witness to the finite-
  difference nonlinear KKT witness, including node order and symbolic fill
  under two elimination orders. It also probes BMOPFTools' checked-KKT callback
  and its near-singular rejection guard, and runs one minimal parameterized OPF
  through DiffOpt with a finite-difference sensitivity check. The solver-
  provided KKT matrix is captured with ordered JuMP variable/constraint
  metadata; four remaining callback rows are retained as an explicit internal
  boundary, and solver-native ordering statistics remain outside the export.
  A regular JuMP mirror records native affine/quadratic variable support (rows
  and nonzeros), with a separate JuMP/MOI `NLPEvaluator` view retained for the
  nonlinear block. It is deliberately marked as model-level, not solver-
  internal KKT ordering or factorization data.
  The witness also records BMOPFTools' differentiability report, including
  active, near-active, weakly-active, and violated inequality labels plus
  qualifications; `ready` is state provenance, not a proof of LICQ, strict
  complementarity, second-order sufficiency, global optimality, or branch
  stability.
  It also compares a two-member parallel source with its scalar equivalent:
  the tested voltage sensitivity is preserved while KKT structure changes.
- `experiments/generated/guarded-parallel-reduction-witness.json`: scoped
  singular-map rejection, multi-retained support accounting, and
  state-conditioned recovery-map evidence for the parallel-limit cases. The
  nominal-``\pi`` certificate adds a separate singular-shunted refusal probe;
  neither artifact claims an exact full-map singular reduction or a global AC bound.
  The nominal-``\pi`` certificate additionally contains a series-only singular
  endpoint-voltage-drop recovery witness: the full two-end map remains
  rank-deficient, while the declared zero-neutral rows are recovered exactly
  without a pseudoinverse. Singular shunted reductions remain open.
- `experiments/generated/transformer-control-family-witness.json`: a scoped
  control-law witness for scalar magnitude, phase-angle, independent-phase,
  mechanically coupled, automatic-deadband, and tap-dependent-loss cases. Each
  control law now has a small JuMP/Ipopt feasibility probe; this is solver-backed
  control-domain evidence. Phase-angle and tap-dependent-loss maps run through
  a two-bus AC served-current probe, while independent-phase and mechanically
  coupled maps run through a three-phase uncoupled probe. These are network
  boundary tests. A fourth probe adds mutual impedance, neutral displacement,
  and explicit return-current KCL; it is still a small fixture, not a claim
  about a full neutral-coupled unbalanced OPF.
- `experiments/generated/node-breaker-state-witness.json`: a generated
  node--breaker fixture with open, closed, and unknown switch states, including
  connectivity contraction and member/adjoining/compiled-bus radiality.
- `experiments/generated/running-network-radiality-witness.json`: derived
  base/switch-open/line-outage states for the running-network fixture,
  retaining line identity, transformer winding provenance, and ordered
  conductor-terminal maps.
- `experiments/generated/conductor-terminal-lift-witness.json`: conductor-
  terminal junctions, ordered line/switch ports, three-winding transformer
  incidence, and state-conditioned switch contraction for the running fixture.
- `experiments/generated/five-bus-conductor-terminal-lift-witness.json`: the
  scalar two-terminal special case on the five-bus line-identity fixture,
  retaining fourteen endpoint ports, seven line factors, and the parallel
  fibre without adding multiconductor or switching semantics;
- `experiments/generated/multiwinding-terminal-lift-witness.json`: direct
  structural lifting of the serialized three-winding transformer contract to
  ordered winding ports, preserving WYE neutral and DELTA terminal semantics
  while keeping internal grounding and excitation shunt observations separate;
- `experiments/generated/multiwinding-typed-kron-witness.json`: direct
  typed-Kron precondition evidence for the serialized transformer terminal
  assembly. The declared DELTA block is singular without terminal grounding,
  so elimination is refused rather than replaced by a pseudoinverse, while
  the eliminated winding's limit observation remains explicit.
- `experiments/generated/hierarchy-boundary-witness.json`: checked container
  hierarchy, typed source/target boundaries, partial refinement, open-system
  gluing, and state-conditioned switch boundary maps.
- `experiments/generated/public-api-manifest.json`: the versioned package
  facade boundary, separating stable multigraph/Kron primitives from
  experimental solver-backed evidence.
- `experiments/generated/state-space-unit-witness.json`: checked typed
  variables, unit families and per-unit bases, boundaries, and explicit switch
  state domains.
- `experiments/generated/semantic-evaluator-matrix.json`: release-oriented
  traceability rows binding all sixteen certificates to their semantic
  evaluator source and test path.
- `experiments/generated/clean-package-matrix.json`: the latest separately
  instantiated package-checkout result, pinned to the BMOPFTools commit used
  for the clean run.

The Julia certificate generators attach the canonical typed state-space/unit
crosswalk directly through `TransformationContracts.attach_typed_interfaces`.
For legacy artifacts or a bulk migration, run
`python3 scripts/attach_typed_certificate_interfaces.py`; the artifact checker
and package matrix test validate the attachment shape and witness reference.

The dependency-light package candidate is
`package/GraphModelsForPowerNetworks/`. Its source modules are the canonical
implementation of the reusable core; `experiments/src/GraphModelsForPowerNetworks.jl`
and the four corresponding transformation paths are compatibility entry points
for the solver-backed experiment project. The package is versioned `0.1.0` but
is not yet published or covered by a long-term compatibility promise.

All sixteen transformation artifacts conform to version 1.1.0 of
`schemas/transformation-certificate.schema.json`. The checker enforces the
common required fields, six typed interfaces, classifications, identifiers,
and claim registration.

The fixture is synthetic and released with the book. It is not derived from a
utility model. The numerical values are intended to expose representational
questions; they are not equipment-design recommendations.

The local BMOPFTools checkout may contain uncommitted work. The provenance file
therefore records its commit, dirty status, tracked-diff hash, and hashes for
untracked files. A result is called pinned only when `dirty` is `false`.

Run `bash scripts/reproduce_clean_fixture.sh` to clone the current BMOPFTools
commit into an isolated temporary directory, execute the fixture and tests, and
compare the clean export with the canonical fixture. Its retained record is in
`experiments/generated/clean-reproduction`.

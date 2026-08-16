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
julia --project=experiments experiments/run_five_bus_transformer_lowering.jl
julia --project=experiments experiments/run_four_winding_lowering.jl
julia --project=experiments experiments/run_layer_lens_api_witness.jl
julia --project=experiments experiments/run_running_network_cycle_space.jl
julia --project=experiments experiments/run_translation_traps.jl
julia --project=experiments experiments/run_narrow_circuit_transformations.jl
julia --project=experiments experiments/run_load_grounding_witnesses.jl
julia --project=experiments experiments/run_balanced_transmission_witness.jl
julia --project=experiments experiments/run_four_wire_impedance_model_ladder.jl
julia --project=experiments experiments/run_active_radiality.jl
julia --project=experiments experiments/run_topology_projection_witness.jl
julia --project=experiments experiments/run_nodal_source_recovery_witness.jl
julia --project=experiments experiments/run_nodal_recovery_guards_witness.jl
julia --project=experiments experiments/run_multiconductor_recovery_witness.jl
julia --project=experiments experiments/run_noisy_multiconductor_recovery_witness.jl
julia --project=experiments experiments/run_nonlinear_grounding_local_bound_witness.jl
julia --project=experiments experiments/run_compiled_views_surgery_witness.jl
julia --project=experiments experiments/run_australian_carson_reproduction.jl
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
python3 scripts/reproduce_explicit_earth.py
python3 scripts/reproduce_balanced_transmission.py
python3 scripts/reproduce_load_models.py
python3 scripts/reproduce_connection_maps.py
python3 scripts/reproduce_load_continuation.py
python3 scripts/reproduce_neutral_kron.py
python3 scripts/check_artifacts.py
```

The Australian source-backed reproduction is regenerated with:

```bash
julia --project=experiments experiments/run_australian_carson_reproduction.jl
```

`data/australian_source_inputs.toml` contains only construction-level inputs
lifted from the `ImpedanceModels.jl` line-library history.  The generated
Carson primitives and OpenDSSDirect solves are written to
`generated/australian-carson-reproduction.json`.  The Australian overhead
`Zabcn` and underground `CS1035` matrices are loaded only as independent
reference outputs.  The source repository does not identify a raw cable
construction that maps to `CS1035`, so the artifact records that gap rather
than silently using the published matrix as an input.  The separate
`data/australian_source_audit.toml` file is a small machine-readable register
of provenance status: `lifted` and `derived_reference` describe source-backed
fields, while `inferred_from_probe` and `unresolved` identify hypotheses and
open mappings.  It records the overhead 60 Hz/conductor-order explanation as
an inference, and the underground negative-height/OpenDSS reference-plane
workaround as a modelling caveat.

The generated record additionally validates against the v0.1
`power-network-impedance` interchange contract in
`data/impedance_contract_schema.toml`.  Its required fields keep ordered
terminals, series/shunt blocks, units, lineage, views, and findings together;
ampacity limits and grounding assumptions are included as first-class fields;
the contract does not upgrade an inferred or unresolved field into a source
fact.

Each generated load row also carries a package-independent
`LinearAlgebra`-only constant-power reference solve.  Voltage and line losses
agree across balanced and unbalanced rows.  The artifact separates those
line losses from total losses because OpenDSS `Circuit.Losses()` excludes the
separately modelled grounding-reactor loss.

The underground fixture includes `balanced_low_grounding` and
`balanced_high_grounding` rows, so neutral-voltage sensitivity to the grounding
factor is recorded alongside the balanced and unbalanced load rows.

The explicit-earth Kron probe can be regenerated independently with:

```bash
julia --project=experiments experiments/run_explicit_earth_kron.jl
python3 scripts/reproduce_explicit_earth_kron.py
python3 scripts/reproduce_grounding_impedance_sweep.py
python3 scripts/reproduce_nonlinear_grounding_probe.py
python3 scripts/reproduce_nonlinear_two_point_grounding.py
python3 scripts/reproduce_nonlinear_two_point_continuation.py
python3 scripts/reproduce_three_member_state_envelope.py
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
- `experiments/generated/four-wire-impedance-model-ladder.json`: a deterministic
  four-wire impedance-model path from a coupled conductor primitive through
  neutral/phase reduction and sequence views, with preservation layers and
  explicit risk tags for each transformation;
- `experiments/generated/balanced-transmission-witness.json`: a balanced
  three-bus nominal-``\pi`` network solved in phase coordinates and in its
  positive-sequence scalar image, with voltage, nodal-residual, and branch-
  current recovery checks;
- `experiments/generated/balanced-transmission-independent-reproduction.json`:
  an independent standard-library complex solve of that same network, with
  phase/scalar values compared against the Julia witness;
- `experiments/generated/load-model-independent-reproduction.json`: an
  independent damped fixed-point reproduction of the CP/CI/CZ/ZIP load rows,
  including the separate active/reactive ZIP coefficient maps and their
  voltage/current decision margins;
- `experiments/generated/connection-map-independent-reproduction.json`: an
  independent evaluation of the recorded wye and delta terminal maps;
- `experiments/generated/load-continuation-independent-reproduction.json`: an
  independent continuation reproduction that compares converged rows and
  failure scale while avoiding false precision for divergent iterates;
- `experiments/generated/neutral-kron-independent-reproduction.json`: an
  independent reproduction of the four-conductor midpoint neutral-current
  recovery and retained limit violation, including the linear midpoint shunt
  probe and its KCL/current-limit checks;
- `experiments/generated/explicit-earth-kron-witness.json` and
  `experiments/generated/explicit-earth-kron-independent-reproduction.json`:
  a synthetic five-conductor ``(a,b,c,n,e)`` midpoint with an explicit
  neutral--earth bond, separate neutral and earth KCL recovery, and a retained
  neutral-current limit, together with a standard-library reproduction. The
  same artifact includes a three-segment extension with two explicit grounding
  points and separately recovered bond currents;
- `experiments/generated/grounding-impedance-sweep-witness.json` and
  `experiments/generated/grounding-impedance-sweep-independent-reproduction.json`:
  a finite four-case sweep of the two grounding impedances under one fixed
  neutral limit, showing that recovered currents and feasibility can change
  while the structural reduction remains fixed;
- `experiments/generated/nonlinear-grounding-probe-witness.json` and
  `experiments/generated/nonlinear-grounding-probe-independent-reproduction.json`:
  a local state-dependent neutral--earth bond probe showing why the reduced map
  must be recomputed after an endpoint state shift;
- `experiments/generated/nonlinear-two-point-grounding-witness.json` and
  `experiments/generated/nonlinear-two-point-grounding-independent-reproduction.json`:
  a distributed two-bond state-dependent grounding probe with frozen-map failure
  and recomputed-chain recovery;
- `experiments/generated/nonlinear-two-point-grounding-continuation.json` and
  `experiments/generated/nonlinear-two-point-grounding-continuation-independent-reproduction.json`:
  a finite five-state endpoint continuation with recomputed nonlinear bonds,
  frozen-map residuals, and neutral-limit margins;
- `experiments/generated/three-member-state-envelope-independent-reproduction.json`:
  an independent standard-library Newton/bisection reproduction of all four
  three-member AC state-envelope boundaries;
- `experiments/generated/certified-approximation-witness.json`: a declared
  residual-to-state-to-constraint-to-decision margin chain for the Ward
  scenario fixture, including feasible, ambiguous, and violated cases;
- `experiments/generated/degree-two-series-certificate.json`: the executable
  guarded series-elimination rule, including an element-pair mutual-coupling
  rejection and the cross-coupled negative witness that invalidates the
  uncoupled impedance sum by about 11.65% in the recorded fixture;
- `experiments/generated/narrow-circuit-transformations-witness.json`: scalar
  floating star--delta equivalence, grounded-star rejection, and the measured
  loss from adapting unequal endpoint shunts to one shared field;
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
  finite tap enumeration, including a phase-selective unbalanced two-scenario
  tap-pair ledger;
- `experiments/generated/transformer-tap-ac-independent-certificate.json`: a
  separate finite-difference Newton, continuation, and bisection reproduction
  of all tap-conditioned boundaries and the selected tap, including explicit
  failed-bracket guards;
- `experiments/generated/transformer-tap-three-scenario-independent-certificate.json`:
  an independent reproduction of the nine phase-selective scenario/tap
  boundaries and the complete 27-branch tap-path ledger, including the
  independently checked 15-branch at-most-one-movement policy;
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
- `experiments/generated/translation-trap-witnesses.json`: package-independent
  witnesses for connectivity versus energization, complex symmetry versus
  Hermitian structure, terminal-specific nominal-pi currents and ratings, and
  four negative anti-patterns: heterogeneous series merging, external-ground
  absorption, line--transformer flattening, and BIM/BFM branch-index loss.
- `experiments/generated/load-grounding-witnesses.json`: scoped numerical
  comparisons that hold the bus--branch graph fixed while changing (i)
  CP/CI/CZ/ZIP load laws, (ii) explicit wye/delta connection maps, and (iii)
  floating, impedance-grounded, and ideal-grounded neutral relations. It also
  contains a scoped E₂ explicit-earth-conductor case with
  an earth-conductor outage and a phase-to-earth protection threshold. The
  artifact also records maintenance state, two fault classes, an illustrative
  inverse-time relay curve, and a CT-saturation sensitivity probe. It reports
  voltage, current, residual, decision margins, and a scalar continuation probe
  rather than claiming a general load-flow or grounding theorem.
- `experiments/generated/explicit-earth-independent-reproduction.json`: a
  standard-library Python Gaussian-elimination reproduction of the explicit
  earth, CT, and illustrative relay calculations, compared row-by-row with
  the Julia witness.
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
  multiconductor Kron fixture covering coordinate covariance, dense
  within-partition actions, affine boundary recovery, source-current limits,
  reciprocity conventions, fixed-injection scope, and positive/negative
  line--shunt library realizability cases.
- `experiments/generated/five-bus-typed-kron-witness.json`: direct scalar
  five-bus Kron evidence eliminating the pendant bus ``m`` through line ``u``
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

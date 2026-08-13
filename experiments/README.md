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
julia --project=experiments experiments/run_transformer_factor_completion.jl
julia --project=experiments experiments/run_transformer_tap_decision_compilation.jl
julia --project=experiments experiments/run_transformer_tap_ac_decision.jl
julia --project=experiments experiments/run_transformer_tap_ac_independent_reproduction.jl
julia --project=experiments experiments/run_multiconductor_parallel_ac.jl
julia --project=experiments experiments/run_four_wire_parallel_ac.jl
julia --project=experiments experiments/run_pi_four_wire_parallel_ac.jl
julia --project=experiments experiments/run_five_bus_cycle_space.jl
python3 experiments/generate_five_bus_cycle_figure.py
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
  independent continuation, and BMOPFTools primitive cross-checks.
- `experiments/generated/five-bus-cycle-space-analysis.json`: a line-identity
  incidence and cycle-space analysis of the five-bus multigraph. It records a
  three-dimensional source cycle space, the two-dimensional simple projection,
  an exact scalar `Ybus` aggregation check, the parallel-limit decision
  witness, and BMOPFTools' parallel-aware extra-edge count.
- `experiments/generated/five-bus-figure-manifest.json`: hashes binding the
  verified five-bus analysis to the generated cycle-basis, transformation-map,
  and feasible-set figures used in the chapter.

All fifteen transformation artifacts conform to version 1.1.0 of
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

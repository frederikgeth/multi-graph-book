# [Computational case guide](@id computational-cases)

**Page status:** teaching guide to existing evidence and the scalar opening lesson.

Choose a case by the question you want to answer. Commands below run from the
repository root. Start with the scalar lesson; it needs only Python 3 and
prints its result without creating files. The Julia studies use the pinned
`experiments` environment and may regenerate their recorded artifacts.

## First calculation: parallel members

```sh
python3 experiments/lessons/parallel_members.py
python3 experiments/lessons/parallel_members.py --check
```

Expect a passing 165 A aggregate check, a failing 150 A first-member check,
and a derived 110 A aggregate cap. The [opening lesson](@ref
first-failure-parallel-branches) derives every number. Change the voltage
drop, first-member rating, or open-member state and predict the result before
running it. This is exact arithmetic for a declared resistive circuit.

## Assemble a model, then choose its scope

```sh
python3 experiments/lessons/assemble_network.py --check
python3 experiments/lessons/assemble_network.py --misattach-load
python3 experiments/lessons/model_choice.py --check
python3 experiments/lessons/model_choice.py --benchmark
```

The [assembly lesson](@ref source-to-canonical-model) derives the matrix and
checks recovered equipment currents. The deliberate mapping error solves its
own equations but fails the original circuit checks. The [model-choice
exercise](@ref numerical-consequences) compares nominal exactness with an
interval-robust current limit and measures local evaluation cost with recovery.
These commands print results without changing the evidence collection.

## Import, edit, and interpret a model

The [practical modelling chapter](@ref building-and-changing-models) works
through three failures: a rating sentinel misread as a physical zero, a star
reduction updated by deleting the wrong derived edges, and scaled multipliers
reported as physical prices. Derive the expected behavior, run the deliberately
faulty alternatives, then use the source-semantic checks to distinguish them:

```sh
python3 experiments/lessons/practical_model_checks.py
python3 experiments/lessons/practical_model_checks.py --check
```

The 15 test methods include unknown and unrepresentable fields, stale reductions,
linear basis checks, objective/constraint scaling, and nonunique multipliers.
The field adapter is not a complete MATPOWER importer; the dispatch example is
an analytically solved scalar LP, not an OPF solve. No files are written.

## Five further investigations

The coordinate and Kron commands run checks; the case generators update their
artifacts. Read the associated source and target assumptions before interpreting
an accepted transformation. An inapplicable result can correctly identify that
a requested rule does not cover the input.

### Eliminate two series sections

Read [series elimination](@ref degree-two-series-rule), then predict which
assumptions permit elimination and which quantities need recovery.

```sh
julia --project=experiments experiments/run_series_elimination.jl
```

Inspect `experiments/generated/degree-two-series-certificate.json` for the
guards, recovered quantities, and coupled near-miss.

### Relabel conductors

Read [conductor normalization](@ref conductor-coordinate-normalization).
Predict which arrays must change together under a conductor permutation.

```sh
julia --project=experiments experiments/test/coordinate_normalization.jl
```

Inspect the test output and assertions for accepted coordinate actions and
rejected inconsistencies. A relabelling should not change the declared physics.

### Recover a hidden current violation

Read [Kron reduction](@ref kron-ward-opti-kron). Decide whether an exact boundary
relation alone settles an internal neutral-current constraint.

```sh
julia --project=experiments experiments/test/running_network_typed_kron.jl
```

Inspect the boundary residual assertions and recovered neutral-limit witness.

### Put the parallel error in an AC network

Read the [parallel AC case](@ref multiconductor-parallel-ac-case). Predict
whether retaining a terminal equation also retains member feasibility.

```sh
julia --project=experiments experiments/run_multiconductor_parallel_ac.jl
```

Compare the source, naive, lifted, and pruned results in this artifact:

```text
experiments/generated/multiconductor-parallel-ac-certificate.json
```

### Change the transformer tap domain

Read the [transformer tap case](@ref transformer-tap-ac-decision-case). Predict
what a fixed tap snapshot can establish about an adjustable study.

```sh
julia --project=experiments experiments/run_transformer_tap_ac_decision.jl
```

Inspect the tap domain, local solve, recovery, and objective in this artifact:

```text
experiments/generated/transformer-tap-ac-decision-certificate.json
```

## Prepare the larger studies

The [recorded review-case workflow](@ref executable-running-network) creates
an isolated environment and a fresh output directory:

```sh
bash scripts/reproduce_clean_fixture.sh --check
bash scripts/reproduce_clean_fixture.sh
```

It pins the recorded Julia/package combination and runs the scoped returned-
solution checks. It preserves the earlier historical evidence. For other
maintainer case generators above, instantiate the `experiments` environment
with the sibling `BMOPFTools.jl` checkout and check their paired identity:

```sh
julia --project=experiments -e 'using Pkg; Pkg.instantiate()'
python3 scripts/check_federated_knowledge.py --check --bmopf-root ../BMOPFTools.jl
```

These direct generators may update tracked artifacts; use a separate checkout
when investigating them. A passing pair check binds the current knowledge
exports, not every historical experiment. The specialized construction study
has its own [Australian Carson reproduction](@ref australian-carson-reproduction)
boundaries.

## Record the result you can defend

For each run, record the input revision, model assumptions, command, numerical
method and tolerances, source/target quantities, and source checks after
recovery. State whether the evidence is an identity, a numerical witness, or a
local solver result. Explain the next question it leaves unanswered.

For example, a passing coordinate permutation checks consistency of a model
under relabelling. It does not establish that the original conductor data were
correct. Agreement between two solution methods strengthens evidence for the
specified equations; shared construction assumptions still need scrutiny.

The [study workbook](@ref study-workbook) turns these records into a complete
exercise. The [knowledge-base index](@ref knowledge-base-index) provides the
full artifact and claim inventory when you need more detail.

## Read independence at the level of the calculation

The scalar assembly uses a separate equipment evaluator, but shares the
conductances and circuit laws with its stamp builder. The transformer tap
comparison changes the numerical algorithm while sharing primitive matrices
and case assembly. The balanced transmission comparison uses a separate
Gaussian-elimination implementation on the declared common fixture. Each
check challenges a different possible error; none authenticates the inputs
merely by agreeing numerically.

The running-case verification adds post-solve line-current recovery through
package-owned primitives. Its complete-feasibility gate remains indeterminate.
The Australian construction study separately records unresolved provenance of
an external reference matrix. Inspect those boundaries before treating another
successful run as independent support for a physical-model claim. Independent
human review is a further evidence dimension, with no promoted claims here.

## Reproduce the teaching diagrams

The numerical diagrams read the standard-library lessons; the redundancy plate
reads the maintained certificate files. From the repository root:

```sh
python3 experiments/render_teaching_figures.py
python3 experiments/render_parallel_certificate_geometry.py
python3 scripts/test_teaching_figures.py
```

Rendering requires `rsvg-convert`; the checks use only Python's standard library.
Four regression tests check current SVG generation, the parallel witness and
circle scales, the certificate circle scale, and served-fraction bar ratios.
They do not replace scientific or visual review. The SVGs and PNG companions
are maintained together; colour is supplemented by labels, outlines and line
styles.

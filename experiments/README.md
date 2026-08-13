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
python3 scripts/check_artifacts.py
```

The view renderer requires Pillow. The generated PNG is committed, so Pillow is
not required to build the book unless that figure is being regenerated.

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

All five transformation artifacts conform to
`schemas/transformation-certificate.schema.json`. The checker enforces the
common required fields, classifications, identifiers, and claim registration.

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

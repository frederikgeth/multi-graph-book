# Structure-Preserving Graph Models for Power Networks

This repository is a scientific book and living knowledge base on graph representations,
projections, compilation, normalization, and reduction of power-network models.

The central premise is that there is no universally correct "power-system graph." A graph
representation is adequate only relative to the physical, operational, and decision questions it
must support. The project develops typed physical and electrical representations, traceable derived
views, and explicit preservation contracts for transformations between them.

The general baseline is a multiconductor network with arbitrary ordered terminals, explicit neutral
and grounding semantics, full conductor coupling, multi-terminal and multiwinding devices, and
continuous or discrete decision variables. Balanced transmission models are treated as important
derived cases rather than the universal source representation.

The current drafting foundation includes:

- the [reader-facing book plan](BOOK_PLAN.md);
- the scope, representation taxonomy, proposed architecture, and preservation contracts;
- a BMOPFTools-aligned notation contract and a common multiconductor running case;
- a schema-valid numerical running fixture, six generated representation views, and PF/OPF checks;
- executable parallel-branch, conductor-normalization, degree-two-series, and composed preservation certificates;
- a common transformation-certificate JSON schema and validated composition law;
- a solved source/naïve/exact-lifted two-bus parallel decision comparison;
- complete source maps for the six generated views and a claims ledger;
- a systematic scoping-review protocol and evidence-matrix schema;
- projection, compilation, reduction, and guarded normalization;
- a literature map, research agenda, terminology, and seed bibliography.

See [ROADMAP.md](ROADMAP.md) for the proposed work plan and
[QUALITY_CONTROL.md](QUALITY_CONTROL.md) for the evidence and review policy.

## Build locally

Install Julia, then instantiate the documentation environment:

```bash
julia --project=docs -e 'using Pkg; Pkg.instantiate()'
```

Build the HTML site:

```bash
julia --project=docs docs/make.jl
```

Build HTML and the single-file PDF. The PDF uses the bundled Tectonic artifact, so a system TeX
installation is not required:

```bash
julia --project=docs docs/make.jl --pdf
```

Outputs are written to `docs/build/` and `docs/latex_build/`.

## Run the executable slice

With the local `BMOPFTools.jl` repository beside this one:

```bash
julia --project=experiments -e 'using Pkg; Pkg.instantiate()'
julia --project=experiments experiments/run_vertical_slice.jl
julia --project=experiments experiments/run_series_elimination.jl
julia --project=experiments experiments/run_coordinate_series_composition.jl
julia --project=experiments experiments/run_parallel_decision_comparison.jl
julia --project=experiments experiments/test/runtests.jl
julia scripts/check_claims.jl
python3 scripts/check_artifacts.py
bash scripts/reproduce_clean_fixture.sh
```

The generated provenance states whether the BMOPFTools checkout was clean. The
isolated reproduction script has verified fixture version 0.1.0 against clean
BMOPFTools commit `b7aa9a1bb48bcc8b790d3bcf5417d6a32036352a`; dirty development
runs remain recorded separately.

## Write content

Add Markdown pages under `docs/src/` and register them in the `PAGES` list in `docs/make.jl`.
Static assets belong under `docs/src/assets/`. Citations use DocumenterCitations syntax and the
BibTeX database at `docs/src/references.bib`; see [CONTRIBUTING.md](CONTRIBUTING.md).

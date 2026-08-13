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
- a schema-valid numerical running fixture, six illustrated representation views, a simple-topology quotient map, and PF/OPF checks;
- executable parallel-branch, conductor-, transformer-winding-, reference-invariant multiwinding-leakage-, terminal-assembly-, fixed-linear transformer-completion-, parameterized tap-decision-, solver-backed and separately reimplemented transformer-network-, degree-two-series, and composed preservation certificates;
- a typed version 1.1 transformation-certificate JSON schema and validated composition law;
- solved source/naïve/exact-lifted linear and multiconductor AC parallel decision comparisons;
- complete source maps for all generated views and a claims ledger;
- a systematic scoping-review protocol and evidence-matrix schema;
- projection, compilation, reduction, and guarded normalization;
- a literature map, research agenda, terminology, and seed bibliography.

See [ROADMAP.md](ROADMAP.md) for the proposed work plan and
[QUALITY_CONTROL.md](QUALITY_CONTROL.md) for the evidence and review policy.

The HTML knowledge base is the primary product. Its generated [knowledge-base indexes](docs/src/reference/knowledge-base-index.md)
and [chapter-status page](docs/src/reference/chapter-status.md) provide retrieval and evidence
state directly from the claims ledger and generated artifacts. The PDF is a secondary curated
serialization of the same Markdown sources.

The separately reimplemented transformer-network check shares the certified
transformer matrices and case assembly with the primary experiment. It is
independent as a numerical solution path, not yet an independent nameplate or
model-construction reproduction.

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
julia --project=experiments experiments/run_transformer_winding_normalization.jl
julia --project=experiments experiments/run_multiwinding_leakage_compilation.jl
julia --project=experiments experiments/run_multiwinding_terminal_assembly.jl
julia --project=experiments experiments/run_transformer_factor_completion.jl
julia --project=experiments experiments/run_transformer_tap_decision_compilation.jl
julia --project=experiments experiments/run_transformer_tap_ac_decision.jl
julia --project=experiments experiments/run_transformer_tap_ac_independent_reproduction.jl
julia --project=experiments experiments/run_multiconductor_parallel_ac.jl
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

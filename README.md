# What Power-Network Models Preserve

*Graphs, reductions, and decision boundaries*

This repository is a problem-first scientific book and living knowledge base about what is lost
when a power-network model is projected, compiled, normalized, or reduced.

The central problem is not choosing the smallest or most familiar graph. It is deciding whether a
representation still answers the physical, operational, and decision question that motivated the
model. A simplified view may preserve a terminal equation while losing asset identity, grounding,
limits, controls, feasible decisions, measurements, or provenance.

The book develops the vocabulary and tests needed to expose those losses. Typed representations,
traceable views, transformation rules, and certificates are proposed tools for responding to the
problem; they are not presented as a completed universal transformation theory.

The general baseline is a multiconductor network with arbitrary ordered terminals, explicit neutral
and grounding semantics, full conductor coupling, multi-terminal and multiwinding devices, and
continuous or discrete decision variables. Balanced transmission models are treated as important
derived cases rather than the universal source representation.

The current drafting foundation includes the following problem-first route:

- the [reader-facing book plan](BOOK_PLAN.md), including current, reference, worked-case, and
  future-application boundaries;
- the problem statement, representation obligations, canonical-model contract, and preservation
  vocabulary;
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

## Two complementary products

The long-form monograph follows one argument: problem and counterexample, representation
obligations, canonical model, valid collapses and failure modes, preservation contracts,
transformations and recovery, then worked cases and consequences. It is the route for learning
the thesis.

The HTML knowledge base is the exhaustive retrieval surface. Its generated [knowledge-base
indexes](docs/src/reference/knowledge-base-index.md), [chapter-status page](docs/src/reference/chapter-status.md),
claims ledger, literature records, and artifacts are the route for checking a term, claim,
certificate, source, or unresolved boundary. The PDF is a secondary curated serialization of the
same Markdown sources; it follows the argument route but does not reproduce every retrieval index.

See [How to use this book](docs/src/start/how-to-use-this-book.md) for the recommended routes,
evidence labels, and the boundary between established literature, repository witnesses, and open
proposals.

The former `power-network-graph-models/` directory is retained as an archived
historical seed for provenance only; it is not part of the maintained build.

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

On macOS, if the bundled Julia artifact is unavailable or mismatched, install a native Tectonic
binary with Homebrew and point Documenter at it:

```bash
brew install tectonic font-dejavu
DOCUMENTER_TECTONIC="$(command -v tectonic)" julia --project=docs docs/make.jl --pdf
```

The override is optional and affects only the PDF compiler; HTML uses no TeX installation.
The build script supplies a temporary Fontconfig path for the per-user Homebrew font
installation, so no global font-cache configuration is required. On macOS,
`docs/make.jl` also uses `scripts/tectonic-font-wrapper.sh` to point XeTeX at
the per-user DejaVu font files when name-based lookup fails. Set
`MULTIGRAPH_DEJAVU_FONT_DIR` if those files are installed elsewhere.

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
python3 scripts/check_claim_mentions.py
python3 scripts/check_evidence_summary.py
python3 scripts/check_artifacts.py
python3 scripts/check_rendered_outputs.py
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

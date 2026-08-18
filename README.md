# What Power-Network Models Preserve

*Graphs, reductions, and decision boundaries*

[![CI](https://github.com/frederikgeth/multi-graph-book/actions/workflows/docs.yml/badge.svg)](https://github.com/frederikgeth/multi-graph-book/actions/workflows/docs.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://frederikgeth.github.io/multi-graph-book/)

[Read the HTML book](https://frederikgeth.github.io/multi-graph-book/dev/) ·
[Download the long-form PDF](https://frederikgeth.github.io/multi-graph-book/dev/GraphModelsForPowerSystems.pdf)

> [!WARNING]
> This is a rapidly evolving, early-stage initiative. Structure, terminology, claims, and APIs
> (including the LLM-accessibility routes below) can change without notice. Nothing here should
> yet be treated as a stable interface or a finished reference.

> [!IMPORTANT]
> This project is developed with substantial assistance from large language models, under human
> direction and review. Content has not yet completed full independent human review end to end.
> See [QUALITY_CONTROL.md](QUALITY_CONTROL.md) for the evidence and review policy, and treat
> claims accordingly until they carry a recorded review status.

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

The separately reimplemented transformer-network check listed above shares the certified
transformer matrices and case assembly with the primary experiment. It is independent as a
numerical solution path, not yet an independent nameplate or model-construction reproduction.

See [ROADMAP.md](ROADMAP.md) for the proposed work plan and
[QUALITY_CONTROL.md](QUALITY_CONTROL.md) for the evidence and review policy.

## Accessibility

The same source content is organized two ways, for two different reading tasks. The **long-form
monograph** follows one argument: problem and counterexample, representation obligations,
canonical model, valid collapses and failure modes, preservation contracts, transformations and
recovery, then worked cases and consequences — the route for learning the thesis. The **HTML
knowledge base** is the exhaustive retrieval surface built from the same source: generated
[knowledge-base indexes](docs/src/reference/knowledge-base-index.md), a
[chapter-status page](docs/src/reference/chapter-status.md), the claims ledger, literature
records, and artifacts, for checking a term, claim, certificate, source, or unresolved boundary
rather than reading start to end. See [How to use this book](docs/src/start/how-to-use-this-book.md)
for the recommended routes, evidence labels, and the boundary between established literature,
repository witnesses, and open proposals.

Both are available through four access routes:

**a) Raw Markdown.** The canonical source text lives under [`docs/src/`](docs/src/) as plain
Markdown with DocumenterCitations-style citations, readable directly on GitHub and diffable
without building anything. Works for either route.

**b) HTML site (Documenter).** A generated, cross-linked HTML site with search — the primary
surface for the knowledge base (indexes, chapter-status page, claims ledger), and also renders the
monograph pages in argument order. Build it locally with
[Documenter.jl](https://documenter.juliadocs.org/) as described under
[Build locally](#build-locally) below, or read it via the deployed GitHub Pages site once CI
publishing is set up (see the note in that section).

**c) PDF (Tectonic).** A single-file serialization following the monograph's argument route; it
does not reproduce the knowledge base's retrieval indexes. [Download the rendered
PDF](https://frederikgeth.github.io/multi-graph-book/dev/GraphModelsForPowerSystems.pdf), or build
it locally with the bundled Tectonic artifact as described under [Build locally](#build-locally).

**d) MCP access for LLMs.** A retrieval interface over the same corpus for LLM clients, closer in
spirit to the knowledge base than the monograph — an LLM client can query the book directly
instead of relying on its own memory. See [`llm/README.md`](llm/README.md) for the full design
(answer contract, retrieval methods, evaluation). In short:

```bash
python3 scripts/generate_llm_corpus.py --write   # build the retrieval corpus
python3 scripts/mcp_llm_server.py                # serve it to an MCP client over stdio
```

This exposes `book_context`, `book_search`, and the corpus manifest resource over the MCP
stdio JSON-RPC transport. A plain HTTP/JSON service (`scripts/serve_llm_access.py`) and a
command-line search tool (`scripts/search_llm_corpus.py`) are also available for non-MCP clients.
Every response is grounded in the book's claims and sources and returns an explicit
`unsupported` or `under_retrieved` status rather than an uncited answer when the book does not
support one — model memory is not treated as book evidence. This layer is as early-stage as the
rest of the project: routes, tool names, and the retrieval method are still subject to change.

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

CI (`.github/workflows/docs.yml`) already builds the HTML and PDF and deploys the HTML site to the
`gh-pages` branch on every push to `main`. GitHub Pages serving from that branch still needs to be
turned on in the repository settings (and works without restriction once the repository is
public); until then, building locally is the reliable way to read the HTML site or PDF.

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

For the consolidated internal release gate, first rebuild the HTML and PDF,
then write the hashed candidate manifest:

```bash
python3 scripts/check_release_candidate.py --write
```

Subsequent checks use the manifest to detect drift in the claims, bibliography,
review record, source files, generated artifacts, rendered HTML, and PDF:

```bash
python3 scripts/check_release_candidate.py --check
```

The release gate records internal reproducibility only; it does not promote any
claim to external review or replace human literature double-coding.

The generated provenance states whether the BMOPFTools checkout was clean. The
isolated reproduction script has verified fixture version 0.1.0 against clean
BMOPFTools commit `b7aa9a1bb48bcc8b790d3bcf5417d6a32036352a`; dirty development
runs remain recorded separately.

## Write content

Add Markdown pages under `docs/src/` and register them in the `PAGES` list in `docs/make.jl`.
Static assets belong under `docs/src/assets/`. Citations use DocumenterCitations syntax and the
BibTeX database at `docs/src/references.bib`; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The repository is dual-licensed:

- **Book text, documentation, data, and other written material** are licensed under the
  [Creative Commons Attribution 4.0 International License
  (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE) for the
  full legal text. In short: you may share and adapt the material for any purpose, including
  commercially, as long as you give appropriate credit, link to the license, and indicate if
  changes were made.
- **Source code** — the Julia package under [`package/`](package/), the Julia experiments and
  tests under [`experiments/`](experiments/), [`docs/make.jl`](docs/make.jl), and the
  Julia/Python/shell scripts under [`scripts/`](scripts/) — is licensed under the BSD 3-Clause
  License. See [LICENSE-CODE](LICENSE-CODE) for the full legal text.

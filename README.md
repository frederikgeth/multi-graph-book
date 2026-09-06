# Power-System Modelling for Computation

*From circuit equations to optimization and software*

[![CI](https://github.com/frederikgeth/multi-graph-book/actions/workflows/docs.yml/badge.svg)](https://github.com/frederikgeth/multi-graph-book/actions/workflows/docs.yml)

[Read the HTML book and reference library](https://frederikgeth.github.io/multi-graph-book/dev/) ·
[Download the core PDF](https://frederikgeth.github.io/multi-graph-book/dev/GraphModelsForPowerSystems.pdf)

This book teaches how to carry physical assumptions, equipment identities,
constraints, and recoverable quantities from circuit equations into a
computational power-system model. It serves scientifically demanding power
engineers and computer scientists or operations researchers entering the field.

Start with [A plausible model gives the wrong answer](docs/src/start/first-failure-parallel-branches.md).
Two parallel members preserve their summed admittance while a naive rating
changes the feasible set. Derive the failure and repair it with a calculation
that requires only Python 3:

```sh
python3 experiments/lessons/parallel_members.py
```

The [author's preface](docs/src/start/preface.md) explains the experience behind
the work. The [book plan](BOOK_PLAN.md) sets out the eight-part teaching route,
scientific corrections, drafting stages, and review criteria.

## Read, run, and inspect

- **Teaching book:** the selective PDF and HTML route starts with the failure,
  then develops equipment equations, conductors and grounding, computational
  graphs, transformations, constraints, evidence, and an end-to-end study.
- **Reference library:** HTML retains all specialist chapters, terminology,
  research records, generated indexes, claims, and open boundaries. Those
  records support lookup without becoming compulsory PDF chapters.
- **Computational cases:** the [case guide](docs/src/start/computational-cases.md)
  connects lessons to commands, expected evidence, and assumptions to vary.

Canonical Markdown remains under `docs/src/`. The current migration reuses
longer reference chapters in parts of the core; their shorter teaching versions
remain drafting work. PDF links to omitted reference material open the online
library. The existing PDF filename is retained for stable download links.

> This is a developing scientific and teaching draft, produced with substantial
> language-model assistance under human direction. Full independent human
> review remains incomplete. Read claims with their scope and evidence status;
> see [QUALITY_CONTROL.md](QUALITY_CONTROL.md).

## Optional language-model access

The deterministic corpus, qualification-aware context packets, source hashes,
and `unsupported` / `under_retrieved` outcomes expose the same maintained
knowledge through CLI, HTTP and MCP. See [llm/README.md](llm/README.md) and the
[ChatGPT](docs/src/start/chatgpt-access.md) and
[Claude](docs/src/start/claude-access.md) guides.

```sh
python3 scripts/generate_llm_corpus.py --write
python3 scripts/mcp_llm_server.py
```

The [architecture](ARCHITECTURE.md) separates book-owned scientific statements
from executable package behavior in BMOPFTools. Computational reproduction,
source provenance, and independent human review remain distinct evidence.

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

For the isolated, recorded review case (Julia 1.12.6), preserving existing evidence:

```bash
bash scripts/reproduce_clean_fixture.sh --check
bash scripts/reproduce_clean_fixture.sh
```

The command prints a fresh run directory. It pins the case sources and dependency
environment and runs scoped verification, including rejection of an altered
voltage result. The full-feasibility evidence gate intentionally remains
`indeterminate`; see the [verification lesson](docs/src/cases/executable-running-network.md).
The historical August environment was not fully recorded and is not silently
reconstructed by this command.

For maintainer regeneration, use Julia 1.11 or later with the local
`BMOPFTools.jl` repository beside this one. These direct generators can replace
tracked artifacts; use an isolated checkout for exploratory runs:

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

Add Markdown pages under `docs/src/` and register them in `PAGES_HTML` (and `PAGES_PDF` for core material) in `docs/make.jl`.
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

# Structure-Preserving Graph Models for Power Networks

This repository is a scientific book and living knowledge base on graph representations,
projections, compilation, normalization, and reduction of power-network models.

The central premise is that there is no universally correct "power-system graph." A graph
representation is adequate only relative to the physical, operational, and decision questions it
must support. The project develops typed physical and electrical representations, traceable derived
views, and explicit preservation contracts for transformations between them.

The initial notes cover:

- the scope, thesis, representation architecture, and preservation contracts;
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

## Write content

Add Markdown pages under `docs/src/` and register them in the `PAGES` list in `docs/make.jl`.
Static assets belong under `docs/src/assets/`. Citations use DocumenterCitations syntax and the
BibTeX database at `docs/src/references.bib`; see [CONTRIBUTING.md](CONTRIBUTING.md).


# [Review protocol and evidence status](@id review-protocol-evidence-status)

**Page status:** generated scoping-review snapshot and evidence-status record.

This page is generated from `review/snapshot-manifest.json` and the canonical
evidence matrix. It publishes the review state without implying that a
single-coded seed corpus is an independently validated systematic review.

## Published snapshot

| field | value |
| --- | --- |
| protocol version | `0.1.0` |
| snapshot date | `2026-08-17` |
| matrix records | 29 |
| matrix SHA-256 | `770b9f9baa4720e8e89f514e470ba7baec07ace45ea3fd1d0590dbda8c03342b` |
| deduplication rows | 29 |
| deduplication SHA-256 | `9288671ce375781afbc940e65c05a4d10275099af329784cbe105097cacc5d95` |
| independent human double-coding | no |

### Screening and coding counts

| dimension | counts |
| --- | --- |
| screening status | include: **28**; exclude: **1**; uncertain: **0** |
| coding status | `single_coded`: **29** |
| exactness labels | `exact`: **11**; `not_reported`: **1**; `outer`: **1**; `scenario_approximate`: **8**; `unclassified`: **8** |

The current snapshot is therefore a **single-coded seed snapshot**, not a
double-coded corpus. The 2026-08-15 second-coding log recommends eight
rows for promotion after slot repairs and identifies six substantive coding
conflicts; those recommendations remain pending and are not silently
reflected in the canonical matrix.

## Search coverage

The protocol names the following information sources:

- IEEE Xplore
- Scopus
- Web of Science
- Engineering Village/Compendex
- Inspec
- MathSciNet or zbMATH where available
- arXiv
- relevant standards and official software documentation

The dated search runs included in this snapshot are:

- [`2026-08-14-seed-batch.md`](search-runs/2026-08-14-seed-batch.md)
- [`2026-08-15-formulation-landscape.md`](search-runs/2026-08-15-formulation-landscape.md)
- [`2026-08-15-information-model-citation-chase.md`](search-runs/2026-08-15-information-model-citation-chase.md)
- [`2026-08-16-multiphase-and-practical-reductions.md`](search-runs/2026-08-16-multiphase-and-practical-reductions.md)

The search-run files record query families, available platforms, and
limitations for each run. The protocol also requires backward and forward
citation chasing, duplicate resolution, and a saved-search rerun before a
tagged release; these are not claimed complete merely because a row is in
the matrix.

## Evidence-status interpretation

A populated matrix row means that one source-to-target result was coded at a
declared scope. It does not mean that the source is a proof of the book's
architecture, that an exactness label applies to a feasible set, or that a
software conversion preserves provenance and limits. The `exactness_object`,
`recovery_map`, `constraint_map`, and `provenance_map` fields must be read
together.

The second-coding and independent-technical-review documents are retained
as review evidence, but they are not substitutes for an independent human
double-coding pass. The canonical matrix remains the source of published
counts; dated snapshots and reconciliation notes explain proposed changes
without rewriting history.

## Reproducibility inputs

The manifest records 8 hashed protocol, coding, bibliography, and search-run inputs.
Run `scripts/check_review_snapshot.py` to verify the matrix,
deduplication register, record identifiers, and input hashes against this
published snapshot.

The protocol's promised PRISMA-style flow is represented here as a scoped
count table rather than a clinical-review claim: the available evidence is
a seed search with one explicit exclusion, and the screening/coding pipeline
is still being expanded.

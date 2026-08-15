# Search run: 2026-08-15 formulation and graph-model landscape

**Protocol:** 0.2.0  
**Run date:** 2026-08-15  
**Purpose:** expand the scoping-review seed matrix from network-reduction papers
to graph, port, and circuit-formulation precedents. This is still a seed run,
not an exhaustive systematic review or a double-coded release.

## Queries

The following portable queries were executed as web searches and then checked
against the primary record or publisher/official landing page where available:

1. `"power network" graph representation port factor hypergraph multigraph`
2. `"modified nodal" network analysis voltage source branch current`
3. `"sparse tableau" power flow node breaker optimal power flow`
4. `"port-Hamiltonian" graph interconnection electrical network`
5. `typed graph transformation" electrical network rewrite provenance`

The search strings are preserved in `review/search-strings.md`; database-specific
translations, export files, deduplication, and citation chasing remain future
work.

## Records added

The run added six formulation/framework rows to
`review/evidence-matrix.csv`:

- `EV-0005` — Ho, Ruehli, and Brennan, modified nodal analysis;
- `EV-0006` — Hachtel, Brayton, and Gustavson, sparse tableau;
- `EV-0007` — Park, Holzer, and DeMarco, sparse-tableau node--breaker OPF;
- `EV-0008` — Baez and Fong, compositional passive linear networks;
- `EV-0009` — van der Schaft and Maschke, port-Hamiltonian systems on graphs;
- `EV-0010` — Ehrig et al., typed algebraic graph transformation.

All rows are `include` and `single_coded`. They are coded as scoped precedents,
not as evidence that one formulation dominates the others or that the book's
source architecture is uniquely canonical.

## Matrix effects

The evidence matrix now contains ten included single-coded records: four
network-reduction/topology seeds, three circuit-formulation records, and three
graph/port/transformation-framework records. `scripts/check_evidence_matrix.py`
passes the controlled vocabulary and schema checks.

## Limitations and next actions

- No Scopus, Web of Science, Compendex, MathSciNet, or IEEE Xplore export was
  available in this run.
- Search-result pages were used only to locate records; full-text coding should
  be independently repeated for every included row.
- Deduplication, backward/forward citation chasing, and a second coder remain
  open.
- The next evidence pass should add information-model and engineering-compiler
  records, then test whether the graph-family taxonomy is missing a recurring
  power-system representation.

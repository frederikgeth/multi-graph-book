# [Search run: 2026-08-14 seed batch](@id search-run-2026-08-14-seed-batch)

**Protocol:** 0.1.0  
**Run date:** 2026-08-14  
**Purpose:** small seed expansion for the scoping-review matrix; not an
exhaustive database search and not double-coded.

## Queries

1. `power system network reduction Kron Ward equivalent multiconductor paper`
2. `power system parallel line redundant flow limits optimization paper`
3. `CIM CGMES TopologicalNode connectivity topology processing official documentation`

The web search run returned the following primary or official records used for
seed coding:

- [Structure- & Physics-Preserving Reductions of Power Grid Models](https://arxiv.org/abs/1707.03672)
- [Structure-preserving Optimal Kron-based Reduction of Radial Distribution Networks](https://arxiv.org/abs/2508.15006)
- [CGM Building Process Implementation Guide v2.0](https://eepublicdownloads.entsoe.eu/clean-documents/CIM_documents/Grid_Model_CIM/CGM%20BUILDING%20PROCESS%20IMPLEMENTATION%20GUIDE_v2.0.pdf)
- [Identifying Redundant Flow Limits on Parallel Lines](https://molzahn.github.io/pubs/molzahn-redundant_flow_limits.pdf)

## Matrix effects

The run added `EV-0002` through `EV-0004` to
`review/evidence-matrix.csv`; `EV-0001` was already present. All four rows are
`single_coded` and pass `scripts/check_evidence_matrix.py`. The records are
deliberately coded with scoped exactness and limitations rather than being
promoted to established claims.

## Limitations

- No IEEE Xplore, Scopus, Web of Science, Compendex, or MathSciNet export was
  available in this run.
- Deduplication, citation chasing, full-text screening, and second-coder review
  remain outstanding.
- Search-result snippets were used only to locate primary/official records;
  the matrix notes identify where full-text coding is still incomplete.

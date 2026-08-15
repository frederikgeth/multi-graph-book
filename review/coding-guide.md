# Evidence-matrix coding guide

**Guide version:** 0.2.0  
**Applies to:** `review/evidence-matrix.csv`

This guide turns the scoping protocol into row-level decisions. It is intended
to make a second coding pass reproducible; it does not promote a single-coded
row to an established result.

## Unit of coding

Code one source-to-target result at one declared scope. A paper may therefore
produce multiple rows when it contains distinct transformations or study
domains. Do not merge a paper's abstract, software implementation, and
theorem into one row if they have different targets or preservation claims.

## Screening rules

- `include` when the source defines or evaluates a representation,
  transformation, topology processor, recovery/lifting map, or directly
  relevant circuit/graph formulation.
- `exclude` only with one controlled exclusion reason from
  `review/evidence-schema.json`.
- `uncertain` when the available record is insufficient for a defensible
  include/exclude decision. Do not use `not_reported` to hide missing full text.

## Field rules

| Field | Coding rule |
| --- | --- |
| `source_model`, `target_model` | Name the mathematical/data object, not merely the software package or algorithm. |
| `transformation_type` | Use `projection` for information loss, `compilation` for a change of variables/equations, `normalization` for within-family coordinate cleanup, `topology_quotient` for state/connectivity contraction, and reduction types only when variables or network structure are eliminated. Use `other` when the operation does not fit. |
| `exactness` | Code the authors' declared domain, then qualify it in `limitations`; use `unclassified` when no defensible exact/inner/outer/scenario label is available. |
| `exactness_object` | Record what the exactness label applies to: an equation identity, boundary behaviour, feasible set, connectivity view, representation definition, or observation sample. Do not compare labels across different objects. |
| `phase_neutral_ground_scope` | Record explicit treatment. Absence of discussion is `not_reported`, not evidence of omission. |
| `multi_terminal_scope` | Distinguish native n-port support from pairwise compilation or no statement. |
| `preserved_observations` | List what is actually shown or specified, not what a reader might infer. |
| `retained_constraints` | Separate equations from ratings, switching decisions, objectives, and feasible sets. |
| `recovery_map`, `provenance_map` | Use `none reported` when the source does not provide one; do not infer reversibility from an equivalent boundary response. |
| `evidence_type` | `proof`/`derivation` for mathematical arguments, `empirical` for measured study results, `software` for implementation documentation or code, `standard` for standards/profile material, `engineering_practice` for operational procedures, and `mixed` for a combination. |
| `coding_status` | `single_coded` means one pass; `double_checked` requires an independent second pass and a recorded resolution of disagreements. |

## Second-coder procedure

1. Copy the current matrix to a dated working snapshot without editing the
   canonical file.
2. Re-read the source record and code independently using this guide.
3. Compare controlled fields first, then free-text scope and limitations.
4. Record disagreements by `record_id` and field; resolve by discussion or
   retain `conflict` with a note.
5. Change `coding_status` to `double_checked` only after the resolution is
   recorded and the DOI/title duplicate register has been updated.
6. Run `scripts/check_evidence_matrix.py` and preserve the dated snapshot,
   query log, and matrix checksum.

## Interpretation guard

The evidence map describes the literature; it is not itself a proof that the
book's architecture is canonical. In particular, an exact boundary equation,
a software conversion, and a standard topology view can all be valid while
preserving different power-network identities, constraints, decisions, and
provenance.

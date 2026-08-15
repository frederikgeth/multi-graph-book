# Evidence-matrix reconciliation note

**Date:** 2026-08-15  
**Status:** automated reconciliation; not human double coding

This note records the controlled-field repairs applied to the canonical
`review/evidence-matrix.csv`. The dated second-coding snapshot remains
unchanged. All rows remain `single_coded`; a later independent human pass must
still confirm or revise these decisions before any row is marked
`double_checked`.

## Controlled-field resolutions

| Record | Field | Reconciliation | Reason |
| --- | --- | --- | --- |
| `EV-0002` | `transformation_type` | `approximate_reduction` | The source describes network reduction with multiple equivalence meanings; `other` hid the elimination operation. Exactness remains `unclassified`. |
| `EV-0003` | `exactness` | `scenario_approximate` | The evidence is scenario- and linearized-error-bounded; it is not an exact/outer feasible-set certificate. |
| `EV-0008` | `transformation_type` | `exact_behavioral_reduction` | Port black-boxing hides internal variables while preserving declared boundary behaviour; it is not merely a change of equations. |
| `EV-0009` | `transformation_type`, `exactness` | `other`, `unclassified` | The record defines a port-Hamiltonian representation and interconnection language rather than documenting an exact power-network compilation. |
| `EV-0010` | `transformation_type` | `other` | Algebraic graph rewriting is a rewrite framework, not a change of variables/equations; exactness remains unclassified. |
| `EV-0013` | `transformation_type` | `approximate_reduction` | The OpenDSS procedures eliminate or aggregate network structure; their option-specific preservation domain is not formalized. |
| `EV-0007`, `EV-0010`, `EV-0012` | `provenance_map` | `none reported` | Limitation prose was in the wrong slot and has been moved into `limitations`. |

## Exactness object

Every row now carries `exactness_object`, which identifies what an exactness
label refers to. This prevents an equation identity, a boundary-behaviour
black box, a connectivity quotient, and a feasible-set statement from being
counted as the same kind of exact result.

The current matrix has no `exclude` or `uncertain` rows, so it still does not
support a PRISMA-style screening flow. The genuine second-coder task remains
open.

## Coverage expansion

The canonical matrix now includes seven priority records from the verified
bibliography seed: the classical Ward family (`EV-0015`--`EV-0017`), exact
scalar Kron reduction (`EV-0018`), line-limit-preserving equivalencing
(`EV-0019`), recoverability (`EV-0020`), and compound polyphase nodal
assembly (`EV-0021`). These are deliberately coded at their documented scope;
they do not turn external equivalencing into a universal decision-preserving
transformation, or a compound nodal matrix into an invertible asset model.
Their deduplication entries and snapshot checksum were refreshed together with
the matrix.

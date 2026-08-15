# Independent-review packet: highest-risk claims (refreshed)

**Packet date:** 2026-08-15  
**Purpose:** provide a current, reproducible hand-off for independent
mathematical and power-system review of the highest-risk claims. This packet
records local reproducibility only; empty reviewer fields are not evidence of
independent validation.

The 2026-08-14 packet remains in `review/archive/` as a historical snapshot.
This refresh incorporates the repaired series, typed-Kron, transformer, and
parallel-case records without rewriting that archival document.

## Review protocol

For each claim, the reviewer should:

1. read the linked chapter and inspect the cited generated artifact;
2. run the listed test in a clean environment where practical;
3. check assumptions, coordinate/order conventions, and scope;
4. record `accept`, `revise`, or `reject`, with a short technical reason;
5. identify whether any issue is mathematical, numerical, semantic, or
   presentation-related.

A successful solver run is not a global optimality or physical-realizability
proof unless the claim explicitly says so.

## Local reproduction status (not independent review)

The current packet tests pass under Julia 1.12.6 with `--startup-file=no` and
the `experiments` project:

| Test | Result |
| --- | ---: |
| `typed_kron.jl` | 20 / 20 |
| `running_network_typed_kron.jl` | 13 / 13 |
| `multiconductor_parallel_ac.jl` | 41 / 41 |
| `series_elimination.jl` | 22 / 22 |
| `transformer_winding_normalization.jl` | 12 / 12 |

These results establish local reproducibility of the packet commands only;
they do not fill the reviewer record below.

## Claims for review

| Claim | Core question | Chapter | Artifact | Reproduction |
| --- | --- | --- | --- | --- |
| `TR-KRON-001` | Does the power-dual block-coordinate action commute with typed Schur reduction under the stated partition and fixed-injection assumptions? | `docs/src/transformations/kron-ward-opti-kron.md` | `experiments/generated/typed-kron-certificate.json`; `experiments/generated/running-network-typed-kron-witness.json` | `julia --project=experiments experiments/test/typed_kron.jl`; `julia --project=experiments experiments/test/running_network_typed_kron.jl` |
| `TR-PAR-004` | Do the source, lifted, and exact-pruned AC formulations preserve the declared feasible set, and is the summed-limit aggregate a relaxation? | `docs/src/cases/multiconductor-parallel-ac-decision.md` | `experiments/generated/multiconductor-parallel-ac-certificate.json` | `julia --project=experiments experiments/test/multiconductor_parallel_ac.jl` |
| `TR-SER-001` | Do the guarded degree-two series assumptions exclude pairwise mutual coupling and preserve the stated terminal relation? | `docs/src/transformations/degree-two-series-elimination.md` | `experiments/generated/degree-two-series-certificate.json` | `julia --project=experiments experiments/test/series_elimination.jl` |
| `TR-XFMR-001` | Does terminal normalization preserve the full WYE/DELTA incidence relation, the dual current map, declared limits, and complex power? | `docs/src/transformations/transformer-winding-coordinate-normalization.md` | `experiments/generated/transformer-winding-normalization-certificate.json` | `julia --project=experiments experiments/test/transformer_winding_normalization.jl` |

## Scope cautions

- `TR-KRON-001` is a finite-dimensional linear theorem. The running-network
  witness is a four-conductor midpoint example and now includes an explicit
  neutral-shunt witness; it does not establish a general nonlinear or
  transformer-internal elimination theorem.
- `TR-PAR-004` is a proportional two-conductor AC case. The reported values
  are on the traced high-voltage branch, Ipopt solves are local, and exact
  pruning relies on exact proportionality. The independent re-derivation was
  automated, not human peer review.
- `TR-SER-001` is exact terminal behaviour only under its declared linear,
  series-only, uncoupled-junction assumptions; it is not closure of a
  homogeneous physical line library.
- `TR-XFMR-001` normalizes typed terminal/coil incidence. Its certificate now
  records the dual terminal-current map, terminal-versus-coil limit semantics,
  and executable power checks; compact vector-group serialization remains
  outside the claim.

## Reviewer record

| Claim | Reviewer | Date | Decision | Issue class | Notes |
| --- | --- | --- | --- | --- | --- |
| `TR-KRON-001` |  |  |  |  |  |
| `TR-PAR-004` |  |  |  |  |  |
| `TR-SER-001` |  |  |  |  |  |
| `TR-XFMR-001` |  |  |  |  |  |

Until these rows are completed by an independent reviewer, the claims remain
locally validated rather than independently reviewed.

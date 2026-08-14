# Independent-review packet: highest-risk claims

**Packet date:** 2026-08-14  
**Purpose:** make independent mathematical and power-system review of the
highest-risk claims reproducible. This packet is preparation for review; an
empty reviewer field is not evidence of independent validation.

## Review protocol

For each claim, the reviewer should:

1. read the linked chapter and inspect the cited generated artifact;
2. run the listed test in a clean environment where practical;
3. check the stated assumptions, coordinate/order conventions, and scope;
4. record `accept`, `revise`, or `reject`, with a short technical reason;
5. identify whether the issue is mathematical, numerical, semantic, or
   presentation-related.

The reviewer should not treat a successful solver run as a global optimality
or physical-realizability proof unless the claim explicitly says so.

## Local reproduction status (not independent review)

On 2026-08-14 the five packet reproduction tests were rerun with
`--startup-file=no`, the `experiments` project, and a clean-plus-user Julia
depot path to avoid shared precompile state. All passed:

| Test | Result |
| --- | ---: |
| `typed_kron.jl` | 20 / 20 |
| `running_network_typed_kron.jl` | 7 / 7 |
| `multiconductor_parallel_ac.jl` | 41 / 41 |
| `series_elimination.jl` | 15 / 15 |
| `transformer_winding_normalization.jl` | 10 / 10 |

These results establish reproducibility of the local packet commands only;
they do not fill the independent reviewer record below.

## Claims for first review

| Claim | Core question | Chapter | Artifact | Reproduction |
| --- | --- | --- | --- | --- |
| `TR-KRON-001` | Does the power-dual block-coordinate action commute with the typed Schur complement under the stated invertibility assumptions? | `docs/src/transformations/kron-ward-opti-kron.md` | `experiments/generated/typed-kron-certificate.json`; `experiments/generated/running-network-typed-kron-witness.json` | `julia --project=experiments experiments/test/typed_kron.jl`; `julia --project=experiments experiments/test/running_network_typed_kron.jl` |
| `TR-PAR-004` | Do the source, lifted, and exact-pruned AC formulations preserve the declared feasible set, and is the summed-limit aggregate genuinely a relaxation? | `docs/src/cases/multiconductor-parallel-ac-decision.md` | `experiments/generated/multiconductor-parallel-ac-certificate.json` | `julia --project=experiments experiments/test/multiconductor_parallel_ac.jl` |
| `TR-SER-001` | Does zero-injection degree-two elimination require any additional mutual-coupling or boundary assumptions beyond those stated? | `docs/src/transformations/degree-two-series-elimination.md` | `experiments/generated/degree-two-series-certificate.json` | `julia experiments/test/series_elimination.jl` |
| `TR-XFMR-001` | Is right-multiplication by the inverse terminal permutation the correct typed-factor normalization, including WYE/DELTA incidence and round-trip voltage behavior? | `docs/src/transformations/transformer-winding-coordinate-normalization.md` | `experiments/generated/transformer-winding-normalization-certificate.json` | `julia experiments/test/transformer_winding_normalization.jl` |

## Scope cautions to record

- `TR-KRON-001` is a finite-dimensional linear theorem. The running-network
  witness is a four-conductor series-line midpoint example; it does not add
  shunts, nonlinear loads, or transformer-internal elimination to the theorem.
- `TR-PAR-004` is an empirical JuMP/Ipopt case with a closed-form comparison;
  the local nonlinear solves are not presented as global OPF certificates.
- `TR-SER-001` is exact terminal behavior under its declared linear series
  assumptions, not closure of a homogeneous physical line library.
- `TR-XFMR-001` normalizes typed terminal/coil incidence. Compact vector-group
  serialization and every grounding convention are outside the claim.

## Reviewer record

| Claim | Reviewer | Date | Decision | Issue class | Notes |
| --- | --- | --- | --- | --- | --- |
| `TR-KRON-001` |  |  |  |  |  |
| `TR-PAR-004` |  |  |  |  |  |
| `TR-SER-001` |  |  |  |  |  |
| `TR-XFMR-001` |  |  |  |  |  |

Until these rows are completed by an independent reviewer, the claims remain
locally validated rather than independently reviewed.

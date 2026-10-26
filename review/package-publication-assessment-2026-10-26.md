# Package candidate publication assessment

**State:** prepared author assessment; no package branch or PR is published by
this work, and no integration pin is changed. This is not a merge recommendation.

## Candidate and review size

The clean local candidate is `6c6515153a6c9d3ed8f59605033c05a5022fa392`, tree
`26c5162bcc5bf24fa502bdc979063ef659694242`, on
`codex/coverage-aware-feasibility`. It contains 31 commits over the published
book pin `97c274946091859b7d9b0e822c96f1e7f9f50c7e`: 113 changed files,
18,756 inserted lines and 228 deleted lines. Much of the addition is bounded
examples, fixtures, tests and generated metadata, but that does not remove the
need for implementation review.

The package export keeps its 107 record IDs: no IDs are added or removed, and
104 serialized records differ. Source-hash propagation is included in that
count; it is not a count of 104 behavioral changes. Inspect semantic metadata
and implementation separately. The Finding registry still has 383 codes.

## Separate the proposed changes for review

| Review area | Package-owned change | Evidence to inspect |
| --- | --- | --- |
| Independent evaluation | `audit_linear_solution` and broader `audit_solution`; declared units/tolerances, coverage and partial-evidence behavior | Direct equations, incidence, unsupported/missing-input cases, serialization and source-bound companion |
| Device and bound scope | Sources, loads, switches, generators, bounded transformer families, voltage/angle/sequence limits and bounded AC IBR/control families | One positive, negative and refused case per admitted family; compare with the book reference's stated boundary |
| Native construction | Shared physical IBR voltage magnitudes with controller-specific aggregation; related transformer documentation corrections | All 72 reference combinations, unique definitions, semantic inputs, legacy overrides, local normalization and native hard-limit comparisons |
| Runtime discovery | Existing API/export records updated with source identity and applicability | Generated export freshness and stable IDs, without promoting scientific claims or execution-MCP exposure |

The independent audit must not use the model builder, native curve/cache or
profiler as its oracle. Reconstructed shunt/return contributions remain distinct
from independently supplied observations. Known failures survive incomplete
coverage. A passing audit does not establish selected-objective correctness,
global optimality, arbitrary custom constraints or physical adequacy.

## Recorded evidence and what is new

At the R2 candidate, the recorded full package suite has 54,774 passes and
37 broken tests; the focused repair has 2,169 passing assertions, including
1,512 semantic-input/definition assertions. The book companion has 1,687 passing
assertions and 50 source bindings. The full suite was not rerun during this
handoff preparation. The handoff validation record separately identifies its
fresh relocated-clone run and environment hashes; do not relabel an older run
as new because the source identity matches.

The book's earlier `bda2772` hosted docs/integration results, and any later book
CI result, do not execute this unpublished candidate. The ordinary integration
continues to test its immutable published pin. Synthetic handoff tests establish
portability behavior, not scientific validation, agent performance or reader
learning.

## Current blockers and decisions

1. Obtain scoped implementation/domain feedback and disposition findings through
   the existing review process. No external reviewers are populated yet.
2. Review the candidate's unsupported topologies, live-provider/filter/DC and
   physical-control boundaries. Do not treat a complete supported coverage row
   as a certificate for a larger problem.
3. The 54-occurrence book readiness queue is now resolved by 51 deterministic
   arithmetic bindings and three bindings to a reconstructed recorded solver
   observation. See `prose-number-resolution-2026-10-26.md` and its machine
   record. The gate passes all 200 high-precision literals; 99 JSON artifacts
   are inventoried. This closes that specific blocker, without claiming that
   the comprehensive release gate passes. The earlier frozen handoff retains
   its original open queue and requires this separate resolution addendum.
4. Decide how to publish the package proposal. A concrete draft description is
   prepared in `package-candidate-draft-pr-2026-10-26.md`; publication and package
   CI have not occurred. The local Git handoff makes exact sources available
   for review without silently changing the public integration contract.

## Order after an explicit publication decision

Publish the reviewed package branch as a draft proposal, keep its full review
diff visible, and run package-owned CI. Review and address findings before
merging. The accepted immutable source may be a later commit or merge commit;
do not assume the current candidate ID will be the eventual integration pin.

Then use the book integration README: select that exact clean package revision
and tree; deliberately update the integration Project, Manifest and profile;
regenerate the executable export and federated pair; inspect both source diffs;
run live-pair and pinned Julia integration checks. Preserve September replay
profiles. Promote a PSK implementation state only when its actual linked export
exists and the live pair passes; the legacy witness-validation contract must not
be conflated with the newer independent-audit API.

Execution-MCP promotion, a complete teaching edition and external-review labels
remain separate decisions. The portable handoff is neither a new release
manifest nor a replacement for `scripts/check_release_candidate.py`.

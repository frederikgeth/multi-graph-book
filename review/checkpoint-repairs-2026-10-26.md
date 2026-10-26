# Review checkpoint repairs

Date: 2026-10-26. This addendum follows the preserved
[review checkpoint](scientific-pedagogical-checkpoint-2026-10-26.md).
It records repairs to its two high-priority findings, not external peer review
or a release decision. Machine-readable source and run bindings are in
`checkpoint-repairs-evidence-2026-10-26.json`.

## R1: responsive retrieval qualification

Book commit `f577013` requires actual nominal-voltage-base intent rather than
generic DELTA/load vocabulary. Phrase matching distinguishes "nominal voltage"
from "at the nominal operating point". Two exposed fallback routes now require
their own graph-membership or iteration-failure topics.

The original question, "Are three delta terminals three independent load coils?",
returns `under_retrieved` with related sources and a warning, rather than an
unrelated mandatory answer basis. HTTP, CLI, MCP and Markdown checks preserve
that behavior. Nominal-base, coil-current and formulation routes remain covered.
All 46 adversarial cases and 108 existing route/answer-contract cases pass.

The ten added cases are now development regressions. They do not measure a
deployment error rate or establish arbitrary-question or multi-intent coverage.
Structural/source validation remains distinct from semantic answer correctness.

## R2: controller inputs and shared physical magnitudes

Package commit `6c6515153a6c9d3ed8f59605033c05a5022fa392`, tree
`26c5162bcc5bf24fa502bdc979063ef659694242`, caches physical magnitude definitions
independently of controller aggregation. Per-phase and averaged controller
inputs retain distinct semantic keys. The obsolete audit refusal for six mixed
four-leg combinations is removed after the complete native reference matrix
builds successfully. Independent residuals still do not authenticate a build.

Fresh validation on this candidate:

- 72/72 single-pair/four-leg reference combinations build with zero violated
  supplied-point native primal rows.
- 2,169 focused assertions pass, including 1,512 unbalanced floating-neutral
  input/definition checks in SI and per-unit coordinates.
- The full package suite passes: 54,774 passed, 37 broken, 54,811 total.
- The book companion passes 1,687 assertions; all 50 source hashes, the candidate
  profile and locked environment bindings match. Known hard-cap violations
  remain failures with complete supported coverage.
- The running case retains its three default-solve generator-bound violations
  and zero unknown checks; the tighter-solve audit passes. It has no IBR and is
  not evidence of control-law coverage.

This package candidate remains local and unpublished. The book's published
integration still selects `97c274946091859b7d9b0e822c96f1e7f9f50c7e`.
PSK implementation statuses, historical replay and execution MCP exposure are
unchanged.

## Delivery and CI portability

The updated explanation appears in the 82-page HTML library and a fresh
233-page local PDF, `output/pdf/review-repairs-2026-10-26.pdf`. Physical pages 173
and 174 were inspected after rendering; the table and transfer exercise fit on
the closing control page. A whole-document character check found no text outside
the paper at a one-point tolerance. No missing-glyph warning was found. The
freshness gate rejects the older checkpoint PDF, which describes the old failure.
The PDF binary and full local run outputs are generated, not committed.

The original draft PR's documentation job failed at the local-link gate because
two historical review links required a sibling checkout. Those links now select
the immutable published package revision on GitHub. This repairs portability
without changing the reviewed evidence. Hosted checks must be rerun on the new
PR head; local validation is not a hosted-pass claim.

The book reproducibility sequence, exact published-pair check, math, claim,
artifact/link, PDF-reference, rendering and synthetic benchmark/pilot gates
pass. Synthetic conformance evidence remains separate from measured agent runs.

## Remaining review work

R1 is repaired for the recorded questions; general semantic relevance remains
an evaluation obligation. R2 is repaired on the bound local candidate, pending
publication and integration review. The next work is teaching hierarchy and
workbook evidence-generation labeling (R3/R4), domain/reader review, then a
deliberate package publication and pin decision (R5). Feature expansion remains
paused. No external-review or implementation-status promotion follows from
these checks.

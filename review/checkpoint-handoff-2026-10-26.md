# Portable review handoff checkpoint

**State:** local author/domain review preparation. No reviewer was contacted,
no package branch was published, and no release or external-review status is
promoted. This extends the existing four-track packet and response ledger.

## Deliverable and frozen scope

The local archive is `output/review/checkpoint-review-2026-10-26.zip` (56,167,704
bytes). It contains the book and package Git bundles, the complete rendered
HTML library, the unchanged 208-page PDF, a relocatable candidate environment,
the bounded review request and verification/unpack commands. Julia and its
dependency cache/binaries are not included; first installation can require
network access. The archive hash and validation bindings are in
`checkpoint-handoff-evidence-2026-10-26.json`.

The source baseline is book `c5416242116e5ba1df9dc03676367d04a3d82da0` and package
candidate `6c6515153a6c9d3ed8f59605033c05a5022fa392`. The rendered teaching sources
remain the `bda2772` snapshot and match the selected baseline's source hashes.
The newer baseline adds the prose-number gate repair, explicit findings and
refreshed artifact inventory. Wrapper preparation materials are separately
hashed; they are not retrospectively claimed to be in the frozen book commit.

Use the [bounded review request](checkpoint-review-request-2026-10-26.md) for
existing Tracks B/C and a formative reader pass within Track D. It distinguishes
worked exercises from participant-unexposed assessment and leaves the response
ledger empty until actual review. The [publication assessment](package-publication-assessment-2026-10-26.md)
and [prepared package PR description](package-candidate-draft-pr-2026-10-26.md)
make the next decision concrete without publishing or repinning anything.

## Fresh portability evidence

- Six synthetic Git-fixture tests pass, including relocation after source paths
  disappear, exact repository identity, unchanged transitive lock declarations,
  tamper rejection, refusal to overwrite and unsafe archive-path rejection.
- The actual handoff verifies and unpacks into fresh repositories. Both remain
  clean at the exact selected commit/tree; the new environment changes only the
  BMOPFTools path to a relative sibling location.
- Julia 1.12.6 instantiates the new environment from cached dependencies with
  network resolution disabled. Both portable environment files remain byte-for-byte
  unchanged. This does not imply an uncached machine can install offline.
- The fresh book clone passes the full LLM/scientific reproducibility sequence.
  The fresh candidate passes its Finding registry and executable-export checks.
- The relocated companion passes 1,687 assertions across 25 test sets, with all
  50 source bindings under the unpacked root and both environment hashes matching.
  All 72 reference combinations build; the running default point retains three
  known bound failures and zero unknowns, while the separate tighter point passes.
- The previous `bda2772` book head passes all hosted checks. These do not execute
  the unpublished package candidate. The full package suite was not rerun for
  this handoff; its prior result remains separate evidence.

## Newly exposed readiness work

The prose-number checker crashed when quantizing a wide exact integer under
Decimal's default precision. The repair uses a local precision sufficient for
the candidate and preserves scientific-notation precision, so a small displayed
number cannot falsely match zero. Five regression tests pass, including sign,
rounding, wide values, nonfinite refusal and context isolation.

The repaired gate **fails on 54 unbound prose-number occurrences**. They are
recorded in `prose-number-audit-2026-10-26.json`. An unbound occurrence is a
missing machine-checked provenance link, not proof that the numerical value is
wrong. Validate the relevant formula and input before adding a genuine derived
binding or correcting prose. Do not bind an unrelated artifact or lower the
precision threshold. The artifact inventory is refreshed to 97 JSON files.

This is a reviewable source handoff with explicit open findings, not a passing
comprehensive release candidate. The existing release manifest is unchanged.
No PSK, claim-review, published integration or execution-MCP state changes.

## Next work

Resolve the 54 number-binding occurrences, obtain bounded domain/reader feedback
and disposition it through the existing ledger, then decide package publication
and a deliberate integration upgrade. The portable handoff removes the local
source-access obstacle for review; it does not remove these evidence obligations.

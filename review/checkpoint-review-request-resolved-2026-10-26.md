# Resolved October checkpoint: bounded review request

**State:** prepared author/domain/reader review request; nobody has been
contacted or assigned. No external review or pilot result is claimed.

This supplements the existing four-track packet and uses its response ledger.
It narrows the next pass to the newly audited material and its teaching route.
In the unpacked handoff, paths below are relative to the handoff root; the book
repository is `book/` and the package repository is `BMOPFTools.jl/`.

## Frozen inputs and first actions

- Book baseline: `e1748ca582950e2cdb3151e058f822e70c48d447`.
- Package candidate: `6c6515153a6c9d3ed8f59605033c05a5022fa392`.
- Published package pin remains `97c274946091859b7d9b0e822c96f1e7f9f50c7e`.
- Read `handoff-manifest.json`, verify the handoff, then unpack it into a new
  directory using its README. Read `review.pdf`; open `html/index.html` for the
  full reference library. Git bundles contain the sources. Julia dependencies
  and binary artifacts are not included.

Start with the numerical chapter (physical PDF pages 125-137), control chapter
(138-147) and the workbook's evidence-generation table (181-182). The complete
18-section audit reference is in HTML and
`book/docs/src/reference/numerical-audit-reference.md`; it is deliberately
outside the selective PDF. The matching 18 old browser fragments and their
continuation links must still work.

This is a frozen scientific/teaching baseline. The handoff wrapper and this
review request are separate preparation materials, not additions retrospectively
claimed to be in that book commit. The full internal release gate and any later
publication decision remain separate from source portability checks.

The render remains the teaching snapshot from `bda2772`; its source hashes
match this baseline. The baseline also restores the August literature seed's exact archived
bibliography input, keeping later bibliography checks separate. It includes
the resolution of all 54
previously unbound high-precision occurrences. Read
`book/review/prose-number-resolution-2026-10-26.md` and its JSON record;
the historical diagnostic and earlier handoff remain unchanged. Run these
checks from `book/` before reviewing the scientific interpretation:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 experiments/lessons/prose_number_witnesses.py --check
PYTHONDONTWRITEBYTECODE=1 python3 experiments/lessons/recorded_generator_bound.py --check
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_prose_numbers.py
```

The current gate passes 200 high-precision occurrences (144 existing direct
artifact matches and 56 explicit bindings). The new bindings select exact
result fields: 51 deterministic occurrences and three occurrences of the
recorded generator excess, each checking all three phases. The new evidence
is an author check of those declared points, not human review or a proof of
semantic relevance for the 144 legacy direct matches. The inventory contains
99 JSON artifacts; the HTML reference index includes both new evidence
artifacts and has a read-only freshness check. The comprehensive
release-candidate manifest remains a
separate historical artifact and is not promoted by this handoff.

## Suggested bounded allocation

Use existing Track B for winding, neutral/earth and DELTA observation choices;
Track C for returned-point verification, objective scope and controller
intersections; Track D for navigation and formative comprehension. Choose
one focused slice per reviewer and record unexamined slices explicitly. No
person is assigned and no response is prefilled. A useful first return names
one checked passage, its exact model/observation, a nearby excluded case and
an `accept`, `revise` or `reject` disposition. Record package implementation
findings in the package scope, rather than treating them as new book theorems.

## Existing Track B: circuit observations and bounds

**Suggested scope:** one focused pass by a multiconductor/circuit reviewer.
Read the coverage workflow, then select the transformer-current, phase-neutral,
sequence/VUF and DELTA-incidence sections from the audit reference. Inspect
`LOAD-CONNECTION-002`, `LIMIT-NEUTRAL-001` and `NUMERICAL-004/005` in
`book/claims/claims.toml`; inspect the package fixture/example for each selected
section rather than generalizing from the running case.

Return a disposition on these questions:

1. Are supplied, reconstructed and unassessed quantities distinguished at the
   calculation that uses them? Can an evaluated identity hide missing evidence?
2. Do the transformer series/terminal currents and excitation contribution name
   the right observation for each limit? Are native parameter conventions
   clearly bounded rather than presented as universal transformer laws?
3. Do voltage/angle checks retain ordered pairs, the correct neutral/earth
   reference and the undefined zero-voltage/VUF domains?
4. Can terminal KCL or total power be mistaken for a check of every DELTA coil?
   Does the text preserve the distinction between the map kernel and the coil laws?
5. Are any physical, dynamic, thermal or manufacturer-compliance conclusions
   stronger than the static authored models support?

For a counterexample, provide the smallest changed field or observation, the
expected obligation and unit, the actual outcome and the affected source anchor.
Do not fill a missing current or residual with zero to make an example pass.

## Existing Track C: feasibility and control intersections

**Suggested scope:** one focused pass by an optimization/verification reviewer.
Read `book/docs/src/foundations/numerical-consequences.md`, the control chapter,
the workbook and `LIMIT-MULTIPLICITY-001`, `LIMIT-CONVEXITY-001`,
`NUMERICAL-004/005`. The independent audit and native model are separate
comparison paths; object identity is not the audit oracle.

1. Do solver status, primal validation, coverage completeness and optimality
   remain separate? Can the default point's three failures be confused with the
   tighter point's pass or the historical witness gate's indeterminate result?
2. Does a control equality intersect its active cap and hard capability limits,
   rather than silently clip, prioritize, or replace them?
3. Does magnitude sharing preserve controller-specific averaging and local
   device normalization? Is the removal of the six constructor refusals justified
   by the full 72-case reference matrix and semantic-input regressions?
4. Are smoothing recipes explicitly assumed, with no authentication or physical
   controller-compliance claim? Are the boundaries for live providers and
   unsupported topologies visible beside the conclusions?
5. Does the PDF/reference split leave enough reasoning to assess the scope
   without erasing the detailed negative cases?

The candidate companion is runnable after environment setup in the handoff
README. Preserve a fresh output and log, including failures. Compare source
bindings and coverage, not just its final status string. The running case has
no IBR; use the dedicated control fixtures for control questions.

## Reader pass within existing Track D

**State:** formative exercise design, not recruited participants or a learning
experiment. The broader book plan proposes 8-12 readers across power/CS/OR;
this checkpoint does not claim that pilot has started or that these exercises
are unseen assessment items.

Ask a willing reader to first explain the two-feeder cancellation example,
then distinguish the three workbook evidence generations, and finally follow
one PDF reference into the detailed HTML section. Use their own words before
showing the worked guidance. Record setup problems, ambiguous terms, lost links,
where they needed help and whether their conclusion exceeded the stated scope.
Do not score a worked book exercise as unseen transfer or infer a causal
learning improvement from a successful walkthrough.

For a later learning assessment, prepare and freeze new participant-unexposed
tasks and answer guidance separately; record assistance and prior exposure.
Do not reuse the now-known retrieval regressions as blind evaluation evidence.

## Return findings through the existing ledger

The process is defined in `book/review/external-review-packet-2026-08-17.md`.
Use `book/review/external-review-response-ledger.csv` and its existing fields:
finding ID, track, reviewer, date, severity, affected claim, chapter, decision,
issue class, disposition, evidence, follow-up and status. Use the existing B/C/D
track IDs and `accept`, `revise` or `reject`; an unreviewed field stays empty.
For navigation-only issues, name the page/anchor and leave the affected claim
empty rather than inventing a scientific claim.

Separate the reviewer's finding from the author's response and the evidence
that resolves it. No claim becomes externally reviewed without a named person,
date, bounded scope and recorded disposition. AI-assisted author checks remain
author checks. Do not publish the candidate, merge, change the integration pin
or upgrade PSK states as an automatic consequence of a passing handoff.

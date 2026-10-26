# Scientific and pedagogical review checkpoint

Date: 2026-10-26. Review baseline: book `debc18a12242d6b4a2cb31b8060a85c7dbd4c62f`;
package candidate `3bfef78de0ff6f63fe201450136b97e0accac7a4`.

The review checkpoint is ready for author and domain-reader inspection. The
fresh PDF includes the recent verification and IBR-control lessons. Release
remains on hold: a fresh question still receives an unrelated qualified retrieval
basis, and the candidate retains the known four-leg monitor-key constructor
failure. Address those before expanding the catalogue or promoting the package pin.

This is an AI-assisted author review, not external peer review, an independent
proof audit, or a reader-learning experiment. The claim ledger remains at
115 self-checked, six independently implemented and zero externally reviewed
claims. No PSK implementation state, package pin, historical replay profile or
execution MCP exposure is promoted by this checkpoint.

## Snapshot and review evidence

The reviewed sources and output hashes are recorded in
`checkpoint-evidence-2026-10-26.json`. The local deliverable is
`output/pdf/review-checkpoint-2026-10-26.pdf`; it is generated, not committed.
The published integration still selects package `97c274946091859b7d9b0e822c96f1e7f9f50c7e`.
The development candidate and the published pin serve different purposes.

The review covers the recent numerical/control chapters, their source-bound
companion, the reader/workbook route, the structured evidence boundary, the
original October diagnostic questions, and PDF delivery. It includes:

- A fresh 233-page PDF and the 82-page HTML library, with deployment disabled.
- A contact-sheet scan of every PDF page, detailed inspection of selected
  contents, equation, table, control and workbook pages, and a whole-document
  text-bound check at a one-point tolerance. No off-page text characters or
  missing-glyph warnings were found in the final build. Small TeX box warnings
  remain inside the paper bounds; the inspected tables are readable.
- Fresh equal-reference, mixed-aggregation and legacy-override constructor probes
  on the frozen candidate. The first and third build with zero violated supplied
  primal rows; the mixed-aggregation case raises the recorded duplicate-key error.
- A separate 80-digit Decimal substitution of the displayed combined-control
  example, without native curve helpers. It gives Q = 1.20801180125 var,
  an availability-based P cap of 0.969501524614 W, and a minimum-PF P floor of
  1.61068240167 W. The fixed-state interval is empty under those assumptions.
- Eight fresh semantic probes, plus request-validation and properly formed modern
  MCP discovery checks, retained in `checkpoint-probes-2026-10-26.json`.
- Revalidation of all 50 source bindings in the previous 1,615-assertion companion.
  Its execution and the previous 53,262-pass/37-broken package suite were not
  rerun as new full-suite experiments; package code and its bound sources are
  unchanged. The fresh constructor probes and book checks are separate runs.

## Findings and acceptance criteria

### R1 High priority: unrelated qualification still survives source validation

**Freshly reproduced.** The question

> Are three delta terminals three independent load coils?

returns `qualified`, selecting `wye-delta-share-nominal-voltage-base` with
score 0.606667. Its mandatory answer basis concerns phase-to-neutral versus
line-to-line nominal voltage anchors. It does not resolve coil arity or what
"independent" means in the question. The packet nevertheless reports
`validation.valid=true` and valid source/citation checks.

This is the same class of defect identified in the previous review: a valid
packet can answer a different question. The earlier zero-voltage and
small-impedance probes now select relevant contracts; that does not establish
that semantic false qualification is closed generally. One mismatch in these
eight targeted questions is a diagnostic observation, not a prevalence estimate.

The topic gate in `scripts/llm_retrieval.py:84` admits generic `delta` or `load`
terms for the nominal-base route. The coil-current route separately requires
current/KCL language. Those gates are consistent with the observed wrong-route
selection; broadening a route without a question-specific discriminator would
risk another false qualification.

**Next action:** add this observation as a regression during the semantic repair.
Require actual voltage-base intent for the nominal-base contract. Use a relevant
connection/coil basis only when its scope answers the question; otherwise retain
related material and return `under_retrieved`. Preserve legitimate nominal-base
questions and test adjacent arity, current, voltage and multi-intent questions.
Do not lower a global threshold or change a fixture expectation merely to obtain
passing metrics. Keep future blind questions separate from this known regression.

**Acceptance:** this query no longer qualifies the nominal-base contract; the
answer basis is relevant or explicitly unqualified. Existing legitimate routes,
source binding, abstention, HTTP/CLI/MCP and reproducibility gates still pass.

### R2 High priority: native monitor sharing blocks six four-leg combinations

**Reproduced on the frozen candidate.** A combined profile using
`PN_PER_PHASE` for Volt-var and `PN_AVERAGED` for Volt-watt raises an
`ArgumentError` for an already registered magnitude-definition key. Equal
references and a valid legacy averaging override build in the comparison probes.
The previous full reference matrix recorded 30/36 four-leg builds and 36/36
single-pair builds.

The native monitor cache key includes aggregation, while the registered
magnitude-definition key omits it
(`ext/BMOPFOpfExt/ibr.jl:225` and `:232` in the candidate). The independent audit
correctly keeps `droop_native_applicability` unknown while retaining known
law/capability/current evidence. No source equation or physical infeasibility
conclusion follows from the constructor failure.

**Next action:** share the physical per-phase magnitudes independently of
aggregation, retain family-specific semantic keys and affine means, and test
both family orders and legacy overrides. Remove the audit refusal only after
native construction and the source-bound comparison matrix pass.

**Acceptance:** all admitted reference combinations build and pass their supplied
primal checks, without duplicate definitions, lost semantic keys, normalization
sharing or changes to the declared laws. Existing unsupported fallbacks and
physical/live-provider boundaries remain explicit.

### R3 Medium priority: the numerical chapter has become a development catalogue

The numerical chapter occupies physical PDF pages 125-163, followed by controls
on pages 164-173. In the source, `Scope and open work` occurs before the long
sequence of device-audit subsections (`numerical-consequences.md:689` and following).
Those subsections consequently sit under an apparent closing section. Repeated
candidate/provenance reminders and per-field trace details interrupt the teaching
argument. The content is valuable; the current hierarchy makes its role harder
to understand.

**Next action:** consolidate around a small sequence: declare observations and
tolerances, show aggregate cancellation, construct a coverage table, distinguish
reconstruction from independent evaluation, then use representative device and
control failures. Group exhaustive applicability traces as clearly named
reference material. Decide their PDF placement deliberately rather than deleting
them or silently dropping their knowledge-base access.

**Acceptance:** each main section has a learning question and transfer task;
provenance details are available without dominating the argument. Preserve stable
anchors or explicit compatibility links, the worked counterexamples, corpus
source binding and the full HTML reference route when reorganizing.

### R4 Medium priority: workbook verification needs an explicit version label

`docs/src/start/computational-cases.md:182` states that the complete-feasibility
gate remains indeterminate. The worked assessment in
`docs/src/cases/study-workbook.md:127` concludes that the full residual bundle is
missing. Those statements describe the older recorded lesson. The numerical
chapter also presents the newer candidate's zero-unknown bounded electrical
coverage, its three default generator-bound failures, and a separate tighter pass.

These are compatible observations about different APIs/runs, but a learner
following the capstone can read them as one current verdict. Passing a bounded
coverage audit still does not authenticate the built problem, recover arbitrary
hidden state, verify the selected objective, or establish physical adequacy.

**Next action:** put the historical replay, current published integration and
local independent-audit candidate side by side, with their commands, revisions
and distinct verdicts. Link the worked assessment to that table. Preserve the
historical result instead of replacing it with a new solve.

**Acceptance:** a learner can identify which run is indeterminate, which returned
point has three known failures, and which tighter point passes the scoped audit,
without interpreting any of them as unrestricted feasibility or optimality.

### R5 Release gate: accessibility and external evidence remain open

The development candidate has not been published or absorbed into the integration
pin. Reader-facing chapters identify it as local; the release must retain that
qualification until its revision is retrievable and its locked integration is
reviewed. PSK-000013's existing implemented witness-validation contract must not
be conflated with the newer independent audit API.

The structured inventory remains 121 claims, 18 PSK records and 34 misconception
IDs. Six claims have independently implemented evidence, none external review;
16 misconceptions still have no PSK link or explicit exclusion, and 33
established-result entries remain in the citation/derivation classification queue.
Those queues do not by themselves prove the statements false. They require
review of the cited result, book derivation or bounded computational basis.

Held-out hybrid recall remains approximately 47.1%, with five zero-recall cases.
Passing curated routing/status gates does not close R1, establish broad answer
faithfulness, or measure reader learning. Neural results remain archived on the
prior corpus. Agent conformance fixtures and dry runs remain synthetic.

**Acceptance:** publish/repin only after reviewing the chosen package revision,
locked environment and executable boundary; obtain domain and reader feedback
before upgrading review or learning claims. Package execution-MCP promotion,
lessons F-G/capstone completion and later H-J material remain separate work.

## Rendering defects resolved in this checkpoint

The first fresh compilation failed on legacy `\rm` math notation rejected by
`memoir`; HTML had accepted it. Other diagnostics exposed unrenderable literal
approximation glyphs, missing explicit bold/italic font faces in the macOS wrapper,
and long inline paths/identifiers overflowing the text measure.

The corrections use `\mathrm` and `\approx`, preserve complete font-face
mappings, allow PDF-only inline-code breaks at punctuation, and split long
controller equations. The continuation state set is displayed separately, and
the closing control scope/exercise is shortened to avoid a two-line spill page.
All numeric token sequences across the six edited chapter sources are unchanged.
The equations and scope qualifications were checked against their original forms.

The stronger rendered check now rejects the older 168-page PDF for missing current
control content. The math-hygiene check also rejects the old legacy-font source.
These are actual negative checks, not an assumption that successful compilation
proves freshness or scientific correctness. The generated review PDF is kept
outside Git; its hash is in the evidence record. Renderer-only PNG differences
were restored to their committed versions.

## What goes to readers and what stays structured

| Material | Delivery at this checkpoint | Continuing authority |
| --- | --- | --- |
| Main scientific argument, equations, examples and exercises | 31 selected source pages in PDF; also HTML | Maintained chapter Markdown |
| Device, voltage and control lessons | Numerical and IBR chapters in both formats | Chapters plus package-owned executable evidence |
| Full reference/library navigation and indexes | 51 additional HTML source pages; PDF links out where needed | Generated views over canonical registries |
| Claim grades, misconceptions, PSK scope and cross-repository IDs | Selected explanations and reference views | Claims/knowledge/misconception registries, not the rendered summaries |
| Full audit implementation, fixtures and solver outputs | Selected results explained in the book | BMOPFTools and source-bound experiment records |
| Retrieval packets, evaluations, hashes and transport behavior | Technical access layer and selected documentation | Deterministic corpus/service and manifests |

The prose remains retrievable after it is rendered. The PDF and knowledge base
are overlapping views with distinct purposes; rendering does not migrate
scientific authority out of the source registries or promote package behavior.

## Next bounded milestone

1. Repair R1 with topic-specific qualification/refusal tests.
2. Repair R2 and then remove the corresponding audit refusal with native evidence.
3. Consolidate the teaching hierarchy and label the workbook's three evidence
   generations, preserving anchors and historical replay.
4. Run author/domain-reader review on the resulting paired HTML/PDF snapshot.
5. Review publication and integration repinning as a separate decision.

No package implementation repair, push, deployment, external review or pin
upgrade was performed in this checkpoint.

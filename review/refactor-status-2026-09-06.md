# Author review: first refactor and teaching draft

Date: 2026-09-06. Working title: **Power-System Modelling for Computation**.
Subtitle: **From circuit equations to optimization and software**.

This records the first implementation tranche of [BOOK_PLAN.md](../BOOK_PLAN.md),
following the [critical review](critical-scientific-editorial-review-2026-09-05.md).
It is an AI-assisted editing and verification record, not external human review
or certification of the complete book. Changes are available in the working
tree; this work did not commit or publish them.

## What is ready to review

The PDF now selects 26 source pages, grouped into eight teaching parts with a
preface and references. The complete HTML route retains every existing chapter
and includes the three new pages: 77 pages in total. The final core PDF has
155 physical pages, including cover and contents. Its contents list shows parts
and page-level entries rather than every internal heading.

The earlier routes each contained the same 74 pages. Selection now makes the
PDF a substantially smaller reading task while keeping specialist material,
generated indexes, research logs, and client setup available in HTML. Existing
page-level anchors and claim/PSK identities remain stable. The public PDF
filename is retained for existing download links, despite the new cover title.

| Review item | Concrete change |
| --- | --- |
| [Plan](../BOOK_PLAN.md) | Audience, scope, eight-part migration, editorial rules, and staged acceptance criteria |
| [Preface](../docs/src/start/preface.md) | Draft author voice connecting modelling difficulties, software development, and PowerModelsDistribution to the teaching purpose |
| [Opening lesson](../docs/src/start/first-failure-parallel-branches.md) | Prediction, derivation, a repaired aggregate rating, runnable exact calculation, changed assumptions, exercises, and answer guidance |
| [Home](../docs/src/index.md) and [reading guide](../docs/src/start/how-to-use-this-book.md) | Shorter entry point and a clear route through the core and supporting library |
| [Computational case guide](../docs/src/start/computational-cases.md) | Questions, commands, and evidence to inspect for the scalar lesson and five further investigations |
| [Study workbook](../docs/src/cases/study-workbook.md) | A capstone assignment over existing evidence, including applicability, recovery, and a failed near-miss |

The title describes the reader's task across equations, transformations,
optimization, and software. Graphs remain an important tool within that scope.
The subtitle adds the concrete progression. Two alternatives worth comparing
during author review are *Computational Power-System Modelling* (more compact)
and *From Circuits to Computation: Power-System Modelling* (more narrative).
Neither title implies a new general theory or a complete power-engineering
textbook. Audience response to the title has not been measured.

## Scientific changes

1. **Joint observations.** The preservation definition now equates joint
   feasible observation images for fixed admissible inputs. It explicitly
   separates marginal agreement, objective correspondence, decision-domain
   preservation, and source recovery. `PRESERVE-001`, `PSK-000007`, terminology,
   vocabulary, and retrieval qualifications follow that correction. Three
   evaluation cases exercise the marginal-versus-joint misconception.
2. **Current and apparent-power limits.** The opening chapter and `LIT-PAR-001`
   distinguish actual apparent-power feasible regions from the auxiliary
   quadratic current comparisons used in the parallel-member redundancy
   argument. The summed-rating witness remains valid. A rounded scalar value
   is now marked as approximate.
3. **Shared voltage coordinates.** The BIM/BFM case and its figure now show how
   member parameters and constraints express member-current limits with shared
   voltage products. Independent member voltage variables are not inherently
   necessary. The displayed scalar identities declare their series-only,
   fixed-state scope; the implied-current bound declares a positive lower
   voltage magnitude.
4. **Preorder and quotient.** Query answerability is identified as a preorder
   under the stated identity/composition assumptions; the partial order is on
   equivalence classes under mutual answerability. The corresponding figure
   and framework explanation have been updated.

These corrections do not promote any verification status. The ledger still
contains 109 claims: 103 self-checked, six independently implemented, and zero
externally reviewed. The exact-arithmetic review witnesses demonstrate the
three mathematical objections; they do not establish every theorem or every
downstream application in the book.

## Computational evidence and infrastructure

The scalar lesson uses standard-library Python and rational arithmetic. Its
displayed output matches the command exactly. Five checks cover the original
violation, the binding boundary, reversed current, a changed rating, and an
outage. It is a teaching calculation for a declared resistive model, not a new
package certificate or a physical rating-validation study.

The deterministic corpus, context/answer contracts, access fixtures, evaluations,
and source-hash binding have been regenerated. No competing retrieval authority
has been introduced. Agent benchmark conformance and pilot fixtures remain
synthetic; no measured agent run or reader trial was performed.

The supplied sibling checkout was at `5b51d2f3`, while the previous federation
pin reflected the earlier `4c4dafdd` export. Its executable-knowledge generation
check passed. Comparison of the old and current exports found changes in source
hash metadata, with contract identifiers, entry points, Findings, and fixture
identities unchanged. Inspection also found an expanded source-path declaration
for solved-network feasibility, including engine code and tests. The live
package engine has upstream changes; this was not a complete review or rerun of
all package tests. The book's pair manifest was deliberately repinned to the
supplied clean checkout and passed both snapshot and live-pair checks. No sibling
package file was edited.

## Verification results

| Check | Result |
| --- | --- |
| Scientific knowledge generation | Pass: 18 PSK records |
| Federated knowledge, snapshot and live sibling | Pass |
| Deterministic LLM reproducibility | Pass: corpus, retrieval, fixtures, adversarial cases, routes, answer contracts |
| Selected scientific Julia tests | Pass: series 35, typed Kron 51, winding normalization 12, multiconductor parallel AC 41; 139 assertions in total |
| Scalar lesson and independent mathematical witnesses | Pass: five lesson cases and three review witnesses |
| Scientific/editorial checks | Pass: math hygiene, claim mentions, vocabulary, callouts, prose-number bindings, evidence summary |
| Artifacts and figures | Pass: 122 required artifacts; 65 figure pairs; obsolete navigation diagrams retired |
| Routes and rendered output | Pass: unique anchors on 77 HTML pages; 26 selected PDF sources; compact contents, expected teaching content, image alt text, PDF raster smoke test |
| Agent benchmark substrate and pilot validation | Pass, including the live sibling boundary; synthetic status unchanged |

The HTML and PDF were rebuilt using the repository's Documenter/Tectonic
pipeline. A temporary writable Julia depot overlay avoided sandbox cache-write
failures. Selected final pages were rendered for visual inspection, including
the cover, contents, opening lesson, corrected equations, guide, and workbook.
This is not a fresh visual audit of every inherited page. The build reports the
large HTML search-index size and overfull boxes in inherited material as
warnings; a complete typography pass remains necessary. A PDF annotation audit
also checked internal destinations and the local HTML counterparts of links
to the online reference library. This validates the newly built counterparts;
the edited website has not been deployed.

The optional neural benchmark was not rerun on the revised corpus. Its earlier
result is explicitly archived against its prior corpus, with current-corpus
comparison requiring a new pinned run. The full release-candidate certification
was not refreshed. The deterministic pass must not be presented as a new neural
benchmark or complete release certification.

Held-out hybrid evidence recall at 10 changed from 46.6% to 46.0%; zero-recall
cases changed from five to six of 33. Held-out router firing remains 25/33
(75.8%). Curated routing and contract completeness remain 100%. The held-out
questions are synthetic and clustered, and those metrics measure different
things. This editing pass has not demonstrated improved retrieval generalization
or answer accuracy. Preserve that diagnostic; investigate it separately without
tuning claims or the teaching prose to the held-out questions.

## What this tranche leaves for review and further drafting

Stages A–D of the plan are implemented. The eight-part route initially groups
existing chapters; it is not eight newly rewritten chapters. The opening lesson
is the first full teaching rewrite. Some inherited pages still repeat context,
carry dense notation, or use reference-style tables. The capstone is an assignment
over existing fixtures, not a new solved end-to-end application or a fully
worked answer key.

Review the preface first for biographical accuracy, voice, and the account of
language-model assistance. Then review the opening lesson and the four scientific
changes above. Inspect the PDF route for prerequisite gaps, duplication, and
whether each selected chapter earns its place. Check whether the experiment
guide makes a first successful run and a meaningful mutation sufficiently clear.

After the author's corrections, the next substantial drafting pass should turn
Part 2 into a continuous equipment-to-admittance construction exercise, then
apply the same example–derivation–check–mutation pattern to the remaining parts.
A worked capstone answer and instructor guidance should precede a teaching
release. Seek bounded human mathematical review and a formative trial with
8–12 readers across the intended power/CS/OR audience. Neither scientific
correctness throughout nor teaching effectiveness has yet been established by
that kind of independent review.

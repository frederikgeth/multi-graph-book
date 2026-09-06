# Follow-up corrections for author review

Date: 2026-09-06. This records the implementation following the accepted
`follow-up-review-2026-09-06.md`. It supplements the earlier refactor status;
neither automated checks nor this AI-assisted review constitute human peer review.

## What changed

| Review finding | Implemented correction |
| --- | --- |
| Conditioning versus ordering | Exact singular values and the corresponding 2-norm condition number are permutation invariant; sparse fill, pivoting, runtime and numerical estimation are distinguished. |
| Validation and provenance | Software restrictions and study completeness are distinguished from mathematical validity. Recording an inference does not convert it into a declared fact. |
| Nodal relation versus solvability | A floating two-node resistor demonstrates a valid singular nodal relation, compatible injections and voltage-datum selection. Direct-solve regularity is scoped to the boundary-conditioned problem. |
| Reproduction and dates | Default replay binds case sources, package commit, Julia version and a resolved environment. Current and historical-reconstruction modes are separate. Every run uses a new directory outside the repository. New execution timestamps are truthful; the old constant date is identified as unauthenticated historical metadata. |
| Returned-solution verification | The running-network lesson uses the package solution profile and recomputes all four line terminal-current maps. An altered voltage triggers a voltage finding and fails current recovery. The full feasibility-evidence gate must remain `indeterminate` because its complete residual bundle is absent. |
| Equipment-to-equations teaching | A worked resistive equipment table proceeds through orientation, numerical stamps, boundary elimination, exact solve, recovered currents, KCL and power checks. Node permutation, branch reversal, a wrong attachment and transfer exercises are executable. |
| Useful model choice | A scalar parallel case compares nominal and robust decisions over a declared conductance interval. Exact margin calculations explain why 99 A is accepted and 109 A changes decision. Optional local timing includes recovery and is explicitly a microbenchmark. |
| Independence and generated prose | The case guide identifies shared inputs, primitives, assembly and algorithms, and distinguishes human review. Retrieval report counts now derive from their inputs. |

The retrieval Markdown renderer also incorrectly treated a string-valued
assumption as a sequence of characters. It now renders each complete assumption,
and answer validation requires the qualification to survive rendering. The
existing JSON contract and deterministic retrieval architecture are preserved.

The final numerical-page review also replaced a schematic forward-error estimate
with an explicit bound and short derivation, stating its nonsingularity, norm,
nonzero-solution and small-backward-error assumptions. Coordinate changes now
relate solution sets by a bijection rather than calling different coordinates
literally unchanged.

## Reproduction evidence and an environment defect found during checking

The ignored local experiments Manifest contained PowerIO 0.7.3, outside the
current BMOPFTools PowerIO 0.9 compatibility requirement. Passing tests in that
environment were insufficient evidence of a supported setup. A fresh resolution
selected PowerIO 0.9.0; the reviewed baseline and relevant scientific tests were
then run in that environment.

The recorded profile is `experiments/reproduction/review-2026-09-06/` and uses
Julia 1.12.6 and BMOPFTools commit
`5b51d2f361dab91bd7c16711019584407da79ed8`. Its book sources are bound by hash
because this is an author-review working tree, not a newly published commit.
Deliberate changes to those bound inputs require a reviewed profile refresh;
development runs can instead use `--mode current`.

The pinned replay passed in a fresh clone and run directory. It checked the
locked Manifest identity, exact recorded fixture export hash, all engineering
fields against the maintained fixture, selected PF/OPF outputs within declared
tolerances, and the nine verification assertions. The exporter schema URI differs
from the August fixture; that metadata difference is recorded separately from
the equal engineering payload. PF active loss is approximately 554.3170285 W;
OPF objective is approximately -13.20000239 in the synthetic fixture's units.

Historical reconstruction also passed using the recorded old package commit and
freshly resolved dependencies, checking fixture identity. It is **not** recovery
of the missing historical dependency lock or a claim of complete historical
numerical replay. Both isolated checks used locally cached Julia packages; this
was not a clean-machine network installation. Maintained historical outputs were
not overwritten and the sibling package source was not changed.

## Checks and limits

- Exact Python construction, model-choice and opening-lesson checks; four
  reproduction-workflow regression tests.
- Nine running-network verification assertions, including the deliberately
  rejected voltage and the required `indeterminate` full-evidence result.
- 101 relevant Julia scientific assertions: series elimination (35), running
  typed Kron witness (13), winding normalization (12), multiconductor AC
  parallel comparison (41).
- Scientific knowledge generation, snapshot and live federation checks, and
  deterministic LLM reproducibility, including 72 audience-specific answer
  contracts. Synthetic agent benchmark conformance and pilot checks retain
  their original evidence classification.
- Markdown, figures, artifact/certificate references, selective PDF routing and
  rendered-output checks; rebuilt HTML and PDF, with visual inspection of the
  revised lesson, numerical, reproduction and verification pages.

No claim was promoted to external review: the ledger remains 109 claims,
103 self-checked, six independently implemented, zero externally reviewed.
Passing freshness checks does not establish scientific truth or retrieval
completeness. The final held-out hybrid recall at ten is 46.6%, with five of 33
queries returning zero relevant results in that metric. The neural benchmark is
not part of the deterministic gate and was not rerun for this correction tranche.

The multiconductor lesson shares package primitives and input data. It does not
independently recompute every transformer/device equation or nodal KCL, establish
global optimality, or validate the physical model against measurements. Completing
that verifier belongs in BMOPFTools; the book now exposes the gap rather than
filling missing residuals with fabricated passing evidence. The scalar assembly
lesson does provide a complete separate equipment/KCL check for its small scope.

## Suggested author review order

Read the new first section of `source-to-canonical-model.md`, the model-choice
section in `numerical-consequences.md`, and the reproduction/verification sections
of `executable-running-network.md`. Then assess the worked answer in the study
workbook and the evidence-independence notes in the computational case guide.
Keep the working title and eight-part route for this review. Reader testing and
the remaining inherited chapter rewrites are still future work; no publication,
external contact, or measured hosted-agent experiment was performed.

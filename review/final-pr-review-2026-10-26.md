# Final review of PR #10

Completed 2026-10-27 (Australia/Brisbane), continuing the October 26 review series.

**Assessment:** the corrected draft is ready for scoped domain and reader review.
I found no further material error in the mathematical examples and applicability
statements examined. This is an AI-assisted author review, not independent
scientific validation or a recommendation to publish the package candidate.

PR base: `938224a3f9cc1f3b83d65ebb426f59e882561910`. Reviewed head:
`106d03a478a93490a2c9d2af62743a777de55ec4`. Fixes are in `45910ce`.
The PR has 150 changed files at that baseline; much of the volume is generated
evidence and corpus data. This pass concentrates on the new teaching spine,
its algebra and examples, audit applicability, reproduction instructions,
evidence wording and rendered delivery. It does not replace review of the
separate unpublished BMOPFTools implementation.

## Findings fixed

1. **P1: control applicability was overstated.** The control chapter listed
   `THREE_LEG` and then said every controller below applied per branch. That
   invited readers to apply Volt-var/Volt-watt outside their admitted domain.
   The opening now distinguishes constant/minimum PF from droop, identifies
   the local candidate requirement and preserves the unresolved physical
   adequacy of the cyclic three-leg convention.
2. **P2: the case guide called a mutable environment pinned.** The
   `--project=experiments` commands use a sibling checkout and an unlocked
   developer environment. They are now labelled maintainer studies, with the
   recorded replay and published integration kept separate. Python 3.11+ is
   stated explicitly.
3. **P2: solver-status wording contradicted the verification lesson.** The
   multiplicity chapter began by saying a successful solve answered the supplied
   equations. It now calls the output a candidate that must be checked, then
   distinguishes feasibility, intended model and uniqueness.
4. **P2: PF conventions and construction policy needed qualification.** The
   chapter now defines RMS phasors, injection signs and the signed-target
   convention. It explains why rejecting a constant target below the minimum
   is a construction policy: P = Q = 0 still satisfies both weighted laws.
   Additional bounds may exclude that point. Policy rejection alone is not a
   mathematical infeasibility certificate.
5. **P2: numeric matches were easy to overread as provenance.** Eight literals
   on added PR lines still depended on the global numeric pool. Each now has
   a field-level binding to a calculation of its own observation and units.
   These cover the neutral-current imaginary component, separate A²/V²
   magnitudes and source/IBR price rates. All prose literals selected by the
   existing four-decimal gate on added PR lines now have explicit bindings.
   The checker labels its remaining 136 inherited pool matches as unscoped
   numerical agreement, rather than implying passage-specific evidence.
6. **P3: implementation history interrupted the lesson.** Repeated running-case
   verdicts and publication-status lists were removed from the control chapter.
   Minimum-PF JSON now follows the equations and worked intersection, rather
   than interrupting their derivation. IBR is expanded at first use and JSON
   snippets are identified as field excerpts. A stale count of diagnostic
   artifacts was also removed. Scientific qualifications remain beside the
   results they limit.

## Scientific and engineering checks

The five earlier rational spot checks still give identical results after the
prose edits. An additional exact check with constant target 3/5, minimum 4/5
and P = Q = 0 confirms the policy/algebra distinction. The eight new number
bindings are calculated from the authored V/I, winding and price inputs;
displayed answers are not used as calculation inputs. Separate equal-valued
current and voltage observations retain different fields and units.

The zero-voltage attribution agrees with Section VI-D2, equation (30), of the
[four-wire formulation manuscript](https://arxiv.org/html/2204.08126v1), and
Section II-B, equations (21)–(22), of the
[zero-voltage paper](https://arxiv.org/html/2211.03969v3). The book's scalar
counterexamples remain its own derivations. Sections 2.3.2 and 4.4.2 of the
[author-hosted convex optimization text](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)
support the cited affine-preimage and cone facts; complete OPF convexity is
not inferred from an individual convex cap.

The full book Julia experiment suite passes in an isolated temporary expansion
of the published integration lock. Loaded BMOPFTools is checked against the
published tree; the mutable sibling and global environment are excluded.
No Julia or package source changed. The full package suite and candidate
companion were not rerun as part of this final document review.

The primary scientific/federation/LLM gates pass, including the exact published
pair, 117 audience cases and 60 adversarial cases. Number checks pass with
64 explicit bindings and 136 inherited consistency matches. The 53 deterministic
observations, recorded generator reconstruction, 99-artifact inventory,
synthetic benchmark/pilot checks, claims, figures, math and reference checks pass.
No neural benchmark, agent trial or reader study was conducted.

## Rendered result

`output/pdf/final-pr-review-2026-10-26.pdf` is a fresh 208-page render. The HTML
library remains 83 pages. Fifteen physical PDF pages differ from the previous
teaching render: 131, 138–143, 145–148 and 167–170. All were rendered to images
and inspected, with closer checks of the control equations, capability table,
policy block, monitor table and case-guide opening. The whole-document text
check found no characters outside the paper at a one-point tolerance. No missing
glyph was reported. Small TeX box warnings remain within the page; no clipping
or overlap was observed on the inspected pages.

The first local build failed in the bundled Tectonic executable before producing
a TeX log. The existing system-compiler override completed the build with
Tectonic 0.17.0; no source workaround or relaxed gate was needed. The preceding
review head passed all hosted checks. These fixes require their own hosted run.

## Limits and next review

The 136 inherited numeric-pool matches are not a complete provenance audit of
the older book. The exact examples and test results do not validate equipment
data, dynamic controllers or the physical three-leg convention. One question
about the unpublished monitor implementation still returns `under_retrieved`;
it must not acquire authority from an unrelated mathematical contract.

Claims remain 117 self-checked, six independently implemented and zero externally
reviewed. Named domain feedback and a reader pass remain necessary. The package
candidate stays unpublished, the integration pin and PSK implementation states
are unchanged, and the historical release manifest is not refreshed. Existing
portable archives retain their frozen sources; this review and PDF are later
deliverables. The result is a more defensible teaching draft, not a completed
teaching edition or a passing new release candidate.

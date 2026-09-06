# Practical chapter: author-review status, 6 September 2026

The addition is *Building and changing a model you can check*, before the
capstone workbook in Part 8. It uses three small, separate models rather than
expanding the running network or introducing another sequence of chapters.

## Implemented scope

- MATPOWER case-format sentinel semantics: an explicit zero rating, a finite
  zero bound, missing data and an inapplicable check are distinct. A numerical
  round trip can preserve a number while changing its meaning. The field-level
  exporter refuses states this single field cannot represent.
- A three-arm resistive star after an outage: deleting edges in the reduced
  triangle gives the wrong remaining conductance. Balance and symmetry do not
  expose it; recovered source currents and boundary basis checks do.
- A scalar dispatch LP: objective and constraint scaling change raw duals;
  duplicated constraints permit nonunique multipliers. Physical demand
  sensitivity requires the declared mapping and perturbation.

Each example includes a deliberate error, a discriminating check, a check that
misses the problem, and an exercise with an expected result. The chapter links
these practices to incremental computation, translation validation and
sensitivity analysis using primary sources. It does not claim these ideas are
absent from power-systems literature.

The standard-library script has 15 passing test methods. It is a teaching
witness, not a complete importer, general incremental reduction engine or OPF
solver. Its source-equation and matrix evaluations share the declared physical
model; their agreement is not independent validation of that model.

## Integration and validation

The chapter is in both reading routes, with links from source construction,
the case guide and workbook. Repeated graph-navigation prose in the source
construction chapter is shortened; its headings and anchors remain. No files
are deleted in this addition. Two evidence-summary figure layouts are repaired
while refreshing their ledger counts.

Three claims and three misconception contracts are added. The ledger contains
112 claims: 106 self-checked, six independently implemented and zero externally
reviewed. All 18 stable PSK identities remain; no package capability is added.
The bibliography audit covers 73 records and 43 unique DOIs.

Scientific knowledge, snapshot/live federation and the complete deterministic
LLM reproducibility gate pass. The corpus has 912 records and 81 audience-specific
answer-contract cases, including nine new cases. Held-out hybrid recall at ten
remains 46.6%, with five zero-recall queries among 33. These limits are not hidden
by the answer-contract pass rate. Synthetic benchmark conformance and pilot
checks pass; no measured agent experiment was performed.

Adding claims exposed a regeneration dependency: writing an archived neural
snapshot attempted to evaluate the new cases against the previous corpus.
Snapshot writing now depends only on its historical report. A regression test
checks that it succeeds without current corpus/configuration inputs and never
calls the evaluator. The archived neural result is unchanged; compatibility
metadata is refreshed, not presented as a new neural benchmark.

The new 15 example tests, snapshot regression, four existing reproduction
regressions and pinned-profile check pass. Earlier Julia scientific and returned-
solution checks are documented in the preceding correction report; this addition
does not change that Julia code or the pinned package checkout.

HTML and PDF build successfully: 78 HTML pages, 27 selected source pages and
165 PDF pages. The four-page practical chapter and its transition to the
workbook were visually inspected. Rendered-output, artifact, figure, math,
anchor and route checks pass; 132 internal PDF links and 39 links from PDF to
the HTML library resolve against the local build.

## Remaining review

Review the examples' assumptions, sign/unit conventions, author voice and
exercise difficulty. Reader usefulness has not yet been measured. External
scientific review and the proposed formative reader pilot remain outstanding.

The tiny-impedance current-selection example, nondifferentiable solution-map
exercise and nonunique-dispatch regression remain proposals. They are deferred
until author review of this chapter; no implementation evidence is claimed.

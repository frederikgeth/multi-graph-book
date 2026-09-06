# Book plan: Power-System Modelling for Computation

**Working title:** *Power-System Modelling for Computation*
**Subtitle:** *From circuit equations to optimization and software*
**Decision basis:** author's acceptance of the September 2026 scientific and
editorial review. The title and new prose remain drafts for author review.

## Reader and scope

The core serves power engineers who want explicit modelling assumptions, and
computer scientists and operations researchers building power-system
applications. It assumes linear algebra, complex arithmetic, elementary circuit
laws, and willingness to follow a derivation. Introduce specialized graph,
multiconductor, and software concepts when an example needs them.

The first edition concentrates on steady-state power flow and optimal power
flow: model construction, transformation, and verification. A multiconductor
baseline makes omitted assumptions visible; scalar and balanced models remain
useful first examples and valid specializations. State estimation, protection,
dynamics, planning, and graph learning remain reference or research boundaries
wherever the evidence does not establish an application.

After the core, a reader should be able to assemble a model from identified
equipment and terminals, justify a simplification, recover original quantities,
check their constraints, and explain what the computation establishes.

## Three maintained reading surfaces

1. **The book:** a selective eight-part argument in HTML and PDF.
2. **The reference library:** the complete HTML treatment, including specialist
   derivations, terminology, research records, claim indexes, and unresolved work.
3. **The computational cases:** a short guide to runnable examples, their
   evidence, mutations, and the full artifact inventory.

These are views of the same sources. Preserve chapter anchors, stable claim and
PSK IDs, source hashes, deterministic retrieval, qualification/abstention
semantics, and the book/package authority boundary. PDF references to omitted
material must open the corresponding HTML page rather than a missing PDF anchor.

## Eight-part core and migration map

| Part | Learning outcome | Canonical material |
| --- | --- | --- |
| 1. A plausible model gives the wrong answer | Derive, reproduce, and repair the parallel-rating failure | First failure |
| 2. From equipment to equations | Follow identities, terminals, orientations, and stamps | Source-to-canonical; orientation; circuit formulations |
| 3. Conductors, connections, and ground | State connection/grounding assumptions and justify balance | Load models; earth models; positive-sequence specialization |
| 4. Graphs for different computations | Distinguish topology, incidence, and matrix support | Many graphs; five-bus cycles; two-level topology |
| 5. Transformations and recovery | Establish scoped exactness and recover original quantities | Corrected contracts; series; conductor coordinates; Kron/Ward |
| 6. Constraints and decisions | Retain member constraints and controls | Parallel AC; transformer taps; corrected BIM/BFM |
| 7. Evidence for a computation | Distinguish derivation, residual, adequacy, and reproduction | Numerical consequences; Australian construction; experiment guide |
| 8. An end-to-end modelling study | Construct, edit, interpret, and defend a study | Practical model checks; running-network specification and execution; study workbook |

The initial migration groups existing chapters into these parts; it does not
claim every inherited chapter has already received a full prose rewrite. The
opening lesson, preface, reading guide, experiment guide, and study workbook are
the first new teaching drafts. Framework catalogs, multiwinding detail, indexes,
research logs, and LLM-client setup remain in the reference library.

## Editorial contract

Open with a physical or computational question. Give the necessary assumptions,
work a small example, derive the result, check it, and change one assumption.
End with a transfer exercise and enough guidance to assess the answer. Each
chapter must teach a distinct capability.

Keep load-bearing scope beside the result. Reduce repeated context, navigation,
architecture promises, and generic warnings. Introduce labels before array
coordinates once, then use them consistently. Do not make each lesson carry the
entire research program.

The signed preface explains the author's experience, including software work and
PowerModelsDistribution. Personal experience is identified as such; broader
claims about culture, prevalence, or textbook defects require evidence. Use
versioned examples when discussing a software defect and acknowledge precedents.

## Implementation plan and acceptance criteria

| Stage | Work | Acceptance criterion |
| --- | --- | --- |
| A. Scientific corrections | Joint observations; current/apparent-power distinction; shared BIM coordinates; preorder | Prose, claims, PSK, vocabulary, figures and retrieval agree; mathematical witnesses pass |
| B. Reader refactor | Working title; concise home/guide; preface; eight-part selective route | Existing HTML pages remain reachable; core PDF excludes exhaustive indexes, logs and client setup; links resolve |
| C. Initial teaching draft | Executable opening lesson, exercises and answers; case guide; capstone workbook | First lesson runs with standard-library Python; input, prediction, recovery and limits are explicit |
| D. Regeneration and verification | Inspect executable export changes, deliberately repin, regenerate, build | Scientific/live-pair/LLM gates, route checks, relevant tests and rendered-output checks pass |
| E. Author review | Inspect corrections, title, voice, opening, route and evidence limits | Author records corrections; drafting does not promote claims to external review |
| F. External review and reader pilot | Bounded human review; 8–12 formative readers across power/CS/OR | Named review scope and dispositions; assess unseen-case reasoning, setup and reproduction |
| G. Complete teaching edition | Rewrite inherited material using pilot evidence; reviewed releases | Coherent core with tested exercises and explicit coverage; expand specialist material as needed |

A–D are the current implementation tranche. E is the author's planned detailed
review. F–G remain future work. This tranche does not include external contact,
publication, or measured hosted-agent experiments. Existing synthetic benchmark
fixtures remain synthetic.

## Review order

Read the preface and opening lesson first, then the corrected preservation
definition and BIM/BFM passage. Inspect the PDF contents and experiment guide
before specialist chapters. `review/refactor-status-2026-09-06.md` records actual
checks, remaining limitations, and the next editing pass.

## Follow-up corrections completed for author review

The accepted follow-up review adds a complete equipment-to-solution lesson with
exact arithmetic and deliberate mapping failures, an interval model-choice
exercise, and a package-backed returned-solution verification exercise. It also
corrects conditioning, validation, rank and provenance wording, separates pinned
replay from historical reconstruction, and records a supported Julia environment.
See `review/corrections-status-2026-09-06.md` for verification and remaining limits.

This completes the follow-up implementation tranche, not the full teaching
edition. Review these new lessons before rewriting the remaining inherited core
chapters. Full all-device and nodal KCL verification of the multiconductor case
remains a package-owned extension; the current lesson explicitly reports that
missing evidence. External scientific review and reader pilots remain stages
E–G above.

## Practical chapter and priority counterexamples

The accepted next addition is *Building and changing a model you can check*,
placed before the capstone workbook. Its three completed standard-library
witnesses cover source-field semantics, a star reduction after an outage, and
dual scaling/nonuniqueness. Each includes a deliberately faulty operation, a
discriminating check, a test that misses the error, and transfer exercises.
The same chapter connects the calculations to translation validation,
incremental computation and sensitivity analysis through primary sources.
Repeated graph-navigation prose in the source-conversion chapter is shortened.
See `review/practical-chapter-status-2026-09-06.md` for the completed checks,
evidence limits and author-review scope.

The tiny-impedance current-selection experiment, nondifferentiable solution-map
exercise, and nonunique-dispatch regression example remain proposed extensions.
They are not described as implemented results. Choose among them after author
review of the three priority examples rather than adding more chapters now.

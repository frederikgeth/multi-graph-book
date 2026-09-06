# Further scientific and teaching review

Date: 2026-09-06. Scope: the working draft after the first refactor. This is
targeted AI-assisted review, not independent human peer review. No scientific
source, executable artifact, or evidence status is changed by this note.

The further reading strengthens the case for finishing a small construction
and verification course before expanding the reference taxonomy. The first
refactor improved selection and the opening lesson. Most inherited core pages
still require teaching rewrites. Findings below distinguish demonstrated errors,
scope ambiguities, implementation gaps, and editorial judgments.

## 1. Correct conditioning versus ordering

**Definite mathematical wording error.** In
`docs/src/foundations/numerical-consequences.md:196–208`, the rank-aware effective
2-norm condition estimates are said to depend on node ordering.

For permutation matrices P and Q, PAQ has the same singular values as A.
Consequently, kappa_2(PAQ) = kappa_2(A) for nonsingular A. A ratio of the same
selected singular values is also invariant under permutation. Reordering can
change sparse factorization fill, pivoting behavior, runtime, and floating-point
estimation details. It does not change the exact spectral condition number.
Changing units, scaling, the operator itself, or the rank cutoff is different.

Fix the sentence and use it to teach the distinction between intrinsic
conditioning in declared norms and algorithmic consequences of ordering. Keep
the useful warning about rank-deficient exports and meaningless finite
condition estimates. This does not invalidate the recorded matrix values.

## 2. Separate model requirements from software policies

**Overbroad examples and an epistemic wording error.** The validation table in
`docs/src/foundations/source-to-canonical-model.md:48–64` lists multiple active
sources, no voltage bounds, and a slack-only objective as typical failures.
These need the precise model or implementation restriction that makes them
fail. Multiple compatible voltage sources can define a valid circuit. Absence
of explicit voltage bounds alone does not establish ill-posedness; equations
can determine voltages uniquely. An objective involving only slack injection
can define a meaningful optimization problem. Conversely, adding bounds does
not establish feasibility, uniqueness, or numerical stability.

At lines 77–78, an inference is described as not a source fact *until* recorded
as a provenance-bearing finding. Recording an inference does not make it a
declared source fact or authenticate it. Retain its inferred status, assumptions,
and supporting evidence after recording it. A declared source value can also
be erroneous: origin and truth are separate attributes.

Replace generic failure examples with scoped examples, and distinguish invalid
data, unsupported representation, study incompleteness, and mathematical
well-posedness. This should precede expanding the validation taxonomy.

## 3. Clarify existence of a nodal relation versus unique solvability

**Scope ambiguity, not a refutation of the registered reference-label warning.**
The regularity discussion in
`docs/src/foundations/circuit-formulations-and-lowering.md:205–228` needs to make
clear which linear system is required to be invertible and for which solve.

A resistor of conductance g between two floating nodes has the exact nodal
matrix g[[1,-1],[-1,1]]. It is singular because a common voltage offset does
not change currents. Its voltage-difference/current relation remains exact;
a compatible current injection plus a voltage datum gives a unique selected
voltage state. Matrix assembly, gauge freedom, invertibility after boundary
conditions, and nonlinear PF/OPF solvability are separate questions.

The existing claim that a reference *label* alone proves no rank property is
sound. Preserve it. Revise the adjacent prose so singularity of an exported
operator cannot be mistaken for inability to represent the circuit in nodal
equations. Connect this explicitly to the later running-network export, which
reports numerical rank 18 of 20 without claiming the entire model invalid.

## 4. Make historical reproduction a distinct, immutable operation

**Concrete implementation/documentation mismatch.** The historical fixture
chapter names BMOPFTools revision `b7aa9a1b...`, but its displayed no-argument
command invokes `scripts/reproduce_clean_fixture.sh`, whose default revision
at line 6 is the supplied sibling's current HEAD. Lines 20–26 copy only the
Project file and instantiate a fresh environment. The experiments Manifest is
ignored by Git; the separately tracked package Manifest is not copied by this
script. Thus the default operation is a clean current-revision run with newly
resolved dependencies, not replay of the historical pinned environment.

The script also writes into the maintained `clean-reproduction` directory.
Normal case commands can likewise regenerate artifacts. Readers need to be
able to compare their output with the published record without overwriting the
record they are trying to reproduce.

`experiments/run_vertical_slice.jl:203` writes the literal date `2026-08-13`
under `generated_at` on every invocation. If this is a fixture-definition date,
name it accordingly; a new execution needs truthful run metadata. Keep volatile
execution metadata separate from deterministic scientific content hashes.

Provide a published-result mode that resolves an explicit book/package pair,
uses a recorded supported environment, and writes to a new run directory. A
separate development mode can exercise the current checkout. Compare equations,
observations, feasibility, and stated numerical tolerances rather than requiring
identical nonlinear solver iterates. Retain immutable historical records.
The role of manifests in reconstructing package environments is documented by
[Julia Pkg](https://pkgdocs.julialang.org/v1/toml-files/#Manifest.toml).

This finding follows from code inspection. I did not perform a new clean-machine
install or overwrite the historical artifacts during this review.

## 5. Make the running case demonstrate independent source verification

**Gap in the inspected integration path.** The running-case solve assertions in
`experiments/test/runtests.jl:44–53` check termination, positive PF loss, and a
few generator bounds. The generator summary records statuses and values; it
does not publish a complete independent source-feasibility audit for that run.
Other tests do check residuals on other fixtures, so this is not a claim that
the repository has no scientific residual testing.

For the core capstone, explicitly connect a solved result to the package-owned
verification capabilities, exposing their implemented scope and unresolved
checks. Recompute supported device equations, balances, and member limits from
the returned physical state. Include one altered voltage or current result that
the verifier rejects. A passing solver status must not carry the exercise.

The fixture's negative generator cost is honestly described as a device for
making a decision observable, without economic interpretation. It remains useful
as a software fixture. A later teaching capstone should give readers a motivated
modelling decision with a nontrivial tradeoff and a worked answer, while keeping
the old fixture and its identity intact.

## 6. Replace architecture exposition with a completed construction

**Editorial judgment with concrete source evidence.** Part 2 begins with
`source-to-canonical-model.md`, a useful list of ingestion obligations, but it
does not take a small actual source record through every numerical stamp into a
solved model. The adapter crosswalk is explicitly a checklist, not a working
importer. In `circuit-formulations-and-lowering.md:16–23`, the reader is told
which chapter owns several architectural boundaries before doing a calculation.

That does not yet answer the difficulty that motivated this book: how to build
the matrix correctly and understand the result. Use a small equipment table,
named terminals, oriented incidence, primitive matrices, explicit assembly,
reference treatment, a solve, and recovered terminal quantities. Show both
indexed equations and readable arrays. Then permute terminals and deliberately
break one map. Finish with an unseen variant and an answer rubric.

Keep the specialist taxonomy available, but introduce each new abstraction when
this construction needs it. BMOPFTools can implement the example; its data-model
requirements should remain clearly distinct from general circuit obligations.
The reader should acquire a transferable method before needing to learn the
repository's full vocabulary of contracts, factors, views, and identities.

## 7. Add evidence for choosing a useful level of detail

**Teaching gap, not an absence of all approximation work.** The book has noisy
recovery, local bounds, grounding sweeps, and positive examples of exact
simplifications. The core still emphasizes exactness and counterexamples more
than a researcher-facing choice under a practical error budget.

Create one connected comparison: a specified study, two or three model choices,
declared input uncertainty, a meaningful source constraint margin, observed error,
and measured total computational cost including recovery. Explain which choice
is defensible for that task and why the answer changes near a binding constraint.
Do not turn a tiny synthetic timing comparison into a general performance claim.

This would make precision useful for selecting a model as well as diagnosing
an invalid claim. It would also give CS/OR readers a clearer path from the
resource into their own computational experiments.

## 8. Audit evidence independence and generated explanatory prose

**Existing caveats are good; presentation and maintenance can improve.** The
transformer comparison changes numerical algorithms while sharing matrices and
case assembly, and says so explicitly. Retain it. For each major result, show
which of data, primitive construction, equation assembly, algorithm, and human
review are independent. Prioritize the largest shared dependency in the argument
when commissioning another check, rather than adding another closely related
successful solve. Give users the smallest independently checkable witness first.

A concrete metadata defect remains: `scripts/evaluate_llm_retrieval.py:381–382`
hard-codes 27 questions and nine evidence sets, while its generated report now
correctly reports 33 questions and 11 clusters elsewhere. Compute these narrative
counts from the same input. Passing freshness/hash checks can faithfully
reproduce a stale explanatory sentence. This is a small correction but a useful
reason to audit what each passing gate actually establishes.

## Recommended next tranche

First correct the conditioning statement and the scoped validation/rank/provenance
wording. Repair the reproduction modes and run-date semantics before inviting
outside readers to execute the book. Then finish one equipment-to-solution lesson
and its independent source-verification exercise. Use those to test prerequisite
load, setup, and transfer with readers. Add the model-choice comparison next.

Keep the eight-part route and working title during this tranche. More chapter
names, diagrams of the architecture, or closely related certificates have lower
priority than those completed reader tasks. The remaining specialist chapters
can be rewritten using what the first completed lessons reveal.

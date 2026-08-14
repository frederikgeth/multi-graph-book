# Response to the expert review (2026-08-13)

## Disposition

I agree with the review's central diagnosis: the book has a strong negative
case for preserving distinctions, but its next milestone must add a positive
collapse result, repair a small number of mathematical statements, and make
the proposed architecture and evidence status executable and auditable.

| Review theme | Disposition | Response |
|---|---|---|
| Typed Kron covariance and reciprocity | **Agree — urgent** | Recheck the voltage/current dual convention, distinguish similarity from power-dual congruence, and state exactly when symmetry/reciprocity is coordinate-invariant. `TR-KRON-001` remains provisional until this is corrected. |
| Defective bridge proof, under-quantified contracts, and over-strong line--shunt proposition | **Agree — urgent** | Correct the proof by contradiction, quantify all admissible observations and inputs, and describe the line--shunt result as an exact stamping/realization construction with its `N(N−1)/2` block cost. |
| Six versus eight eliminated current variables | **Agree — urgent** | The certificate has 13 real source variables versus 5 real target variables: eight real variables, or four complex member currents. |
| Certificate numerical robustness | **Agree** | Add condition numbers, backward-error estimates, and a decision-margin field now. Interval arithmetic is a later strengthening, not a prerequisite for this pass. |
| Untested `(𝔄, 𝔓, Λ)` architecture | **Agree, with a choice of emphasis** | Instantiate one minimal port--factor object and one checked `Λ` link on the running case first. If that slice cannot carry a useful result, demote the architecture from “spine” to an explicitly scoped proposal rather than defending it rhetorically. |
| Missing positive-sequence/transmission collapse | **Agree — highest reader-facing priority** | Add a controlled specialization with declared balance, transposition, grounding, and decision assumptions. Do not label arbitrary current `ℓ3` parameters as balanced merely because the chapter uses the running fixture. |
| Earth/ground scope | **Agree** | Add the model-class taxonomy now; defer a full Carson or explicit-earth implementation until the scope and tests are settled. |
| Node--breaker, data standards, ratings, numerical consequences | **Agree** | These are necessary crosswalks and scope definitions, but should follow the mathematical integrity pass. |
| State estimation, protection, contingency, and broader category-theoretic claims | **Agree on scope correction** | Mark these as future or partial coverage in the front matter. Category-theoretic language should remain a formalisation direction unless the book supplies concrete objects, maps, and examples. |
| “Extract three papers first” | **Agree as a dissemination track** | Useful and strategically sound, but not a gate on correcting or extending the book. |

There are no substantive recommendations that I reject outright. The
qualifications above prevent the fixes from creating a new overclaim: in
particular, the positive-collapse chapter must be derived from explicit
assumptions, and numerical certification must distinguish nominal exactness
from robustness under parameter uncertainty.

## Roadmap and acceptance criteria

### F0. Integrity and consistency pass

1. Repair the Kron covariance/reciprocity statements, bridge proof,
   preservation-contract quantifiers, and line--shunt proposition.
2. Split the claims ledger into `claim_type` (`definition`, `theorem`,
   `empirical`, `practice`, `proposal`, `open`) and `verification`
   (`unreviewed`, `self-checked`, `independently-implemented`,
   `externally-reviewed`). Render both fields in the book.
3. Correct the README qualifier, variable count, running-fixture/spec drift,
   tap-witness explanation, chapter-count statement, duplicated taxonomies,
   running-example policy, and monochrome figure violations.
4. Move drafting-process instructions out of reader-facing chapters.

**Exit:** every affected claim has a correct statement, a visible epistemic
label, and a passing local check; no known internal inconsistency remains in
the reviewed set.

### F1. Auditable mathematical and numerical evidence

1. Add the side-by-side Schur-complement and phase-to-neutral formulas, with a
   numerical witness and explicit grounding/invertibility guards.
2. Extend redundancy certificates with condition numbers, backward-error
   bounds, and a margin-to-limit field; reject cases too close to the margin.
3. Build and test one minimal `𝔓`/`Λ` instance using the running network,
   including source identity, terminal factors, observations, and recovery.

**Exit:** the core claims can be reproduced from checked artifacts without
   relying on prose-only architecture or unstated numerical assumptions.

### F2. Positive theory and physical scope

1. Draft **When the general model collapses** before adding more reductions.
2. Derive the balanced positive-sequence case from explicit transposition,
   symmetry, grounding, and decision assumptions; report residuals when those
   assumptions are only approximate.
3. Add the ideal-reference, reduced-earth-return, and explicit-earth-conductor
   model classes, and attach scope guards to existing results.
4. Mark state estimation, protection, contingency, and data-exchange material
   as current, partial, or future scope.

**Exit:** a transmission planner can see a rigorous path from the general
model to the familiar positive-sequence model, while a multiconductor reader
can see exactly where that path stops applying.

### F3. Practice crosswalks

1. Add node--breaker and topology-processing material.
2. Add versioned CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER
   crosswalks.
3. Define rating semantics before extending constraint-preservation claims.

**Exit:** each external vocabulary is mapped to a declared internal object,
with unresolved mappings marked rather than implied.

### F4. Numerical consequences and reader path

1. Cover scaling, conditioning, Jacobian sparsity, fill-in, and solver effects.
2. Rebuild **Start here** around the running network, five-bus counterexample,
   first collapse result, and scope; move long worked cases later.
3. Consolidate repeated parallel-flow exposition and repair the reviewed figure
   grammar, including generated variable/constraint and `Ybus`/Jacobian views.

**Exit:** the opening route is shorter and more useful, while the computational
consequences of each representation are visible rather than implicit.

### F5. Dissemination and figure package

Develop the figure set and three paper-sized extraction tracks in parallel:

- multiconductor parallel-limit redundancy;
- certificate schema and composition;
- reference-invariant multiwinding leakage compilation and tap decisions.

The first paper track should follow, rather than precede, the F0 corrections
and the F1 independent artifact checks.

## Immediate decision

Proceed with **F0**, then F1 and F2 in that order. The only design checkpoint
is after the first executable `𝔓`/`Λ` slice: retain the architecture as the
book's reference architecture if it supports a useful running-case result;
otherwise narrow its claim to a documented proposal and keep the electrical
and asset/dependency models as separate, explicitly linked frameworks.


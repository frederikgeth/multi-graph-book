# Scientific and pedagogical review of the book and BMOPFTools integration

Date: 2026-10-25. Book: `938224a3f9cc1f3b83d65ebb426f59e882561910`.
BMOPFTools: `97c274946091859b7d9b0e822c96f1e7f9f50c7e`.

The initiative has a strong scientific organizing principle: preserve the meaning
of a computational study through model construction, transformation, solution,
and recovery. The corrected joint-observation definition, parallel-member
lesson, explicit evidence boundaries, and separation of scientific knowledge
from executable checks are worth retaining. The next milestone should be a
small, trustworthy teaching sequence with current executable companions.

The highest-priority defects are **false qualification in retrieval**, **a stale
book/package pairing**, and **MCP protocol drift**. The largest scientific
development gap is still an independently evaluated, coverage-aware feasibility
audit of the running network. New package capabilities make several excellent
lessons possible, but expanding the catalogue before closing those gaps would
make the initiative harder to trust and harder to teach.

This is a targeted AI-assisted technical review, not external human peer review
or a complete proof audit. Scientific classifications remain unchanged. Proposed
examples below are designs, not new experimental results.

## Review basis and synchronization

Both initial working trees were clean. Remote branches and tags were fetched.
The book was fast-forwarded to remote `main`; its previously checked-out teaching
branch already had the same tree. BMOPFTools' local `main` had two commits absent
from remote `main`, so it was preserved. Its original documentation branch was
fast-forwarded to remote `main`, producing the reviewed revision above. That
branch still has a deleted remote upstream; its content is current.

There are no fetched BMOPFTools release tags, and the GitHub releases collection
returned an empty list. `Project.toml` remains version `0.1.0`; `CHANGELOG.md`
calls it unreleased. Thus “a couple of releases behind” is best understood here
as substantial revision/dependency drift. There are **43 first-parent commits**
between the book's September replay pin `5b51d2f…` and current BMOPFTools.
The current package requires PowerIO `0.11.6`; the book's recorded replay uses
PowerIO `0.9.0`. Those are different environments, even though BMOPFTools reports
the same package version. [Release collection](https://github.com/frederikgeth/BMOPFTools.jl/releases)

The review covered the architecture, quality policy, book plan and open tranches;
the opening lesson, preservation definition, circuit-formulation and numerical
chapters, BIM/BFM case, practical modelling chapter and capstone; PSK/claim
registries; federation, retrieval and MCP implementations; recent package
history; updated learning routes, first case, admittance, substitution,
verification, transformer, scenario, sensitivity and spatial documentation;
and selected corresponding code and tests. It did not re-audit every reference,
rebuild the PDF, run the full package suite, or measure reader learning.

## Findings to address first

### 1. Retrieval can qualify an answer to a different question

**High priority, reproduced.** In
[`scripts/llm_retrieval.py`](../scripts/llm_retrieval.py), the misconception router
uses word-overlap scoring with a default threshold of 0.34. Context assembly
sets `qualified` whenever mandatory records exist. The source and answer checks
validate record integrity and inclusion; they do not establish that the selected
contract answers the user's question.

Fresh probes through `BookLLMService.response` produced:

| Question | Selected contract | Returned status | Assessment |
| --- | --- | --- | --- |
| Does a zero terminal voltage make power balance equivalent to KCL? | `terminal-permutation-is-cosmetic` | `qualified` | Wrong question: the mandatory basis concerns coordinate actions and Kron reduction. |
| Can I replace a small impedance by an ideal switch without changing current sharing? | `reference-matrix-match-proves-source-provenance` | `qualified` | Wrong question: the mandatory basis concerns Australian Carson/reference-matrix provenance. |
| Can a small transformer leakage be rounded to zero in `ybus_augmented`? | None | `under_retrieved` | Appropriate refusal to provide a qualified package-specific answer, but missing current integration guidance. |
| Does `ybus_linearized` with `fold=:all` compute a Jacobian? | None | `under_retrieved` | Same integration gap. |
| Can I merge two buses because their GPS coordinates coincide? | None | `under_retrieved` | Useful missing scientific route. |

The first two responses also returned `validation.valid=true`. That flag means
the packet passed its structural/source checks; it does not mean the answer is
scientifically responsive. This is an actual semantic false-positive, not merely
poor top-k recall. It affects MCP, HTTP and CLI because the service is shared.

Keep the deterministic design. Add these as negative routing cases, then add
unseen variants with distracting vocabulary, negation, multiple questions and
adjacent domains. Require enough topic-specific evidence to qualify a contract;
when coverage is ambiguous, retain the supporting material and return
`under_retrieved`. Review route margins, required discriminating terms and
multi-intent coverage before changing thresholds globally. A higher global
threshold alone may exchange false qualification for excessive refusal.

Acceptance: these two questions must no longer receive unrelated qualified
answers; existing legitimate routes must retain their qualifications; report
false-qualification rate and abstention calibration separately from recall.
The eight probes here are diagnostic observations, not a prevalence estimate.
Reproduce with
[`scientific-review-probes-2026-10-25.py`](scientific-review-probes-2026-10-25.py);
the captured output is
[`scientific-review-probes-2026-10-25.json`](scientific-review-probes-2026-10-25.json).

### 2. The live federation is stale and its runtime identity is incomplete

**High priority, reproduced.** The scientific export and book-only pair check
pass, but the live check fails:

```sh
python3 scripts/check_federated_knowledge.py --check --bmopf-root ../BMOPFTools.jl
```

The pinned executable corpus hash begins `0f4b2d1e…`; current BMOPFTools begins
`645e6b36…`. All fourteen contract source hashes differ. Recipe hashes and both
property-suite bindings also change. The contract, recipe and property-suite ID
inventories remain unchanged. Hash changes are evidence of different sources,
not proof that all fourteen contract semantics changed.

The pair manifest binds content hashes but lacks an explicit immutable package
revision from which a user can obtain that content, despite the architectural
requirement for revision/release pairing. The September replay profile has a
package commit, but that is a separate identity serving a different purpose.
The MCP manifest resource is also only `service.health()`: it reports a corpus
ID, release label and count, not the corpus file hash, pair hash, or executable
revision. The release label still names the August internal candidate.

Retain content hashes and add a retrievable immutable revision or snapshot
locator at the integration-release level. Expose those identities in discovery
and packets. Keep a clear distinction between a historical compatible pair and
the currently installed execution server. Do not mark an old pair invalid merely
because a newer package exists; do refuse to describe the two as the same pair.

The standard LLM gate intentionally checks only the book snapshot. Add a separate
integration CI job checking out the **declared package revision**, generating or
checking its export, and exercising the pair plus representative recipes. A
scheduled or manually invoked latest-main compatibility job can detect future
drift, but ordinary reproducibility must not depend on live upstream `main`.

The ignored local `experiments/Manifest.toml` still resolves PowerIO `0.9.0` while
pointing at the now-current sibling package requiring `0.11.6`. Treat that as an
unsupported development combination. Preserve the committed historical replay
lock; resolve a separate current environment and record it deliberately.

### 3. Both MCP servers target the previous protocol generation

**High priority for current-client compatibility.** Both adapters advertise
`2025-11-25` and support `2025-06-18`. The official latest specification resolves
to **2026-07-28**. Its changes include `server/discover`, per-request version and
capability metadata, required result-type fields and cache metadata. This is a
protocol change, not a date substitution. [Official changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

A client supporting both generations can fall back to the existing handshake;
a modern-only client cannot assume interoperability with these legacy servers.
Implement and test both generations if retaining existing clients is a goal.
[Official compatibility rules](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)

There are also defects within the declared older protocol:

- The book silently converts a null query into the string `None` and a limit of
  `1.9` into `1`, despite declaring string/integer input types.
- An unrecognized notification receives an error response with `id:null`.
  Notifications must receive no response under the declared protocol. The
  package handler has the same fallback pattern and should receive the same
  regression test. [Notification rule](https://modelcontextprotocol.io/specification/2025-11-25/basic)
- Existing route tests exercise supported traffic but do not establish full
  protocol conformance. The modern discovery probe returns method-not-found.

Validate request envelopes and arguments without coercing malformed types;
distinguish parsing, invalid-request, invalid-parameter and execution errors;
test unknown notifications, invalid IDs and version negotiation. Add output
schemas and read-only annotations as useful client guidance, not as scientific
guarantees. Keep both adapters thin.

The **capability split remains sensible**: the book exposes two knowledge tools;
BMOPFTools exposes six execution tools, including only two curated scientific
contract adapters. The current package MCP already forwards spatial analysis and
its `spatial_enabled` opt-out. Fourteen Julia contracts do not imply fourteen
MCP tools. Promote additional contracts only with explicit input mappings,
applicability/refusal cases and tested recipes. Do not expose arbitrary Julia or
add solving merely to enlarge the tool list.

### 4. Complete independent feasibility verification is still missing

**High scientific priority, confirmed by current docs and execution.** The
updated package tutorial explicitly says `profile_solution` does not independently
reconstruct branch equations, terminal KCL, losses or the objective. The book's
lesson adds four line-current recovery checks but shares package primitive
construction. The solved-network contract checks supplied witness fields; it
does not generate or authenticate comprehensive residual evidence.

I ran the current book verification lesson against current BMOPFTools using its
test environment. All nine assertions pass, including rejection of the changed
voltage and the required **`indeterminate`** full-feasibility result. The package
update has not closed this gap.

Develop a package-owned verifier with explicit device/terminal coverage, original
equation residuals, KCL, both-end limits, grounding/source conditions, recovered
quantities, losses and objective evaluation where applicable. Missing devices or
fields must remain unassessed. Include corruption cases that preserve aggregate
power balance while violating one local equation. Publish the shared components
between builder and checker so “independent” has a precise meaning.

The book should teach a complete tiny example first, then present the running
network's coverage table. Do not fill the witness bundle with zeros to obtain a
pass, rename the declaration gate as a verifier, or infer global optimality from
small residuals. Sources:
[package verification tutorial](../../BMOPFTools.jl/docs/src/tutorial_trust_but_verify.md),
[book verification code](../experiments/lessons/verify_running_network.jl).

### 5. Delivery inventories need reconciliation

**Medium priority.** `OPEN_TRANCHES.md` still says 18 of 23 misconceptions are
linked, with five remaining. Current counts are **18 of 26**, with eight
unlinked: the original five plus source-field round trips, outage updates and raw
multiplier interpretation. The package Finding registry now has **381** codes;
book planning prose still says 353. The claim ledger has **112** entries:
106 self-checked and six independently implemented, with none externally reviewed.

There are 27 legacy `established_result` entries without citation keys. This is
an audit queue, not proof that those statements are false or all need external
citations: some are short original derivations. Each should identify whether it
rests on a cited theorem, an explicit book proof, or finite numerical evidence.
Do not promote a finite test to a theorem through the status label.

Generate inventory counts where practical and update maintained plans. Preserve
dated review snapshots as historical records. The existing high-priority fixes
to joint observations, BIM member constraints, apparent-power geometry and
permutation-invariant conditioning are present; do not reopen them as if they
were still unfixed.

## What recent BMOPFTools work contributes

The changelog alone understates the changes. The following reviewed groups in
the first-parent history are the most relevant to the book. PR numbers identify
merged work, not tagged releases.

| Package change | Consequence for this initiative |
| --- | --- |
| PowerIO 0.11 compatibility and conversion fidelity; current 0.11.6 requirement (#385, #395, #402, #424, #433, #463) | Teach semantic import checks and versioned schema boundaries; preserve original conversion failures and distinguish decoding from model validation. |
| Both-end current/angle verification, PF nameplate exception, exact versus modeled Volt-watt evidence (#397, #401, #403) | Every limit needs a coordinate, endpoint, operating-mode and formulation interpretation. A smoothed controller residual differs from compliance with the exact law. |
| Safe re-solves, case families and staged shared-model construction (#399, #428, #432) | Extend the existing rebuild lesson to parameter changes, immutable base cases, failed-scenario retention and genuinely coupled periods. |
| Switch-state topology and open-switch Ybus correction (#426, #435) | Compare bus and conductor connectivity, explicit switch state and boundary-conditioned solvability. An open switch must not be silently aliased. |
| Connection maps, indices and delta geometry (#440, #441, #457) | Labels and terminal count do not determine coil ownership. Teach ordered incidence maps before arrays. |
| Transformer current ratings, coil loading/headroom, effective phase relations, three-leg evidence (#439, #442–#445) | Separate terminal currents, coil powers, nominal screening, authored vector-group text and derived phase correspondence. |
| IBR Q bounds, minimum PF and droop rating bases (#438, #446, #448) | Add a compact operating-domain exercise; P, available P, installed VA, Q limits and control settings are distinct quantities. |
| Ideal transformer shunts and leakage policy; regulator, center-tap and n-winding borders (#456, #458–#461) | Distinguish unavailable admittance inverses from invalid physical relations; retain finite leakage and shunts in a bordered formulation. |
| Spatial diagnostics and reorganized docs (#425, #450, #462, #466) | Make geometric evidence a review aid with explicit coverage and provenance; link to the new synthetic first-case route rather than requiring external utility data. |

The updated package docs already supply a useful progression: inspect a bundled
case, solve, inspect verification coverage, then branch to modelling choices and
extensions. The book should explain why those operations are meaningful and
when they fail, while linking to package-owned API recipes. Avoid copying an API
tutorial into a second maintenance location.

## New examples to develop

Each example should have a question, prediction, smallest derivation, executable
positive case, one discriminating mutation, recovery check, transfer exercise and
worked assessment. Start with analytic or standard-library calculations; make
the package-backed extension a second step. Existing coverage should be extended
where named, rather than starting a new chapter for every item.

### A. Power balance can lose KCL at zero voltage

**First priority; extend circuit formulations and the verification lesson.**
Let a terminal's current-balance residual be `r_I`. The corresponding power
residual is `V conjugate(r_I)`. At `V=0` it vanishes for every `r_I`; power balance
alone cannot enforce KCL. A one-amp residual provides a minimal witness.

For a pure impedance, contrast `I=YV` with only
`V conjugate(I)=conjugate(Y)|V|²`. The latter leaves current unrestricted at zero
voltage. Demonstrate that adding a small neutral-voltage lower bound changes the
domain rather than repairing the equivalence proof.

Acceptance: separate current/power residuals; a nonzero-voltage positive case;
the zero-voltage counterexample; no inference that every power formulation is
invalid. Connect to the package's native impedance substitution tests and the
four-wire formulation literature cited in
[exact substitutions](../../BMOPFTools.jl/docs/src/formulation_substitutions.md).

### B. An ideal transformer is a relation, not a huge admittance

**First priority; extend the MNA section.** Work a single-phase 230:115 V device
with one finite secondary earth connection. Compare a finite-leakage voltage-only
stamp, a bordered port formulation and the exact zero-leakage limit. Keep the
magnetizing/grounding shunts exactly once.

Use the package convention `CV=Zi`, with scaled current `i=y₀w` and bordered
blocks `A=y₀C`, `D=y₀²Z`. Crossing `xfmr_z_min_ohm` selects a representation;
it does not set nonzero `Z` to zero. A unity ratio does not bond isolated neutrals.
Include missing nominal voltage as a rejection, rather than assuming ratio one.

Acceptance: terminal-current and power agreement with an independently written
scalar relation at finite `Z`; convergence to the ideal case; a missing/doubled
shunt mutation; explicit reference and free-mode analysis. Only then extend to
center-tap or partly singular n-winding examples. The package already provides
finite witnesses in its ideal-transformer and leakage-policy tests.

### C. Tiny impedances can select currents that ideal switches cannot

**First priority; complete an already proposed practical extension.** Two parallel
resistances `R₁=ε`, `R₂=2ε` carrying fixed total current `I` divide it as
`I₁=2I/3`, `I₂=I/3`. Their voltage difference tends to zero as `ε→0`.
Replacing both by ideal shorts retains the equal-voltage condition but does not
select that member-current split. Different resistance ratios give different
limits while the limiting bus voltages agree.

Apply one member rating to show why “the voltages barely changed” is an
insufficient acceptance test. Keep this distinct from example B: retaining finite
leakage in a border is a reformulation, while replacing resistance with zero is
a change of model. Do not extrapolate the resistor result into a universal
regularization convergence theorem.

### D. Delta terminal maps and coil coordinates

**Next priority; extend load/connection teaching.** Use the coil-incidence map
`C`: coil voltage is `CV`, terminal injection is `Cᵀi_coil` for real signed
incidence. Three cyclic delta coils can carry separate loads, but their voltages
satisfy a cycle relation and the map has a common-mode nullspace. Two phase
terminals define one coil; three define three cyclic coils. A neutral is not
silently discarded to manufacture a valid delta map.

Mutate phase order, append a neutral, mismatch power-array lengths and confuse
line-to-line with phase-to-neutral nominal voltage. Recover terminal powers and
verify their sum against coil powers. Match the supported package domain, while
distinguishing its representation restrictions from universal circuit impossibility.

Acceptance: independently derived coil enumeration, orientation and power-dual
current action, a valid permutation, and rejected malformed maps. Existing
`PSK-000004` and `PSK-000012` may provide links after scope review; do not assume
their current checks already validate the whole lesson.

### E. A parameter crossing zero and a stale solved model

**Next priority; extend the current rebuild/outage chapter.** Parameterize
`I(θ,V)=θYV`. At `θ=0`, deleting the term based on its numerical value destroys
the intended family when `θ` becomes positive. Compare fresh construction,
symbolic update with the package's `resolve_opf!`, and faulty term deletion.

Use current equations evaluated at the updated parameters, not termination
status, as the discriminator. Also change topology to demonstrate when rebuilding
is required. Keep three failures separate: discarded symbolic dependence,
stale optimizer evaluation, and a structural change outside the update API.

Acceptance: parameter sequence including zero, fresh-versus-reused physical
outputs and residuals, input fingerprints, and explicit handling of a failed
solve. The version-specific optimizer workaround stays in BMOPFTools.

### F. Equal geography is not equal electrical identity

**Next priority; extend source-to-canonical modelling with a visual exercise.**
Use co-located transformer ports, two circuits sharing a route and an open
switch. Add a direct line beside a two-section path with a grounding shunt at
the intermediate bus. Ask which objects could be merged and what evidence is
missing. The correct answer can be “retain and inspect.”

Vary declared CRS, coordinate accuracy and physical versus electrical length.
A coordinate-free topology layout must not become geographic evidence; matching
route and line lengths may share an upstream source. Distinguish candidate,
data contradiction and confirmed human disposition.

Acceptance: retained equipment identities, explicit conductor maps, an
indeterminate missing-CRS case, and coverage/truncation reporting. Use Tellegen
optionally for inspection, with an offline diagram/JSON path so the scientific
exercise remains reproducible. Link package spatial reports rather than
reimplementing their heuristics in the book.

### G. The endpoint and coil behind a thermal limit

**Next priority; extend the existing BIM/BFM lesson.** Choose a line with shunt
charging so its two terminal currents are not negatives of each other. Construct
a case where checking only one end misses a limit. Then use an unbalanced
transformer to distinguish total nameplate VA, coil loading and winding current.

Acceptance: currents recomputed from terminal voltages and device equations;
both-end checks; a coil overload hidden by a total-power summary; distinct
nominal headroom screening and solved feasibility. Connect this to the package's
recent rating and verification work without treating result fields as independent
proof of the primitive equations.

### H. A derivative at an active-set transition

**Second teaching tranche; extend multiplier interpretation.** Start with
`min ½(x−θ)²` subject to `x≤c`. The solution is `min(θ,c)`: its derivative is
one below the transition and zero above it, with no ordinary derivative at
`θ=c`. Central finite differences at the kink need not represent either branch.

Then bridge to the package's selected-branch voltage-sensitivity example. Compare
analytic, finite-difference, forward and reverse derivatives away from transitions;
report step size, active set, scaling, residuals and branch selection. Keep an
equation Jacobian, solution sensitivity, objective-value derivative and raw
multiplier distinct. This is more instructive than another smooth nominal test.

### I. Scenario snapshots are not a coupled operating policy

**Second teaching tranche; extend the capstone after the synthetic first case.**
Use the package's evening/midday/cloudy feeder scenarios. Hold installed inverter
VA fixed while changing available PV power. Then add a two-period storage energy
balance so two individually feasible snapshots cannot be combined arbitrarily.
Keep failed scenarios in the result table.

Acceptance: immutable base case, non-accumulating edits, explicit time/index and
availability semantics, recovered constraints and a coupled counterexample.
This naturally introduces planning versus operation without claiming a full
planning, reliability or dynamics treatment.

### J. Controller approximation and the physical operating envelope

**Second teaching tranche.** Compare exact and smoothed Volt-watt laws near a
breakpoint, then impose converter VA, declared Q and minimum-PF bounds. Include
`P=0` and nonzero-Q requests to force an explicit choice of generation versus
STATCOM operating domain. A package generation-domain refusal is not a universal
claim that inverters cannot provide reactive support at zero active power.

Acceptance: residuals against both modeled and exact control laws; explicit
controller, base and mode declarations; no compliance claim based solely on
optimization termination. Keep regional standard interpretation outside the
exercise unless the applicable standard is independently reviewed.

## Pedagogical structure and larger missing work

Keep the eight-part core and specialist HTML library. The corrected opening is
good, but it still moves from an elementary 110 A example into certified
redundancy and multiconductor extensions. Make the end of the elementary lesson
an explicit stopping point with a transfer assessment; put the advanced material
on a clearly optional continuation. A first reader should be able to succeed
without first understanding the research catalogue.

Use a three-stage sequence: exact scalar prediction, small multiconductor
transfer, then package-backed case. Introduce each new abstraction at the point
where the scalar example fails. Retain the same physical IDs across equipment
tables, diagrams, equations and outputs. Separate learner worksheets from worked
answers so exercises test transfer rather than transcription.

The most valuable larger additions are:

1. **A verification coverage matrix.** For each device/observable, distinguish
   supplied-result consistency, independently evaluated equation, shared primitive,
   cross-tool comparison and physical measurement. This should accompany runtime
   reports and the capstone, not live only in architecture prose.
2. **Model adequacy and identifiability.** The book already has provenance and
   uncertain-model examples. Add a small inverse problem where multiple parameter
   choices fit one operating point but differ under a new excitation. Define the
   extra measurement needed to discriminate them. Reproducible, feasible equations
   do not authenticate ratings, load laws or construction data.
3. **Quantified approximation tied to a decision.** Extend the existing robust
   interval lesson into error bounds and decision margins: a voltage approximation
   is useful only relative to the limit being decided. Include composition and
   domain dependence; report an inconclusive case near the boundary. Do not demand
   exactness when a certified bounded approximation answers the study question.
4. **Independent scientific review and reader testing.** Prioritize the preservation
   definition, zero-voltage formulation boundary, transformer bases/grounding,
   feasible-set arguments and sensitivity interpretation. Test whether readers can
   reject an unseen unsafe transformation, identify missing evidence and run a
   small example. Passing repository checks is not a learning outcome.
5. **A versioned compatibility release process.** Publish an integration record
   identifying both sources, resolved dependencies, data licences, generated hashes
   and executed checks. Keep historical replay and current compatibility separate.
   The package's replacement of externally restricted fixtures makes a completely
   bundled synthetic teaching route especially practical.
6. **Independent evaluation of knowledge use.** Expand held-out questions by
   misconception/domain family, not merely audience paraphrase. Report route
   precision, unsafe qualification, counterexample retrieval and supported refusal.
   Preserve synthetic scorer, pilot and measured-agent evidence distinctions. The
   current agent-pilot design still needs its documented human re-review; a broad
   automated benchmark is lower priority than repairing false qualification.

Do not expand the first edition into full protection, dynamics, planning or
geospatial asset repair just because an adjacent API or diagram exists. Give
those topics an explicit boundary and a discriminating small example when useful.
The thesis remains steady-state model construction, transformation and verification.

## Delivery order and acceptance criteria

| Order | Deliverable | Acceptance |
| --- | --- | --- |
| 1 | Retrieval correctness repair | Wrong-topic qualified packets are prevented; current positive cases remain supported; new negative/held-out cases retained. |
| 2 | Reviewed current pairing and environment | Deliberate package pin, fresh supported environment, export/recipe checks, live pair and LLM gates all pass; historical replay remains unchanged. |
| 3 | MCP compatibility and identity | Legacy and modern protocol tests, strict arguments, notification handling, discoverable source/pair identity; same scientific packet semantics. |
| 4 | Three compact lessons A–C | Analytic positive cases, discriminating failures, recovery and unseen transfer exercises; package behavior linked at a pinned version. |
| 5 | Coverage-aware feasibility verifier | Explicit missing coverage, independent local residuals, realistic tampering tests; no global-optimality promotion. |
| 6 | Lessons D–G and a revised capstone | One coherent learner route tested with representative readers; new claims/PSKs only where scientifically justified. |
| 7 | Sensitivity, scenario and controller extensions | Reviewed domain boundaries and measured teaching benefit; no expansion based only on implementation availability. |

## Checks performed

| Check | Result |
| --- | --- |
| Scientific knowledge generation | Passed, 18 PSK records. |
| Book-only federation | Passed. |
| Federation against current BMOPFTools | Failed, stale pair as described above. |
| Full deterministic LLM reproduction | Passed: 913 corpus records, 81 audience cases, 33 held-out questions, nine adversarial cases, route/answer checks. |
| Retrieval metrics | Contract-expanded completeness 100%; held-out hybrid recall@10 46.6%; router firing 75.8%; five of 33 zero-recall cases. These are distinct metrics. |
| New review probes | Reproduced two wrong-topic qualified packets, input coercion and a response to an unknown notification. |
| Neural record | Archive check passed; previous-corpus negative result remains archived and requires a real rerun for current comparison. |
| Four Python lesson suites | Passed, including 15 practical modelling tests. |
| Recorded replay input check | Passed source/environment hashes; this command does not execute the historical replay. |
| Current running-network verification lesson | Nine assertions passed in the package test environment; full gate remains indeterminate. |
| Package Finding/export generation | Passed: 381 Finding codes; executable export reproducible. |
| Package scientific contracts/export/interface/MCP | Passed: contract tests and property suites, 1,184 export assertions, 173 JSON-interface assertions, 54 MCP assertions. |
| Selected recent delta/transformer tests | Passed: 173 delta geometry, 161 ideal shunts, 1,302 nominal-voltage, 1,043 leakage-policy, 397 regulator, 582 center-tap, 89 n-winding reference, 1,302 n-winding port and 110 open-delta assertions. |

The selected recent delta/transformer run exercised the non-solver paths; optional
JuMP/Ipopt branches in those files were not enabled. The separately run current
book verification did load JuMP/Ipopt and solve. An initial isolated regulator
test invocation omitted a shared helper; rerunning in the repository's declared
include order passed. That invocation error is not a package defect.

The verification command was:

```sh
julia --project=../BMOPFTools.jl/test --startup-file=no \
  experiments/lessons/verify_running_network.jl /tmp/mgb-review-current-verification-2026-10-25.json
```

This is current compatibility evidence in an existing package test environment,
not a fresh-machine installation or a complete new pinned replay. No canonical
scientific content, package behavior, federation pin, or historical evidence was
rewritten during this review. The new files are the review and its diagnostic
probe script/output.

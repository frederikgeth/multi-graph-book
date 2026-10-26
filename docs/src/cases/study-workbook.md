# [An end-to-end modelling study](@id study-workbook)

**Page status:** draft capstone workbook over the existing running fixture; no new solved application is claimed.

Your task is to explain and defend a computational model, including one
transformation and its recovery checks. Use the existing multiconductor
running fixture. Its difficulty is deliberate: it combines conductor
connections, grounding, parallel equipment, and a multiwinding transformer.
You are now using these features together after studying smaller examples.

Before extending this case, complete one correction from
[Building and changing a model you can check](@ref building-and-changing-models).
Its import, outage-update and multiplier examples show how to choose a
discriminating check and state what remains unverified.

Before accepting a simplified circuit or its computed result, also work the
[zero-voltage current/power boundary](@ref zero-voltage-kcl), the
[finite/ideal transformer relation](@ref ideal-transformer-port-lesson), and
[vanishing-impedance current selection](@ref vanishing-impedance-current-selection).
For each, state the retained equation, the discriminator that detects a wrong
model, and a boundary case in which voltage agreement alone would mislead you.

Before treating a solved capstone as feasible, complete the
[verification coverage lesson](@ref verification-coverage-lesson). Report which
rows were evaluated, reconstructed or unassessed, and keep the local package
candidate separate from the published integration pin.

Before using delta-load result arrays, complete the
[coil-current lesson](@ref delta-coil-current-lesson). Recover terminal currents
and test the individual coil laws even when KCL and total power agree.

Before reusing a compiled scenario, complete the
[parameter-update lesson](@ref parameter-reuse-lesson). Compare against a fresh
build, check the current law at the requested inputs, and retain failed scenarios
without carrying forward an earlier valid result.

Before interpreting a unique solver output, work the
[solution-multiplicity example](@ref unintended-solution-multiplicity). State
whether a competing point violates physics, violates a limit, differs only in
unobserved coordinates, or has a different objective value.

## 1. Declare the study

### [Choose the evidence generation](@id running-case-evidence-generations)

**Learning question.** Which program evaluated which returned point? The same
running input appears in three evidence generations. Their verdicts describe
different checks and runs, not successive labels for one result. Revision
prefixes below identify the full revisions in the named profiles.

| Evidence generation | Package revision and check | Recorded verdict and boundary |
| --- | --- | --- |
| September review replay | `5b51d2f361da`; profile and four line-current recoveries | Scoped checks pass; the complete-feasibility witness gate is `indeterminate` because the full independent residual bundle is absent. |
| Published integration | `97c274946091`; the same scoped verification lesson in the current locked integration | The lesson still requires that `indeterminate` refusal. Passing integration is not an all-device/KCL audit. |
| Local independent-audit candidate | `6c6515153a6c`; separate `audit_linear_solution` and `audit_solution` APIs | The linear audit retains 42 unassessed obligations. The broader audit finds three generator P-bound failures and zero unknowns at the default-solve point; a separate tighter-solve point passes its bounded electrical checks. |

From the repository root, choose the matching route:

```sh
# September replay: its recorded environment and source hashes
bash scripts/reproduce_clean_fixture.sh --check
bash scripts/reproduce_clean_fixture.sh

# Published integration: requires the exact clean checkout selected by its profile
python3 scripts/check_bmopf_integration.py --bmopf-root ../BMOPFTools.jl

# Local candidate: only after preparing its exact clean revision and locked environment
julia --startup-file=no --project="$MGB_AUDIT_ENV" \
  experiments/lessons/verify_linear_coverage.jl "$MGB_AUDIT_ENV/coverage.json"
```

The immutable locators are, respectively,
`experiments/reproduction/review-2026-09-06/profile.json`,
`experiments/integration/profile.json` and
`experiments/integration/linear-audit-candidate.json`.
The candidate is **local and unpublished**; it cannot be substituted into the
published command. Its environment setup and fresh-output requirements are in
`experiments/integration/README.md`. A historical reconstruction or an unlocked
current-mode run is a different operation from the September replay.

The candidate's three violations exceed their unchanged power tolerance by
about 0.00997 W each; all 26 KCL rows and aggregate power pass. The tighter run
uses different solver settings, not different authored limits. The running case
has no IBR, so its result does not exercise the control catalogue. None of these
checks authenticates arbitrary hidden constraints, a selected objective, global
optimality, input provenance or physical adequacy.

**Transfer task.** Attach a verdict to its revision, API, returned-point identity
and tolerances. Explain why a passing tighter point neither repairs the default
point's violations nor supplies the September lesson's missing residual bundle.

Read [The running multiconductor network](@ref running-network) and
[Executable running network](@ref executable-running-network). State the
operating state, the quantities the study observes, and the decision domain
actually solved by the fixture. Distinguish fixed data from optimized
variables. List at least one question the fixture does not answer.

Use the existing PF/OPF study as your starting task. Introducing a new
contingency, estimator, or protection calculation would require its own model
and evidence; those are possible extensions after this exercise.

## 2. Trace equipment into equations

Choose one line, one grounding relation, and one transformer winding. For each,
record its stable identity, ordered terminals, units, and the equations and
constraints that use its quantities. Locate its contribution in a generated
view. Explain any virtual node or arc encountered along that path.

Draw a small part of the equipment topology and the corresponding matrix
support. Identify an adjacency whose meaning changes between those views.
Use the source maps supplied with the fixture rather than guessing equipment
identity from a matrix entry.

## 3. Predict a transformation

Choose a transformation already supported by a listed case in the
[computational guide](@ref computational-cases). State its source, target,
applicability guards, joint observations, and recovery map. Predict which
constraints need evaluation on recovered quantities.

Do not assume that a transformation tested on a separate small fixture is
applicable to the complete running network. Either establish the guards for
its chosen subsystem, or keep the small fixture as the transformation study
and explicitly record that boundary. A justified rejection is a valid result.

## 4. Reproduce and recover

Follow the execution command and environment in the associated case chapter.
Record the actual software revisions, inputs, solver status where applicable,
residuals, and tolerances. Compare source and target observations. Recover the
eliminated quantities and evaluate the source constraints that depend on them.

Run the [returned-solution verification exercise](@ref executable-running-network).
Record the four line-current residuals, the package profile's findings, and the
reaction to the altered `i2.a` voltage. Explain which source quantities were
recomputed and which data or primitive construction were shared. The full
feasibility-evidence gate in the September/published scoped lesson should return
`indeterminate`; explain the missing
all-device equation and nodal KCL evidence instead of converting that refusal
into a passing result.
If you also run the local candidate, submit its separate default and tighter
point records using the [evidence-generation table](@ref running-case-evidence-generations).

If the case is locally solved, describe it as a local numerical comparison.
Use a derivation or a separate bound for any stronger feasible-set or
optimality statement. Explain which construction data and algorithms are
shared by any independent comparison.

## 5. Challenge the conclusion

Propose one nearby input change that violates a guard: an internal shunt, a
finite grounding impedance, a changed conductor order, or a changed control
domain. Predict whether it should cause rejection or require a different
rule. Run the corresponding existing negative test where available and
record its actual result. Keep a proposed extension distinct from one you
have executed.

## Submit a short scientific account

Your account should contain the study question; source assumptions and input
identity; one diagram; the transformation and recovery equations; a compact
comparison of predicted and observed quantities; the failed near-miss; and a
precise conclusion. Include the commands needed to reproduce the work.

A satisfactory account allows another reader to identify what was checked,
where the original constraints enter, and why the conclusion stops at its
stated boundary. A small residual alone is insufficient. If data, applicability,
or recovery remain unresolved, explain the missing evidence and the next
calculation that would resolve it.

## Worked assessment of the verification step

A defensible account reports that the unaltered case satisfies the lesson's
line-current and power-balance tolerances, while the altered voltage violates
a voltage bound and disagrees with currents recovered from the line primitives.
It distinguishes initialization and active-bound warnings from violated
constraints. This is the September/published scoped lesson's assessment in the
[evidence-generation table](@ref running-case-evidence-generations). It does not
infer global optimality from `LOCALLY_SOLVED` or call
the whole model independently verified. The missing full residual bundle is
an explicit conclusion for that gate, not a failed exercise. A local candidate
account additionally distinguishes the default point's three violations from
the tighter point's scoped pass and retains both records.

For a smaller complete decision argument, reproduce the [interval model-choice
exercise](@ref numerical-consequences): explain why a 109 A nominally accepted
transfer is not robust over the declared conductance interval. Submit the
monotonicity argument and recovered member currents. Keep its scalar scope
separate from the multiconductor running fixture.

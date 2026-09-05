# [An end-to-end modelling study](@id study-workbook)

**Page status:** draft capstone workbook over the existing running fixture; no new solved application is claimed.

Your task is to explain and defend a computational model, including one
transformation and its recovery checks. Use the existing multiconductor
running fixture. Its difficulty is deliberate: it combines conductor
connections, grounding, parallel equipment, and a multiwinding transformer.
You are now using these features together after studying smaller examples.

## 1. Declare the study

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
feasibility-evidence gate should return `indeterminate`; explain the missing
all-device equation and nodal KCL evidence instead of converting that refusal
into a passing result.

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
constraints. It does not infer global optimality from `LOCALLY_SOLVED` or call
the whole model independently verified. The missing full residual bundle is
an explicit conclusion, not a failed exercise.

For a smaller complete decision argument, reproduce the [interval model-choice
exercise](@ref numerical-consequences): explain why a 109 A nominally accepted
transfer is not robust over the declared conductance interval. Submit the
monotonicity argument and recovered member currents. Keep its scalar scope
separate from the multiconductor running fixture.

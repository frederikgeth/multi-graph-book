# [How to use this book](@id how-to-use-this-book)

**Page status:** selective teaching route and reference-library guide.

Begin with the parallel-member lesson. Make a prediction, work through the
algebra, and run its short Python calculation. You can then follow the eight
parts below, or enter at the first unfamiliar modelling task.

## Follow the teaching route

| Part | Start here | What to work out |
| --- | --- | --- |
| 1. A plausible model gives the wrong answer | [Parallel members](@ref first-failure-parallel-branches) | Derive a valid aggregate rating and its state boundary |
| 2. From equipment to equations | [Source to canonical model](@ref source-to-canonical-model) | Carry identities, terminals, orientations and units into equations |
| 3. Conductors, connections, and ground | [Load connections](@ref load-models-and-decision-dependence) | Identify the voltage and return path each device uses |
| 4. Graphs for different computations | [One network, many graphs](@ref one-network-many-graphs) | Separate physical topology from computational coupling |
| 5. Transformations and recovery | [Preservation contracts](@ref preservation-contracts) | Declare joint observations and recover eliminated quantities |
| 6. Constraints and decisions | [Parallel AC decision case](@ref multiconductor-parallel-ac-case) | Check the source constraints after a transformation |
| 7. Evidence for a computation | [Numerical consequences](@ref numerical-consequences) | Distinguish residual checks, conditioning, model adequacy and reproduction |
| 8. An end-to-end modelling study | [Study workbook](@ref study-workbook) | Record and defend a reproducible study |

The PDF selects material for these eight parts. Specialist derivations,
exhaustive indexes, research logs, and language-model setup remain in HTML.
Links to reference pages outside the PDF open the online library. The legacy
PDF filename is retained so existing download links continue to work.

## Work with the examples

Keep a short record of the source assumptions, predicted result, observed
result, and explanation of any difference. Change one condition at a time.
Use the [computational case guide](@ref computational-cases) to choose a
command and understand what its output establishes.

Power engineers may move quickly through familiar circuit laws while checking
the conventions. CS and OR readers should use the
[notation reference](@ref reference-notation-conventions) for terminal and
phasor conventions. The general multiconductor case is introduced in stages;
it need not be the first model you implement.

## Check the evidence

A definition states the convention used here. A derivation supports a result
under its stated assumptions. An executable witness records a declared case
and tolerance. An independent implementation may still share input data or
model assembly. External review requires a recorded human reviewer and scope;
the current claims ledger has no entries in that category.

Use the [evidence map](@ref reference-evidence-map) and
[knowledge-base index](@ref knowledge-base-index) when a result needs closer
inspection. A numerical value, a schema-valid certificate, and a physical
validation answer different questions.

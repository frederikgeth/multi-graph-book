# [Power-System Modelling for Computation](@id home)

**Page status:** overview of the teaching draft and complete reference library.

*From circuit equations to optimization and software*

Two parallel lines each have a 100 A rating. Replacing them by one line with
the same total admittance and a 200 A rating can admit an operating point that
overloads one of the original lines. The calculation looks consistent until
the member currents are recovered.

Start with [A plausible model gives the wrong answer](@ref
first-failure-parallel-branches). Derive the failure, run the calculation, and
repair the rating. The example leads to the book's central question: which
physical quantities, constraints, and decisions survive the model you compute
with?

## Read the book

The teaching route develops eight skills: diagnose a model failure; construct
equipment equations; handle conductors and grounding; choose a computational
graph; transform and recover a model; preserve constraints and decisions;
assess numerical evidence; and defend an end-to-end study.

Follow [How to use this book](@ref how-to-use-this-book), or download the
[core PDF](GraphModelsForPowerSystems.pdf). Read the [author's preface](@ref
author-preface) for the experience that motivated the work. The route is a
selective draft: some parts still use longer reference chapters while their
teaching versions are developed.

The intended readers are scientifically demanding power engineers and computer
scientists or operations researchers developing power-system applications.
Bring linear algebra, complex arithmetic, and elementary circuit laws. The
first experiment requires only Python 3; Julia is used in the larger studies.

## Run and inspect

The [computational case guide](@ref computational-cases) connects lessons to
commands, expected evidence, and questions to investigate. The
[study workbook](@ref study-workbook) provides a structure for recording and
defending a complete modelling experiment.

## Consult the reference library

The HTML library retains the full specialist treatment and evidence records.
Use the [knowledge-base index](@ref knowledge-base-index),
[terminology](@ref reference-terminology), and [chapter status](@ref
chapter-status) to locate a claim and its scope. [Scope and thesis](@ref
scope-and-thesis) explains the proposed representation architecture and the
limits of current application coverage.

The current draft has no claims recorded as externally reviewed. Derivations,
repository tests, independent numerical implementations, and human review are
distinct evidence categories. The [evidence map](@ref reference-evidence-map)
reports the maintained inventory.

For optional language-model access to the same sources, see the
[ChatGPT guide](@ref chatgpt-access) or [Claude guide](@ref claude-access).

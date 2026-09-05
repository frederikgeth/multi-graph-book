# Scientific, editorial, and audience review

Date: 2026-09-05. Reviewed book revision: `f2b5361cc7091a4816783f5e82f4df4a5cc7720e`.

This is an advisory, AI-assisted review, not external human peer review. It does
not update the claims ledger or certify the whole book. The review combines
targeted mathematical scrutiny, source comparisons, selected executable checks,
and an inventory of the reading routes. Audience and title recommendations are
editorial judgments and hypotheses to test with readers.

## Judgment

The initiative has a useful core and a credible specialist audience. Its strongest
contribution is teaching researchers to carry physical meaning, assumptions,
constraints, and recoverable quantities through the construction and
transformation of computational power-system models. The parallel-member
counterexample is a clear demonstration of why matching equations need not
preserve an optimization problem.

The current draft is not ready to be treated as a dependable reference throughout.
There are specific mathematical overstatements in central passages, the external
human review ledger is empty, and the reading route gives too much weight to
reference infrastructure and repeated framing. These problems justify focused
revision, not abandoning the initiative. Neither the scientific value nor the
remaining correctness risk can be inferred from the volume of generated artifacts.

The most valuable next milestone is a small, externally reviewed teaching core
with reproducible experiments and reader trials. Expanding the taxonomy or adding
more nearby numerical cases has lower priority.

## What was inspected and checked

Read the architectural and quality-control policies; the README, home, reading
guide, scope, opening counterexample, preservation definitions, selected
representation passages, series elimination and composition, positive-sequence
collapse, BIM/BFM audit, Australian construction reproduction, evidence summary,
prior technical review, benchmark status, and associated code/artifacts. Inspected
both documentation route declarations and inventoried all routed Markdown pages.
This was not a line-by-line review of all 74 pages, all references, or all proofs.
No fresh HTML/PDF build or visual pagination audit was performed.

| Check | Outcome in this review |
| --- | --- |
| Scientific knowledge generation, `--check` | Passed: 18 PSK records |
| Federated pair against book snapshot | Passed |
| Federated pair against `../BMOPFTools.jl` | Failed: manifest stale against supplied checkout |
| LLM reproducibility | Passed, including corpus, retrieval, routes, fixtures, and answer contracts; neural benchmark excluded by this command |
| Degree-two series tests | 35/35 passed |
| Typed Kron tests | 51/51 passed |
| Transformer winding normalization tests | 12/12 passed |
| Multiconductor AC parallel comparison | 41/41 passed |

The first combined Julia invocation encountered a sandbox cache-write restriction
when loading JuMP. The AC test was then successfully run with
`julia --startup-file=no --compiled-modules=no --project=experiments experiments/test/multiconductor_parallel_ac.jl`.
This was an environment restriction, not an assertion failure.

The stale live pair does not invalidate the historical pinned result or prove a
package defect. It means the current sibling checkout and the committed pair
cannot be described as the same verified combination. Resolve which executable
revision is intended, inspect both sides, then repin deliberately. This review
does not change the pair identity.

The ledger currently contains 109 claims: 103 self-checked and 6 independently
implemented, with none externally reviewed. Claim types are 39 theorem, 42
empirical, 15 definition, 8 proposal, and 5 practice records. These are registry
classifications, not 39 independently proved new theorems. There are 95 JSON files
under `experiments/generated`, including supporting/provenance artifacts; these
are not 95 independent experiments.

## Findings requiring scientific correction

### 1. Joint observations must be preserved when decisions depend on their relationships

Location: [preservation-contracts.md](../docs/src/foundations/preservation-contracts.md),
lines 16–37. High priority; the issue concerns the scope of the definition.

The displayed definition equates the image of each `h` in a family separately.
This is a coherent definition of marginal observational agreement, but it does
not in general establish joint observable-set or decision equivalence.

Take source set `{(0,0),(1,1)}` and target set `{(0,1),(1,0)}`. With observations
`h1(a,b)=a` and `h2(a,b)=b`, both models have the same image `{0,1}` for every
listed observation. Their joint sets differ, and maximizing `a+b` gives 2 versus
1. The definition detects this only if a sufficiently rich joint observation or
the relevant combined objective is included explicitly.

For the intended decision-preservation claim, define a joint observation map
`O=(h1,...,hk)` and require equality of its feasible images for each admissible
input, together with the stated objective correspondence and recovery obligations.
Alternatively state an appropriate closure/separation requirement on the family.
Make explicit whether `u` is a fixed input or a decision optimized over a domain;
domain correspondence is an additional obligation. Do not imply that separate
matches of voltages, currents, constraints, and objectives automatically preserve
their relationships.

### 2. Apparent-power feasible regions are not generally PSD quadratic regions in voltage coordinates

Location: [first-failure-parallel-branches.md](../docs/src/start/first-failure-parallel-branches.md),
lines 125–137. High priority; a source interpretation error in a prominent example.

The passage says a current or apparent-power limit has feasible set
`{x : xᵀMx ≤ 1}` after rating normalization. For a fixed linear branch,
`|I|²=xᵀQx` is quadratic. However,

`|S_i|² = |U_i|² |I_i|²`

is generally quartic in the real voltage coordinates. Even the real-voltage
slice of a unit-admittance series branch is nonconvex under `|S_i|≤1`: endpoint
voltages `(1,2)` and `(2,2.5)` each give `|S_i|=1`, while their midpoint
`(1.5,2.25)` gives `|S_i|=9/8`. A PSD quadratic sublevel set is convex, so it
cannot be that actual apparent-power feasible set.

[Molzahn's paper](https://molzahn.github.io/pubs/molzahn-redundant_flow_limits.pdf),
equations (1)–(3), instead cancels the shared terminal-voltage magnitude in a
comparison of normalized apparent-power flows on parallel members. This yields
a comparison of normalized squared currents, which can be studied with quadratic
forms. The redundancy argument survives; the book should distinguish its
auxiliary quadratic comparison sets from the original apparent-power regions.
The scalar summed-rating counterexample itself remains sound.

### 3. Shared voltage variables do not erase member-specific constraints

Location: [bim-bfm-parallel-lines.md](../docs/src/cases/bim-bfm-parallel-lines.md),
lines 47–51. High priority; an overstatement of representational impossibility.

The warning suggests that a shared `W_ij` prevents a theorem from quantifying
member-current limits, and that introducing `W_lij` supplies the needed
expressiveness. The passage's preceding equations already recover member powers
using shared voltage products and member-indexed admittances.

For fixed scalar series members in the exact lifted voltage model,

`|I_l|² = |Y_l|² (W_ii + W_jj - 2 Re W_ij)`.

Each member can therefore have its own current limit without an independent
member-indexed voltage-product variable. Retained member parameters, maps, and
constraints are what matter. Separate variables may be useful, but adding them
with equality constraints can be a redundant reformulation; allowing them to vary
independently may change a relaxation. The index alone establishes neither result.
Switching and outages require their own state variables and conditional laws;
this fixed-state counterargument does not establish those extensions.

Replace the warning with a distinction between shared physical coordinates and
discarded member data/constraints. The simpler displayed branch formulas should
also explicitly declare their series-only, no-tap scope before the later
nominal-pi discussion.

### 4. The information comparison is initially a preorder, subject to closure assumptions

Location: [scope-and-thesis.md](../docs/src/foundations/scope-and-thesis.md),
the paragraph declaring a partial order after `M1 ≽_Q M2`. Medium priority,
especially for the intended CS and mathematical audience.

Distinct representations can answer the same queries in both directions: a
permutation of coordinates is an immediate example. Mutual answerability does
not imply equality of representations, so antisymmetry is not established.
Assuming identities and admissible composition give reflexivity and transitivity,
the relation is a preorder. A partial order can be defined on equivalence classes
under mutual answerability. State these assumptions and the quotient rather than
calling the relation a partial order on raw representations.

The first three objections have exact-arithmetic demonstrations in
[critical-review-witnesses-2026-09-05.py](critical-review-witnesses-2026-09-05.py).
They are independent of repository model assembly. They do not test every
downstream use of the affected definitions; a correction needs a search through
claims, figures, vocabulary, retrieval passages, and certificates.

## What deserves confidence, and what remains unestablished

The scalar parallel example correctly separates aggregate terminal response from
individual constraints, and provides an algebraic witness as well as a solved
case. The selected AC comparison tests pass. The current series chapter includes
the mutual-coupling and series-only corrections identified by the older review;
those historical findings should not be reported as still unfixed. Current
series, Kron, and winding tests also pass.

Other strong features are explicit refusal conditions; separation of finite
grounding from a reference convention; retention of unresolved construction
provenance in the Australian case; distinction between schema validity and truth;
and honest limits on solver optimality and independence. The proposed architecture
is explicitly labelled as a proposal. Preserve those qualifications.

Four different questions need separate evidence:

1. Is the mathematical statement true under its assumptions?
2. Does the implementation correctly realize that mathematical model?
3. Does the model adequately represent the physical study or equipment?
4. Does the teaching resource improve a reader's scientific work?

Most current executable evidence bears on the second question and selected
instances of the first. Agreement of two solvers sharing an erroneous primitive
does not settle the third. Teaching effectiveness has not been measured here.
Large artifact counts and small numerical residuals do not bridge these gaps.

Retain independence provenance at the level of inputs, primitive construction,
assembly, numerical algorithm, implementation, and reviewer. The existing caveats
about shared transformer matrices are good practice. Identify automated reviews
as automated near their titles, so readers do not have to reach a final caveat to
understand what 'independent' means.

The LLM check reports 100% contract completeness on its routed evaluation cases,
but held-out hybrid recall at 10 is 46.6%, routing fires on 75.8%, and 5 of 33
held-out queries have zero recall at 10. Those are distinct metrics; the passing
gate is a regression result, not general answer accuracy. The agent benchmark
correctly labels committed examples as scorer/conformance fixtures and the pilot
as not yet executed. Keep that research separate from reader learning outcomes.

## Audience, usefulness, and differentiation

The strongest initial audience is graduate students and early-career researchers
building or modifying PF/OPF models, together with scientifically demanding power
engineers and CS/OR researchers entering that work. The common task is to turn a
model into a trustworthy computation while understanding its limits. Broader
graph learning, protection, dynamics, and standards audiences should initially
be adjacent readers, not equal promises of coverage.

There is direct evidence of adjacent teaching demand, but not yet evidence of
demand for this particular book. Steven Low's
[Power System Analysis](https://netlab.caltech.edu/book/) explicitly targets
students and researchers interested in analytical structure and includes
unbalanced three-phase networks. Davidson and Jenkins's
[power-systems optimization course](https://github.com/Power-Systems-Optimization-Course/power-systems-optimization)
combines Julia/JuMP, theory, notebooks, assignments, and projects. These are
important comparators: 'rigorous power-system mathematics' alone does not
differentiate this initiative.

PowerModelsDistribution already documents
[engineering-to-mathematical conversion](https://lanl-ansi.github.io/PowerModelsDistribution.jl/stable/manual/eng2math.html),
including grounding and transformer mappings. Treat it as a concrete precedent
and case-study environment. The distinctive opportunity is explaining and
checking the scientific obligations across those mappings, with examples that
readers can transfer to their own software. Do not imply that typed component
models, multiconductor modelling, or engineering compilers originate here.

[PGLib-OPF](https://github.com/power-grid-lib/pglib-opf) supplies a useful model of
a tightly scoped benchmark resource with a declared problem formulation. Its
existence does not prove the book's demand, but supports making the counterexample
collection a usable, citable research artifact in its own right.

What the next generation cares about should be treated as hypotheses about
research tasks, not assumptions about age or attention span. Likely needs are:
finding a tractable research problem, understanding another field's assumptions,
getting a first correct implementation running, debugging a plausible result,
reusing evidence in a paper, and receiving credit for useful contributions.
Precision serves these needs when it changes what a reader can derive or check.

Test with approximately 8–12 target readers across power, CS, and OR backgrounds.
Give them one tutorial, then a previously unseen nearby counterexample. Record
completion time, setup failures, interpretation errors, source-model checking,
and unjustified claims. Ask an instructor to use a module. This is formative
evidence, not a statistically powered estimate of effectiveness. For a stronger
comparison later, use matched tasks, a comparison resource, counterbalanced
order, and blinded scoring. Do not use page views, praise, or GitHub stars as a
substitute for demonstrated learning and reuse.

## Structural diagnosis and proposed book

Both route declarations currently include the same 74 Markdown pages, in partly
different orders. They total 138,880 whitespace-delimited source tokens counted
with Python `str.split()`; this includes equations, markup, and tables and is not
a count of rendered prose words. Reference pages account for 38,333 and research
record pages for 9,690. The first-failure chapter is tenth in the PDF route, with
11,266 source words before it, although earlier pages already contain smaller
examples. ChatGPT/Claude setup and large generated indexes are in the PDF route.
README wording that the PDF omits retrieval indexes does not match the build.

The principal editorial problem is repetition of motivation and architecture
before readers obtain a concrete capability. The content repeatedly explains
what the book will distinguish, how to navigate it, what a figure is, and what
a proposed framework might support. These passages can be accurate and still
interrupt the argument. Adding another reading guide will not fix that.

Create three views of the maintained source: a selective book, a reference
library, and an executable case collection. Keep stable chapter anchors, PSK
identities, source hashes, retrieval contracts, and the deterministic access
machinery. Selection and presentation can change without deleting evidence or
introducing a competing knowledge base.

A concrete eight-chapter core would be:

| Chapter | Reader learns to do | Existing material to draw on |
| --- | --- | --- |
| 1. A plausible model gives the wrong answer | Diagnose the parallel-rating failure by hand | First failure; compact dispatch comparison |
| 2. From equipment to equations | Stamp a model with explicit labels, orientations, terminals, and units | Source-to-canonical; two-level topology; circuit formulations |
| 3. Conductors, connections, and ground | Derive a small unbalanced model and state its grounding assumptions | Connection/load maps; earth models; valid positive-sequence specialization |
| 4. Graphs for different computations | Choose and construct asset, topology, incidence, and sparsity views | Many graphs; cycle examples; formal frameworks as needed |
| 5. Transformations and recovery | State and establish a scoped preservation result | Corrected contracts; series and Kron cases; coordinate actions |
| 6. Constraints and decisions | Preserve feasible decisions, recover limits, and reason about controls | Parallel AC; transformer taps; BIM/BFM after correction |
| 7. Evidence for a computation | Check residuals, conditioning, assumptions, and independent reproduction | Numerical consequences; selected provenance examples |
| 8. An end-to-end modelling study | Assemble, transform, solve, recover, and defend a result | One coherent four-wire case with selected variants |

Start with a scalar case, add a small conductor/connection example, then grow one
network as needed. Keep the difficult running fixture as an integration test;
introducing all of its complications at once makes it a poor first lesson.
Explain the broad baseline without requiring the broadest model for every
calculation. Include positive examples showing when a familiar simplification
is sufficient and saves work.

As an editorial budget, aim initially for roughly 35,000–50,000 source prose
words in the core; calibrate this after drafting and reader testing. Keep the
multiwinding derivation sequence as specialist reference material until the core
requires it. Move exhaustive indexes, research/search logs, release traces,
certificate field inventories, and LLM-client setup outside the main PDF.

Each chapter should earn its place with a distinct learning outcome. A useful
pattern is: physical question, explicit assumptions, minimal example,
derivation, computational check, nearby failure, and transfer exercise. State
load-bearing assumptions beside the mathematics. Replace repetitive broad
warnings with precise qualifications at the point where they matter. A short
paragraph explaining a useful result can often replace a full context-setting
page.

## Use the computational evidence as teaching material

Make five to eight flagship experiments easy to discover and run. Each should
offer a diagram, the scientific question, minimal input, environment and command,
expected diagnostic output, source/target/recovered comparisons, and a deliberate
mutation that changes the answer. Include a hand-checkable anchor wherever
possible. Package-owned behavior remains in BMOPFTools; the book teaches the
scientific reasoning and links to executable contracts.

For the opening case, have readers predict the member currents, reproduce the
165 A aggregate versus 150 A member violation, derive the correct 110 A scalar
aggregate cap for this fixed case, and then explain why that scalar repair does
not preserve independent outages. This turns a warning into usable knowledge.
For a reduction case, have readers recover an eliminated current and check its
original limit. For a coordinate case, reorder labels without changing physics,
then deliberately reorder only one coupled object and diagnose the failure.

Provide a working default environment and direct links to expected outputs.
Students should not need to configure an LLM service or understand the whole
federated architecture to complete the first experiment. Teach interpretation of
checks, including inapplicable and indeterminate outcomes. Keep the full artifact
inventory available for expert inspection. Consider versioned citable releases
of reviewed lessons and cases, and contribution paths for small counterexamples,
reproductions, and errata with explicit contributor credit.

## Title and personal framing

Recommended working title:

**Power-System Modelling for Computation**

*From circuit equations to optimization and software*

This fits the proposed teaching structure and tells the intended reader why to
open the book. The subtitle is a commitment: the core must actually teach the
transition into implementation and verification. The introduction should limit
the first edition to its supported steady-state scope. Graphs and preservation
remain central methods without having to carry the whole title.

Two alternatives are **Power-System Models, Made Explicit**, with subtitle
*Structure, transformations, and computational evidence*, for a more personal
teaching voice; and **Structure and Transformation of Power-System Models**,
with subtitle *Theory, counterexamples, and computation*, if the project remains
primarily a research monograph. These are editorial candidates, not claims of
title uniqueness. Avoid 'certified', 'correct', or 'complete' as blanket promises
in the title while the stated evidence boundaries remain.

The present title, *What Power-Network Models Preserve*, identifies the research
question but gives little sense of the practical modelling skill on offer.
'Decision boundaries' in its subtitle also has an established machine-learning
association that can misdirect readers. The original multigraph framing would
likewise understate the roles of constitutive equations, software, and decisions.

The author's motivation belongs in a short signed preface, with one concrete
technical example in the opening chapter. It supplies a human reason for the
book and explains why its details matter. Describe personal experience as
personal experience. Broad claims about engineering culture, textbooks, or
software quality require evidence and should not become the premise of the work.

Suggested author-voice draft, to adapt for factual accuracy:

> This book grew out of difficulties I encountered while learning to build
> power-system models and developing research software. I could often find a
> formula for assembling an admittance matrix, yet still struggle to determine
> exactly what its indices represented, which assumptions justified a
> simplification, and how to recover the equipment quantities my study needed.
> Working on software, including PowerModelsDistribution, made those questions
> practical: a convention left implicit in a derivation eventually becomes an
> implementation choice. I want the next researcher to spend less time
> reconstructing those choices, and more time asking useful scientific questions.
> The examples here make the choices explicit and provide calculations that
> readers can inspect, challenge, and reproduce.

Frame PowerModelsDistribution as part of the experience that developed these
questions, acknowledging what it already makes possible. If discussing a defect,
name a version, a reproducible example, its consequence, and its resolution.
Critique the specific assumption or behavior rather than assigning motives or
characterizing a whole professional community.

## Recommended sequence

First correct the three high-priority mathematical passages and the preorder
terminology, tracing their downstream representations. Resolve the intended
federated pair. Commission narrowly scoped human review of the repaired
foundations and flagship examples; the existing external-review packet is a
useful starting point.

Then produce one complete opening lesson under the proposed title and build the
selective PDF/HTML route. Test it with the actual target readers before
reorganizing every specialist chapter. Continue with a small reviewed release
whose promises match its contents. Use adoption, successful reproduction, and
performance on unseen modelling tasks to decide what to expand next.

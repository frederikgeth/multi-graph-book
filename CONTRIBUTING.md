# Contributing

## Authoring principles

1. Lead with the preservation question, not the preferred graph data structure.
2. Separate physical objects, mathematical realizations and algorithmic views.
3. State model assumptions at the point where they are used.
4. Give counterexamples whenever a familiar simplification has a restricted
   validity domain.
5. Keep citations adjacent to the claims they support.
6. Preserve uncertainty rather than converting incomplete evidence into
   confident prose.

## Chapter forms

Use the chapter form that matches the work. The complete editorial contract is in
[`BOOK_PLAN.md`](BOOK_PLAN.md).

**Representation chapters** define their objects and relations, the questions they answer, their
characteristic omissions, maps to neighbouring representations, the running example in that view,
and known failure modes.

**Transformation chapters** contain a motivating decision context, source and target categories,
the rule, preconditions and negative application conditions, preservation contract, proof or error
definition, recovery and provenance maps, a positive example, a minimal counterexample, and
executable tests where possible.

**Application chapters** begin with the analysis or decision task, derive its representation
obligations, compare candidate views, and measure consequences in feasibility, active limits,
objective value, and decisions—not state error alone.

**Reference entries** are compact cards recording definition, aliases, source and target types,
preserved properties, characteristic losses, recovery, evidence, and related entries.

### Evidence boundary banner

Load-bearing chapters should place a compact evidence boundary immediately after the page-status
line. Keep the wording specific to the chapter and distinguish a derivation or executable witness
from external review:

```markdown
!!! note "Evidence boundary"
    **Scope:** [model, fixture, and observation family].
    **Evidence:** [definition, derivation, theorem, executable witness, or independent numerical reproduction].
    **Numerical optimality:** [not applicable, locally solved only, branch-scoped, or globally certified].
    **Unresolved boundary:** [global, physical, solver, uncertainty, or external-review claims that remain open].
```

The banner is a reader-facing summary, not a replacement for the claims ledger, certificate, or
literature citation. A numerical reproduction of the same fixture is not an independently assembled
physical model, and a locally solved nonlinear optimization problem is not a global optimality proof.

## Translation-trap callouts

Use the controlled callouts introduced in
[`docs/src/foundations/translation-traps.md`](docs/src/foundations/translation-traps.md):

- **Graph-theory trap** when a graph concept is applied to an unnamed or
  inappropriate representation;
- **Circuit-theory trap** when a conservation or device claim exceeds its
  factorization or constitutive assumptions;
- **Power-system shorthand** when a familiar phrase is useful but becomes
  ambiguous outside its conventional context;
- **Decision-model consequence** when a representation choice changes what can
  be constrained, chosen, observed, or recovered.

Write each callout as a Documenter admonition, give a precise replacement
statement, and link to the definition or result that supports it. A callout is
not a substitute for a definition, derivation, counterexample, or claim-ledger
entry.

## Mathematical notation

Follow [`docs/src/foundations/notation-and-conventions.md`](docs/src/foundations/notation-and-conventions.md),
which is based on the BMOPFTools model specification.

- Use ``\ell ij`` for line ``\ell`` oriented from bus ``i`` to bus ``j``.
- Use only the element index for element-intrinsic data, such as ``\mathbf Z_\ell``.
- Use an oriented triple for terminal quantities, such as ``\mathbf I_{\ell ij}``.
- Preserve device and winding indices for multiwinding transformers until an explicit compilation
  creates two-terminal elements.
- Declare terminal ordering, current direction, units, and base transformations.
- Do not make colour the only carrier of mathematical meaning.

## Citation syntax

References use DocumenterCitations syntax:

```markdown
Kron reduction is analyzed in detail by Dörfler and Bullo
[DorflerBullo2013](@cite).
```

Add the corresponding checked entry to `docs/src/references.bib`. Use stable,
descriptive keys. Do not add a citation that has only been seen in another
paper's reference list. Record the publisher, DOI-registration, standard-body,
or official-project verification in `review/bibliography-audit.toml`, then run:

```sh
julia scripts/check_bibliography.jl
```

## Claims ledger

High-consequence definitions, exactness statements, counterexamples, and
computational results belong in `claims/claims.toml`. Keep the chapter path,
scope, assumptions, evidence type, and unresolved review work explicit. Run

```sh
julia scripts/check_claims.jl
```

before submitting a change. The checker rejects duplicate identifiers, unknown
statuses, missing chapter paths, and missing BibTeX keys.

## Development decisions

Consequential software and cross-repository architecture choices belong in the
[development research and decision log](docs/src/literature/development-decision-log.md),
not the scientific claims ledger. Add the next stable `DLOG-NNNN` entry with
the question, options, decision, reason, evidence, known downside, and
conditions for revisiting. Retain rejected approaches and supersede old entries
instead of rewriting their rationale. Run

```sh
python3 scripts/check_development_log.py
```

before submitting a log change. Scientific statements still follow the claims,
PSK, citation, and evidence-review process; a DLOG entry cannot reclassify them.

## Agent benchmark records

Benchmark specifications and measured agent runs are different evidence
objects. A task or synthetic scorer fixture must not be described as an agent
observation. Keep the benchmark status at `substrate_only_no_agent_runs` until
controlled run artifacts exist, and preserve the exact condition, model
revision, corpus, federated pair, package export, tool settings, and scoring
version for every run.

For the first slice, run both the repository-local and live sibling checks:

```sh
python3 scripts/check_agent_benchmark.py --check
python3 scripts/check_agent_benchmark.py --check --bmopf-root ../BMOPFTools.jl
python3 scripts/check_agent_benchmark_pilot.py --check --bmopf-root ../BMOPFTools.jl
```

BMOPFTools owns executable oracle behavior. Benchmark code may invoke and pin
its contracts, recipes, fixtures, and Findings, but must not duplicate or
silently reinterpret their runtime semantics.

Generated fixtures, certificates, view source maps, and local Markdown links
are checked with:

```sh
python3 scripts/check_artifacts.py
```

Before an internal release candidate is handed to reviewers, rebuild the
HTML/PDF and run the consolidated gate:

```sh
python3 scripts/check_release_candidate.py --write
python3 scripts/check_release_candidate.py --check
```

When changing claims, PSKs, or canonical source pages, regenerate the derived
cross-repository artifacts first:

```sh
python3 scripts/regenerate_all.py
```

The command assumes sibling checkouts at `../BMOPFTools.jl`; pass
`--bmopf-root /path/to/BMOPFTools.jl` when using another layout. It runs the
scientific export, federated pair check, LLM corpus and derived retrieval/access
evaluations, neural compatibility marker, and agent-benchmark artifacts in
dependency order. Follow it with the answer-contract and release checks above.

The first command records the candidate's observed counts and hashes; the
second fails if any release input or generated output has drifted. This gate is
not external review and does not convert the single-coded literature seed into
a double-coded review.

The package-independent degree-two and coordinate/composition rules can be tested without BMOPFTools:

```sh
julia experiments/test/series_elimination.jl
julia experiments/test/coordinate_normalization.jl
julia experiments/test/transformer_winding_normalization.jl
```

The multiconductor nonlinear decision cases require the experiments
environment and run as part of `experiments/test/runtests.jl`.

New machine-readable transformation results must conform to
`schemas/transformation-certificate.schema.json`. Register their certificate
ID in the claims ledger and include positive, rejection, and recovery tests as
appropriate.

## Changes to definitions

Definitions form the interoperability contract of the book. A change to a core
term should identify:

- affected chapters;
- whether the old and new meanings are extensionally different;
- consequences for software schemas and proofs;
- migration wording or aliases.

## Review roles

As the project grows, seek distinct reviewers for:

- graph theory and formal transformations;
- circuit and multiconductor modeling;
- transmission operations;
- distribution engineering and grounding;
- optimization and decision equivalence;
- protection and utility asset practice;
- software/data interoperability.

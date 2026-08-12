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

## Proposed chapter template

Each technical chapter should contain:

1. problem and motivating decision context;
2. source and target model categories;
3. variable, port and orientation definitions;
4. transformation or projection;
5. preservation contract;
6. assumptions and negative application conditions;
7. proof, derivation, or error definition;
8. recovery and constraint maps;
9. counterexamples and failure modes;
10. implementation practice;
11. literature comparison;
12. unresolved questions.

## Citation syntax

References use DocumenterCitations syntax:

```markdown
Kron reduction is analyzed in detail by Dörfler and Bullo
[DorflerBullo2013](@cite).
```

Add the corresponding checked entry to `docs/src/references.bib`. Use stable,
descriptive keys. Do not add a citation that has only been seen in another
paper's reference list.

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


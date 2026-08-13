# Quality-control policy

This project aims to become a scientific reference rather than an opinionated
collection of notes. Quality control is therefore part of the content model.

## 1. Claim classification

Every substantive claim should be recognizable as one of:

- definition adopted by the book;
- theorem or established result;
- empirical result;
- standard or documented engineering practice;
- interpretation or synthesis;
- proposal;
- conjecture or open question.

The text should not slide from one category into another. In particular,
implemented software behavior is not evidence of general correctness, and
terminal equivalence is not evidence of decision-set or asset equivalence.

## 2. Source hierarchy

Prefer, in order:

1. standards and normative specifications for data-model claims;
2. peer-reviewed primary papers or authoritative monographs for scientific
   claims;
3. official software documentation and source code for implementation claims;
4. theses and technical reports when they contain otherwise unavailable detail;
5. review papers for discovery and synthesis;
6. secondary web sources only as pointers to primary material.

Every important source should be read, not cited from a search-result abstract.

## 3. Bibliographic checks

Before a source is marked `verified`:

- verify title, authors, year, venue, volume, pages, DOI and version;
- prefer DOI plus an open-access URL when available;
- distinguish preprints from final publications;
- record the standard or software version and access date;
- confirm that the cited source supports the nearby claim;
- avoid citing a later paper for a result originating in an earlier source.

Any unresolved metadata should be marked explicitly in the BibTeX entry and in
the claims ledger rather than silently completed from memory.

## 4. Claims ledger

The machine-readable ledger at `claims/claims.toml` uses the fields:

```text
claim_id, chapter, claim_text, status, evidence_type, citation_keys,
model_scope, assumptions, reviewer, review_date, unresolved_issue
```

High-consequence claims—especially exactness, non-existence, standards
interpretation, and industry-practice prevalence—must have entries.

## 5. Mathematical review

Every transformation should be checked at four levels:

1. dimensions, units, orientation and conductor coordinates;
2. local component equations;
3. network interconnection and boundary behavior;
4. operational/decision feasible sets.

Proofs should state the model class and excluded cases. Numerical evidence must
not be presented as proof of an exact identity.

## 6. Counterexample-first testing

Each accepted rewrite requires:

- at least one positive minimal example;
- at least one rejected near-miss;
- an adversarial example involving a hidden shunt, grounding, measurement,
  limit, control, coupling, or discrete state where relevant;
- a round-trip or recovery test when an inverse exists.

## 7. Reproducibility

Computational chapters should specify:

- exact input model and schema version;
- transformation trace and certificate;
- software environment and solver versions;
- tolerances and observation metrics;
- source and reduced decision variables;
- recovery and feasibility checks in the original model.

## 8. Review gates

A chapter progresses through:

1. `outline`;
2. `draft`;
3. `source-checked`;
4. `mathematically-reviewed`;
5. `reproducible` where applicable;
6. `release-candidate`;
7. `published`.

No chapter should be called authoritative merely because the site renders.

## 9. Automated checks

The current CI fails on:

- unresolved Documenter cross-references;
- missing BibTeX keys;
- malformed equations;
- broken internal links;
- duplicate claim identifiers;
- incomplete bibliography-audit coverage;
- generated view maps that reference unknown source objects or stale figure and fixture hashes;
- clean-reproduction artifacts that disagree with the canonical fixture or recorded commit;
- transformation certificates that violate the versioned common schema or use an unregistered claim ID;
- the package-independent degree-two, conductor, transformer-winding, multiwinding-leakage, terminal-assembly, fixed-linear transformer-completion, parameterized tap-decision, and composition tests;
- local source/reduced/recovered feasibility checks for both parallel decision cases and the
  solver-backed transformer tap network case;
- an optimizer-independent continuation/Newton reproduction of the transformer tap network case,
  including explicit infeasible and unbracketed-search rejections;

Planned extensions include:

- unclassified normative words such as "always," "exact," or "preserves" in
  designated scientific sections unless accompanied by a claim record;
- transformation examples that fail source-model recovery tests.

External-link checking should run on a schedule because publisher sites can be
unstable.

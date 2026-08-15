# Systematic scoping-review protocol

## Status and objective

**Protocol version 0.1.0; drafted before systematic screening.** The current
bibliography is a seed set and is not evidence that the search is complete.
The matrix schema and controlled fields are checked by
`scripts/check_evidence_matrix.py`; this does not promote single-coded seed
rows to double-coded evidence.
This protocol governs the first reproducible scoping review of graph
representations and transformations for decision-focused power-network models.

The primary question is:

> Which source and target power-network model categories are connected by a
> stated transformation, and what structure, behaviour, constraints, decisions,
> provenance, and recovery information does that transformation preserve?

Secondary questions concern closure of physical device classes, explicit
multiconductor and grounding treatment, multi-terminal devices, approximation
domains, and executable implementations.

## Scope

Include work that contributes at least one of the following:

- a formal or operational definition of a power-network representation;
- an exact, conservative, relaxed, or approximate network transformation;
- a topology-processing or model-compilation procedure;
- a recovery, lifting, provenance, or constraint-transfer construction;
- an empirical evaluation in power flow, OPF, state estimation, faults,
  topology processing, planning, or a directly relevant adjacent study;
- a general circuit, graph-transformation, or compositional result with an
  explicit map to power-network modelling.

The multiconductor, explicit-neutral, multiwinding, and decision-constrained
case is the baseline. Balanced transmission studies remain eligible, but their
scope assumptions are coded rather than silently generalized.

Exclude work concerned only with graph learning, geographic visualization,
communication networks, markets, or generic numerical sparsity unless it makes
an explicit representation or transformation claim relevant to electrical
network models. Exclude inaccessible records only after reasonable attempts to
obtain sufficient metadata and technical content; retain the exclusion reason.

## Information sources

Search IEEE Xplore, Scopus, Web of Science, Engineering Village/Compendex,
Inspec, MathSciNet or zbMATH where available, arXiv, and relevant standards and
official software documentation. Use publisher or DOI-registration metadata for
bibliographic verification. Record the platform, query, filters, result count,
and export time for every run.

Searches are supplemented by:

1. backward citation chasing from included sources and authoritative reviews;
2. forward citation chasing in at least two available citation indexes;
3. author and project searches for important preprints and software methods;
4. targeted standard-body and official-project searches;
5. duplicate detection by DOI, then title and authors.

The initial query families are in [search-strings.md](search-strings.md).

## Screening procedure

1. Import raw records without overwriting source metadata.
2. Normalize identifiers and mark exact or probable duplicates.
3. Screen title and abstract against the scope rules.
4. Screen full text and assign one primary exclusion reason when excluded.
5. Code eligible studies using [evidence-schema.json](evidence-schema.json).
6. Perform backward and forward citation chasing after the first eligible set.
7. Re-run saved searches before a tagged book release.

Screening decisions use `include`, `exclude`, or `uncertain`. Allowed full-text
exclusion reasons are `wrong_domain`, `no_representation_or_transformation`,
`no_technical_content`, `superseded_duplicate`, `insufficient_access`, and
`language_or_format_unassessable`. Uncertainty is resolved by discussion and
the resolution is logged; it is never silently changed.

## Evidence coding

The canonical row store is [evidence-matrix.csv](evidence-matrix.csv). Each row
describes one result at one declared scope; a paper may therefore occupy several
rows. Controlled fields and allowed values are defined by the JSON schema.
The operational field rules and second-coder procedure are in
[coding-guide.md](coding-guide.md), while DOI/title duplicate decisions are
recorded in [deduplication-register.csv](deduplication-register.csv).
The current seed snapshot is recorded in [snapshot-manifest.json](snapshot-manifest.json)
and checked by `scripts/check_review_snapshot.py`; the manifest deliberately
states that independent double-coding has not yet occurred.

Critical coding dimensions are:

- source and target model families;
- physical features and conductor/ground treatment;
- transformation type and operating domain;
- preserved observations and feasible-set classification;
- retained limits, discrete decisions, objectives, and source identities;
- recovery, constraint, and provenance maps;
- proof, empirical, software, standard, or engineering-practice evidence;
- executable availability and independent-review state.

Absence of discussion is coded `not_reported`, not `no`. Exactness claims are
recorded in the authors' scope and separately assessed against the book's
preservation-contract vocabulary.

## Quality and bias controls

- Preserve raw exports and query logs under a dated review snapshot.
- Verify DOI-bearing metadata against the DOI registration or publisher.
- Separate publication type and venue from technical evidence strength.
- Do not treat citation count, software popularity, or standards adoption as a
  proof of preservation.
- Give negative results and counterexamples the same eligibility as positive
  transformations.
- Record conflicts of interest when an included tool or paper is authored by a
  reviewer.
- Require a second reviewer for high-consequence inclusion decisions and all
  claims promoted to `established_result` in the book.

## Synthesis and reporting

Report a PRISMA-style flow count, but describe this as a scoping review rather
than a clinical systematic review. Synthesis is organized by model categories,
transformation type, preservation dimensions, power-system features, and
decision task. Quantitative aggregation is used only for commensurate metrics;
otherwise the output is an evidence map and structured gap analysis.

Every published snapshot records protocol version, database coverage, last
search date, matrix checksum, unresolved screening conflicts, and deviations
from this protocol.

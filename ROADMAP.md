# Work plan and roadmap

## Guiding outcome

Produce a citable, open scientific book and executable knowledge base that
explains power-network graph model categories and provides verified,
provenance-aware transformations among them.

The roadmap separates **publication infrastructure**, **knowledge synthesis**,
**formal results**, and **software/experiments** so that progress in one does
not masquerade as completion of the others.

## Phase 0 — Repository and editorial foundation

**Target:** first two weeks.

- Choose the final title, repository name, license and citation metadata.
- Establish Documenter HTML and PDF builds in CI.
- Add issue templates for claim verification, new transformations and source
  reviews.
- Implement the claims ledger and bibliography-verification table.
- Define style rules for equations, diagrams, terminology and epistemic labels.
- Freeze a versioned glossary for the first drafting cycle.

**Exit criterion:** clean local/CI builds; every existing scientific claim is
either cited, labeled as a proposal, or entered as unresolved.

## Phase 1 — Systematic scoping review

**Target:** months 1--2.

Run reproducible searches across:

- circuit/network theory and inverse electrical networks;
- Kron, Ward, REI and dynamic equivalents;
- distribution feeder reduction and aggregation;
- topology processing, CIM/CGMES and utility model management;
- graph rewriting and model-driven engineering;
- port-Hamiltonian, bond-graph and compositional systems;
- network sparsification and Schur-complement approximations;
- optimization-preserving and constraint-aware reduction;
- protection-, grounding- and asset-aware simplification.

Code each source by source/target model, physical detail, exactness,
observations, retained constraints, phase/neutral treatment, provenance, and
implementation availability.

**Exit criterion:** publishable literature matrix, explicit search protocol,
and a gap analysis stronger than the current provisional assessment.

## Phase 2 — Foundations and taxonomy

**Target:** months 2--4.

- Define asset graph and hierarchical port--factor semantics.
- Define relative expressiveness by query families.
- Formalize projection, compilation, normalization, exact behavioral reduction
  and approximation.
- Define preservation certificates and transformation composition.
- Map CIM, PowerModelsDistribution, OpenDSS and other representative tools into
  the framework.

**Exit criterion:** internally consistent Part I draft reviewed by experts from
at least graph/formal methods and power-system modeling.

## Phase 3 — Verified local transformations

**Target:** months 4--8.

Develop complete chapters and executable tests for:

1. conductor-coordinate normalization;
2. ideal-switch contraction and state-resolved topology;
3. degree-two series elimination;
4. homogeneous physical line merging;
5. parallel-bundle representation and constraint recovery;
6. grounding extraction;
7. multiwinding transformer compilation;
8. selected `Y`--`Δ` and star-mesh relations with explicit scope.

**Exit criterion:** each rule has guards, proof/derivation, provenance model,
positive and negative examples, and source-feasibility recovery tests.

## Phase 4 — Decision-preserving case studies

**Target:** months 7--12.

Prioritize:

- heterogeneous parallel-line OPF;
- four-wire grounding-aware state estimation;
- topology cleaning of real distribution models;
- multiwinding transformer realization;
- feeder reduction for hosting capacity or dynamic operating envelopes.

Compare transformations by both state error and decision error: feasibility,
active limits, discrete choices, objective value, and contingency outcomes.

**Exit criterion:** open benchmark cases and at least one journal-quality study
showing a consequential failure of conventional reduction plus a certified
alternative.

## Phase 5 — General theory and formalization

**Target:** year 2.

- Establish closure and non-closure results for important device classes.
- Study rewrite termination and critical pairs.
- Formalize linear core results and selected rewrite proofs in Lean.
- Develop exact, inner, outer and scenario-approximate constraint projection
  theory.
- Connect compositional black-box semantics to nonlinear and discrete
  power-system factors.

**Exit criterion:** one or more theorem-led papers and mechanically checked core
results.

## Phase 6 — Reference implementation and community release

**Target:** year 2 onward.

- Release a Julia transformation library independent of a specific optimizer.
- Provide CIM/CGMES, OpenDSS and PowerModelsDistribution adapters.
- Integrate generated model views with PowerOptLab/BMOPFTools experiments where
  appropriate, without defining the research agenda around those packages.
- Establish a versioned transformation registry and community review process.
- Publish tagged book editions with archived source, PDF and bibliography.

## Immediate next sprint

The next Codex session should:

1. validate and correct every seed BibTeX entry;
2. establish the systematic-review protocol and evidence matrix schema;
3. expand the representation chapter into formal definitions and worked
   examples;
4. specify the degree-two rewrite as an executable certificate;
5. design the adversarial micro-network corpus;
6. add CI for HTML, PDF, citations and internal links.

The most valuable first theoretical target is the distinction between
behavioral series equivalence and closure within a physical line class. The
most valuable first decision counterexample is heterogeneous parallel branches
with individual current or power limits.


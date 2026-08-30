# [Development research and decision log](@id development-decision-log)

**Page status:** maintained development record; not a scientific claims ledger.

This log records consequential software and architecture choices for the
federated `multi-graph-book` and BMOPFTools initiative. It preserves rejected
approaches and known costs so that later contributors can distinguish a
deliberate boundary from an unfinished implementation.

Scientific claims, counterexamples, and evidence status remain in the book's
claims ledger and scientific knowledge registry. This page may point to that
evidence, but it cannot establish or reclassify scientific claims. Package
behavior, Findings, fixtures, and runtime applicability remain owned by
BMOPFTools.

## Entry format

Use the next stable `DLOG-NNNN` identifier and retain old entries. A later
decision supersedes an entry by changing its status to `superseded` and linking
the replacement; it does not rewrite the earlier rationale. Every entry records
the question, options, decision, reason, evidence, known downside, and
conditions for revisiting. Use `rejected` when the recorded outcome is to retain
but not promote an attempted approach.

## DLOG-0001 — Federate authorities instead of duplicating them

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** cross-repository ownership and dependency direction

### Question

Where should scientific meaning and executable package behavior be authoritative?

### Options considered

- merge both products into one repository;
- duplicate claims and executable semantics in both repositories;
- keep separate authorities and pair their generated exports explicitly.

### Decision

The book owns scientific statements, evidence status, misconceptions, and
stable `PSK-*` identities. BMOPFTools owns runtime behavior, applicability,
Findings, fixtures, and executable records. The book integrates explicitly
pinned exports from both sides.

### Reason

Each repository must remain useful and testable on its own, while paired
answers must still identify the exact scientific and executable evidence used.

### Evidence

`ARCHITECTURE.md`, both repository `AGENTS.md` files, the executable and
scientific manifests, and `scripts/check_federated_knowledge.py` implement and
check this boundary.

### Known downside

A coordinated change requires regeneration and review in both repositories,
and an unrepinned pair deliberately remains stale.

### Conditions for revisiting

Revisit if separate ownership prevents either repository from releasing
independently, or if a reviewed replacement can preserve offline package use,
source-hash binding, and explicit pair identity with less coordination cost.

## DLOG-0002 — Preserve deterministic retrieval as the knowledge authority

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** book LLM retrieval and answer generation

### Question

Should a generic embeddings or retrieval-augmented generation stack replace the
book's existing LLM machinery?

### Options considered

- replace the current system with an embeddings-first corpus and generic RAG;
- make an opaque hosted retriever authoritative;
- retain deterministic packets, routing, refusal semantics, hashes, and
  evaluations, while treating neural retrieval only as a measured candidate.

### Decision

The deterministic corpus, context packets, MCP/HTTP/CLI routes,
`unsupported`/`under_retrieved` semantics, and source hashes remain the
authority. Neural methods may complement this baseline only through recorded,
reproducible evaluation.

### Reason

The existing machinery makes qualification, counterexample, refusal, and
provenance behavior inspectable. Replacing it would discard capabilities that
generic similarity retrieval does not establish.

### Evidence

The `llm/` corpus and evaluation artifacts, `scripts/check_llm_reproducibility.py`,
and the release-candidate gate exercise the retained routes and semantics.

### Known downside

The deterministic pipeline has more explicit metadata and regeneration work,
and its lexical baseline can have limited raw recall.

### Conditions for revisiting

Revisit when a candidate is evaluated on the pinned corpus and preserves or
improves contract completeness, qualification and counterexample recall,
abstention, reproducibility, and source binding.

## DLOG-0003 — Keep execution adapters curated and thin

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** BMOPFTools JSON, CLI, and MCP execution surfaces

### Question

Should automation expose arbitrary Julia calls or every package function?

### Options considered

- allow arbitrary Julia evaluation;
- mechanically expose the public Julia API;
- promote reviewed operations through explicit parameter and result mappings.

### Decision

Expose only curated operations backed by package APIs, allowlists, structured
responses, recipes, and tests. Solver invocation and arbitrary evaluation stay
outside the current read-only transport surface.

### Reason

A narrow mapping makes applicability, input hashing, statuses, and returned
evidence reviewable without inventing a second package API in transport code.

### Evidence

BMOPFTools' execution response schema, adapter registry, six MCP tools, contract
recipes, and execution-interface tests enforce the current surface.

### Known downside

Useful Julia capabilities are unavailable to agents until a transport mapping
is designed, documented, and tested.

### Conditions for revisiting

Revisit for a concrete operation with a stable runtime API, bounded inputs,
unambiguous status semantics, a pedagogical recipe, and evidence that exposing
it improves a real workflow.

## DLOG-0004 — Treat seeded expected rejections as runtime evidence

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** property testing and scientific evidence boundaries

### Question

Do minimized failures from the controlled property suites automatically become
new scientific counterexamples?

### Options considered

- promote every generated rejection into the scientific registry;
- omit negative generated cases from the federated record;
- export them as classified package evidence without widening the linked claim.

### Decision

An `expected_contract_rejection` demonstrates deterministic runtime behavior
inside the suite's declared generator domain. It is not, by itself, a new
scientific counterexample or a broader validation claim.

### Reason

The current mutations deliberately violate declared contracts. Calling those
expected rejections discoveries would confuse an oracle check with new
scientific evidence.

### Evidence

The two BMOPFTools `property_suite` exports record generators, seeds, oracles,
minimizers, classifications, and `does_not_establish` boundaries; the book's
federated trace preserves those fields.

### Known downside

Potentially interesting minimized witnesses require a separate human review
before they can enrich the scientific negative-knowledge registry.

### Conditions for revisiting

Revisit a witness when it is not an injected contract violation, survives
independent reproduction, has a scientifically meaningful minimal fixture, and
can be reviewed through the book's normal claim and evidence process.

## DLOG-0005 — Do not promote the archived neural retrieval candidate

- **Date:** 2026-08-30
- **Status:** rejected
- **Scope:** experimental neural retrieval candidate

### Question

Did the pinned neural, hybrid, or reranked candidate improve enough on the
evaluated corpus to replace the deterministic retrieval baseline?

### Options considered

- promote the candidate despite the recorded failure;
- delete the unsuccessful experiment;
- archive the result and require a current-corpus rerun before reconsideration.

### Decision

Do not promote the candidate. Retain the archived negative result and its model
and corpus compatibility metadata.

### Reason

The recorded candidate status is `fail`; an unqualified promotion would hide a
negative result and weaken the reproducible baseline.

### Evidence

`llm/generated/neural-retrieval-evaluation.json`, its Markdown report, and
`scripts/check_neural_benchmark.py` retain the setup, metrics, compatibility
state, and promotion outcome.

### Known downside

The current system does not gain any potential semantic-retrieval benefit from
that candidate, and the archived result becomes stale as the corpus evolves.

### Conditions for revisiting

Rerun against the current pinned corpus with recorded models and thresholds.
Promote only if the candidate passes the declared criteria without regressing
contract completeness, refusal behavior, or reproducibility.

## DLOG-0006 — Preserve asymmetric book-only negative knowledge

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** federated negative-knowledge coverage

### Question

Should every book-owned negative record have a placeholder BMOPFTools contract?

### Options considered

- manufacture empty contracts and Findings for symmetry;
- omit records that have no executable counterpart;
- retain the scientific record and mark executable status `not_applicable`.

### Decision

Keep book-only records when the scientific negative knowledge is useful, and
represent the absence of meaningful package behavior explicitly as
`not_applicable`.

### Reason

Federation joins distinct authorities; it does not require false structural
symmetry. Empty package records would imply executable support that does not
exist.

### Evidence

The structured negative-result, numerical-pathology, scope-boundary, and open-
question records exercise this state in the generated scientific and federated
manifests.

### Known downside

Consumers must understand that a valid federated record may intentionally lack
an executable check.

### Conditions for revisiting

Add a BMOPFTools link only when concrete package behavior, an applicability
boundary, stable diagnostics, and testable evidence genuinely exist.

## DLOG-0007 — Establish the benchmark substrate before claiming agent effects

- **Date:** 2026-08-30
- **Status:** accepted
- **Scope:** first scientifically constrained agent-benchmark slice

### Question

Should the first benchmark milestone immediately report model comparisons, or
first freeze tasks, conditions, scoring, oracles, and provenance?

### Options considered

- run whichever hosted model is convenient and report an exploratory score;
- defer all benchmark work until a full multi-model study is funded;
- establish a transparent deterministic substrate and distinguish its
  conformance fixtures from later controlled agent runs.

### Decision

Deliver the substrate first. The initial parallel-member slice records seven
cumulative conditions, an invalid-assumption case, an abstention case,
structured scoring, and live book/package source binding. Its status remains
`substrate_only_no_agent_runs` until controlled runs are added.

### Reason

Without a frozen protocol, a model score cannot be separated from prompt,
resource, tool, corpus, or scorer drift. Synthetic scorer fixtures are useful
software evidence, but presenting them as agent observations would manufacture
a research result.

### Evidence

`benchmarks/agent/parallel-member-limits-v1.json`, the two agent-benchmark JSON
schemas, `scripts/check_agent_benchmark.py`, and its generated conformance
report implement the chosen boundary against the pinned federated pair.

### Known downside

This milestone produces no answer to the comparative research question. The
transparent oracle is also unsuitable for a contamination-resistant public
leaderboard without additional held-out task governance.

### Conditions for revisiting

Advance to `pilot` only after pre-registering model revisions, sampling and
tool settings, condition exposure, repetitions, exclusions, and resource
budgets. Advance to `measured` only when actual run artifacts and aggregation
rules are source-bound and independently auditable.

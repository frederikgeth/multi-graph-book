# Open tranches: federated scientific knowledge and executable guardrails

This issue tracks the work that remains after the initial cross-repository
federated-knowledge tranche. The merged foundation and current execution branch deliver the architecture,
stable PSK links, fourteen executable knowledge slices, minimized negative
fixtures, generated manifests, deterministic federated retrieval, and release
integrity checks. The work below is intentionally follow-up work; it is not a
blocker for merging the initial PRs once CI is green.

The authority for repository ownership and dependency direction is
[`ARCHITECTURE.md`](ARCHITECTURE.md).

## Maintained delivery status (2026-08-30)

| Tranche | State | Delivered boundary | Next open item |
|---|---|---|---|
| 1. Execution interface | Core complete | Two curated contract adapters plus parse/intake, case analysis, supplied-result verification, offline Finding explanation, and a six-tool read-only MCP adapter over the same envelopes | Promote another contract only when its transport mapping and evidence justify it |
| 2. Documentation and recipes | Core complete | Assistant guide, `llms.txt`, two scientific-contract recipes, and tutorial-derived parse, analysis, verification, and Finding-explanation recipes | Keep examples synchronized; solving remains outside this transport slice |
| 3. Negative-knowledge taxonomy | Core complete | Fourteen executable links plus book-only structured negative-result, numerical-pathology, scope-boundary, and open-question records | Add further records only for evidence-backed high-risk questions |
| 4. Property-based testing | Core complete | Seeded terminal-permutation and unit/base serialization suites with deterministic replay, minimization, classification, and federated pins | Add further properties only where an existing contract has a clear generator and oracle |
| 5. Research/decision log | Core complete | Stable `DLOG-*` format, eight seeded decisions, contributor guidance, CI/release validation, and reader/LLM access | Add or supersede entries when consequential choices are made |
| 6. Agent benchmark | Human gate reached | Substrate plus a four-condition, balanced, source-bound pilot design; run schema, exclusions, aggregation, and synthetic dry runs are tested | Human review, exact system/settings freeze, and execution authorization are mandatory before preregistration or real runs |
| 7. Review maturation | Ongoing external dependency | Internal gates and review packet exist | Independent review and claim reclassification |

Update this table and the two detailed status paragraphs below whenever a
milestone lands; completed work should not remain described as open.

## 1. BMOPFTools execution interface

Build the execution-facing complement to the book's existing knowledge MCP.

**Current status (2026-08-30):** core complete. The versioned JSON envelope,
curated API/CLI adapter registry, input hashes, all four scientific statuses,
and request-error separation are implemented for `PSK-000001` and
`PSK-000002`. A separate `analyze-case` API/CLI route now parses one BMOPF JSON
case and returns the complete standard analysis/validation report with status
`completed`; ERROR and WARNING Findings do not masquerade as transport errors.
A separate `verify-solution` route profiles a supplied result without invoking a
solver. Its execution status remains distinct from solver termination and the
independent report's Finding severity. A deterministic `explain-finding` route
looks up all 341 documented package codes in a generated offline registry,
preserving declared links while refusing inferred causes, repairs, PSK links,
and external PowerIO namespaces. A distinct `parse-case` route now reports
decode/migration/normalization evidence and a compact inventory without running
validation. Its deliberately incomplete recipe input proves that parse
completion can coexist with `E.SCHEMA.REQUIRED`. A read-only stdio MCP adapter
now exposes exactly these six settled operations, plus the executable manifest
and response schema as resources. It reuses the existing execution envelopes,
constrains local file access to declared roots, and does not add scientific
retrieval, solver invocation, or arbitrary Julia evaluation. The recipe source
hashes bind both CLI and MCP transport implementations.

Scope:

- stable JSON output for selected parse, validation, analysis, solution,
  contract, counterexample, and Finding-explanation operations;
- a small, documented CLI surface;
- a thin MCP adapter that follows the standard tool/resource protocol and can
  run alongside PowerMCP servers;
- no runtime dependency on the book and no exposure of every Julia function.

Acceptance criteria:

- the adapter is a thin wrapper around stable BMOPFTools APIs;
- outputs include contract/Finding/PSK identifiers and applicability status;
- local tests cover successful, inapplicable, indeterminate, and failing cases;
- a pinned pair can be exercised without reading the sibling repository's
  working tree dynamically.

## 2. BMOPFTools agent-facing documentation and recipes

Turn the existing pedagogical tutorials into a small, CI-tested recipe library.

**Current status (2026-08-30):** core complete. `llms.txt`, the assistant guide,
and CI-tested `parallel_member_limits`, `neutral_ground_reference`, and
`analyze_case` recipes are implemented. The grounding recipe complements the
pedagogical grounding tutorial; the analysis recipe reuses the small tutorial
network and makes the triage misconception explicit: completed analysis is not
a clean or solver-ready case. The `verify_solution` recipe reuses the
trust-but-verify tutorial's independent profiling pattern and a minimized
claimed-feasible counterexample: `LOCALLY_SOLVED` is not evidence that voltage
limits hold. The `explain_finding` recipe distinguishes a canonical code
meaning from one observed instance and does not diagnose a root cause or invent
a repair. The `parse_case` recipe makes the intake/validation boundary
executable with no invented PSK identity. The core recipe set is complete for
the current transport slice; solving remains explicitly outside it.

Scope:

- canonical examples for parsing, validation, analysis, solving, verification,
  Finding explanation, and negative-case reproduction;
- explicit misconception callouts and links to the relevant PSK records;
- machine-facing entry points such as `llms.txt` or an equivalent documented
  manifest for BMOPFTools;
- examples that remain usable without the book being installed.

Acceptance criteria:

- recipes are short, composable, and executable in CI;
- each high-risk recipe states assumptions and expected guardrails;
- documentation distinguishes software behavior, numerical evidence, and
  scientific claims.

## 3. Broaden the negative-knowledge taxonomy

The PSK schema supports `misconception`, `antipattern`, `counterexample`,
`negative-result`, `failure-mode`, `invalid-inference`, `numerical-pathology`,
`software-antipattern`, `scope-boundary`, and `open-question`. The initial
records currently emphasize modelling antipatterns and invalid inferences.

**Current status (2026-08-30):** core complete. `PSK-000015` records the
archived compact-neural-retrieval and generic-reranking experiment as a
reproducible `negative-result`. The subtype requires the full negative-result
quality fields, is routed through a three-audience misconception contract, and
is exposed explicitly in context packets. Its execution relationship is
`not_applicable`: the result belongs to the book's retrieval evaluation and no
BMOPFTools contract, Finding, or fixture is invented. `PSK-000016` adds the
first `numerical-pathology`: the independently reproduced load-continuation
iteration boundary is separated from unproven infeasibility, saddle-node, and
load-model-ranking conclusions. It is likewise book-owned and routed through
three audience contracts. `PSK-000017` adds the first `scope-boundary`, making
the exact scalar coupled-corridor lattice domain and its unestablished physical
and decision extensions separately retrievable through the existing
mutual-coupling audience cases. `PSK-000018` adds the first structured
`open-question`: the source construction behind the Australian `CS1035`
reference matrix remains unresolved after the recorded frequency discriminator,
and three new audience routes preserve the known evidence, missing provenance,
and resolution criteria without relabelling the separate UGHV fixture. The four
targeted structured classes are now exercised end to end; further taxonomy
growth is evidence-driven rather than quota-driven.

Scope:

- add high-value records for negative results, numerical pathologies, scope
  boundaries, and unresolved questions;
- preserve existing misconception IDs while migrating them into the shared
  taxonomy;
- require question, setup, failure criterion, evidence, scope, and
  “does-not-establish” statements for negative results;
- add BMOPFTools-specific records only where the executable evidence supports
  them, without duplicating book prose.

Acceptance criteria:

- every new record has a stable PSK ID, evidence status, source anchors, and
  explicit scope;
- fixture-level evidence is not promoted to a theorem;
- generated corpus and federated manifests remain reproducible.

## 4. Property-based testing and the counterexample factory

Generalize the current deterministic metamorphic tests into a controlled
property-based mechanism.

**Current status (2026-08-30):** core complete. The first controlled suite is
implemented for `PSK-000012` and BMOPFTools'
`terminal_permutation_invariance` contract. A committed SplitMix64 seed record
defines 64 reciprocal, strictly diagonally dominant complex series matrices
with one through six conductors and explicit bijections. Exact coordinate
actions must pass; a deliberate matrix corruption must fail with
`E.CONTRACT.PERMUTATION_RELATION_MISMATCH`; and the failure is projected to a
one-conductor witness and rechecked. Two executions must produce identical
summaries. The executable export and federated pair pin the generator domain,
algorithm, seed, case count, expected code, minimizer, failure classification,
and source hash. These are classified as expected contract rejections, not new
scientific counterexamples.

The second suite now exercises `PSK-000014` over 64 positive finite SI base
maps. It performs JSON encode/decode round trips with reordered map keys, then
independently mutates the unit system, one base value, and the semantic hash.
All 192 injected failures must produce their distinct stable Finding codes and
all minimize to one-base witnesses; a second execution must reproduce the same
summary. Its metadata explicitly refuses the inference that a declaration-only
pass computes physical SI-to-per-unit equivalence or authenticates the hash.
Together the two suites establish the initial generator, replay, oracle,
minimization, classification, export, and federation mechanism. Additional
properties are evidence-driven extensions rather than prerequisites for this
core tranche.

Candidate properties include consistent bus/conductor relabelling, unit/base
conversion, serialization round-trips, valid fixed-linear equivalence, and
recovery of source quantities.

When a property fails, the workflow should be:

```text
failure -> reproduce -> minimize -> classify -> regression test or knowledge record
```

Acceptance criteria:

- generated cases remain inside declared physical/model domains;
- failures are reproducible from recorded seeds and metadata;
- minimized failures become fixtures when scientifically meaningful;
- software defects and genuine scientific boundary cases are classified
  separately.

## 5. Research and decision log

Core mechanism complete. The reader-facing
[`development-decision-log.md`](docs/src/literature/development-decision-log.md)
defines stable `DLOG-*` entries and is indexed by the existing documentation
and deterministic LLM corpus. Six seed entries preserve the principal choices
and rejected approaches already exercised by this initiative: repository
authority, deterministic retrieval, curated execution adapters, property-suite
evidence classification, the archived neural candidate, and asymmetric
book-only negative knowledge.

Each entry should record:

- question;
- options considered;
- decision;
- reason;
- evidence;
- known downside;
- conditions for revisiting the decision.

`scripts/check_development_log.py` checks stable ordering, metadata, required
sections, and the boundary from the claims ledger in documentation CI and the
release-candidate gate. Contributor guidance requires rejected entries to be
retained and superseded decisions to link their replacement. This log is for
software and architecture decisions. Scientific claims remain in the book's
claims ledger.

## 6. Scientifically constrained agent benchmark

First transparent substrate delivered. `ABENCH-PARALLEL-LIMITS-001` uses the
settled `PSK-000001` vertical slice to test two distinct outcomes: rejecting a
summed-rating outer relaxation and abstaining when the scalar contract is
generalized to an unspecified multiconductor, shunted model. The canonical
specification, task and submission schemas, scorer, source-bound manifest, and
reader-facing protocol are committed under `benchmarks/agent/`, `schemas/`,
and [`agent-benchmark.md`](docs/src/literature/agent-benchmark.md).

Seven cumulative conditions preserve the planned comparison ladder:

Compare progressively richer conditions, such as:

```text
LLM alone
+ repository documentation
+ machine-readable scientific knowledge
+ execution tools
+ workflow guidance
+ executable contracts
+ negative-knowledge retrieval
```

Measure code, schema, model-semantic, physical, numerical, scientific-inference,
reproducibility, invalid-assumption detection, and abstention performance.

The first slice scores eight of these dimensions and explicitly marks
`code_correctness` unscored because it is a structured review task rather than
an isolated patch task. Three synthetic submissions test the scorer: one
conforming response passes, while an unsafe approval and an out-of-domain
overclaim fail. Their generated report is labelled
`harness_conformance_only_not_agent_results`; it does not compare models or
conditions.

The benchmark must preserve the deterministic retrieval baseline and report
qualification/counterexample recall, not only top-k retrieval scores.

The controlled-pilot design is now committed. It freezes
`C0_MODEL_ONLY`, `C1_REPOSITORY_DOCS`, `C5_EXECUTABLE_CONTRACTS`, and
`C6_NEGATIVE_KNOWLEDGE`; four balanced repetitions per selected system; case
and condition order; exact source-hash-bound resource bundles; read-only tool,
time, and output budgets; capture requirements; pre-score exclusions; and
dimension-level aggregation without imputation or a top-line accuracy number.
The run-record schema and three synthetic dry runs exercise an eligible pass,
an eligible unsafe response, and a retained pre-response exclusion. They are
harness tests, not agent observations.

The tranche has reached its mandatory human gate. A reviewer must now approve
the task and resource exposure, select each provider and exact model revision,
freeze provider-specific sampling and reasoning settings, authorize cost and
data handling, and decide whether the transparent tasks require a held-out
counterpart. Until then, the design remains
`design_complete_execution_not_authorized`: it is not pre-registered, no real
model may be run, and no condition effect may be claimed.

## 7. Review and evidence maturation

These items are release-quality follow-ups rather than implementation blockers:

- obtain independent review and populate reviewer fields;
- cite or reclassify the remaining uncited `established_result` claims;
- rerun the neural retrieval benchmark against the current corpus;
- retain the archived negative result and its compatibility metadata;
- document that the current release is internally validated, not externally
  reviewed.

## Suggested order

1. Complete the mandatory human review gate, then freeze and pre-register the
   controlled agent-benchmark pilot before running it; continue promoting
   executable contracts or properties only when their mappings and evidence
   are unambiguous.
2. External review and evidence maturation in parallel as reviewers become
   available.

Each tranche should add tests, generated artifacts, and explicit scope rather
than silently expanding the scientific claims of either repository.

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
| 1. Execution interface | In progress | Two curated contract adapters plus parse/intake, case analysis, supplied-result verification, and offline Finding explanation with distinct execution/solver/Finding/contract statuses | Add only a thin MCP/PowerMCP adapter over the settled operations |
| 2. Documentation and recipes | Core complete | Assistant guide, `llms.txt`, two scientific-contract recipes, and tutorial-derived parse, analysis, verification, and Finding-explanation recipes | Keep examples synchronized; solving remains outside this transport slice |
| 3. Negative-knowledge taxonomy | Queued | Initial PSK taxonomy and fourteen executable links | Select and scope the first new non-modelling record |
| 4. Property-based testing | Queued | Deterministic metamorphic tests and minimized fixtures | Define the generator domain and seed record |
| 5. Research/decision log | Queued | Decisions currently recorded in architecture and handover prose | Add the lightweight decision-log format |
| 6. Agent benchmark | Deferred | Deterministic retrieval evaluation exists | Start after the execution surface stabilizes |
| 7. Review maturation | Ongoing external dependency | Internal gates and review packet exist | Independent review and claim reclassification |

Update this table and the two detailed status paragraphs below whenever a
milestone lands; completed work should not remain described as open.

## 1. BMOPFTools execution interface

Build the execution-facing complement to the book's existing knowledge MCP.

**Current status (2026-08-30):** in progress. The versioned JSON envelope,
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
completion can coexist with `E.SCHEMA.REQUIRED`. The optional thin
MCP/PowerMCP adapter remains open.

Scope:

- stable JSON output for selected parse, validation, analysis, solution,
  contract, counterexample, and Finding-explanation operations;
- a small, documented CLI surface;
- an optional thin MCP or PowerMCP-compatible adapter;
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

Create a lightweight development research log for architectural choices and
rejected approaches.

Each entry should record:

- question;
- options considered;
- decision;
- evidence;
- known downside;
- conditions for revisiting the decision.

This log is for software and architecture decisions. Scientific claims remain
in the book's claims ledger.

## 6. Scientifically constrained agent benchmark

After the execution and retrieval surfaces stabilize, evaluate whether explicit
positive and negative domain knowledge improves coding-agent reliability.

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

The benchmark must preserve the deterministic retrieval baseline and report
qualification/counterexample recall, not only top-k retrieval scores.

## 7. Review and evidence maturation

These items are release-quality follow-ups rather than implementation blockers:

- obtain independent review and populate reviewer fields;
- cite or reclassify the remaining uncited `established_result` claims;
- rerun the neural retrieval benchmark against the current corpus;
- retain the archived negative result and its compatibility metadata;
- document that the current release is internally validated, not externally
  reviewed.

## Suggested order

1. Thin MCP/PowerMCP adapter over the now-settled execution interface; continue
   promoting contracts only when their transport mappings are unambiguous.
2. Broader negative-knowledge records.
3. Property-based testing and minimized counterexamples.
4. Research/decision log.
5. Agent benchmark.
6. External review and evidence maturation in parallel as reviewers become
   available.

Each tranche should add tests, generated artifacts, and explicit scope rather
than silently expanding the scientific claims of either repository.

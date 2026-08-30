# Scientifically constrained agent benchmark

This directory contains the controlled benchmark substrate described in the
roadmap. The first slice is `ABENCH-PARALLEL-LIMITS-001`, a transparent pair of
parallel-line review tasks linked to `PSK-000001` and BMOPFTools' existing
`parallel_member_limit_preservation` contract.

It is intentionally **not** an agent result. The committed submissions are
conformance fixtures for the scorer: one correct response and two deliberately
unsafe responses. They prove that the harness distinguishes an approved
scientific response from an invalid assumption and an out-of-domain overclaim;
they do not measure a model or compare conditions.

Generate or check the source-bound benchmark manifest with the usual sibling
checkout:

```sh
python3 scripts/check_agent_benchmark.py --write --bmopf-root ../BMOPFTools.jl
python3 scripts/check_agent_benchmark.py --check --bmopf-root ../BMOPFTools.jl
```

`--write` also repins the deterministic passing conformance fixture to the
current corpus and pair identity. It refuses to rewrite a non-fixture system.
Measured submissions are never part of this regeneration path.

The check without `--bmopf-root` remains repository-local and verifies the
recorded BMOPFTools hashes against the pinned federated export. A live sibling
check additionally hashes every referenced package source.

Score a structured submission without changing the committed conformance
report:

```sh
python3 scripts/check_agent_benchmark.py \
  --score benchmarks/agent/submissions/conforming-c6.json
```

The condition bundles are cumulative. An experimental run must record the
exact condition, model and revision, run identifier, and pinned book/package
provenance. Runs under different conditions should otherwise use the same
prompt, task ordering, runtime limits, and scoring version.

## Controlled pilot package

`pilot/parallel-member-limits-pilot-v1.json` freezes the parts of the first
pilot that do not depend on a provider decision: the four initial conditions,
four balanced repetitions, case ordering, exact resource bundles, read-only
tool policy, budgets, capture requirements, exclusions, and aggregation. The
pilot and run-record JSON schemas are checked by
`scripts/check_agent_benchmark_pilot.py`.

The pilot status is deliberately
`design_complete_execution_not_authorized`. Provider, exact model revision,
execution interface, and provider-specific sampling settings remain empty.
Human review is mandatory before those fields are frozen, the record is called
pre-registered, or any hosted model is run.

The three records under `pilot/dry-runs/` exercise successful scoring, an
unsafe response, and a pre-response exclusion. They reuse deterministic
fixtures and are aggregated as
`synthetic_dry_run_harness_only_not_agent_results`; they are not observations
from an agent.

With the usual sibling checkout, regenerate or check the design artifacts:

```sh
python3 scripts/check_agent_benchmark_pilot.py --write \
  --bmopf-root ../BMOPFTools.jl
python3 scripts/check_agent_benchmark_pilot.py --check
```

The pilot writer likewise refreshes only the submission hashes in records
explicitly labelled `synthetic_dry_run`; it refuses measured records.

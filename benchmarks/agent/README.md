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

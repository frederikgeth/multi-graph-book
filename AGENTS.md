# Repository guidance for coding agents

Read `ARCHITECTURE.md` before changing scientific knowledge, retrieval, or cross-repository links. This repository owns scientific statements, scope, evidence status, misconceptions, counterexamples, and stable `PSK-*` identities. `BMOPFTools.jl` owns executable package behavior, APIs, Findings, fixtures, and implementation applicability.

Preserve the existing LLM machinery. Extend the deterministic corpus, context packets, MCP/HTTP/CLI service, `unsupported`/`under_retrieved` semantics, source-hash binding, and retrieval evaluations. Do not introduce a parallel generic embeddings/RAG stack as the authority.

When changing a PSK record:

1. Keep its scientific content in `knowledge/psk.toml` and its schema in `schemas/power-system-knowledge.schema.json`.
2. Use stable IDs; do not renumber an existing `PSK-*` record.
3. Mark executable work `implemented` only when the linked BMOPFTools export exists and the live pair check passes.
4. Regenerate scientific knowledge, the LLM corpus, evaluations/fixtures when stale, and the federated pair manifest when either side changes.
5. Never copy BMOPFTools implementation prose into the PSK registry; link by contract, Finding, and fixture IDs.

Primary gates:

```bash
python3 scripts/generate_scientific_knowledge.py --check
python3 scripts/check_federated_knowledge.py --check
python3 scripts/check_federated_knowledge.py --check --bmopf-root ../BMOPFTools.jl
python3 scripts/check_llm_reproducibility.py
```

To repin a deliberately changed executable export:

```bash
python3 scripts/check_federated_knowledge.py --write --bmopf-root ../BMOPFTools.jl
```

Review the generated diff and both source repositories before committing the new pair identity.

When changing `benchmarks/agent/`, keep substrate, conformance-fixture, pilot,
and measured-run evidence states distinct. Synthetic scorer fixtures are not
agent results. Validate the benchmark locally and, when package-owned oracles
are referenced, against the sibling BMOPFTools checkout; do not copy package
contract semantics into book-owned scoring code.

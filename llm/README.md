# LLM-accessibility layer

This directory contains the curated inputs and generated records used to make
the book retrievable by language-model applications. It is not a second copy of
the book and it is not an authority independent of the Markdown chapters,
claims ledger, vocabulary registry, evidence artifacts, or release manifest.

The design separates three concerns:

1. `misconceptions.toml` records questions for which a tempting short answer
   omits a load-bearing qualification.
2. `evaluation-cases.toml` records audience-specific regression questions and
   the evidence that a grounded answer must retrieve.
3. `generated/corpus.jsonl` contains deterministic section, claim, and concept
   records produced from canonical repository sources. Its companion manifest
   binds those records to source hashes and the internal release candidate.

Run:

```sh
python3 scripts/generate_llm_corpus.py --write
python3 scripts/check_llm_accessibility.py
python3 scripts/evaluate_llm_retrieval.py --write
```

The generated corpus is deliberately model- and database-independent. A later
search service may build lexical, embedding, reranking, or graph indexes from
it, but those indexes must retain the corpus manifest identifier and may not
silently change the scientific content.

The corpus manifest records the document-selection rule. Four generated
navigation pages (`chapter-status`, `evidence-map`, `knowledge-base-index`, and
`vocabulary-indexes`) are excluded because they duplicate canonical ledgers and
would dominate retrieval without adding independent scientific evidence. Their
upstream chapters, claims, and vocabulary sources remain bound by hash.

## Answer contract

Applications using this corpus should construct an answer from these fields
before rendering it into audience-specific prose:

1. direct answer supported by the book;
2. named representation, model, state, study, and exactness object;
3. assumptions and load-bearing qualification;
4. relevant counterexample or failure consequence;
5. audience-language translation without semantic drift;
6. supporting claim IDs, source anchors, and evidence status;
7. unresolved or unreviewed boundary.

If the book does not support an answer, applications should abstain or label
external information separately. Model memory is not book evidence.

## Search and context packets

The current baseline is deliberately local and model-independent. It uses BM25
lexical ranking, character n-gram TF-IDF, rank-fused hybrid retrieval,
controlled-vocabulary expansion, and curated misconception routing. Search the
corpus with:

```sh
python3 scripts/search_llm_corpus.py "Do loads belong in Ybus?"
```

Build a structured packet for an answer renderer with:

```sh
python3 scripts/search_llm_corpus.py \
  "Can parallel circuits use one total MVA rating?" \
  --audience power_engineer --context-packet --json
```

Fuzzy misconception matches also apply topic gates on easily confused routes.
A shared word such as `terminal`, `impedance`, or `KCL` does not by itself
establish that a permutation, construction-provenance, or solver-status contract
answers the question. A complete curated query phrase can still route directly.
These gates reduce known false qualifications; they do not prove semantic
coverage of arbitrary or multi-intent questions. Related material without a
responsive contract remains `under_retrieved`.

For example, DELTA coil-count or voltage-map questions do not establish nominal
voltage-base intent. That route requires a base/anchor/normalization marker or
the phrase "nominal voltage"; "at the nominal operating point" is insufficient.
The neighboring graph-membership and iteration-failure routes also require
their own topic evidence, so suppressing one false match cannot simply expose
those unrelated fallbacks. The October 26 R1 question and adjacent cases are
now known regressions, not blind evaluation evidence.

The adversarial evaluation includes near-domain negative questions and reports
false qualification separately from retrieval recall. Questions without target
evidence are excluded from recall averages, rather than counted as perfect
retrieval. Both evaluation reports bind the router source hash. A response's
`validation.valid` flag checks packet structure, source identity and required
claim/citation inclusion; it is not independent scientific answer validation.

The packet keeps evidence classes separate. `counterexamples` names concrete
delimiting cases, `negative_results` preserves failed experiments with their
criteria and scope, `numerical_pathologies` records observed algorithmic
behavior plus the checks needed before drawing a physical conclusion, and
`scope_boundaries` separates established domains from unproven extensions.
`open_questions` preserves known evidence, attempted discriminators, missing
information, and explicit resolution criteria without presenting an unknown as
an unsupported topic or a negative result.
Book-only records leave `executable_checks` empty rather than inventing a
BMOPFTools counterpart.

The generated `retrieval-evaluation.md` report keeps raw lexical recall
separate from surface-semantic and contract-expanded recall. Contract expansion may add evidence
mandated by a detected dangerous-shortcut contract; it must never be reported
as if the ordinary ranker retrieved that evidence unaided.

The report also includes a benchmark-only provenance-graph traversal. It links
records through shared canonical sources and misconception identities. On the
current synthetic held-out set it improves recall@10 over hybrid, but it remains
an explicit diagnostic/opt-in method rather than the default production ranker.

The held-out benchmark is synthetic and not human-validated evidence. Multiple
audience phrasings share target evidence sets. The generated report derives
the current question and target-cluster counts directly from its input;
question count is not a count of independent scientific observations.
The report therefore includes counts, zero-recall cases, cluster structure, and
contract-router firing coverage alongside percentages.
The current router-firing release floor is 2/3: a provisional regression floor
chosen so that the three-audience structure requires coverage of at least two
audience phrasings on average. It is not evidence of robust generalization.

## Optional neural benchmark

Neural retrieval is an opt-in comparison layer, not a bundled scientific
dependency. The adapter requires an immutable model revision and records the
model ID, revision, artifact hash, embedding dimension, runtime version, and
normalization policy. A remote model therefore also needs an externally
recorded artifact/cache SHA-256; a local model directory is hashed directly.

After installing the separately managed `sentence-transformers` environment,
run a comparison such as:

```sh
python3 scripts/benchmark_llm_embeddings.py \
  --model-id <model-id> \
  --revision <immutable-revision> \
  --artifact-sha256 <model-artifact-sha256> \
  --output /tmp/neural-retrieval.json
```

The benchmark compares lexical, character-TF-IDF, hybrid, and neural retrieval
on the held-out paraphrase set. It is a retrieval comparison only: it does not
establish answer faithfulness, citation correctness, or human-calibrated
audience translation. Neural output must retain the corpus release identity and
its embedding provenance before it can be used by a production answer route.

The current pinned experiment is retained in
`generated/neural-retrieval-evaluation.*` and records a negative result: the
compact neural retriever and generic cross-encoder reranker do not beat the
hybrid baseline on this corpus. The hybrid baseline therefore remains the
production candidate. Run `python3 scripts/check_neural_benchmark.py` to verify
that the recorded result still matches the current corpus and baseline report.
When canonical content changes without re-running those external models, the
record is retained as an explicitly archived prior-corpus result and names the
current corpus hash plus the required rerun. The gate must never copy current
lexical scores into an old neural run or present stale neural rankings as a
current comparison. The archive marker can be refreshed with
`python3 scripts/check_neural_benchmark.py --archive-current-drift`; promotion
still requires a genuine model rerun.

## Stable access routes

All supported routes call the same deterministic service and expose the corpus
release identity. The response is an answer packet, not an uncited generated
essay: it contains the supported answer basis, scope, qualifications, failure
consequences, stable sources, and an explicit `unsupported` status when the
lexical abstention floor finds no book support.
When related material is retrieved but no qualified claim contract is found,
the packet uses the distinct `under_retrieved` status and warning so a downstream
model cannot mistake relevance for a supported answer.

Run the local HTTP/JSON service with:

```sh
python3 scripts/serve_llm_access.py --port 8787
```

The stable routes are `GET /healthz`, `GET /v1/manifest`,
`GET|POST /v1/context`, and `GET /v1/search`. Add `format=markdown` to context
or search requests when a Markdown rendering is preferred. The same service is
available to local MCP clients through the newline-delimited JSON-RPC adapter:

```sh
python3 scripts/mcp_llm_server.py
```

It exposes `book_context`, `book_search`, and the corpus manifest resource over
MCP stdio. The book adapter supports modern `2026-07-28` requests and the legacy
`2025-11-25` / `2025-06-18` initialization flow. The ordinary HTTP/JSON routes
above are not an MCP HTTP transport.

Modern requests carry `io.modelcontextprotocol/protocolVersion` and
`io.modelcontextprotocol/clientCapabilities` in `params._meta`, including when
calling `server/discover`. Each request supplies its own metadata. Discovery
returns supported versions, capabilities and server identity; ordinary results
include `resultType: "complete"`. Discovery, tool/resource lists and resource
reads include conservative cache hints (`ttlMs: 0`, `cacheScope: "private"`).
Unknown modern versions return error `-32022` with the requested and supported
versions. Legacy clients continue to use `initialize` and receive legacy result
shapes; an initialization request does not select the modern protocol.

These mappings follow the official
[versioning rules](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning),
[stdio binding](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)
and [result schemas](https://modelcontextprotocol.io/specification/2026-07-28/schema).
Run `python3 scripts/test_mcp_protocol.py` for argument, notification, discovery,
version-mismatch and mixed-client subprocess regressions. The server advertises
no subscriptions, prompt service, sampling, or task extension. Both eras use the
same deterministic service; transport success does not turn `under_retrieved`
or `unsupported` into `qualified` scientific evidence.

The manifest resource, search results and context packets carry `source_identity`:
book corpus/manifest hashes, federated pair hash, and pinned BMOPFTools revision
and export hashes. These describe the reviewed export, not an inspected package
runtime. The separately pinned BMOPFTools execution MCP still implements the
legacy protocol. Its upgrade must be tested in the package and deliberately
repinned through the [integration environment](../experiments/integration/README.md).
The `graph` retrieval method is available only as an explicit diagnostic option;
the default remains hybrid.

# Neural LLM retrieval benchmark

**Status:** `fail`
**Corpus:** `multi-graph-book-mgb-2026-08-17-internal-rc`
**Model:** `sentence-transformers/all-MiniLM-L6-v2` at revision `ea78891063587eb050ed4166b20062eaf978037c`
**Embedding artifact hash:** `507dfbc0b17cb6138f2a9f9e0894df3198cab2bebb23fc46759021e6ee458d02`
**Current-corpus compatibility:** `archived_prior_corpus`
**Archived on:** `2026-08-30`
**Current corpus hash:** `19039725fc0807448d6ff451c5bd0191b01e78e7ddecb1c2c84a36f56f5398d9`
**Current held-out input hash:** `171857dd883acf3ed9a091fac0e2e7485cbd13d5f0477a56af37d010cec16592`
**Required action:** rerun both pinned neural retriever and reranker before comparing them with the current corpus
**Current lexical baseline:** lexical recall@10=44.9%; char_tfidf recall@10=43.9%; hybrid recall@10=46.6%

This report is an opt-in comparison. It does not promote neural retrieval into the release path
or prove answer faithfulness; it measures only held-out evidence-record retrieval.

| Method | Recall@5 | Recall@10 | Complete@10 | MRR@20 |
| --- | ---: | ---: | ---: | ---: |
| `lexical` | 36.0% | 44.0% | 0.0% | 0.206 |
| `char_tfidf` | 35.9% | 44.2% | 3.7% | 0.214 |
| `hybrid` | 40.6% | 45.4% | 3.7% | 0.219 |
| `neural` | 30.9% | 43.4% | 0.0% | 0.207 |
| `hybrid_reranked` | 32.7% | 44.1% | 0.0% | 0.225 |

Neural minus hybrid recall@10: **-2.0%**.
Neural minus hybrid complete@10: **-3.7%**.
**Reranker:** `cross-encoder/ms-marco-MiniLM-L6-v2` at revision `c5ee24cb16019beea0893ab7796b1df96625c6b8`.
**Reranker artifact hash:** `d5d6c60ab5d3e953626f0839cad9292482a5970deeea2551d3223b2f984cee92`.
Hybrid-reranked minus hybrid recall@10: **-1.2%**.
Hybrid-reranked minus hybrid complete@10: **-3.7%**.

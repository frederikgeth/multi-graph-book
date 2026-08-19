# LLM retrieval evaluation

**Generated report:** deterministic evaluation of the committed corpus and question contracts.

**Status:** `pass`<br>
**Corpus:** `multi-graph-book-mgb-2026-08-17-internal-rc`<br>
**Corpus hash:** `16a07c88d0da4d9df30096a181e0537a4072d3e5fa015a21317dd38e08a5a141`<br>
**Cases:** 30

This report separates ordinary lexical ranking from qualification-aware contract expansion.
The latter is permitted to add mandatory claims and concepts only after the query router identifies
a curated dangerous-shortcut contract. The character n-gram path is a reproducible surface-semantic proxy; neural embeddings are not bundled in this baseline. Graph traversal is diagnostic only and is not enabled by the production service.

## Summary

| Measure | Result | Release gate? |
| --- | ---: | --- |
| Misconception top-1 routing accuracy | 100.0% | yes |
| Open-corpus lexical evidence recall@5 | 30.0% | diagnostic |
| Open-corpus lexical evidence recall@10 | 39.6% | diagnostic |
| Open-corpus complete evidence@10 | 0.0% | diagnostic |
| Evidence-only lexical recall@5 | 40.2% | diagnostic |
| Evidence-only lexical recall@10 | 53.1% | diagnostic |
| Evidence-only complete evidence@10 | 3.3% | diagnostic |
| Contract-expanded mandatory-record recall | 100.0% | yes |
| Complete contract packets | 100.0% | yes |
| Packets with qualification, failure, shorthand, and scope | 100.0% | yes |
| Corpus-release identity agreement | 100.0% | yes |
| Held-out contract-router firing | 22/30 (73.3%) | yes |
| Held-out expected-contract top-1 | 17/30 (56.7%) | diagnostic |
| Held-out hybrid zero-recall@10 cases | 5/30 | diagnostic |

The diagnostic lexical scores are intentionally not release thresholds. A perfect contract score
cannot be reported as a better ranker score: it measures whether an identified high-risk question
received all evidence mandated by the curated contract.

## Held-out paraphrase benchmark

These questions are not used by the contract router during corpus construction. They test ordinary
retrieval and routing generalization against synthetic paraphrases across the three audiences.
They are not human-validated evidence: 27 cases are three audience phrasings for nine target
evidence sets, so the effective target count is nine rather than 27 independent questions.

| Method | Recall@5 | Recall@10 | Complete@10 | Complete cases | Zero-recall cases | MRR@20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lexical` | 36.5% | 44.7% | 0.0% | 0/30 | 5/30 | 0.207 |
| `char_tfidf` | 34.4% | 44.5% | 0.0% | 0/30 | 5/30 | 0.209 |
| `hybrid` | 39.4% | 45.9% | 0.0% | 0/30 | 5/30 | 0.221 |
| `graph` | 37.1% | 52.2% | 30.0% | 9/30 | 5/30 | 0.243 |

Held-out contract-router firing: **22/30 (73.3%)**; release floor: **66.7%**.
Expected-contract top-1 agreement: **17/30 (56.7%)**; this remains diagnostic because the set is synthetic and clustered.
Target clusters: **10**, with cluster sizes `[3, 3, 3, 3, 3, 3, 3, 3, 3, 3]`; percentage differences are therefore not independent observations.
Hybrid versus lexical complete@10: **0/30** versus **0/30**; hybrid zero-recall@10: **5/30**.
Graph versus hybrid complete@10: **9/30** versus **0/30**.

| Held-out case | Audience | Expected route | Observed top-1 | Router fired | Lexical complete@10 | TF-IDF complete@10 | Hybrid complete@10 | Graph complete@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HOLDOUT-GRAPH-STUDENT` | `student` | `one-universal-network-graph` | `one-universal-network-graph` | yes | no | no | no | yes |
| `HOLDOUT-GRAPH-SOFTWARE` | `software_engineer` | `one-universal-network-graph` | `none` | no | no | no | no | yes |
| `HOLDOUT-GRAPH-POWER` | `power_engineer` | `one-universal-network-graph` | `radial-is-representation-independent` | yes | no | no | no | no |
| `HOLDOUT-YSPLIT-STUDENT` | `student` | `loads-generators-fixed-graph-membership` | `loads-generators-fixed-graph-membership` | yes | no | no | no | yes |
| `HOLDOUT-YSPLIT-SOFTWARE` | `software_engineer` | `loads-generators-fixed-graph-membership` | `loads-generators-fixed-graph-membership` | yes | no | no | no | no |
| `HOLDOUT-YSPLIT-POWER` | `power_engineer` | `loads-generators-fixed-graph-membership` | `loads-generators-fixed-graph-membership` | yes | no | no | no | yes |
| `HOLDOUT-YBUS-STUDENT` | `student` | `nodal-operator-is-source-network` | `none` | no | no | no | no | yes |
| `HOLDOUT-YBUS-SOFTWARE` | `software_engineer` | `nodal-operator-is-source-network` | `none` | no | no | no | no | no |
| `HOLDOUT-YBUS-POWER` | `power_engineer` | `nodal-operator-is-source-network` | `none` | no | no | no | no | no |
| `HOLDOUT-PARALLEL-STUDENT` | `student` | `parallel-admittance-implies-decision-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |
| `HOLDOUT-PARALLEL-SOFTWARE` | `software_engineer` | `parallel-admittance-implies-decision-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |
| `HOLDOUT-PARALLEL-POWER` | `power_engineer` | `parallel-admittance-implies-decision-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |
| `HOLDOUT-RADIAL-STUDENT` | `student` | `radial-is-representation-independent` | `none` | no | no | no | no | no |
| `HOLDOUT-RADIAL-SOFTWARE` | `software_engineer` | `radial-is-representation-independent` | `radial-is-representation-independent` | yes | no | no | no | no |
| `HOLDOUT-RADIAL-POWER` | `power_engineer` | `radial-is-representation-independent` | `radial-is-representation-independent` | yes | no | no | no | no |
| `HOLDOUT-KRON-STUDENT` | `student` | `kron-reduction-preserves-everything` | `kron-reduction-preserves-everything` | yes | no | no | no | no |
| `HOLDOUT-KRON-SOFTWARE` | `software_engineer` | `kron-reduction-preserves-everything` | `kron-reduction-preserves-everything` | yes | no | no | no | no |
| `HOLDOUT-KRON-POWER` | `power_engineer` | `kron-reduction-preserves-everything` | `kron-reduction-preserves-everything` | yes | no | no | no | no |
| `HOLDOUT-SEQUENCE-STUDENT` | `student` | `transposition-implies-positive-sequence-exactness` | `none` | no | no | no | no | no |
| `HOLDOUT-SEQUENCE-SOFTWARE` | `software_engineer` | `transposition-implies-positive-sequence-exactness` | `none` | no | no | no | no | yes |
| `HOLDOUT-SEQUENCE-POWER` | `power_engineer` | `transposition-implies-positive-sequence-exactness` | `none` | no | no | no | no | yes |
| `HOLDOUT-GROUND-STUDENT` | `student` | `ground-neutral-reference-are-one-node` | `ground-neutral-reference-are-one-node` | yes | no | no | no | no |
| `HOLDOUT-GROUND-SOFTWARE` | `software_engineer` | `ground-neutral-reference-are-one-node` | `ground-neutral-reference-are-one-node` | yes | no | no | no | no |
| `HOLDOUT-GROUND-POWER` | `power_engineer` | `ground-neutral-reference-are-one-node` | `ground-neutral-reference-are-one-node` | yes | no | no | no | yes |
| `HOLDOUT-DECISION-STUDENT` | `student` | `terminal-equivalence-implies-opf-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |
| `HOLDOUT-SELF-LOOP-STUDENT` | `student` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | no |
| `HOLDOUT-SELF-LOOP-SOFTWARE` | `software_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | yes |
| `HOLDOUT-SELF-LOOP-POWER` | `power_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | no |
| `HOLDOUT-DECISION-SOFTWARE` | `software_engineer` | `terminal-equivalence-implies-opf-equivalence` | `loads-generators-fixed-graph-membership` | yes | no | no | no | no |
| `HOLDOUT-DECISION-POWER` | `power_engineer` | `terminal-equivalence-implies-opf-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |

## Audience consistency

| Audience | Cases | Route top-1 | Lexical recall@10 | Contract recall |
| --- | ---: | ---: | ---: | ---: |
| `power_engineer` | 10 | 100.0% | 53.3% | 100.0% |
| `software_engineer` | 10 | 100.0% | 45.7% | 100.0% |
| `student` | 10 | 100.0% | 60.4% | 100.0% |

## Case results

| Case | Audience | Route | Evidence-only recall@10 | Contract complete |
| --- | --- | --- | ---: | --- |
| `EVAL-GRAPH-STUDENT` | `student` | `one-universal-network-graph` | 22.2% | yes |
| `EVAL-GRAPH-SOFTWARE` | `software_engineer` | `one-universal-network-graph` | 33.3% | yes |
| `EVAL-GRAPH-POWER` | `power_engineer` | `one-universal-network-graph` | 33.3% | yes |
| `EVAL-YSPLIT-STUDENT` | `student` | `loads-generators-fixed-graph-membership` | 66.7% | yes |
| `EVAL-YSPLIT-SOFTWARE` | `software_engineer` | `loads-generators-fixed-graph-membership` | 66.7% | yes |
| `EVAL-YSPLIT-POWER` | `power_engineer` | `loads-generators-fixed-graph-membership` | 50.0% | yes |
| `EVAL-YBUS-STUDENT` | `student` | `nodal-operator-is-source-network` | 80.0% | yes |
| `EVAL-YBUS-SOFTWARE` | `software_engineer` | `nodal-operator-is-source-network` | 60.0% | yes |
| `EVAL-YBUS-POWER` | `power_engineer` | `nodal-operator-is-source-network` | 20.0% | yes |
| `EVAL-PARALLEL-STUDENT` | `student` | `parallel-admittance-implies-decision-equivalence` | 66.7% | yes |
| `EVAL-PARALLEL-SOFTWARE` | `software_engineer` | `parallel-admittance-implies-decision-equivalence` | 16.7% | yes |
| `EVAL-PARALLEL-POWER` | `power_engineer` | `parallel-admittance-implies-decision-equivalence` | 50.0% | yes |
| `EVAL-RADIAL-STUDENT` | `student` | `radial-is-representation-independent` | 80.0% | yes |
| `EVAL-RADIAL-SOFTWARE` | `software_engineer` | `radial-is-representation-independent` | 60.0% | yes |
| `EVAL-RADIAL-POWER` | `power_engineer` | `radial-is-representation-independent` | 80.0% | yes |
| `EVAL-KRON-STUDENT` | `student` | `kron-reduction-preserves-everything` | 80.0% | yes |
| `EVAL-KRON-SOFTWARE` | `software_engineer` | `kron-reduction-preserves-everything` | 0.0% | yes |
| `EVAL-KRON-POWER` | `power_engineer` | `kron-reduction-preserves-everything` | 40.0% | yes |
| `EVAL-SEQUENCE-STUDENT` | `student` | `transposition-implies-positive-sequence-exactness` | 50.0% | yes |
| `EVAL-SEQUENCE-SOFTWARE` | `software_engineer` | `transposition-implies-positive-sequence-exactness` | 50.0% | yes |
| `EVAL-SEQUENCE-POWER` | `power_engineer` | `transposition-implies-positive-sequence-exactness` | 75.0% | yes |
| `EVAL-GROUND-STUDENT` | `student` | `ground-neutral-reference-are-one-node` | 75.0% | yes |
| `EVAL-GROUND-SOFTWARE` | `software_engineer` | `ground-neutral-reference-are-one-node` | 100.0% | yes |
| `EVAL-GROUND-POWER` | `power_engineer` | `ground-neutral-reference-are-one-node` | 75.0% | yes |
| `EVAL-DECISION-STUDENT` | `student` | `terminal-equivalence-implies-opf-equivalence` | 0.0% | yes |
| `EVAL-DECISION-SOFTWARE` | `software_engineer` | `terminal-equivalence-implies-opf-equivalence` | 20.0% | yes |
| `EVAL-DECISION-POWER` | `power_engineer` | `terminal-equivalence-implies-opf-equivalence` | 60.0% | yes |
| `EVAL-SELF-LOOP-STUDENT` | `student` | `self-loop-is-a-shunt-or-circuit-loop` | 83.3% | yes |
| `EVAL-SELF-LOOP-SOFTWARE` | `software_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | 50.0% | yes |
| `EVAL-SELF-LOOP-POWER` | `power_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | 50.0% | yes |

## Interpretation and next boundary

This baseline proves deterministic corpus search, high-risk query routing, and complete context-packet
assembly for the current curated cases. It does not prove robust paraphrase coverage outside the test
set, answer-generation faithfulness, citation correctness in generated prose, neural embedding retrieval quality,
or human-calibrated audience translation. Those remain separate roadmap gates.

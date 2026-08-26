# LLM retrieval evaluation

**Generated report:** deterministic evaluation of the committed corpus and question contracts.

**Status:** `pass`<br>
**Corpus:** `multi-graph-book-mgb-2026-08-17-internal-rc`<br>
**Corpus hash:** `9493f1e67b665b16772158ca0129850d1b24eb8603b7b0b665bfd2a872057073`<br>
**Cases:** 45

This report separates ordinary lexical ranking from qualification-aware contract expansion.
The latter is permitted to add mandatory claims and concepts only after the query router identifies
a curated dangerous-shortcut contract. The character n-gram path is a reproducible surface-semantic proxy; neural embeddings are not bundled in this baseline. Graph traversal is diagnostic only and is not enabled by the production service.

## Summary

| Measure | Result | Release gate? |
| --- | ---: | --- |
| Misconception top-1 routing accuracy | 100.0% | yes |
| Open-corpus lexical evidence recall@5 | 25.8% | diagnostic |
| Open-corpus lexical evidence recall@10 | 36.7% | diagnostic |
| Open-corpus complete evidence@10 | 0.0% | diagnostic |
| Evidence-only lexical recall@5 | 39.1% | diagnostic |
| Evidence-only lexical recall@10 | 48.9% | diagnostic |
| Evidence-only complete evidence@10 | 2.2% | diagnostic |
| Contract-expanded mandatory-record recall | 100.0% | yes |
| Complete contract packets | 100.0% | yes |
| Packets with qualification, failure, shorthand, and scope | 100.0% | yes |
| Corpus-release identity agreement | 100.0% | yes |
| Held-out contract-router firing | 25/33 (75.8%) | yes |
| Held-out expected-contract top-1 | 19/33 (57.6%) | diagnostic |
| Held-out hybrid zero-recall@10 cases | 5/33 | diagnostic |

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
| `lexical` | 32.7% | 44.9% | 0.0% | 0/33 | 5/33 | 0.201 |
| `char_tfidf` | 36.8% | 44.8% | 0.0% | 0/33 | 6/33 | 0.223 |
| `hybrid` | 37.9% | 46.6% | 0.0% | 0/33 | 5/33 | 0.218 |
| `graph` | 40.6% | 57.6% | 27.3% | 9/33 | 4/33 | 0.258 |

Held-out contract-router firing: **25/33 (75.8%)**; release floor: **66.7%**.
Expected-contract top-1 agreement: **19/33 (57.6%)**; this remains diagnostic because the set is synthetic and clustered.
Target clusters: **11**, with cluster sizes `[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]`; percentage differences are therefore not independent observations.
Hybrid versus lexical complete@10: **0/33** versus **0/33**; hybrid zero-recall@10: **5/33**.
Graph versus hybrid complete@10: **9/33** versus **0/33**.

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
| `HOLDOUT-GROUND-STUDENT` | `student` | `ground-neutral-reference-are-one-node` | `mutual-coupling-is-an-ordinary-parallel-network` | yes | no | no | no | no |
| `HOLDOUT-GROUND-SOFTWARE` | `software_engineer` | `ground-neutral-reference-are-one-node` | `ground-neutral-reference-are-one-node` | yes | no | no | no | no |
| `HOLDOUT-GROUND-POWER` | `power_engineer` | `ground-neutral-reference-are-one-node` | `ground-neutral-reference-are-one-node` | yes | no | no | no | yes |
| `HOLDOUT-DECISION-STUDENT` | `student` | `terminal-equivalence-implies-opf-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |
| `HOLDOUT-COUPLING-STUDENT` | `student` | `mutual-coupling-is-an-ordinary-parallel-network` | `mutual-coupling-is-an-ordinary-parallel-network` | yes | no | no | no | no |
| `HOLDOUT-COUPLING-SOFTWARE` | `software_engineer` | `mutual-coupling-is-an-ordinary-parallel-network` | `mutual-coupling-is-an-ordinary-parallel-network` | yes | no | no | no | no |
| `HOLDOUT-COUPLING-POWER` | `power_engineer` | `mutual-coupling-is-an-ordinary-parallel-network` | `mutual-coupling-is-an-ordinary-parallel-network` | yes | no | no | no | no |
| `HOLDOUT-SELF-LOOP-STUDENT` | `student` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | no |
| `HOLDOUT-SELF-LOOP-SOFTWARE` | `software_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | yes |
| `HOLDOUT-SELF-LOOP-POWER` | `power_engineer` | `self-loop-is-a-shunt-or-circuit-loop` | `self-loop-is-a-shunt-or-circuit-loop` | yes | no | no | no | no |
| `HOLDOUT-DECISION-SOFTWARE` | `software_engineer` | `terminal-equivalence-implies-opf-equivalence` | `loads-generators-fixed-graph-membership` | yes | no | no | no | no |
| `HOLDOUT-DECISION-POWER` | `power_engineer` | `terminal-equivalence-implies-opf-equivalence` | `terminal-equivalence-implies-opf-equivalence` | yes | no | no | no | no |

## Audience consistency

| Audience | Cases | Route top-1 | Lexical recall@10 | Contract recall |
| --- | ---: | ---: | ---: | ---: |
| `power_engineer` | 15 | 100.0% | 49.7% | 100.0% |
| `software_engineer` | 15 | 100.0% | 43.2% | 100.0% |
| `student` | 15 | 100.0% | 53.8% | 100.0% |

## Case results

| Case | Audience | Route | Evidence-only recall@10 | Contract complete |
| --- | --- | --- | ---: | --- |
| `EVAL-GRAPH-STUDENT` | `student` | `one-universal-network-graph` | 22.2% | yes |
| `EVAL-GRAPH-SOFTWARE` | `software_engineer` | `one-universal-network-graph` | 33.3% | yes |
| `EVAL-GRAPH-POWER` | `power_engineer` | `one-universal-network-graph` | 33.3% | yes |
| `EVAL-YSPLIT-STUDENT` | `student` | `loads-generators-fixed-graph-membership` | 50.0% | yes |
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
| `EVAL-COUPLING-STUDENT` | `student` | `mutual-coupling-is-an-ordinary-parallel-network` | 80.0% | yes |
| `EVAL-COUPLING-SOFTWARE` | `software_engineer` | `mutual-coupling-is-an-ordinary-parallel-network` | 60.0% | yes |
| `EVAL-COUPLING-POWER` | `power_engineer` | `mutual-coupling-is-an-ordinary-parallel-network` | 80.0% | yes |
| `EVAL-SOLVER-VALIDITY-STUDENT` | `student` | `solver-termination-implies-validated-solution` | 50.0% | yes |
| `EVAL-SOLVER-VALIDITY-SOFTWARE` | `software_engineer` | `solver-termination-implies-validated-solution` | 25.0% | yes |
| `EVAL-SOLVER-VALIDITY-POWER` | `power_engineer` | `solver-termination-implies-validated-solution` | 25.0% | yes |
| `EVAL-LOAD-BASE-STUDENT` | `student` | `wye-delta-share-nominal-voltage-base` | 40.0% | yes |
| `EVAL-LOAD-BASE-SOFTWARE` | `software_engineer` | `wye-delta-share-nominal-voltage-base` | 40.0% | yes |
| `EVAL-LOAD-BASE-POWER` | `power_engineer` | `wye-delta-share-nominal-voltage-base` | 40.0% | yes |
| `EVAL-TRANSFORMER-TAP-DOMAIN-STUDENT` | `student` | `fixed-tap-snapshot-preserves-adjustable-transformer` | 33.3% | yes |
| `EVAL-TRANSFORMER-TAP-DOMAIN-SOFTWARE` | `software_engineer` | `fixed-tap-snapshot-preserves-adjustable-transformer` | 33.3% | yes |
| `EVAL-TRANSFORMER-TAP-DOMAIN-POWER` | `power_engineer` | `fixed-tap-snapshot-preserves-adjustable-transformer` | 50.0% | yes |
| `EVAL-TRANSFORMER-WINDING-REVERSAL-STUDENT` | `student` | `transformer-end-swap-is-ordinary-edge-reversal` | 16.7% | yes |
| `EVAL-TRANSFORMER-WINDING-REVERSAL-SOFTWARE` | `software_engineer` | `transformer-end-swap-is-ordinary-edge-reversal` | 33.3% | yes |
| `EVAL-TRANSFORMER-WINDING-REVERSAL-POWER` | `power_engineer` | `transformer-end-swap-is-ordinary-edge-reversal` | 16.7% | yes |

## Interpretation and next boundary

This baseline proves deterministic corpus search, high-risk query routing, and complete context-packet
assembly for the current curated cases. It does not prove robust paraphrase coverage outside the test
set, answer-generation faithfulness, citation correctness in generated prose, neural embedding retrieval quality,
or human-calibrated audience translation. Those remain separate roadmap gates.

# Adversarial LLM retrieval evaluation

**Status:** `pass`
**Cases:** 18

This is a deterministic robustness and abstention check, not human-calibrated answer-quality evidence.
Near-domain negatives require under_retrieved rather than unrelated qualified claims. These curated cases do not estimate deployment error rates or establish complete intent coverage.
Recall is averaged over the 8 cases with target evidence; empty target sets are not perfect retrievals.

| Measure | Result | Gate |
| --- | ---: | --- |
| Status accuracy | 100.0% | yes |
| Qualified contract completeness | 100.0% | yes |
| Unsupported-query abstention | 100.0% | yes |
| Unqualified-query status accuracy | 100.0% | yes |
| False qualification on unqualified queries | 0/10 (0.0%) | covered by status gate |
| Hybrid retrieval recall@10 | 44.4% | diagnostic |
| Graph retrieval recall@10 | 61.9% | diagnostic |

| Case | Expected status | Observed status | Hybrid recall@10 | Graph recall@10 | Contract complete |
| --- | --- | --- | ---: | ---: | --- |
| `ADV-YSPLIT-TYPO` | `qualified` | `qualified` | 33.3% | 83.3% | yes |
| `ADV-YSPLIT-SYNONYM` | `qualified` | `qualified` | 50.0% | 83.3% | yes |
| `ADV-PARALLEL-ABBREVIATION` | `qualified` | `qualified` | 66.7% | 83.3% | yes |
| `ADV-KRON-SYNONYM` | `qualified` | `qualified` | 20.0% | 100.0% | yes |
| `ADV-GRAPH-API` | `qualified` | `qualified` | 40.0% | 100.0% | yes |
| `ADV-GROUND-ABBREVIATION` | `qualified` | `qualified` | 75.0% | 0.0% | yes |
| `ADV-SEQUENCE-ABSOLUTE` | `qualified` | `qualified` | 50.0% | 25.0% | yes |
| `ADV-DECISION-QUALIFIER` | `qualified` | `qualified` | 20.0% | 20.0% | yes |
| `ADV-UNSUPPORTED-NEGATIVE` | `unsupported` | `unsupported` | — | — | — |
| `ADV-ZERO-VOLTAGE-KCL` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-ZERO-VOLTAGE-SOLUTIONS` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-ZERO-VOLTAGE-IMBALANCE` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-ZERO-NEUTRAL-RESIDUAL` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-KCL-ALL-VOLTAGES` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-IDEAL-SWITCH-SHARING` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-TINY-RESISTANCE-SHARING` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-IDEAL-CURRENT-LIMIT` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-PARAMETER-REUSE` | `under_retrieved` | `under_retrieved` | — | — | — |

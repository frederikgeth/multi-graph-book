# Adversarial LLM retrieval evaluation

**Status:** `pass`
**Cases:** 22

This is a deterministic robustness and abstention check, not human-calibrated answer-quality evidence.
Near-domain negatives require under_retrieved rather than unrelated qualified claims. These curated cases do not estimate deployment error rates or establish complete intent coverage.
Recall is averaged over the 17 cases with target evidence; empty target sets are not perfect retrievals.

| Measure | Result | Gate |
| --- | ---: | --- |
| Status accuracy | 100.0% | yes |
| Qualified contract completeness | 100.0% | yes |
| Unsupported-query abstention | 100.0% | yes |
| Unqualified-query status accuracy | 100.0% | yes |
| False qualification on unqualified queries | 0/5 (0.0%) | covered by status gate |
| Hybrid retrieval recall@10 | 42.5% | diagnostic |
| Graph retrieval recall@10 | 59.5% | diagnostic |

| Case | Expected status | Observed status | Hybrid recall@10 | Graph recall@10 | Contract complete |
| --- | --- | --- | ---: | ---: | --- |
| `ADV-YSPLIT-TYPO` | `qualified` | `qualified` | 33.3% | 83.3% | yes |
| `ADV-YSPLIT-SYNONYM` | `qualified` | `qualified` | 50.0% | 83.3% | yes |
| `ADV-PARALLEL-ABBREVIATION` | `qualified` | `qualified` | 50.0% | 66.7% | yes |
| `ADV-KRON-SYNONYM` | `qualified` | `qualified` | 20.0% | 100.0% | yes |
| `ADV-GRAPH-API` | `qualified` | `qualified` | 40.0% | 100.0% | yes |
| `ADV-GROUND-ABBREVIATION` | `qualified` | `qualified` | 75.0% | 25.0% | yes |
| `ADV-SEQUENCE-ABSOLUTE` | `qualified` | `qualified` | 50.0% | 25.0% | yes |
| `ADV-DECISION-QUALIFIER` | `qualified` | `qualified` | 20.0% | 20.0% | yes |
| `ADV-UNSUPPORTED-NEGATIVE` | `unsupported` | `unsupported` | — | — | — |
| `ADV-ZERO-VOLTAGE-KCL` | `qualified` | `qualified` | 66.7% | 100.0% | yes |
| `ADV-ZERO-VOLTAGE-SOLUTIONS` | `qualified` | `qualified` | 33.3% | 66.7% | yes |
| `ADV-ZERO-VOLTAGE-IMBALANCE` | `qualified` | `qualified` | 66.7% | 66.7% | yes |
| `ADV-ZERO-NEUTRAL-RESIDUAL` | `qualified` | `qualified` | 33.3% | 33.3% | yes |
| `ADV-KCL-ALL-VOLTAGES` | `qualified` | `qualified` | 33.3% | 66.7% | yes |
| `ADV-IDEAL-SWITCH-SHARING` | `qualified` | `qualified` | 25.0% | 25.0% | yes |
| `ADV-TINY-RESISTANCE-SHARING` | `qualified` | `qualified` | 25.0% | 25.0% | yes |
| `ADV-IDEAL-CURRENT-LIMIT` | `qualified` | `qualified` | 25.0% | 25.0% | yes |
| `ADV-PARAMETER-REUSE` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-DELTA-COIL-CIRCULATION` | `qualified` | `qualified` | 75.0% | 100.0% | yes |
| `ADV-DELTA-INRUSH-BOUNDARY` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-DELTA-COIL-TRANSIENT-BOUNDARY` | `under_retrieved` | `under_retrieved` | — | — | — |
| `ADV-DELTA-EXACT-PHRASE-TRANSIENT` | `under_retrieved` | `under_retrieved` | — | — | — |

# Adversarial LLM retrieval evaluation

**Status:** `pass`
**Cases:** 9

This is a deterministic robustness and abstention check, not human-calibrated answer-quality evidence.

| Measure | Result | Gate |
| --- | ---: | --- |
| Status accuracy | 100.0% | yes |
| Qualified contract completeness | 100.0% | yes |
| Unsupported-query abstention | 100.0% | yes |
| Hybrid retrieval recall@10 | 48.3% | diagnostic |
| Graph retrieval recall@10 | 61.7% | diagnostic |

| Case | Expected status | Observed status | Hybrid recall@10 | Graph recall@10 | Contract complete |
| --- | --- | --- | ---: | ---: | --- |
| `ADV-YSPLIT-TYPO` | `qualified` | `qualified` | 33.3% | 83.3% | yes |
| `ADV-YSPLIT-SYNONYM` | `qualified` | `qualified` | 50.0% | 66.7% | yes |
| `ADV-PARALLEL-ABBREVIATION` | `qualified` | `qualified` | 66.7% | 100.0% | yes |
| `ADV-KRON-SYNONYM` | `qualified` | `qualified` | 20.0% | 60.0% | yes |
| `ADV-GRAPH-API` | `qualified` | `qualified` | 40.0% | 100.0% | yes |
| `ADV-GROUND-ABBREVIATION` | `qualified` | `qualified` | 75.0% | 0.0% | yes |
| `ADV-SEQUENCE-ABSOLUTE` | `qualified` | `qualified` | 50.0% | 25.0% | yes |
| `ADV-DECISION-QUALIFIER` | `qualified` | `qualified` | 0.0% | 20.0% | yes |
| `ADV-UNSUPPORTED-NEGATIVE` | `unsupported` | `unsupported` | 100.0% | 100.0% | yes |

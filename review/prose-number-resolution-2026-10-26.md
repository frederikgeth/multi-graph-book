# Prose-number readiness resolution

**State:** author arithmetic and recorded-point checks; no external review,
scientific-status promotion or package publication.

The 54 unbound occurrences recorded in
`prose-number-audit-2026-10-26.json` now have scoped, source-hash-bound evidence.
The current gate checks 200 high-precision literals: 144 existing direct
artifact matches and 56 explicit bindings (the original two plus these 54).
No prose value, displayed precision or precision-selection threshold changed.
The gate's existing direct-match pool remains a numerical consistency check;
this work does not establish semantic provenance for its other 144 matches.

`experiments/lessons/prose_number_witnesses.py` computes 45 observations for
51 occurrences from the authored computational inputs. Rational complex
arithmetic is exact; roots and exponential values use 90 decimal digits, and
the small angle has exact alternating-series bounds. Power balance,
ampere-turn balance and cyclic-voltage invariants run with the calculations.
The calculation is book-owned algebra, not an independent test of every
package convention or physical device. Display literals appear only in the
occurrence mapping, not as calculation inputs. During implementation the gate
caught an inverted turns ratio in the new witness; correcting that witness
and asserting ideal-power balance confirmed the existing prose value.

The other three occurrences describe the same saved candidate solver point.
`experiments/lessons/recorded_generator_bound_input.json` freezes the relevant
input, returned rectangular voltages and currents, reported powers, and failed
audit rows from the fresh portable companion run. Its provenance records the
full run digest, candidate revision/tree, environment/profile hashes and all
50 source bindings, verified against the clean relocated sources when taking
the excerpt. `recorded_generator_bound.py` independently reconstructs each
WYE phase power using phase minus neutral voltage, then subtracts its authored
upper bound. Decimal reconstruction agrees with the recorded Float64 powers
and residuals within `1e-9 W`; the original `1e-6 W` audit tolerance is retained
separately. All three excesses round to the displayed `0.00997 W`. Every one
of the three prose bindings selects all three excesses, so a single matching
phase cannot satisfy the statement about each phase.

Explicit bindings now select a specific JSON scalar (or several scalars) and
must match it at displayed precision. An unrelated number elsewhere in an
artifact cannot rescue an invalid explicit binding. Seven binding/precision
regressions and four arithmetic/recorded-point regressions pass. Both witness
freshness checks and the prose-number gate are in docs CI and the release
validator. The generated inventory covers 99 JSON artifacts. The accompanying
JSON resolution maps every original queue item to its selected source fields.

Scientific generation (18 records), book federation, federation against the
unchanged published package pin, full LLM reproducibility, artifact/link,
math-hygiene and rendered-output checks pass. HTML remains 83 pages and the
selective PDF 208 pages. The lesson prose and their renders did not change;
these new bindings and execution records remain in the repository's evidence
and review layer. The knowledge registry, package export, integration pin and
evidence statuses are unchanged.

The frozen `checkpoint-review-2026-10-26.zip` and its bounded request still
describe the earlier 54-item queue. They are historical snapshots, not silently
replaced archives. Use this resolution alongside them or create a deliberately
new handoff later. The comprehensive release-candidate manifest remains
historical and is not refreshed or claimed to pass. Scoped domain/reader
feedback, disposition of findings and the package-publication decision remain
the next review obligations. No reviewer has been contacted by this work.

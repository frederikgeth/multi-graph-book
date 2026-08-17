# Evidence-matrix second coding — disagreement log

**Coding date:** 2026-08-15
**Second coder:** Claude (Opus 5), automated independent pass
**Guide:** `review/coding-guide.md` v0.2.0 · **Protocol:** `review/protocol.md` v0.1.0
**Working snapshot:** `review/snapshots/evidence-matrix-second-coding-2026-08-15.csv`
**Canonical matrix at coding time:** 14 rows, all `single_coded`
**SHA-256:** `3bfd987233c110f582375632e1445c519dc1e8929b29de4de5653df62a31b516`
**Checker:** `scripts/check_evidence_matrix.py` → 14 rows valid

Per coding-guide §"Second-coder procedure" step 1, the canonical file was **not edited**. This log
records disagreements by `record_id` and field. **No row is promoted to `double_checked` by this
pass** — see §4.

---

## 1. Summary

| Outcome | Records |
| --- | --- |
| Agree on all controlled fields | EV-0001, EV-0004, EV-0006, EV-0007, EV-0011, EV-0012, EV-0014 (7) |
| Disagreement on ≥1 controlled field | EV-0002, EV-0003, EV-0008, EV-0009, EV-0010, EV-0013 (6) |
| Agree on controlled fields, free-text issue only | EV-0005 (1) |

Controlled-field agreement rate: **8 / 14 (57%)** on `transformation_type` and `exactness`
combined. The disagreements cluster in one place: **`transformation_type` for records where
variables or internal structure are eliminated**, and `exactness` for records where the label is
applied to something other than a feasible set.

---

## 2. Record-level disagreements

### EV-0002 `Grudzien2018` — **conflict** (3 fields)

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `transformation_type` | `other` | `exact_behavioral_reduction` (+ split row) | substantive |
| `exactness` | `unclassified` | `exact` within the declared lossless regime | substantive |
| row granularity | one row | ≥2 rows | procedural |

The paper performs iterative Kron reduction plus line/tree/triangle reductions — variables and
network structure **are** eliminated, so under the guide's rule ("reduction types only when
variables or network structure are eliminated") a reduction type applies and `other` understates it.
The row's own `target_model` says "iteratively Kron-reduced", which contradicts `other`.

Further, the guide's unit-of-coding rule ("do not merge … if they have different targets or
preservation claims") requires splitting: the topology-guided reductions carry a declared
power-flow-equivalence claim in the lossless inductive regime, while coherent-subnetwork
aggregation does not. Coding both as one `unclassified` row hides a stated exactness claim.

**Proposed resolution:** split into EV-0002a (`exact_behavioral_reduction`, `exact`, scope =
lossless inductive regime) and EV-0002b (`approximate_reduction`, `unclassified`, coherent
aggregation).

### EV-0003 `MokhtariRadial2025` — **conflict** (1 field)

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `exactness` | `outer` | `scenario_approximate` | substantive |

`outer` asserts that every source-feasible observation is retained and only nonphysical points are
added. The paper establishes a **linearized voltage-error bound over representative loading
scenarios** — it does not prove feasible-set containment. `scenario_approximate` exists in the
schema for exactly this and is the honest code.

This also conflicts with the book's own treatment: `kron-ward-opti-kron.md` classifies Opti-KRON
as "mixed structural optimization and scenario approximation" and warns explicitly that
"scenario voltage accuracy … is not a surrogate theorem for feasibility". The matrix row is
currently more permissive than the chapter that cites it.

**Secondary note (`limitations`):** the record is an arXiv preprint with no peer-review status;
that should be stated, as the protocol requires publication type to be separated from evidence
strength.

### EV-0008 `BaezFong2018` — **conflict** (1 field)

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `transformation_type` | `compilation` | `exact_behavioral_reduction` | substantive |

Black-boxing eliminates internal wiring and preserves a declared external port relation. That is
the definition of behavioural reduction, and the row's own `retained_constraints` text says
"internal wiring is hidden behind the black-box map". `compilation` denotes a change of
variables/equations without elimination.

### EV-0009 `vanderSchaftMaschke2013` — **conflict** (2 fields)

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `transformation_type` | `compilation` | `not_reported` | substantive |
| `exactness` | `exact` | `not_reported` | substantive |

`source_model` = "port-Hamiltonian systems on graphs"; `target_model` = "graph-based
port-Hamiltonian system representation". That pair is near-identity — the record is a
**representation definition**, not a source-to-target transformation. It is correctly *included*
under protocol scope ("a formal or operational definition of a power-network representation"), but
coding a near-identity map as an `exact` `compilation` makes the two controlled fields
uninformative and inflates the count of "exact" transformations in any synthesis.

**Proposed resolution:** code `transformation_type = not_reported`, `exactness = not_reported`, and
add to `notes`: *included as a representation definition rather than a transformation record.*

### EV-0010 `Ehrig2006` — **conflict** (1 field) + **1 field-placement error**

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `transformation_type` | `compilation` | `other` | moderate |
| `provenance_map` | limitation text | provenance description | data quality |

Algebraic graph transformation is a rewriting framework; a DPO rewrite is not a change of
variables/equations. `other` is the guide's designated code for "does not fit".

The `provenance_map` cell contains *"does not provide the book's electrical equations, grounding,
limits, or utility data semantics"* — that is a limitation, not a description of a provenance map.
See §3 for the systematic version of this.

### EV-0013 `OpenDSSReduction` — **conflict** (1 field) + granularity

| Field | Primary | Second coder | Class |
| --- | --- | --- | --- |
| `transformation_type` | `other` | `approximate_reduction` (+ split rows) | substantive |

Short-line merging, intermediate-bus elimination, parallel-line merging, and lateral aggregation
all eliminate buses or members, so a reduction type applies. `exactness = unclassified` is correct
and should stay — the documentation does not establish preservation domains.

The four documented options have different targets and different preservation claims, so the
unit-of-coding rule calls for one row per option (or a `notes` entry recording the deliberate
merge). As one row, `preserved_observations` cannot be checked against any specific procedure.

### EV-0005 `HoRuehliBrennan1975` — **agree on controlled fields**, free-text over-reading

`multi_terminal_scope` reads "multi-terminal scope is represented through selected branch variables
rather than an ordinary Y-bus graph". MNA's contribution is handling ideal voltage sources and
controlled sources by augmentation; it makes no general n-port statement. Per the guide
("distinguish native n-port support from pairwise compilation or **no statement**"), this is closer
to no statement. Recommend softening rather than a status change.

---

## 3. Cross-cutting findings

### F1 — `provenance_map` contains limitation text in three rows (data quality)

EV-0007, EV-0010, and EV-0012 all use `provenance_map` to record what the source *fails* to
establish for the book, rather than what provenance the source *does* define:

- EV-0007: "paper does not establish the book's full asset/provenance or multiconductor generality"
- EV-0010: "does not provide the book's electrical equations, grounding, limits, or utility data semantics"
- EV-0012: "documentation is version-specific and does not establish universal semantic equivalence"

This is a systematic slot error: the content belongs in `limitations`, and `provenance_map` should
carry `none reported` where no provenance construction exists (the guide explicitly provides that
value). As coded, a synthesis query over `provenance_map` returns prose about the book instead of
about the literature.

### F2 — every row is `include`; the screen has not been exercised (procedural)

All 14 records are `screening_status = include`, with no `exclude` or `uncertain` rows and an empty
`exclusion_reason` column throughout. The protocol's screening procedure and its controlled
exclusion vocabulary are therefore unused, and **no PRISMA-style flow count can be reported**,
because there is no record of screened-and-rejected items. The protocol already states the
bibliography is a seed set; the matrix should carry that caveat explicitly in
`snapshot-manifest.json` so a reader does not mistake it for a screened corpus.

### F3 — 21 of 35 cited sources are absent from the matrix (coverage)

The book's bibliography has 35 entries; the matrix codes 14. Absent:

```
CIMTopologicalNode   CaliskanTabuada2014  Coppo2017          CurtisMorrow2000
DorflerBullo2013     GanLowChordal2014    GanLowMultiphase2014
GethHeidariKoirala2022  GethLiu2022       Jang2013           Kavitha2008
KettnerPaolone2019   MATPOWERCaseFormat   Machowski1988      Mokhtari2027
Monticelli1979       Nanopass2005         PMDEngineering     Pecenak2018
Sistermanns2019      Ward1949
```

Three of these are consequential for the review's own primary question:

- **`DorflerBullo2013`** is the most-cited source in the book and the canonical Kron-reduction
  reference. Its absence from an evidence map about network transformations is the single largest
  coverage gap.
- **`Jang2013`** (line-limit-preserving equivalent) is the closest prior art to the book's central
  decision-preservation thesis and is uncoded.
- **`CurtisMorrow2000`** is the reference for *recoverability* of a network from its response
  matrix — directly on the `recovery_map` coding dimension.

Also absent: `KettnerPaolone2019` (compound nodal admittance properties), both Gan–Low records
(BIM/BFM and chordal relaxation), `Ward1949` and `Monticelli1979` (the Ward family),
`Pecenak2018` and `Sistermanns2019` (feeder and transmission reduction).

Coding these would very likely change the synthesis: the matrix currently contains **no**
peer-reviewed record of classical Kron/Ward external equivalencing, which is the dominant strand of
the literature the book positions itself against.

### F4 — `reviewer` is empty on all rows while `review_date` is populated (consistency)

Every row has `reviewer = ""` but `review_date ∈ {2026-08-13, 2026-08-14, 2026-08-15}`. A review
date without a reviewer is not interpretable. Either populate `reviewer` with the primary coder's
identifier or clear `review_date` until a coder is recorded.

### F5 — `exactness` is not comparable across rows (schema)

`exact` is currently applied to at least four different objects: an algebraic identity (EV-0005,
EV-0006), a state-conditioned connectivity quotient (EV-0004, EV-0011), an external boundary
behaviour (EV-0008), and a constraint-set-preserving presolve (EV-0001). All are defensible under
the guide's "code the authors' declared domain" rule, but the column cannot then be aggregated.

**Recommendation:** add an `exactness_object` field with values such as
`equations | connectivity | boundary_behaviour | feasible_set | observation_sample`. This is a
small schema change that makes the most important column in the matrix analysable.

---

## 4. Resolution status and `coding_status`

Six records carry unresolved substantive disagreements (EV-0002, EV-0003, EV-0008, EV-0009,
EV-0010, EV-0013). Per coding-guide step 5, `coding_status` may move to `double_checked` **only
after** the resolution is recorded and the duplicate register updated.

Recommended dispositions:

| Records | Recommended `coding_status` | Action required |
| --- | --- | --- |
| EV-0001, EV-0004, EV-0006, EV-0007, EV-0011, EV-0012, EV-0014 | `double_checked` | Fix F1 slot errors in EV-0007 and EV-0012 first; then promote. |
| EV-0005 | `double_checked` | Soften `multi_terminal_scope` wording; controlled fields agree. |
| EV-0002, EV-0003, EV-0008, EV-0009, EV-0010, EV-0013 | `conflict` | Resolve by discussion; record the decision and rationale before promotion. |

The duplicate register (`deduplication-register.csv`) was checked: all 14 records are marked
`unique` with normalized DOIs, and no duplicate groups need revision. One note for the register —
EV-0004 (CGMES) and EV-0011 (PowSyBl) are *not* duplicates but do code the **same underlying
transformation** (connectivity node → topological node) from a standard and from an
implementation. That relationship should be recorded so a synthesis does not double-count it as
two independent pieces of evidence.

**This pass does not constitute independent human second coding.** It is an automated
reproduction of the coding guide against the same source records. The `reviewer` field should
record that distinction, and F3 in particular should be resolved by a human coder with full-text
access before any row is described as double-coded.

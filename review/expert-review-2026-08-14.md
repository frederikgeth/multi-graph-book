# External expert review — Structure-Preserving Graph Models for Power Networks

**Reviewer perspective:** power-system numerical modelling (multiconductor steady state, OPF,
network equivalents, data models).
**Material reviewed:** all 45 reader-facing pages under `docs/src` (51,460 words), both navigation
routes in `docs/make.jl`, `claims/claims.toml` (37 claims), `schemas/transformation-certificate.schema.json`,
the 31 artifacts under `experiments/generated/`, `data/running-network/v0.1.0.json`, and all eleven
figures under `docs/src/assets/`.
**Date:** 2026-08-14. Reviewed on its current merits, independently of any earlier assessment.

---

## 1. Overall assessment

This reads as a serious scientific reference in progress, not a proposal document. The
distinguishing features — relative to every adjacent literature I know — are real:

- **Evidence is separated from assertion by construction.** A generated `chapter-status` page and
  `knowledge-base-index`, both hash-stamped to the claims ledger, expose claim type and
  verification level for every page. Almost nothing in this field does that.
- **Two publication routes, genuinely curated.** `PAGES_HTML` (45 entries) and `PAGES_PDF` (21)
  are now different objects rather than one list serving two masters. That is the right
  architecture for a reference monograph plus a retrievable knowledge base.
- **Rules refuse rather than approximate.** Guarded rewrites return structured rejections with the
  failed condition. The Kron chapter now carries a positive *and* negative realizability test.
- **The mathematics I checked is correct.** I verified the five-bus incidence matrix and both
  cycle ranks, `AC = 0`, the bridge set, the series composition `Z₁ + PᵀZ₂P` and constraint
  intersection `C₁ ∩ PᵀC₂`, the phase-to-neutral congruence and the phase-to-phase kernel and
  residual, the Kron affine term and its recovery map, the typed-covariance proof, the `Z_B`
  round-trip and an independent `n = 2` reconstruction of `Y_x^w`, the two-bus DC OPF optima, the
  loop-impedance closed form `z = (10/11)z₁`, and the served-fraction and MW arithmetic in the tap
  case. It holds up.

Two things genuinely stand out as contributions: the **complex-polydisc row-norm redundancy test**
(`TR-PAR-006`/`TR-PAR-007`) — exact worst case `Σ_k |K_ck| I^max_k` with a constructive tightness
argument, generalizing the scalar containment test in a direction that has not been published —
and the **reciprocity-is-convention-relative corollary** in the Kron chapter, which is the sort of
result that saves people months.

The remaining problems are now overwhelmingly problems of **craft and shape**, not correctness.
That is a much better place to be than a book with elegant prose and unchecked claims. The two
things holding it back:

1. **Everything is `self-checked`.** Thirty-six of thirty-seven claims. No amount of additional
   self-generated evidence moves this. External review is now the binding constraint on the whole
   project, and the ledger is honest enough to say so on every row.
2. **The book proves things exactly or not at all.** There is no theory of *certified
   approximation* — see §3.2. That is the gap between this being a valuable critique and being the
   reference people reach for.

---

## 2. Defects a reader will hit

### 2.1 Two figures render dark-on-black and are illegible
`docs/src/assets/preservation-contract-card.png`, `docs/src/assets/transformer-anatomy.png`

Both are composited on a black field with near-black titles, subtitles and footers. On
`preservation-contract-card.png` the heading *"Preservation contract"*, the strapline, and the
footer are effectively invisible; the seven content boxes survive only because they have light
fills. On `transformer-anatomy.png` the title, subtitle and bottom caption are all lost.

The cause is almost certainly SVG→PNG rasterization without an explicit background rect: the SVGs
assume a white page and set dark text fills. `earth-return-ladder.png` and
`parallel-feasible-set-card.png`, from the same batch, render correctly — so the fix is a
background rect (or a rasterizer `--background white`) applied consistently.

This matters more than a normal cosmetic bug for two reasons: the preservation-contract card is
the book's brand element and is meant to repeat at the head of every transformation chapter, and
its own footer reads *"Colour is secondary; headings and text carry the contract in monochrome"* —
directly above a heading that is not legible at all.

### 2.2 `numerical-structure-witness.png` is clipped and overprinted
`docs/src/foundations/numerical-consequences.md:125`

Three separate layout failures in one figure: the lower "Structural Jacobian dependency view"
matrix is cut off mid-row (the `KCL l` row is truncated by the canvas edge), the rotated column
labels (`U_i … I_x`) overprint the subtitle line *"Rows are equations; columns are variables"*, and
the legend (`orange = fill edge`, `blue matrix blocks = equation dependence`) is orphaned in an
otherwise empty right-hand column while the top panel wastes half its width. Canvas height and
subplot layout need fixing in `experiments/generate_numerical_structure_views.py`.

### 2.3 The chapter-status generator ships malformed rows
`docs/src/reference/chapter-status.md`

Pages without an explicit `**Page status:**` line fall back to scraping the leading prose, which
produces cells like:

- row 24: *"foundational definitions and terminology. ## Why an arrow is ambiguous"* — a raw
  Markdown heading in a table cell;
- row 37: **the entire terminology glossary**, ~30 rows of table markup, flattened into one cell;
- rows 15, 22, 29, 33, 34, 36, 40, 42, 46, 51: two-to-three sentences of body prose where a status
  label belongs.

Eleven of fifty-two rows are affected. The fix is to make `**Page status:**` mandatory and fail the
build when it is missing, rather than degrading to prose scraping. This page is the book's headline
credibility device; malformed rows undercut exactly the impression it exists to create.

### 2.4 `ARCH-PORT-001` is invisible in its own chapter
`docs/src/foundations/formal-representation-frameworks.md`

The claim exists in the ledger, the artifact `experiments/generated/port-factor-architecture.json`
exists, and both the knowledge-base index and chapter-status page reference it. The chapter itself
never mentions the witness, never links the artifact, and never states what was validated. A
reader who wants the evidence for the book's central architectural proposal — the port–factor
model — cannot find it from the chapter that defines it.

Worth an audit pass across all claims: the generated indexes currently know things the prose does
not. Any claim whose chapter body does not cite it is invisible to the actual reader.

### 2.5 The certificate schema has diverged from the numerical chapter
`schemas/transformation-certificate.schema.json` vs `docs/src/foundations/numerical-consequences.md:253-260`

The chapter specifies a normative numerical field set (`ordering`, `nnz_input`, `nnz_factor`,
`nnz_fill`, `rank_guard`, `conditioning`, `recovery_cost`) and the tuple `𝒩`. The schema's
top-level properties are `certificate_id, classification, constraint_map, evidence, forgets,
interfaces, preconditions, preserves, provenance, recovery_map, rule_id, schema_version, source,
target` — no numerical block. Meanwhile `pi-four-wire-parallel-ac-certificate.json` has already
grown ad-hoc `margin`, `backward`, and `cond` keys inside `evidence`, outside any typed contract.

Either add an optional typed `numerical` object in schema v1.2 and migrate those keys, or
relabel the chapter's table as a proposal rather than a requirement. Right now the book states a
normative field list that its own schema does not accept.

### 2.6 Axis-label error in a headline figure
`docs/src/assets/parallel-feasible-set-card.png`

The horizontal axis is labelled `|ΔU| (V)` but is drawn from −20 to +20 with intervals symmetric
about zero. A magnitude cannot be negative. Either label it `ΔU (V)` or plot `0…20`.

The same figure also duplicates `five-bus-feasible-sets.png` almost exactly — same 15 V witness,
same intervals, same message — and, despite being titled *"feasible-set geometry"*, is still a
one-dimensional interval bar. The geometry that would earn the title is the complex `ΔU` plane
with the two member discs and the summed constraint; that picture also generalizes directly to
the containment test (one ellipse inside another, plus the singular-cylinder case), which is
currently pure algebra.

### 2.7 Editorial scar tissue in the prose
`docs/src/foundations/numerical-consequences.md:188-190`

> "For avoidance of a common counting error, the source witness has four complex member-current
> coordinates… It therefore has 13 real source variables… The reduction removes eight real
> variables (four complex currents), not six."

A first-time reader has no idea what "six" refers to. The count is already stated correctly in
`multiconductor-parallel-ac-decision.md:165`. Delete the paragraph; corrections belong silently in
the source chapter, not as a defensive footnote in a different one.

---

## 3. Content assessment

### 3.1 "When the general model collapses" is the right chapter, under-delivered
`docs/src/foundations/when-general-model-collapses.md` (837 words)

The chapter does the honest structural work — the invariant subspace, seven explicit assumptions,
the observation-factorization statement `h_abc ∘ E₊ = ĥ₊`, and the refusal to claim the running
fixture as a witness. Three things hold it back:

- **The exactness condition is stated for circulant matrices only.** That is stronger than
  necessary and, more importantly, it skips the case that matters. Practitioners do not ask "is my
  matrix circulant"; they ask "my line is untransposed and my loading is roughly balanced — how
  wrong is positive sequence?" The chapter defines `ρ₊(v)` and then immediately disclaims it as
  "not a decision-error bound", which leaves the reader exactly where they started.
- **No numbers.** The witness JSON contains a diagonalized circulant matrix and a perturbed
  non-circulant residual. Put those values in the chapter. One 3×3 with actual p.u. entries, its
  sequence diagonalization, and the perturbation residual would make the argument land in a way
  that the abstract statement cannot.
- **A convention trap goes unflagged.** `𝒱₊ = {A[0,V₁,0]ᵀ}` with `A = [[1,1,1],[1,a²,a],[1,a,a²]]`
  makes `V₁` the phase-*a* positive-sequence value. The book polices exactly this class of
  convention ambiguity everywhere else; it should police it here.

### 3.2 There is no theory of certified approximation — the largest remaining gap

Every certificate in the book is exact-or-rejected. The vocabulary for approximation exists in
several places — `preservation-contracts.md` defines "scenario approximate",
`numerical-consequences.md` defines the certified/ambiguous/violated margin classification,
`kron-ward-opti-kron.md` reports 1.5–3.3% Ward current errors, `when-general-model-collapses.md`
defines `ρ₊` — but no chapter closes the chain:

```
parameter or model residual → state error → constraint margin → decision margin
```

Each of those chapters names the gap and declines to cross it. Naming a gap repeatedly is not the
same as closing it, and a reader will notice that the book's most-used word ("certificate") never
attaches to an approximate result.

This is the single highest-value chapter still missing. One worked chain — take the Ward
operating-point equivalent already in the fixture, bound its boundary-current error, propagate to a
member-current margin, and classify the resulting decision as certified/ambiguous/violated using
the book's own three-way test — would convert the framework from a filter into a tool. The
machinery is already built; it has not been composed.

### 3.3 Ward is taxonomy without construction
`docs/src/transformations/kron-ward-opti-kron.md:314-370`

The classical / operating-state-extended / Ward–PV / nonlinear family distinction is correct and
well sourced. But no extended-Ward construction is written down, and the defining feature of the
extended variant — fictitious reactive-support injections at boundary buses — is not described at
all. The scenario fixture's middle target, labelled "operating-point Ward", freezes the boundary
injection at the base scenario; that is classical Ward with a calibrated injection, not extended
Ward. Either rename the fixture target or add the construction. Readers in this specific area will
catch it.

### 3.4 The earth/ground ladder classifies more than it models
`docs/src/foundations/earth-ground-models.md`

`E₀`–`E₃` is a good taxonomy and the "not a strict accuracy ladder" framing is right. But no
chapter in the book contains an explicit earth conductor, a Carson or shield-wire model, or a
multi-grounded neutral ladder. The running fixture is asserted to be "at least `E₁` and partly
`E₂`" with no stated criterion, and the phase-to-neutral exactness conditions in
`circuit-coordinate-transformations.md:88-98` still say "negligible current into ground" without
binding to a class. The classification is currently applied post hoc rather than being a modelling
commitment that some artifact discharges. One explicit-`E₂` fixture would settle it and would make
the ladder load-bearing.

Related: `circuit-coordinate-transformations.md` still defines `Z^pn = T Z Tᵀ` and names "neutral
Kron reduction" in its summary table without ever writing `Z_abc = Z_pp − Z_pn Z_nn⁻¹ Z_np`. Those
two 3×3 matrices are the most-confused pair in four-wire modelling and belong on the same page,
side by side, with a small numerical witness showing they differ and which grounding assumption
produces each.

### 3.5 The crosswalk table lists matches where the value is in the mismatches
`docs/src/foundations/data-model-crosswalk.md`

Most cells restate the row label — *"connectivity node → `ConnectivityNode` → engineering
bus/connectivity data → bus connectivity → bus row in `mpc.bus`"*. The genuinely useful content is
compressed into the one-line "Mapping status" column.

Invert it: one row per **known trap**, each with what breaks and what to check. Candidates a
practitioner meets in the first week — phase encoding inside OpenDSS bus-name suffixes;
PowerModelsDistribution applying Kron reduction and per-unit conversion during
engineering→mathematical conversion; MATPOWER packing lines, transformers and phase shifters into
one branch row; CGMES splitting state across SSH/SV profiles so a single file is not a solvable
case. That version is the page people would print and pin up.

### 3.6 Repetition has grown
The parallel-line mechanism now appears in ten places. `index.md` carries a **28-item** numbered
reading list that duplicates the sidebar and is not usable as guidance — it is longer than the
one it replaced. With the two routes now split, `index.md` should carry the PDF argument as one
short paragraph and delegate retrieval to `knowledge-base-index.md`, which does the job properly.

---

## 4. Structure

**What the split achieved.** Worked cases are out of "Start here"; the PDF route is a real
sequence rather than a dump; the generated status and index pages are the right way to make
epistemic state visible; `Part I` absorbing the new physical-modelling chapters kept the
transformation parts clean.

**What it did not.** Two issues remain:

*The PDF route is curated on chapter maturity, not argument value.* `PAGES_PDF` drops
`translation-traps.md` — the book's best and most quotable chapter — while retaining
`conductor-coordinate-normalization.md` (379 words, a permutation). It also drops
`representation-taxonomy`, `representation-maps`, `node-breaker`, `rating-semantics`, and
`data-model-crosswalk`, several of which carry the book's most differentiated material. Re-select
on the question "does the argument survive without this chapter".

*`Part I` now has twelve chapters doing three different jobs* — formal definitions (taxonomy,
frameworks, maps, cycles, orientation, architecture), physical-modelling reference (earth/ground,
node–breaker, ratings), and computational reference (crosswalk, numerical). Split into *Part I —
Representations* and *Part II — Physical and computational reference*. Separately, the four
framework chapters (`representation-taxonomy`, `formal-representation-frameworks`,
`representation-maps`, `representation-architecture`) still total ~5,200 words of substantially
overlapping material and would be stronger as one chapter plus a set of reference cards.

---

## 5. Audience

Three audiences, and the new chapters have sharpened the fit considerably:

- **Unbalanced/distribution modellers and tool builders** (PMD, OpenDSS/DSS-Extensions, CIM
  implementers). `earth-ground-models`, `node-breaker-topology-processing`, `rating-semantics`, and
  `data-model-crosswalk` are now the book's most differentiated material and speak directly to
  this group. Strongest fit by a distance.
- **OPF and optimization researchers.** The redundancy-certificate results are directly usable and
  directly publishable. This group will not read 45 chapters but will cite two papers.
- **Model-exchange and standards people.** The crosswalk plus the provenance/certificate
  discipline is their problem exactly — after §3.5.

A fourth is now within reach: **people who care about solver behaviour**, opened by
`numerical-consequences.md`. That chapter is the most novel framing in the book (nobody in this
field publishes conditioning and fill as part of an equivalence claim), and it converts that
audience only if §3.2 gets closed.

**Strategic note, unchanged in substance.** The binding constraint is external verification, not
additional content. Extracting the redundancy result as a paper is the fastest way to obtain it,
and it would upgrade several ledger rows from `self-checked` to `externally-reviewed` in one step.

---

## 6. Priorities

1. **Fix the two black-background figures, the clipped numerical figure, and the chapter-status
   generator** (§2.1–2.3). Half a day; all four are highly visible and all four undercut the
   credibility the project has otherwise earned.
2. **Surface `ARCH-PORT-001` in its chapter and audit every claim for prose visibility** (§2.4).
3. **Write the certified-approximation chain** (§3.2). One worked example, machinery already built.
   Highest content value available.
4. **Put numbers in the collapse chapter and extend it past the circulant case** (§3.1).
5. **Re-curate `PAGES_PDF` on argument value; restore `translation-traps`** (§4).
6. **Schema v1.2 with a typed `numerical` block, or downgrade the chapter's table** (§2.5).
7. **Invert the crosswalk table into a table of traps** (§3.5).
8. **Add the `Z^pn` vs Kron-reduced `Z_abc` comparison** to the coordinate chapter (§3.4).
9. **Cut `index.md` to a route paragraph** (§3.6).
10. **Submit the redundancy result** and let peer review supply the verification the ledger is
    waiting on (§5).

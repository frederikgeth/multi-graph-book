# External expert review — Structure-Preserving Graph Models for Power Networks

**Reviewer perspective:** power-system numerical modelling (multiconductor steady state, OPF,
network equivalents, data models).
**Material reviewed:** all 36 pages under `docs/src`, `claims/claims.toml`,
`QUALITY_CONTROL.md`, `BOOK_PLAN.md`, `README.md`, `schemas/`, generated certificates under
`experiments/generated/`, `data/running-network/v0.1.0.json`, and the four figures.
**Date:** 2026-08-13.

---

## 1. Overall assessment

The premise is correct, under-served in the literature, and worth a book. The parts that exist
are unusually careful by the standards of this field. Four things are genuinely strong:

- **Orientation, terminal quantities, and power transfer.** The cleanest short treatment of
  arrow semantics, terminal-power pairs, and nominal-π terminal asymmetry I have seen written
  down anywhere. Publishable as a standalone tutorial.
- **Translation traps.** The controlled-replacement idea is the book's best pedagogical
  invention, and the complex-symmetric vs Hermitian item is exactly right.
- **The polydisc row-norm redundancy result** (`TR-PAR-006`/`TR-PAR-007`). This is a small,
  correct, new, and useful theorem — the exact worst case of candidate component *c* over a
  product of retained component discs is `Σ_k |K_ck| I^max_k`, with a constructive argument for
  tightness. It generalizes Molzahn's scalar test in a direction nobody has published.
- **Guard-rejection discipline.** Rules that return structured refusals rather than best-effort
  answers, plus the clean-checkout reproduction script, are better engineering hygiene than most
  published power-system software.

The two structural problems are:

1. **The book's declared central proposal is the least-tested thing in it.** The linked
   asset/port–factor architecture `(𝔄, 𝔓, Λ)` is defined once (`formal-representation-frameworks.md`)
   and then never instantiated. Every executable artifact is matrix algebra on two-terminal or
   multiwinding primitives. No experiment constructs `𝔓 = (Q, J, Φ, j, f, H, X, R)`, no experiment
   instantiates `Λ`, no certificate has `source_type = port_factor`. The reader is asked to accept
   an architecture as the organizing idea of the book while the evidence base is about something
   else.
2. **The argument is entirely negative.** Every worked case shows that a simplification breaks a
   decision. The corresponding positive claim — that the familiar balanced bus–branch model is an
   exact derived case under declared assumptions — is asserted in the abstract, the introduction,
   the scope chapter and the taxonomy, and is *never once derived or demonstrated*. See §4.1.

Both are fixable, and fixing them is worth more than adding any new chapter.

---

## 2. Errors and defects

### 2.1 The typed Kron covariance proposition mishandles complex coordinates
`transformations/kron-ward-opti-kron.md:130–193`

The proposition uses the power-dual convention `v = T ṽ`, `ĩ = Tᴴ i`, giving `Ỹ = Tᴴ Y T`, and
then states: *"The proposition covers phase permutations, compatible sequence-coordinate changes,
and other invertible port-coordinate actions."*

Two problems, both material for a reader who applies it:

- **The sequence claim is convention-dependent and, with the textbook Fortescue matrix, wrong.**
  The standard symmetrical-component convention transforms voltages *and* currents the same way
  (`v_abc = A v_012`, `i_abc = A i_012`), giving the **similarity** `Y_012 = A⁻¹ Y_abc A`. The
  chapter's congruence `Aᴴ Y A` coincides with that only when `A` is unitary. For the common
  unnormalized `A = [[1,1,1],[1,a²,a],[1,a,a²]]`, `Aᴴ ≠ A⁻¹` and the two differ by a factor of 3.
  Either restrict the proposition to `T` unitary up to a real scalar, or state both conventions
  and which current variable each one defines.
- **Reciprocity is not preserved by complex congruence, and the book never says so.** For complex
  symmetric (reciprocal) `Y` and complex `T`, `Tᴴ Y T` is generally *not* complex symmetric. This
  is precisely why sequence impedance matrices of untransposed lines are not symmetric — a fact
  every distribution modeller has been bitten by. Given that `translation-traps.md:234–241` makes
  a point of the symmetric/Hermitian distinction, the omission here is the book's own trap,
  uncaught. Add a corollary: *reciprocity is invariant under real congruence and under complex
  congruence by `T`ᵀ, but not under the power-dual `T`ᴴ action; structural properties are
  coordinate-relative.* That single result would be one of the more valuable pages in the book.

`TR-KRON-001` in the ledger is marked `established_result` on the strength of an algebraic
derivation with no tests and no reviewer. It should not carry that status until the above is
resolved.

### 2.2 Verified numerical inconsistency
`cases/multiconductor-parallel-ac-decision.md:157`

> "…while using the aggregate current relation and six fewer explicit current variables in this
> implementation."

The certificate records `source_solution: {variables: 13}` and `exact_lifted_solution:
{variables: 5}` — **eight** fewer (four complex member currents = 8 real variables). Confirmed in
`experiments/generated/multiconductor-parallel-ac-certificate.json`.

### 2.3 The redundancy certificates have no numerical validity argument
`cases/four-wire-parallel-ac-decision.md`, `cases/pi-four-wire-parallel-ac-decision.md`

Both certificates are computed from an explicit inverse (`Y_ℓ1⁻¹`, `A_ℓ1⁻¹`), and the π case
records `cond(A_ℓ1) = 2922.9`. The theorem ("necessary and sufficient") holds in exact arithmetic;
the certificate is evaluated in floating point. Nothing is currently wrong — the margin is
0.178 vs 0.72 — but a framework whose entire selling point is *certificates* cannot be silent
about this. Minimum fix: record the condition number and a backward-error margin as certificate
fields, and reject when the certified worst case is within that margin of the limit. Better:
evaluate the decisive row norms in interval arithmetic.

A second, larger point: the certificate is exact **for the nominal parameters**. Real impedance
data carry tolerances of several percent. "Exact presolve" should be qualified as exact for the
declared data, with a note that parameter uncertainty converts it into a robustness question.
This is worth a paragraph in `research-agenda.md` Workstream B4.

### 2.4 Defective proof
`foundations/cycles-parallelism-radiality.md:157–162`

> "If the fibre is a singleton, every multigraph path between the two sides projects to a simple
> path using the corresponding simple edge…"

That sentence does not state the argument. The correct form: suppose `π(ℓ) = e` is a simple
bridge and `π⁻¹(e) = {ℓ}`. If `ℓ` were not a bridge, there is an `i–j` path `P` in `G_M − ℓ`;
since no other member maps to `e`, `π(P)` is an `i–j` walk in `G_s − e`, contradicting that `e`
is a bridge. In a book claiming proof-level rigour, this needs rewriting.

### 2.5 Under-specified definition
`foundations/preservation-contracts.md:8–18`

The definition says "exact for observation family `H`" but the displayed equation contains a
single unquantified `h`, and `u` is quantified in the prose but not in the set-builder. Also
`h_M` is introduced and then never used. Tighten to: for all `h ∈ H` and all admissible `u`,
`{h(x,z,u) : (x,z,u) ∈ F_M} = {ĥ(x̂,u) : (x̂,u) ∈ F_M̂}`, with `ĥ` the declared target observation
corresponding to `h`.

### 2.6 The line–shunt realization proposition is weaker than it looks
`transformations/kron-ward-opti-kron.md:218–240`

The hypothesis `Y^K_pq = Y^K_qp = (Y^K_pq)ᵀ` should be **derived** from source reciprocity, not
assumed; and the construction absorbs every diagonal block into a residual shunt, so the
"proposition" is a stamping identity that always succeeds under reciprocity. That is fine — the
chapter says so afterwards — but it should be labelled as such rather than as a realizability
result, and it should state the cost: `N(N−1)/2` full `c×c` blocks, i.e. a complete graph. A
nonzero count on a small example would land the point better than the sentence.

### 2.7 Missing contrast that the four-wire chapter exists to make
`transformations/circuit-coordinate-transformations.md`

The chapter defines `Z^pn = T Z Tᵀ` (neutral current determined by KCL, no earth return) and, in
the summary table, names "neutral Kron reduction `K`" as a separate row — but never writes
`Z_abc = Z_pp − Z_pn Z_nn⁻¹ Z_np` and never puts the two 3×3 matrices side by side. These two
matrices are the single most confused pair in four-wire modelling. They must appear on the same
page, with a small numerical witness showing they differ and a statement of exactly which
grounding assumption produces each.

---

## 3. Misleading, or over-claimed

### 3.1 "Certificate" and `status = established_result`
Twenty claims in `claims/claims.toml`; fifteen carry `status = "established_result"`; **one** has
a `reviewer`/`review_date`, and that one is a literature claim. The rendered book never shows the
verification state at all. Combined with the word "certificate" appearing on every generated JSON
file, the aggregate impression conveyed to a reader is far stronger than the actual evidentiary
state, which is *author-derived, author-implemented, author-checked*.

The `status` field is currently recording claim **type**, not verification **state**. Split it:

```
claim_type       = definition | theorem | empirical | practice | proposal | open
verification     = unreviewed | self-checked | independently-implemented | externally-reviewed
```

and render `verification` as a visible banner in each chapter. This costs a day and is the single
highest-leverage credibility change available.

### 3.2 "Independently reproduced"
`README.md:22` advertises "solver-backed and independently reproduced transformer-network …
certificates". The chapter itself is scrupulous (`cases/transformer-tap-ac-decision.md:168–173`:
"it deliberately shares the certified input matrices and case assembly … not an independent
data-model or transformer-primitive implementation"). The README drops the qualifier. Fix the
README, not the chapter.

### 3.3 The reference architecture is presented as the spine and tested nowhere
See §1.1. `index.md:25–27` and `scope-and-thesis.md:89–99` present `(𝔄, 𝔓, Λ)` as *the* proposal.
`representation-architecture.md` describes the required derived views. Nothing downstream uses
any of it. A reader who takes the book at its word will expect the transformer chapters to be
port–factor constructions; they are dense-matrix constructions with hand-declared block
structure. Either instantiate the running network in `𝔓` with real relations (a genuine and
achievable milestone), or demote the architecture from "central proposal" to "candidate
formalism, not yet exercised" everywhere it is mentioned.

### 3.4 Molzahn's reported numbers
`literature/literature-map.md:72–74` quotes "between 203 and 650 redundant parallel-line limits,
with MIPS OPF runtime reductions of 2.0% to 5.7%". Per the project's own QC policy (§3, "confirm
that the cited source supports the nearby claim"), these should carry a table/figure reference,
not just a citation key.

### 3.5 The running-example policy is stated and then broken
`BOOK_PLAN.md:248–257` commits to **one** synthetic reference network. Five of the six worked
cases (`multiconductor-parallel-ac`, `four-wire-parallel-ac`, `pi-four-wire-parallel-ac`, and the
five-bus cycle chapter) use bespoke two- or five-bus networks unrelated to the running case. That
is a defensible engineering choice — small cases admit closed-form checks — but the policy should
be rewritten to say so, e.g. "one running network for representation comparison; minimal isolated
cases for each transformation, each with an analytic check". Right now the stated policy makes the
drafted content look undisciplined when it is not.

---

## 4. Misleading through omission

### 4.1 The collapse to the balanced model is never performed — the largest gap
The thesis is *"balanced positive-sequence transmission models are important derived cases whose
validity follows from declared assumptions."* This appears in `README.md:13`, `index.md:15–17`,
`BOOK_PLAN.md:33–35`, `scope-and-thesis.md:70–80`, and `representation-taxonomy.md:114–130`.
**No chapter derives it.** There is no symmetrical-components chapter, no transposition analysis,
no sequence-decoupling condition, no worked example of the general model collapsing correctly.

Consequences:
- The book has a negative thesis only. Every executable result says a simplification breaks
  something; nothing says when it does not, which is the reader's actual daily question.
- A transmission engineer reads it as advocacy against their practice rather than as a
  delimitation of it.
- The central claim is, by the book's own QC standard, an unsupported claim repeated in five
  places.

**This should be the next chapter written**, before any further transformation rule. Concretely:
take `ℓ_3` (the four-conductor coupled line) from the running network, state the transposition /
balance / grounding conditions, execute the collapse to a positive-sequence π, certify what is
exact and what is only approximate, and quantify the residual on the fixture. That one chapter
converts the book from a critique into a theory.

### 4.2 Earth is declared distinct from neutral and then modelled as a single ideal node
`notation-and-conventions.md:186–198` insists that reference, earth, neutral, perfect ground and
grounding impedance are five different things. Every executable model then uses `U_i ∈ ℂ^{n_i}` of
*terminal-to-ground* voltages, i.e. one global ideal earth node. There is no earth-return
impedance, no Carson model, no multi-grounded neutral ladder, no earth as a network object. The
four-wire exactness conditions (`circuit-coordinate-transformations.md:88–98`) are stated in terms
of "negligible current into ground" without a model of what ground *is*.

This is the sharpest omission in the book, because the book's stated differentiator is exactly
that it takes grounding seriously. Minimum fix: one section defining the earth-return model class
used (ideal reference node; Carson-reduced; explicit earth conductor), and a statement of which
results hold in which class. `GethHeidariKoirala2022` is your own paper on precisely this and
should carry the section.

### 4.3 Node–breaker / topology processing: zero content
`literature-map.md:96–99` calls CIM connectivity/topological-node quotienting "perhaps the most
widely deployed graph projection in power-system operations". `BOOK_PLAN.md` chapters 12 and 33
promise it. There is no chapter, no rule, no certificate, no example. For the data-model audience
this is the first thing they will look for.

### 4.4 No numerical consequences of representation choice
The book has a "sparsity view" as one of its six views, but nowhere discusses conditioning,
scaling, per-unit choice and Jacobian structure, fill-in cost, or solver behaviour. Panel 6 of the
main figure is decorative. For an audience of *numerical* modellers, "which representation should
I choose" without "what does it cost to solve" is half an answer. One chapter — conditioning of
4-wire vs neutral-eliminated 3-wire, fill-in counts under elimination, the per-unit/SI scaling
trade-off — would materially strengthen the book and is well within reach given the fixture.

### 4.5 No data-model crosswalk
`BOOK_PLAN.md:182–188` promises "software and information-model crosswalks". There is none. A
table mapping the book's objects (bus / terminal / junction / port / factor / winding / grounding
/ member identity) to CIM/CGMES classes, PMD `ENGINEERING` fields, OpenDSS objects, and MATPOWER
columns would be the highest-value single page in the whole book for practitioners, and it is
achievable now.

### 4.6 Rating semantics are argued about but never defined
The entire parallel-line argument turns on ratings, yet there is no reference section
distinguishing continuous vs emergency vs ambient-adjusted ratings, conductor vs terminal-equipment
limits, current vs apparent-power vs thermal-state limits, or CT/relay-imposed limits. The book
repeatedly says "a scalar edge rating replaces several limits" without ever enumerating the
several.

### 4.7 State estimation, protection, contingency, measurements
Promised in the reader promise (`BOOK_PLAN.md:60–71`) and Part IV; entirely absent. The running
network declares measurements and protection zones and then marks them "semantic-only". That is
honest, but the front matter should say plainly which reader promises the current draft does not
yet keep.

---

## 5. Internal inconsistencies

| # | Location | Inconsistency |
|---|---|---|
| I1 | `BOOK_PLAN.md:269` | "not all 42 chapters" — the plan lists **51** numbered chapters. |
| I2 | `index.md:100–107` / `QUALITY_CONTROL.md:8–16` / `claims.toml` | Three different epistemic taxonomies: 5 labels / 7 categories / 3 statuses actually used. |
| I3 | `index.md:100–107` | The five epistemic labels are declared and then **never used anywhere in the text** (zero occurrences outside `index.md`). |
| I4 | `cases/multiconductor-parallel-ac-decision.md:157` | "six fewer" vs. eight (§2.2). |
| I5 | `assets/running-network-views.png` panel 3 vs `representation-maps.md:224` | The figure draws `x1` as a vertex with three edges *inside the bus–branch multigraph panel*; the text says the three-winding transformer is "not an ordinary edge without compilation" and "outside this quotient's domain until compilation". The figure silently performs an unlabelled star compilation, and panels 3 and 4 then look near-identical for `x1` — undercutting "six non-isomorphic views". |
| I6 | `parameterized-transformer-tap-decisions.md:141–146` vs `cases/transformer-tap-ac-decision.md:83–88` | Adjacent chapters select **opposite** taps for the same transformer (1.05 optimal / 0.95 infeasible, then 0.95 optimal / all feasible) with no sentence explaining that the boundary condition changed from a fixed-voltage witness to a network embedding. Reads as a contradiction. |
| I7 | `cases/running-network.md:141–150` vs `data/running-network/v0.1.0.json` | The spec declares a controllable tertiary injection `g_2` at `i_6`; the fixture has **only `g1`**. The fixture has a load **`d4`** with no counterpart in the spec, and a second shunt **`href`** never named in the spec's object list. None of this appears in "What remains semantic-only" (`executable-running-network.md:109–116`), which mentions only switching, contingency, investment, measurements and protection. |
| I8 | `BOOK_PLAN.md:243` vs the figures | "Colour may aid reading but never carries meaning that is unavailable in monochrome." In `five-bus-transformation-map.png` the merged edge `e_ij` is distinguished **only** by being green; in `running-network-views.png` panel 3 the transformer-incident edges are distinguished **only** by being orange. Both fail in monochrome. |
| I9 | `README.md:22` vs `cases/transformer-tap-ac-decision.md:168–173` | "independently reproduced" without the chapter's qualifier (§3.2). |
| I10 | `BOOK_PLAN.md:248–257` vs the drafted cases | One-running-network policy vs five bespoke case networks (§3.5). |

---

## 6. Logic flow and justification

**The macro arc is missing one step.** Current: (1) one network yields many graphs → (2) naive
simplification destroys decisions → (3) here is a certificate discipline. Missing: (4) *and here
is when the simplification is exactly right, and what it buys you*. Without (4) the book cannot
deliver its own reader promise ("choose a representation for a declared study") because it never
demonstrates a *choice* — only refusals. Add §4.1 and one chapter that walks a study question →
candidate representations → selection → validity check.

**"Start here" is four times too long.** Eleven pages, ~7,000 words, containing four escalating
versions of the same parallel-branch counterexample, before the reader reaches "Scope and thesis".
Recommended: Start here = *One network, many graphs* → *five-bus* → *first failure* → *Scope and
thesis* → *running network*. Move the three parallel AC cases and the tap case into a "Worked
cases" part with a one-paragraph pointer from the first-failure chapter.

**The parallel-line message is stated in nine places.** `index.md`, `one-network-many-graphs.md`,
`scope-and-thesis.md`, `five-bus-cycle-spaces.md`, `first-failure-parallel-branches.md`,
`cycles-parallelism-radiality.md`, `guarded-normalization.md`, and three case chapters. State the
mechanism once, in full, and cite it thereafter. Currently ~40% of the drafted evidence base
addresses one narrow phenomenon, while framing implies broad coverage.

**Editorial process leaks into reader-facing text.** `translation-traps.md:279–300` ("Priority for
the next drafting passes… The first pass through the book will enforce ten translations"),
`orientation-terminal-power.md:239–244` ("Every chapter using an arrow must say…"),
`kron-ward-opti-kron.md:407–417` ("Required next results"), and the "Purpose and status" preambles.
Instructions to the author belong in `CONTRIBUTING.md`/`ROADMAP.md`; a reader does not need to know
your drafting order. Keep the *status* declarations (those are scientifically valuable), drop the
*to-do* declarations.

**Justification quality is uneven.** Definitions and scope statements are excellent; derivations
are correct where I checked them (I verified the five-bus incidence matrix, `AC = 0`, both cycle
ranks, the bridge set, the series composition `Z₁ + PᵀZ₂P`, the constraint intersection
`C₁ ∩ PᵀC₂`, the phase-to-neutral congruence, the phase-to-phase kernel and residual, the Kron
affine term and recovery, the `Z_B` round trip and the `n=2` sanity check of `Y_x^w`, the
two-bus DC OPF optima, the loop-impedance closed form `z = (10/11)z_1`, and the served-fraction
and MW arithmetic in the tap case). What is missing is the *connective* justification: why this
rule rather than another, what a reader should do differently on Monday morning.

**Prose register is a real adoption barrier.** Noun stacks like *"executable parallel-branch,
conductor-, transformer-winding-, reference-invariant multiwinding-leakage-, terminal-assembly-,
fixed-linear transformer-completion-, parameterized tap-decision-, solver-backed and independently
reproduced transformer-network-, degree-two-series, and composed preservation certificates"*
(`README.md:22`) are unreadable. The technical content deserves plainer sentences.

---

## 7. Is there an audience?

Yes — three, and the book is currently addressed to none of them squarely.

**A. Unbalanced/distribution modelling researchers and tool builders** (PowerModelsDistribution,
OpenDSS/DSS-Extensions, OpenDSSDirect, GridLAB-D, CIM implementers). *Strongest fit.* They hit
conductor ordering, neutrals, grounding, multiwinding compilation and provenance every week and
have no vocabulary for it. Serve them with §4.2 (earth model), §4.5 (crosswalk), and the
node–breaker chapter.

**B. OPF/optimization researchers.** The constraint-lifting and redundancy-certificate material is
directly usable and directly publishable. This audience will not read a 51-chapter book but will
cite two papers extracted from it.

**C. Network-model-exchange and standards people** (CIM/CGMES, IEC 61970/61968, TSO/DSO model
handover). The certificate/provenance discipline is exactly their problem. They need §4.5 before
they can engage at all.

**Not currently served:** transmission planners (nothing actionable yet, and the tone reads as
critique — §4.1 fixes this); category-theory/formal-methods readers (the categorical content is a
list of open problems, not a result — either recruit a collaborator or stop advertising it).

**Strategic recommendation.** A 51-chapter monograph from a single author, with 20 chapters
drafted and the central architecture untested, is a high-risk first output. Extract three papers
first — (i) multiconductor parallel-member limit redundancy (`TR-PAR-005/006/007`, a clean
contribution), (ii) the transformation-certificate schema and composition law, (iii) reference-
invariant multiwinding leakage compilation and the tap-decision result — then consolidate. Peer
review on the papers will also supply the independent verification the ledger currently lacks.

---

## 8. Diagrams to add

The book is under-illustrated for its subject, and the four existing figures do real work. Ten
concrete additions, in priority order:

1. **The map of maps** (front matter, one page). Frameworks as nodes (`𝔄`, `𝔓`, `G_M`, `G_s`,
   equations, sparsity); arrows labelled `Q_MS`, `C_PM`, `C_PE`, `S_EM`, `R_∂`, `Λ`; linestyle =
   exact / lossy / state-dependent; drawn deliberately as a non-linear poset so the "no ladder"
   claim is *visible*. Right now the reader must assemble this from a table in
   `representation-maps.md`. This is the book's missing cover image.
2. **The four-wire ladder with earth as an explicit node.** Terminals a,b,c,n plus an earth rail,
   grounding impedances, distributed shunts; three overlays showing what `T` (phase-to-neutral),
   `P` (phase-to-phase) and neutral-Kron each delete. This is the diagram the book most needs and
   does not have, and it directly addresses §4.2 and §2.7.
3. **Transformer factor anatomy.** 11 terminals → `A_x` → 9 coil coordinates → `T_x` → `Y^coil` →
   back out through `B_xᴴ`, with excitation and internal-ground branches drawn as separate
   stamps, and an arrow showing where the coil-current limit is enforced and where the recovery
   map re-enters. Five transformer chapters are currently pure algebra; one block diagram would
   carry all of them.
4. **Feasible-set geometry in the complex plane.** Replace the 1-D interval bar in
   `five-bus-feasible-sets.png` with the actual discs `|Y_1 ΔU| ≤ I₁ᵐᵃˣ`, `|Y_2 ΔU| ≤ I₂ᵐᵃˣ` and
   the summed constraint in the `ΔU` plane. Then reuse the same frame for the containment test:
   one ellipse inside another, plus the degenerate cylinder case. That makes the PSD test and the
   polydisc row norm visual rather than algebraic.
5. **A rendered preservation-contract card**, identical in layout, repeated at the head of every
   transformation chapter (source / target / preconditions / preserves / forgets / recovery /
   classification / verification state). Currently the contract table appears in exactly one
   chapter. This is the book's brand element and it is unused.
6. **Kron fill-in.** Before/after `Y_bus` spy plot plus the corresponding graph on a small
   example, with nonzero counts — "fewer variables, denser matrix" in one picture. Supports §4.4.
7. **Provenance lineage for one object.** `ℓ₂` → normalized → composed → target, with certificate
   IDs on the arrows and the recovery path drawn backwards. Makes `TR-COMP-001` concrete.
8. **Active-state radiality, three panels.** Inventory multigraph → active state → simple
   projection, with the two radiality predicates disagreeing in the middle panel. The witness
   already exists in JSON with no figure.
9. **Question × view matrix.** The table in `one-network-many-graphs.md:84–92` rendered as a
   filled/empty grid — the closest thing the book has to a decision aid for its own reader.
10. **Replace panels 5 and 6 of `running-network-views.png` with real generated structures** — the
    actual bipartite variable–constraint graph and the actual `Y_bus`/Jacobian spy plot from the
    fixture. They are currently schematic, which quietly weakens the "every view is generated from
    the source with a source map" claim that the same page makes.

**Figure grammar.** Declare one, once, and enforce it: *shape* = object class (circle = junction,
box = factor/device, rounded = generated object), *fill* = source vs generated, *linestyle* =
active vs inactive vs forgotten. Colour may reinforce but must never be the only carrier — which
is your own rule (`BOOK_PLAN.md:243`) and is currently violated twice (§I8). Every figure caption
should state the *claim* the figure supports, not describe the picture.

---

## 9. Prioritized next actions

1. **Write "When the general model collapses."** Derive the balanced/positive-sequence case from
   `ℓ_3` in the running network, with guards and a quantified residual. Converts the book from
   critique to theory. (§4.1)
2. **Fix the Kron covariance proposition** and add the reciprocity-is-not-coordinate-invariant
   corollary. (§2.1)
3. **Split `status` into `claim_type` + `verification`, and render verification state in every
   chapter.** (§3.1)
4. **Add the earth/ground model section**, and reconcile it with the single-ideal-ground
   assumption in every executable model. (§4.2)
5. **Add the CIM / PMD / OpenDSS / MATPOWER crosswalk table.** Highest practitioner value per page
   in the book. (§4.5)
6. **Fix the ten internal inconsistencies in §5**, especially I5 (figure vs text on the
   transformer), I6 (opposite tap selections) and I7 (fixture vs spec drift). I7 in particular
   should be caught by an automated check, since the repo already validates view maps against the
   fixture.
7. **Restructure "Start here"** to five pages; move the three AC parallel cases into a worked-cases
   part. (§6)
8. **Add conditioning/backward-error fields to the redundancy certificates** and a rejection
   margin. (§2.3)
9. **Instantiate the running network in `𝔓`** with real factor relations and one `Λ` link — or
   demote the architecture claim everywhere. (§3.3)
10. **Extract paper (i)** — multiconductor parallel-member limit redundancy — and submit it. It is
    ready, it is new, and external review is the fastest route to the independent verification the
    ledger is missing. (§7)

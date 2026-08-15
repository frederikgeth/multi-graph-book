# Independent technical review: four highest-risk claims

**Packet reviewed:** `review/archive/independent-review-packet-2026-08-14.md`
**Review date:** 2026-08-15
**Environment:** Julia 1.12.6, `--startup-file=no`, `--project=experiments`, macOS (darwin 25.6.0)
**Scope:** the four listed claims only. This is not a general editorial review, and it
does not assess global OPF optimality, universal physical realizability, or package adapters.

## Method

For each claim I read the chapter, inspected the cited artifact, ran the listed reproduction
test, and then **re-derived the mathematical content independently** in a separate script rather
than relying on the repository's own assertions. Independent scripts are recorded inline below so
the checks can be repeated without this repository's test harness.

## Reproduction status

All five packet commands pass in a clean invocation:

| Test | Result | Packet record |
| --- | ---: | --- |
| `typed_kron.jl` | 20 / 20 | 20 / 20 ✓ |
| `running_network_typed_kron.jl` | **13 / 13** | 7 / 7 — **stale** |
| `multiconductor_parallel_ac.jl` | 41 / 41 | 41 / 41 ✓ |
| `series_elimination.jl` | 15 / 15 | 15 / 15 ✓ |
| `transformer_winding_normalization.jl` | 10 / 10 | 10 / 10 ✓ |

Two packet statements are stale and should be refreshed before the packet is sent to an external
reviewer:

1. the `running_network_typed_kron` count (7 → 13);
2. the TR-KRON-001 scope caution states the running-network witness "does not add shunts", but
   `running-network-typed-kron-witness.json` now contains a `neutral_shunt_witness` block and a
   `shunt_internal_block_is_invertible` check.

---

## TR-KRON-001 — typed Kron reduction and power-dual coordinate actions

**Decision: revise.** Issue class: **semantic** (primary), **mathematical** (secondary).
Non-blocking for the theorem; blocking for the claim record.

### What I verified

I re-derived the covariance identity from scratch on random reciprocal complex data
(`/tmp/indep_kron.jl`), independently of `TypedKronReduction.jl`:

```
per-port block-diagonal   |Ỹ_K − T_B^H Y_K T_B| = 8.11e-15   |ṽ_I recovery| = 6.11e-16   |ĩ_B dual| = 3.21e-15
dense within B and I      |Ỹ_K − T_B^H Y_K T_B| = 2.47e-14   |ṽ_I recovery| = 1.53e-15   |ĩ_B dual| = 2.52e-14
```

The proposition, its affine-injection covariance, and the internal-voltage recovery identity are
**mathematically correct**. The implementation in
`package/GraphModelsForPowerNetworks/src/TypedKronReduction.jl` matches the chapter: `TB'` is
Julia's adjoint, so `Ỹ_XY = T_X^H Y_XY T_Y`, `ṽ_B = T_B^{-1} v_B`, `ĩ_I = T_I^H i_I`, exactly as
stated.

### Issue 1 — the block-diagonality hypothesis is stronger than the proof requires (mathematical)

The second row above uses `T_B` and `T_I` that are **dense** within their partitions, and the
identity still holds to 2.5e-14. Block-diagonality is therefore not a mathematical requirement.
What the proof actually needs is only that the coordinate change respect the **B/I partition**,
i.e. `T = diag(T_B, T_I)` with no B–I mixing.

Per-port block-diagonality within `B` and within `I` is a *modelling* restriction — it keeps the
action local to each port so that port identity and the retained/eliminated partition survive. The
chapter and the claim record present it as a hypothesis of the theorem, which will mislead a
reader into thinking a dense per-subsystem coordinate change is disallowed.

**Suggested wording.** Replace "invertible, block-diagonal changes of retained and internal
terminal coordinates" with:

> Let `T = diag(T_B, T_I)` be invertible and block-diagonal **with respect to the retained/internal
> partition**. Per-port block-diagonality of `T_B` and `T_I` is an additional modelling
> restriction that keeps the action local to each port; the identity below does not require it.

### Issue 2 — the fixed internal-injection assumption is missing from the claim record (semantic, blocking)

`claims.toml` records assumptions as *"retained and internal coordinate actions are invertible and
block diagonal; the internal admittance block is invertible; current coordinates use the
conjugate-transpose power dual."* It does **not** state that `i_I` is fixed and independent of
`v_I`. That assumption is load-bearing: the whole affine term `K_I i_I` collapses without it. My
check confirms the sensitivity — substituting a constant-power internal injection
`i_I(v_I) = (S_I ⊘ v_I)*` at the same operating point gives an injection differing from the fixed
one by 112% in norm.

The chapter inherits the assumption from the preceding proposition, and `model_scope` says "linear
nodal relations", which arguably excludes constant-power devices. But a reviewer reading only the
ledger row cannot see it. **Add to `assumptions`:** *internal injections `i_I` are fixed data,
independent of `v_I`; voltage-dependent internal injections are outside this claim.*

### Issue 3 — the reciprocity corollary can be sharpened (presentational)

The corollary as written is correct. I verified all three cases:

```
Y_K complex-symmetric?      true      (Kron reduction preserves reciprocity)
T^H Y_K T sym, complex T?   false
T^H Y_K T sym, real T?      true
T^T Y_K T sym, complex T?   true
```

The sharper and more useful statement for this claim is the two-part one:
**Kron reduction preserves reciprocity in physical coordinates; the power-dual coordinate action
does not, for complex `T`.** Those are different operations and the corollary currently mixes them
into one sentence about congruence.

### Scope confirmed

The claim is a finite-dimensional linear result. The running-network witness is a legitimate
application (four-conductor line split at a midpoint, with a neutral shunt variant) but adds no
generality to the theorem. Recorded residuals (2e-15 boundary, 7e-17 recovery) are consistent with
double precision. Neither artifact records a condition number for `Y_II` or `T`; for a claim
verified numerically that should be added, though it does not affect the theorem.

---

## TR-PAR-004 — multiconductor parallel-line feasible set and limit preservation

**Decision: accept.** Issue class: **presentational** only. Both recommendations non-blocking.

### What I verified

I re-derived the case from the chapter's stated data alone, without running the repository's
model (`/tmp/indep_par.jl`, `/tmp/indep_par2.jl`).

- `Y₂ = 0.1 Y₁` holds exactly from `Z₂ = 10 Z₁`.
- Phase-to-neutral loop impedances `z₁ = 0.06 + 0.12j`, parallel `z = 0.0545454… + 0.1090909…j`,
  matching the chapter's `0.05454545 + 0.10909091j`.
- I derived the current-limited quadratic from the physics independently
  (`e^{-jθ} = αs/C + zC`, then `|·|² = 1`), obtaining the chapter's stated form. Solving it:

| Case | `C` | `v` | `α` | Chapter |
| --- | ---: | ---: | ---: | --- |
| source / lifted / pruned | 0.66 | 0.9485579 | 0.6138908 | 0.6138908, 0.9485579 ✓ |
| naive summed-limit | 1.20 | 0.9034471 | 1.0630833 | 1.0630833, 0.9034471 ✓ |

Agreement to all seven reported significant figures, from an independent derivation. The
certificate's `objective_served_fraction = 0.6138907961267441` and
`load_voltage_magnitude_pu = 0.9485579228182409` are consistent.

### The two structural claims check out

**Is the summed-limit aggregate genuinely a relaxation?** Yes. Every source-feasible point
satisfies `|I₁ + I₂| ≤ |I₁| + |I₂| ≤ 1.2` by the triangle inequality, so the projection of the
source feasible set onto `(U_j, α)` is contained in the aggregate's. The containment is strict:
the naive optimum requires `|I₁| = 1.2/1.1 = 1.0909 > 0.6`. Outer relaxation confirmed.

**Is the pruning exact?** Yes. `|I₂| = 0.1|I₁| ≤ 0.06 < 0.6` for every source-feasible point, so
the member-2 constraints are implied and their removal cannot change the feasible set.

**Is the current limit really the binding constraint?** The chapter asserts this via a derivative
argument. I checked it directly by tracing `α(C)` to the nose:

```
C:    0.5     0.66    1.0     1.2     2.0     3.0     4.0     5.0     6.0
α:  0.4714  0.6139  0.9026  1.0631  1.6308  2.1555  2.4450  2.4618  2.1592
max α ≈ 2.4618 at C ≈ 5.0
```

Both `C = 0.66` and `C = 1.2` lie well below the nose, so `dα/dC > 0` at both and the current cap
binds in each formulation. The voltage bounds `[0.70, 1.05]` are interior at both solutions
(0.9486, 0.9034) and are not binding, as the chapter states.

### Recommendation 1 (non-blocking, presentational)

The ledger `assumptions` field does not record the branch selection or the local-solve caveat,
although the chapter does. Add: *values are for the traced high-voltage power-flow branch; Ipopt
returns `LOCALLY_SOLVED` and no global-optimality claim is made.* The claim text "have objective
0.6138908" otherwise reads as definitive.

### Recommendation 2 (non-blocking)

`exactness` of the pruning rests on **exact** proportionality by construction. Real member data
would be near-proportional at best, requiring the general PSD/row-norm test. The chapter says this;
the ledger row would be stronger if it did too.

---

## TR-SER-001 — degree-two series elimination assumptions

**Decision: revise.** Issue class: **mathematical**. **Blocking.**

This directly answers the packet's question — *does zero-injection degree-two elimination require
any additional mutual-coupling or boundary assumptions beyond those stated?* **Yes, two.**

### Finding 1 — mutual coupling *between the two eliminated sections* is not excluded, and it invalidates the stated formula

Guard 6 reads "neither element participates in omitted external mutual coupling". Whether coupling
between `ℓ₁` and `ℓ₂` themselves counts as "external" is ambiguous, and it is the physically
likely case: two sections of the same corridor.

If `Z₁₂ ≠ 0`, the correct composite is

```
Z_eq = Z₁ + Z₁₂ P + Pᵀ Z₂₁ + Pᵀ Z₂ P
```

not `Z₁ + Pᵀ Z₂ P`. I constructed a two-conductor witness with plausible coupling magnitudes
(`/tmp/indep_ser_xfmr.jl`):

```
‖Z_eq(stated) − Z_eq(true)‖ = 0.2766
relative error              = 11.65%
```

The implementation cannot express or detect this case. `SeriesElement` has no cross-coupling
field, and the only coupling declaration is `JunctionContext.external_couplings` — a free-text
list attached to the **junction**, while mutual coupling is a property of an **element pair**. The
guard therefore cannot fire for the configuration that breaks the formula.

**Suggested wording** for the guard table:

> neither element participates in mutual coupling with any other element **or with each other**;
> if the two sections are mutually coupled, the exact composite is
> `Z₁ + Z₁₂P + PᵀZ₂₁ + PᵀZ₂P` and this rule does not apply.

**Suggested implementation change:** move the coupling declaration from `JunctionContext` to the
element pair, and add an explicit `mutual_coupling` field to `SeriesElement` so the guard can
reject rather than silently accept.

### Finding 2 — the series-only element class is a precondition, not a guard (semantic)

The chapter's guard table reads as a complete list of conditions. It is not: the derivation also
requires both elements to be **series-only**. In the implementation this is enforced by the type —
`SeriesElement` carries only an `impedance` matrix and has no shunt field — so a nominal-π element
cannot be constructed. That is sound engineering, but it means a reader with π-data can satisfy
guard 4 ("no shunt or grounding at `b`", a property of the junction) while violating an unstated
assumption about the elements. Half of a π-element's shunt sits at `b` and is *inside the factor*,
not "at `b`" as a separate object.

Add a precondition row above the guard table: *both source elements are series-only multiconductor
factors; nominal-π or shunted members require a different rule.*

### What I confirmed as correct

- The algebra `Z_eq = Z₁ + Pᵀ Z₂ P` is exact under the stated assumptions (re-derived by hand).
- `permutation_matrix` builds `P` with `x₂ = P x₁`, matching the chapter's
  `I_{ℓ₂bj} = P I_{ℓ₁ib}` convention; `impedance = first.impedance + transpose(P)*second.impedance*P`
  matches the displayed formula.
- `aligned_limit` implements `C_eq = C₁ ∩ Pᵀ C₂` as a componentwise minimum, correctly.
- The grounding counterexample and its `junction_has_shunt_or_grounding` rejection are correct.
- The refusal to classify the target as a homogeneous physical line is appropriate and well handled
  (`exact_behavioral_composite_not_a_homogeneous_physical_line`).

---

## TR-XFMR-001 — transformer winding-coordinate normalization

**Decision: revise.** Issue class: **presentational** and **semantic**. Mathematics accepted;
certificate content blocking.

### What I verified

I built WYE and DELTA incidence matrices independently and tested the normalization, including the
dual current action that the chapter does not state (`/tmp/indep_ser_xfmr.jl`):

```
grounded wye   coil-voltage residual = 0   terminal-current dual residual = 0   power residual = 1.24e-16
delta          coil-voltage residual = 0   terminal-current dual residual = 0   power residual = 1.15e-16
```

`Â = A Pᵀ` is the **correct** typed normalization. Because `P` is a permutation, `Pᵀ = P⁻¹`, so
`Â Û = A Pᵀ P U = A U` exactly, for both grounded-wye (neutral-differencing rows) and delta
(line-to-line rows). The dual current action `Î = P I` and complex-power invariance
`⟨Û, Î⟩ = ⟨U, I⟩` both hold to machine precision.

I also confirmed the chapter's warning that a `delta_roll`-style **row** relabelling is not
equivalent to the **column** action:

```
A·Pᵀ            = [0 1 −1; −1 0 1; 1 −1 0]
row-shifted A   = [−1 0 1; 1 −1 0; 0 1 −1]     (different matrix)
```

That is a correct and useful caution, and it is the substantive content of the claim.

### Issue 1 — the current/dual action is absent from the certificate (semantic, blocking)

`transformer-winding-normalization-certificate.json` records only voltage relations:

```
constraint_map: A_target = A_source·P' ;  u_target = P·u_source ;  coil_limits unchanged
recovery_map:   A_source = A_target·P  ;  u_source = P'·u_target
```

There is no `i_target = P · i_source` entry, and no statement of the `Â^T = P A^T` dual. For a
claim about *typed-factor* normalization this is an omission: the factor is a two-sided object and
only one side is certified. It also matters practically — **terminal-indexed** currents and limits
do permute, even though coil-indexed limits do not, and the certificate's statement that limits
are "unchanged" is true only for the coil coordinates.

**Suggested addition:** `constraint_map.terminal_current = "i_target = P · i_source"`, plus a note
that terminal-indexed limits permute while coil-indexed limits do not.

### Issue 2 — `preserves: all_declared_source_semantics` is not falsifiable (presentational, blocking)

The `preserves` list is `["all_declared_source_semantics", "winding_terminal_to_coil_voltage_relation",
"winding_connection_semantics", "coil_current_limits", "transformer_and_winding_identity"]`. The
first entry is a blanket claim of a kind no other certificate in the repository makes, and it
cannot be checked. The remaining four are specific and adequate. Delete the first entry.

### Issue 3 — `evidence.checks` is empty (presentational)

Unlike the typed-Kron and running-network artifacts, this certificate's `evidence` contains only
the matrices and orders; `checks` is `{}`. The test file has ten passing assertions whose outcomes
are not recorded in the artifact. An external reviewer reading the artifact alone sees no
verification record.

### Scope confirmed

Compact vector-group serialization and grounding conventions are correctly excluded. The claim's
`unresolved_issue` ("prove which normalized factors can be serialized back into compact
vector-group and delta-roll fields without loss") is the right open question and is well stated.

---

## Reviewer record

| Claim | Reviewer | Date | Decision | Issue class | Notes |
| --- | --- | --- | --- | --- | --- |
| `TR-KRON-001` | Claude (Opus 5), automated independent re-derivation | 2026-08-15 | revise | semantic / mathematical | Identity verified independently. Block-diagonality is stronger than the proof needs; fixed-`i_I` assumption missing from the ledger row (blocking). |
| `TR-PAR-004` | Claude (Opus 5), automated independent re-derivation | 2026-08-15 | accept | presentational | Closed form re-derived from first principles; all reported figures reproduced to 7 s.f. Relaxation, pruning, and binding-constraint claims all confirmed. Two non-blocking wording additions. |
| `TR-SER-001` | Claude (Opus 5), automated independent re-derivation | 2026-08-15 | revise | mathematical | **Blocking.** Mutual coupling between the two eliminated sections is not excluded by the guard and breaks the stated formula (11.65% error in a plausible witness); the implementation cannot express it. Series-only element class is an unstated precondition. |
| `TR-XFMR-001` | Claude (Opus 5), automated independent re-derivation | 2026-08-15 | revise | semantic / presentational | Mathematics correct for WYE and DELTA including the current dual and power invariance. Certificate omits the current map, asserts an unfalsifiable `all_declared_source_semantics`, and records no checks. |

**Reviewer independence caveat.** This review was produced by an automated reviewer working from
the repository contents. It re-derived each result independently rather than accepting the
repository's assertions, and it ran every listed test. It is not a substitute for review by a
named human domain expert, and the `reviewer` fields in `claims.toml` should record that
distinction rather than treating this pass as external peer review.

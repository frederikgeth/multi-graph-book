# [Federated scientific knowledge: end-to-end trace](@id federated-knowledge-trace)

**Page status:** maintained cross-repository implementation trace and scope boundary.

This page traces five scientific statements from book evidence to executable BMOPFTools guardrails and back into the book's existing LLM context packets. The stable ownership rules are defined in the repository-root `ARCHITECTURE.md`; this page is the worked implementation trace.

## First trace: parallel member limits

### The linked objects

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000001` | this book | States the scoped result and what it does not establish |
| Claims | `TR-PAR-001`, `TR-PAR-002`, `TR-PAR-003` | this book | Bind the statement to certificates and source passages |
| Misconception | `parallel-admittance-implies-decision-equivalence` | this book | Routes the dangerous shortcut to mandatory evidence |
| Executable contract | `parallel_member_limit_preservation` | BMOPFTools | Decides the supported scalar case or explicitly refuses it |
| API operation | `check_parallel_member_limit_preservation` | BMOPFTools | Exposes the contract as a structured result |
| JSON execution operation | `check-contract` | BMOPFTools | Returns a versioned response with input hashes and the four-status contract result |
| Executable recipe | `parallel_member_limits` | BMOPFTools | Runs the minimized fixture through the JSON-ready execution API |
| Counterexample fixture | `parallel-rating-outer-relaxation-001` | BMOPFTools | Reproduces a minimized negative witness |
| Finding | `W.CONTRACT.PARALLEL_MEMBER_LIMIT_LOSS` | BMOPFTools | Reports loss of the member-constrained feasible region |

The same identifiers appear in two exports, but their contents do not have two owners. `generated/scientific_knowledge.jsonl` describes the scientific object. BMOPFTools' `generated/executable_knowledge.jsonl` describes code, Findings, and fixtures. `generated/federated-knowledge-pair-manifest.json` pins the matching export hashes and checks that both sides agree on their shared IDs.

### Scientific statement and evidence

`PSK-000001` states that summing fixed linear parallel admittances preserves the unconstrained aggregate terminal relation, while giving the aggregate the sum of member ratings can relax the member-constrained feasible set. Its declared scope is fixed-linear members with common endpoints and voltage coordinates, retained admittances, and explicit current limits.

The record deliberately does **not** establish that all parallel aggregation is invalid, that every aggregate rating is an outer relaxation, or that a scalar witness proves the multiconductor or state-dependent case. The claims and generated book artifacts remain the evidence authority; the package does not independently rewrite that conclusion.

### Executable decision

BMOPFTools receives an explicit mapping from source members to a target aggregate. In its current supported domain it requires scalar, finite, nonzero, series-only impedances, common terminal coordinates, and scalar ratings. It then performs two distinct checks:

1. It verifies that the target admittance equals the sum of the source-member admittances. Failure produces `E.CONTRACT.PARALLEL_TERMINAL_RELATION_MISMATCH`.
2. If terminal behavior is preserved, it compares the exact scalar voltage-drop region induced by every source member rating with the target aggregate-rating region. An inner restriction or outer relaxation produces `W.CONTRACT.PARALLEL_MEMBER_LIMIT_LOSS`.

Missing mapped data produces `W.CONTRACT.INDETERMINATE`. Multiconductor, shunted, singular, or otherwise out-of-domain cases produce `I.CONTRACT.NOT_APPLICABLE`. Those statuses are part of the scientific behavior: the implementation refuses to silently generalize beyond its declared domain.

The same check is available as the source-hash-bound BMOPFTools recipe
`parallel_member_limits`. The pinned pair manifest carries its command,
expected status, expected Finding codes, and recipe source hash. Context packets
therefore expose a directly runnable implementation example without making the
book execute a sibling checkout or copying the package implementation into the
scientific corpus.

For the minimized fixture, the two source lines have resistances 0.1 Ω and 1 Ω and ratings of 100 A each. Their summed admittance is 11 S, so the target resistance is 1/11 Ω. A naïve 200 A aggregate rating permits a voltage drop of about 18.18 V, while the source members permit only 10 V. At the committed 15 V witness, aggregate current is 165 A, but member currents are 150 A and 15 A. The target accepts the point while the first source member is overloaded. The exact scalar target rating is 110 A, not 200 A.

### Retrieval and answer contract

A query such as “Can a preprocessing pass merge parallel branches by summing admittance and capacity?” follows the existing misconception router. The context packet makes the three claims, three vocabulary concepts, and `knowledge:PSK-000001` mandatory. It retains the existing `qualified`, `under_retrieved`, and `unsupported` statuses and source-hash checks.

The packet now also exposes explicit sections:

- `scientific_basis` for the scoped PSK statement and evidence status;
- `known_misconceptions` for the tempting shortcut and required qualification;
- `counterexamples` for book artifacts and stable fixture identities;
- `executable_checks` for the BMOPFTools repository, contract IDs, Finding codes, fixtures, and implementation status;
- `implementation_examples` for concrete executable fixtures and pinned recipes; and
- `unresolved_boundaries` for every claim the scientific object says it does not establish.

These are structured views over mandatory records, not a second retrieval index. The deterministic corpus, release identity, source hashes, retrieval evaluation, MCP route, HTTP route, and CLI route remain the book's established machinery.

BMOPFTools also provides a separate read-only MCP stdio adapter for the six
settled package execution operations. Connecting both servers gives an agent a
book-owned retrieval route and a package-owned execution route; it does not
merge their authority or allow an execution result to silently upgrade a book
claim. The federated recipe pins include the adapter source files, so changes
to that transport invalidate the paired source hashes.

## Second trace: neutral, ground, and reference

The second slice reuses the same cross-repository mechanism for a model-semantics
failure. Its stable chain is:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000002` | this book | States which neutral, grounding, earth-return, and reference relations are distinct |
| Claims | `GROUND-SCOPE-001`, `GROUND-SCOPE-002` | this book | Bind the definition and scoped grounding witness to canonical prose |
| Misconception | `ground-neutral-reference-are-one-node` | this book | Routes the tempting node-0 normalization to mandatory qualification |
| Executable contract | `neutral_ground_reference_preservation` | BMOPFTools | Compares supported representation relations across an explicit bus mapping |
| API operation | `check_neutral_ground_reference_preservation` | BMOPFTools | Returns a structured four-status contract result |
| Executable recipe | `neutral_ground_reference` | BMOPFTools | Runs the minimized fixture through the JSON-ready execution API |
| Counterexample fixture | `neutral-ground-reference-conflation-001` | BMOPFTools | Reproduces continuity and grounding-relation loss on two buses |
| Findings | `E.CONTRACT.NEUTRAL_CONTINUITY_MISMATCH`, `E.CONTRACT.GROUND_REFERENCE_RELATION_MISMATCH` | BMOPFTools | Separately report the two invalid identifications in the fixture |

`PSK-000002` states that an explicit neutral conductor, a finite grounding
relation, a physical earth-return model, and a mathematical voltage reference
are distinct objects. The book owns that definition and the recorded comparison
between floating, finite-impedance, and ideal customer-end grounding. The
package fixture is executable evidence for one concrete transformation, not a
promotion of that fixture into a theorem.

In the fixture source, a phase/neutral feeder connects the source and load
buses. The source neutral is perfectly grounded, while the load neutral has a
finite 0.1 S grounding shunt. The unsafe target retains both simple bus records
and their `n` labels, but removes neutral continuity from the feeder and marks
the load neutral as perfectly grounded. The contract therefore emits two
findings: one for the changed neutral-continuity graph and one for replacing the
finite grounding relation with a perfect local ground. An exact target may
rename the feeder and shunt while preserving all three checked representation
dimensions.

The contract explicitly does not establish electrical terminal equivalence,
explicit-earth-conductor behavior, soil or electrode behavior, grounding-asset
identity or state, fault current, touch voltage, or protection operation. It
returns `inapplicable` for unsupported coupled grounding models and
`indeterminate` when mapped evidence is unavailable.

The source-hash-bound `neutral_ground_reference` recipe makes this second
transport mapping directly runnable. Its pinned command, expected `failed`
status, two expected Finding codes, and source hash are carried by the federated
pair manifest. Context packets therefore expose a concrete operation without
copying BMOPFTools behavior into the book or inferring the bus mapping from
matching names.

Queries from all three audience routes for
`ground-neutral-reference-are-one-node` now make `knowledge:PSK-000002`
mandatory. Their context packets expose the scoped scientific basis, linked
counterexample, implemented BMOPFTools contract, pinned recipe, dedicated
Finding codes, and the unresolved dimensions without changing the deterministic router or its
`qualified`, `under_retrieved`, and `unsupported` semantics.

## Third trace: solver termination and solution validity

The third slice tests an invalid scientific inference about numerical evidence:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000003` | this book | Separates algorithm status from independently validated solution evidence |
| Claims | `NUMERICAL-001`, `NUMERICAL-004` | this book | Require residual/error evidence and define the solution-validation boundary |
| Misconception | `solver-termination-implies-validated-solution` | this book | Routes successful-status shortcuts to mandatory qualification |
| Executable contract | `claimed_solution_validity` | BMOPFTools | Checks the initial supported dimensions of a claimed-feasible result |
| API operation | `check_claimed_solution_validity` | BMOPFTools | Exposes the four-status contract result without rerunning a solver |
| Counterexample fixture | `claimed-feasible-invalid-solution-001` | BMOPFTools | Returns `LOCALLY_SOLVED` together with a declared voltage-limit violation |
| Finding | `E.CONTRACT.CLAIMED_FEASIBLE_SOLUTION_INVALID` | BMOPFTools | Reports that independent evidence contradicts the feasible-status inference |

`PSK-000003` states that a solver termination label is algorithm evidence, not
an independent certificate of finite primal values, model equations, study
limits, recovery, or local/global optimality. The related book diagnostics
artifact already records solver-status and package-diagnostic layers separately;
the package fixture now makes the invalid inference directly executable.

The fixture network declares a 200--260 V bus-voltage range. Its negative
result is labelled `LOCALLY_SOLVED` but reports 180.5 V. The contract first
requires complete numeric `vr`, `vi`, and `vm` data for every declared bus
terminal, then reuses BMOPFTools' existing `profile_solution` implementation.
It retains `E.SOL.VOLT_VIOLATION` as underlying evidence and emits the dedicated
contract finding. A companion 230.5 V result passes only termination status,
result-tree finiteness, and the declared bus voltage/angle dimensions.

That pass is intentionally not a general solution certificate. Network-equation
residuals, thermal and device limits, load-model residuals, power balance,
objective optimality, global guarantees, and solver derivative quality remain
explicitly unassessed. A non-feasible solver status is `inapplicable`; missing
status or bus-terminal evidence is `indeterminate`.

All three audience routes make `knowledge:PSK-000003` mandatory and expose the
counterexample, executable contract, dedicated Findings, and unresolved checks
through the same deterministic, source-hash-bound context machinery.

## Fourth trace: load connection voltage bases

The fourth slice turns an existing package plausibility diagnostic into an
explicit scientific contract:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000004` | this book | States that a voltage-dependent load anchor belongs to its terminal coordinate |
| Claims | `LOAD-BASE-001`, `LOAD-CONNECTION-001` | this book | Define the anchor rule and retain the generated WYE/DELTA connection-map witness |
| Misconception | `wye-delta-share-nominal-voltage-base` | this book | Routes same-numeric-base shortcuts to mandatory qualification |
| Executable contract | `load_voltage_base_consistency` | BMOPFTools | Checks the supported connection-coordinate declaration against a propagated bus base |
| API operation | `check_load_voltage_base_consistency` | BMOPFTools | Exposes pass, fail, inapplicable, and indeterminate outcomes |
| Counterexample fixture | `load-voltage-base-mismatch-001` | BMOPFTools | Assigns a phase-to-neutral anchor to a DELTA ZIP load |
| Finding | `E.CONTRACT.LOAD_VOLTAGE_BASE_MISMATCH` | BMOPFTools | Reports the connection-inconsistent nominal anchor |

`PSK-000004` states that nominal voltage is part of a voltage-dependent load's
constitutive coordinate. WYE uses phase-to-neutral voltage; DELTA uses
line-to-line voltage. On the declared nominal three-phase system those bases
differ by `sqrt(3)`. Copying one numeric value into both declarations therefore
changes normalized constant-current, constant-impedance, ZIP, or exponential
behavior rather than merely changing metadata.

The fixture uses a balanced source with a 230 V phase-to-neutral base. Its
DELTA ZIP load incorrectly declares `v_nom=230` V, while the corresponding
line-to-line base is about 398.37 V. The executable contract reuses the same
source/transformer voltage propagation, connection-coordinate conversion, and
default 0.8--1.25 plausibility band as the existing
`W.LOAD.VNOM_MISMATCH` diagnostic. The negative case produces the dedicated
contract failure; the companion 398.37 V declaration passes.

That pass remains declaration-relative. Source and transformer nominal values,
terminal maps, coefficients, units, operating voltage, network equations, and
equipment limits are unassessed. All three audience routes make
`knowledge:PSK-000004` mandatory and expose those boundaries through the same
deterministic context-packet machinery.

## Fifth trace: adjustable transformer tap domains

The fifth slice preserves a decision domain rather than one transformer
snapshot:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000005` | this book | States why a start tap is not the adjustable decision domain |
| Claims | `TR-XFMR-005`, `TR-XFMR-006` | this book | Establish parameterized tap preservation and its recorded AC-network consequence |
| Misconception | `fixed-tap-snapshot-preserves-adjustable-transformer` | this book | Routes fixed-start shortcuts to the decision-domain qualification |
| Executable contract | `transformer_tap_domain_preservation` | BMOPFTools | Compares supported mapped continuous tap intervals |
| API operation | `check_transformer_tap_domain_preservation` | BMOPFTools | Exposes the four-status comparison and interval witness |
| Counterexample fixture | `transformer-tap-domain-loss-001` | BMOPFTools | Replaces `[0.95,1.05]` by the fixed singleton `1.0` |
| Finding | `E.CONTRACT.TRANSFORMER_TAP_DOMAIN_LOSS` | BMOPFTools | Reports an inner restriction, outer extension, overlap, or disjoint domain |

`PSK-000005` states that exact parameterized preservation retains the mapped
tap identity and complete admissible domain. A tap start is one admissible
initial point, not a substitute for that set. The existing `TR-XFMR-005`
certificate establishes the pointwise parameterized factor and a discrete
decision witness; `TR-XFMR-006` embeds the retained finite tap factor in its
declared AC network and records the consequence of freezing the 1.00 start.
Those book artifacts remain the scientific authority.

The package's initial check is deliberately smaller. It accepts one mapped
two-winding isolating transformer, requires a finite positive continuous source
interval and unchanged subtype/non-tap declarations, and compares the source
and target intervals. Omitting target bounds has its documented package meaning:
a fixed singleton at `tap`. The fixture therefore fails as an
`inner_restriction` and carries a source-admissible, target-inadmissible tap
witness. Retaining `[0.95,1.05]` passes even if the target's admissible start
differs, proving that the implementation does not confuse domain identity with
initialization identity.

That pass does not establish transformer-equation, loss, discrete-position,
coupling, automatic-control, network-feasible-set, objective, optimal-tap, or
solver equivalence. All three audience routes make `knowledge:PSK-000005`
mandatory and expose the book certificates, executable interval check,
counterexample, and unresolved boundaries through the existing deterministic
retrieval path.

## Sixth trace: transformer winding conventions

The sixth slice prevents an ordinary-edge shortcut from silently changing a
typed transformer factor:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000006` | this book | States why transformer endpoint reversal requires a complete typed map |
| Claims | `TR-XFMR-001`, `TR-XFMR-004` | this book | Establish winding-coordinate action and completed fixed-linear factor anatomy |
| Misconception | `transformer-end-swap-is-ordinary-edge-reversal` | this book | Routes bare endpoint swaps to the winding-role qualification |
| Executable contract | `transformer_winding_convention_preservation` | BMOPFTools | Compares supported fixed compact winding conventions |
| API operation | `check_transformer_winding_convention_preservation` | BMOPFTools | Exposes four-status mapped convention evidence |
| Counterexample fixture | `transformer-winding-role-swap-001` | BMOPFTools | Swaps only the two bus fields on a WYE/DELTA record |
| Findings | `E.CONTRACT.TRANSFORMER_WINDING_INCIDENCE_MISMATCH`, `E.CONTRACT.TRANSFORMER_WINDING_BASE_RATIO_MISMATCH` | BMOPFTools | Separate incidence failures from reference/ratio failures |

`PSK-000006` states the broad preservation obligation. The winding-normalization
certificate records the exact terminal-coordinate action and dual current map;
the fixed-factor certificate records the connection incidence, voltage
transfer, leakage, excitation, grounding, and recovery anatomy. Those book
artifacts remain authoritative for the general scientific claim.

The package check covers only fixed-tap `single_phase`, `wye_delta`, and
`delta_wye` records with the same subtype, explicit one-to-one bus mapping,
and stable or explicitly mapped terminal labels. It compares winding-side
identity, ordered coil incidence, winding reference voltages, and fixed
effective coil ratio. Adjustable taps route to `PSK-000005`; subtype-changing
or fully reversed encodings require a complete typed transformation outside
this initial contract.

The negative fixture retains the unordered bus pair but swaps its endpoint
fields while leaving the WYE/DELTA subtype and terminal maps untouched. It
therefore fails on mapped coil incidence. The companion target retains the
convention and passes narrowly. Neither result establishes equality of
leakage, excitation, grounding, limits, complete terminal factors, controls,
network feasible sets, objectives, or solver behavior. All three audience
routes make `knowledge:PSK-000006` mandatory and retain those limits through
the deterministic, source-hash-bound context packet.

## Seventh trace: terminal versus decision equivalence

The seventh slice makes the federation's umbrella preservation question
executable at the declaration boundary:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000007` | this book | Separates terminal equality from observation-indexed decision equivalence |
| Claims | `PRESERVE-001`, `TR-PAR-001`, `TR-PAR-002` | this book | Define the exactness object and exhibit equal terminal behavior with unequal constrained feasible sets |
| Misconception | `terminal-equivalence-implies-opf-equivalence` | this book | Routes unqualified optimization-equivalence claims to the complete preservation obligations |
| Executable contract | `decision_preservation_manifest_completeness` | BMOPFTools | Checks completeness and internal consistency of an exact decision-equivalence declaration |
| API operation | `check_decision_preservation_manifest` | BMOPFTools | Exposes four-status manifest evidence without authenticating it |
| Counterexample fixture | `decision-manifest-terminal-only-001` | BMOPFTools | Claims exact decision equivalence with only a terminal-relation evidence reference |
| Findings | `E.CONTRACT.DECISION_MANIFEST_EVIDENCE_GAP`, `E.CONTRACT.DECISION_MANIFEST_UNRESOLVED_OBLIGATION` | BMOPFTools | Separate omitted support from an explicitly unclosed obligation |

The book's observation-indexed definition and parallel feasible-set witness
remain the scientific basis. The package fixture does not dispute its terminal
certificate; it shows that this one reference cannot close the admissible
domain, observations, constraints, decision variables, objective, and recovery
obligations of an exact decision-equivalence claim.

The evidence-complete companion manifest declares every required dimension and
passes narrowly. That pass means the manifest contains supported dispositions,
not that BMOPFTools has resolved or authenticated the evidence IDs. It does not
compare equations, feasible sets, objectives, optimizers, or recovery maps.
Case-specific contracts such as parallel member-limit preservation and
transformer tap-domain preservation remain the sources of actual evidence for
individual dimensions.

All three existing audience routes now make `knowledge:PSK-000007` mandatory
and expose the completeness contract and terminal-only counterexample through
the same deterministic context packet. The existing unsupported,
under-retrieved, qualification, and source-hash semantics are unchanged.

## Eighth trace: Kron boundary exactness and internal recovery

The eighth slice carries the tutorial's grounding warning into a deliberately
narrow boundary contract:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000008` | this book | Requires the grounding precondition and recovery map for a four-wire-to-three-wire Kron boundary claim |
| Claims | `PRESERVE-001`, `TR-KRON-002`, `TR-KRON-FIVE-002` | this book | Distinguish Schur-complement boundary exactness from internal and decision preservation |
| Misconception | `kron-reduction-preserves-everything` | this book | Routes unqualified Kron-equivalence claims to explicit conditions and unassessed dimensions |
| Executable contract | `kron_boundary_recovery_preservation` | BMOPFTools | Checks endpoint grounding, ordered phase relation, Schur complement, and recovery declaration |
| API operation | `check_kron_boundary_recovery` | BMOPFTools | Reports qualified pass/fail/inapplicable/indeterminate results |
| Counterexample fixture | `kron-boundary-grounding-001` | BMOPFTools | Matches the Schur target while leaving the load neutral floating, so the boundary precondition fails |
| Findings | `E.CONTRACT.KRON_GROUNDING_PRECONDITION`, `E.CONTRACT.KRON_BOUNDARY_RELATION_MISMATCH`, `W.CONTRACT.KRON_RECOVERY_INDETERMINATE` | BMOPFTools | Separate physical precondition failure, relation mismatch, and missing recovery evidence |

The book's existing running-network, explicit-earth, multiple-grounding-point,
and nonlinear witnesses remain the richer scientific evidence. The package
fixture is a pedagogical guardrail and does not replace those witnesses or
claim that a passing boundary check preserves internal limits, protection,
complete feasible sets, objectives, or solver results. All three audience
routes make `knowledge:PSK-000008` mandatory when the existing Kron
misconception is triggered; the deterministic packet and source-hash checks
remain unchanged.

## Ninth trace: positive-sequence collapse applicability

The ninth slice guards a controlled specialization onto the positive-sequence
invariant subspace:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000009` | this book | Requires cyclic factors and a fully declared balanced study domain for positive-sequence restriction |
| Claims | `COLLAPSE-001`, `COLLAPSE-002` | this book | Establish the exact restricted relation and show sequence mixing under a non-circulant perturbation |
| Misconception | `transposition-implies-positive-sequence-exactness` | this book | Routes transposition-only claims to symmetry, grounding, terminal, decision, and observation guards |
| Executable contract | `positive_sequence_collapse_applicability` | BMOPFTools | Checks circulant series/shunt factors, phase order, scalar positive-sequence relation, and explicit domain declarations |
| API operation | `check_positive_sequence_collapse` | BMOPFTools | Reports qualified applicability, failure, and indeterminate results |
| Counterexample fixture | `positive-sequence-collapse-001` | BMOPFTools | Uses a circulant factor but deliberately fails the balanced-domain guard |
| Findings | `E.CONTRACT.SEQUENCE_SYMMETRY_MISMATCH`, `E.CONTRACT.SEQUENCE_DOMAIN_MISMATCH`, `E.CONTRACT.SEQUENCE_RELATION_MISMATCH` | BMOPFTools | Separate operator mixing, study-domain leakage, and target-relation errors |

The passing companion in the contract tests is intentionally narrower than a
balanced-model claim: it leaves phase-specific limits, neutral/earth,
negative/zero-sequence, protection, internal devices, complete feasible sets,
objectives, and solver behavior unassessed. Existing sequence witnesses remain
the scientific evidence; the package check is the refusal boundary that keeps
those claims from being silently promoted.

## Tenth trace: fixed versus state-dependent equivalents

The tenth slice guards the promotion of an operating-point map into a reusable
state-domain equivalent:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000010` | this book | Requires state-domain, calibration, and update provenance for reusable equivalents |
| Claims | `PRESERVE-001`, `TR-KRON-NEUTRAL-005`, `TR-KRON-NEUTRAL-007` | this book | Show that state shifts change nonlinear maps and recovered margins away from calibration |
| Misconception | `base-state-equivalent-is-globally-exact` | this book | Routes frozen operating-point maps to explicit state/update obligations |
| Executable contract | `state_dependent_equivalent_provenance` | BMOPFTools | Checks parameter, domain, base-state, and update-rule declarations |
| API operation | `check_state_dependent_equivalent` | BMOPFTools | Reports frozen-map loss, domain/base mismatches, or qualified declaration pass |
| Counterexample fixture | `state-dependent-equivalent-001` | BMOPFTools | Freezes a source map over a non-singleton load-state domain |
| Findings | `E.CONTRACT.STATE_UPDATE_PROVENANCE_LOSS`, `E.CONTRACT.STATE_DOMAIN_MISMATCH`, `E.CONTRACT.STATE_BASE_ALIGNMENT_MISMATCH` | BMOPFTools | Separate frozen-map, domain, and calibration-state failures |

The package pass is declaration evidence only: it does not validate a
nonlinear update law or establish feasible-set, objective, protection, or
solver equivalence. The book's state-dependent grounding and continuation
witnesses remain the scientific evidence.

## Eleventh trace: floating references and singularity

The eleventh slice makes reference/rank preservation explicit before a
transformed model is accepted:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000011` | this book | Separates voltage-reference incidence and rank from import or solver success |
| Claims | `NUMERICAL-001`, `NUMERICAL-004`, `GROUND-SCOPE-001` | this book | Define numerical/reference obligations and distinguish physical and mathematical grounding |
| Misconception | `reference-or-rank-success-proves-nonsingularity` | this book | Routes successful-import/solver claims to island and rank checks |
| Executable contract | `reference_singularity_validation` | BMOPFTools | Compares mapped island references and rank evidence |
| API operation | `check_reference_singularity` | BMOPFTools | Reports reference loss, singularity change, or qualified pass |
| Counterexample fixture | `reference-singularity-001` | BMOPFTools | Removes a source reference and one rank in the target island |
| Findings | `E.CONTRACT.REFERENCE_LOSS`, `E.CONTRACT.SINGULARITY_CHANGE` | BMOPFTools | Separate reference-incidence and rank-deficiency changes |

The pass does not replace equation-level Ybus/Jacobian or solver validation;
the package checks declaration consistency only. Existing numerical and
grounding evidence remains the scientific basis.

## Twelfth trace: terminal/conductor ordering and permutation

The twelfth slice turns a typed coordinate-action obligation into a narrow
metamorphic primitive check:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000012` | this book | Requires explicit bijective coordinate action on endpoint maps and matrix factors |
| Claims | `TR-KRON-001`, `PRESERVE-001` | this book | Establish typed terminal coordinates and the boundary between primitive and study equivalence |
| Misconception | `terminal-permutation-is-cosmetic` | this book | Routes relabelling shortcuts to endpoint-map and matrix checks |
| Executable contract | `terminal_permutation_invariance` | BMOPFTools | Checks bijection, endpoint maps, and row/column permutation relation |
| API operation | `check_terminal_permutation_invariance` | BMOPFTools | Reports order mismatch, relation mismatch, or qualified pass |
| Counterexample fixture | `terminal-permutation-001` | BMOPFTools | Keeps labels aligned while perturbing one target matrix entry |
| Findings | `E.CONTRACT.TERMINAL_ORDER_MISMATCH`, `E.CONTRACT.PERMUTATION_RELATION_MISMATCH` | BMOPFTools | Separates coordinate-map and primitive-factor failures |

The package pass is not a complete coordinate-transformation theorem. It
leaves downstream limits, nonlinear state, network feasible sets, decisions,
objectives, recovery, and solver behavior unassessed; the book retains those
claims and the pedagogical permutation examples.

## Thirteenth trace: complete solved-network feasibility

The thirteenth slice separates solver status from an independently computed
feasibility witness:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000013` | this book | Requires residual, device-limit, and recovery evidence beyond solver status |
| Claims | `NUMERICAL-001`, `NUMERICAL-004` | this book | Distinguish termination, residual/backward error, and optimality guarantees |
| Misconception | `complete-feasibility-status-is-enough` | this book | Routes status-only claims to independent feasibility checks |
| Executable contract | `solved_network_feasibility_validation` | BMOPFTools | Validates finite residual norms and device-limit witness fields |
| API operation | `check_solved_network_feasibility` | BMOPFTools | Reports residual or device-limit violations, inapplicability, or indeterminacy |
| Counterexample fixture | `solved-network-feasibility-001` | BMOPFTools | Retains `OPTIMAL` while failing one independent power-balance residual |
| Findings | `E.CONTRACT.FEASIBILITY_RESIDUAL_VIOLATION`, `E.CONTRACT.FEASIBILITY_DEVICE_LIMIT_VIOLATION` | BMOPFTools | Separate residual and device-limit failures |

The package validates the supplied witness; it does not calculate residuals or
prove its completeness, global optimality, or full decision equivalence.

## Fourteenth trace: unit/base and serialization invariance

The fourteenth slice binds declared conversion metadata to a canonical payload:

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000014` | this book | Requires explicit unit/base declarations and semantic payload binding |
| Claims | `PRACTICE-ADAPTER-001` | this book | Defines adapter provenance, units, bases, and coordinate retention |
| Misconception | `unit-base-metadata-is-equivalence` | this book | Routes metadata-only or hash-only round-trip claims to explicit checks |
| Executable contract | `unit_base_serialization_invariance` | BMOPFTools | Compares unit system, base map, and canonical semantic hash |
| API operation | `check_unit_base_serialization_invariance` | BMOPFTools | Reports unit, base, payload, or metadata failures |
| Counterexample fixture | `unit-base-serialization-001` | BMOPFTools | Preserves SI metadata while changing the canonical payload hash |
| Findings | `E.CONTRACT.UNIT_SYSTEM_MISMATCH`, `E.CONTRACT.BASE_MAP_MISMATCH`, `E.CONTRACT.SERIALIZED_PAYLOAD_MISMATCH` | BMOPFTools | Separates metadata drift from semantic payload mutation |

The package pass binds declared serialization evidence only; parser/writer
round-trip behavior, hash computation, complete equations, limits, and study
decisions remain separate validation dimensions.

## What generalizes

The federation pattern generalizes to other scientific guardrails:

- one stable PSK identity can link claims, misconceptions, artifacts, executable contracts, APIs, Findings, fixtures, and recipes;
- scientific and executable exports can evolve independently while a pair manifest detects incompatible releases;
- retrieval can make a PSK mandatory through the existing misconception graph;
- implementations can report `passed`, `failed`, `inapplicable`, or `indeterminate` without turning absence of evidence into a pass; and
- source hashes make context packets and cross-repository links auditable.

The numerical formula used by the first contract does **not** generalize automatically. The scalar voltage-drop reduction, lack of shunts, fixed linear admittances, common coordinates, and explicit current ratings are case-specific. The second contract likewise does not turn relation matching into electrical equivalence: its explicit-neutral and scalar neutral-only grounding domain is case-specific. The third contract establishes that the contract/result/refusal machinery generalizes to post-solve evidence, but its initial bus-result coverage is not a universal feasibility or optimality validator. The fourth shows that an existing package diagnostic can be promoted into an auditable contract without duplicating its inference machinery, but declaration consistency is not importer fidelity or solved-model validation. The fifth separates preservation of an adjustable domain from equality at one initialized snapshot, while keeping broader transformer physics and decision equivalence outside the initial package check. The sixth shows how a typed coordinate convention can be checked without pretending that a compact declaration check proves the completed factor or a subtype-changing reversal. The seventh generalizes the routing and refusal pattern to an umbrella evidence manifest while deliberately leaving the truth of every cited dimension to narrower checks. Multiconductor coupling, nonlinear devices, explicit-earth networks, protection quantities, full equation residuals, device constraints, recovery, and global optimality require separate PSK objects or broader contracts with their own evidence and fixtures.

## Reproduction and release pairing

From the book repository with BMOPFTools checked out beside it:

```bash
python3 scripts/generate_scientific_knowledge.py --check
python3 scripts/check_federated_knowledge.py --check --bmopf-root ../BMOPFTools.jl
python3 scripts/check_llm_reproducibility.py
```

From BMOPFTools:

```bash
python3 scripts/generate_executable_knowledge.py --check
julia --project=test --startup-file=no -e \
  'using Test, BMOPFTools; include("test/scientific_contract_tests.jl"); include("test/executable_knowledge_tests.jl")'
```

Changing either export requires regenerating and reviewing the pair manifest. A normal book-only check validates its pinned snapshot; the sibling-aware check proves that the local BMOPFTools checkout still matches that snapshot.

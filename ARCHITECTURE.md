# Federated scientific knowledge and executable guardrails

## Status and authority

This document is the architectural authority for the integration between
`frederikgeth/multi-graph-book` and `frederikgeth/BMOPFTools.jl`. It defines
what belongs in each repository, the allowed dependency directions, and the
contracts between their generated artifacts. Implementation plans, tranche
lists, and session handovers may change more frequently; they must remain
consistent with this document.

The architecture is deliberately federated. The repositories cooperate, but
neither becomes authoritative for the other's subject matter:

- `multi-graph-book` owns scientific and epistemic knowledge: what a claim
  means, its evidence and scope, which inference is unsafe, and which
  preservation question must be asked.
- `BMOPFTools.jl` owns executable evidence about a concrete model, result, or
  declared transformation: what was checked, which preconditions held, what
  passed or failed, and what remains indeterminate.

The central rule is:

> The book states what must be preserved, what can fail, under which
> assumptions, and why. BMOPFTools checks as much of that contract as can be
> established computationally for an actual case.

This is not an architecture for making prose merely easier for a language
model to read. It is an architecture for preserving scientific qualification,
retrieving contradicting evidence, executing applicable checks, and refusing
claims that exceed the available evidence.

## Non-negotiable invariants

The following invariants take precedence over convenience.

1. **Preserve the existing book access machinery.** The book already has a
   deterministic, source-hash-bound corpus; misconception routing;
   qualification-aware context packets; `qualified`, `under_retrieved`, and
   `unsupported` semantics; retrieval and adversarial evaluation; HTTP/JSON,
   Markdown, CLI, and MCP access; and release-bound reproducibility checks.
   Federation extends these components. Replacing them with a generic
   embeddings or vector-database RAG stack would be a regression.
2. **Do not promote evidence.** A fixture observation is not a theorem, solver
   termination is not solution verification, BMOPFTools behavior is not a
   general scientific result, and generated prose is not evidence.
3. **Do not use unindexed equivalence.** Every equivalence or preservation
   statement names the source and target models, domain, state, observations,
   constraints, decisions, objective, and recovery obligations that matter.
4. **Do not infer forgotten information.** A reduced target model normally
   cannot reveal member identities, constraints, or internal quantities that
   were discarded. Checks that need those facts must accept the source model
   and an explicit mapping or transformation record.
5. **Do not create a runtime dependency between repositories.** Ordinary book
   reading and book-only retrieval do not require BMOPFTools. Ordinary
   BMOPFTools parsing, analysis, optimization, and verification do not require
   the book or network access.
6. **Keep transports thin.** Domain logic belongs in clean Julia or retrieval
   APIs. CLI, HTTP, MCP, and future ecosystem adapters expose those APIs; they
   do not become a second implementation of the science.
7. **Keep generated artifacts generated.** Source hashes, indexes, manifests,
   source anchors, finding exports, API inventories, and federated packets are
   derived from canonical sources and are checked for staleness.

## Repository responsibilities

### `multi-graph-book`: scientific authority

The book is the canonical home for:

- claims and definitions, including evidence class, verification status,
  assumptions, model scope, exactness object, and unresolved boundary;
- controlled vocabulary and translations between power engineering, circuit,
  mathematical, graph, software, and machine-learning language;
- misconceptions, invalid inferences, scope boundaries, scientific
  counterexamples, negative results, and open questions;
- preservation-contract definitions and transformation classifications;
- literature evidence, review status, independent reproduction status, and
  explicit limits of the evidence;
- stable cross-repository Power-System Knowledge (`PSK`) objects;
- retrieval evaluation, qualification routing, abstention policy, federated
  context assembly, and audience-aware answer contracts.

The current Markdown, claims ledger, vocabulary registry, misconception
registry, evidence artifacts, certificate schema, and release manifest remain
canonical. The generated LLM corpus and context packets are access artifacts,
not an alternative scientific database.

The book may refer to a BMOPFTools executable contract by stable identifier and
may report the evidence produced by a pinned run. It must not describe one
implementation's behavior as a general theorem unless that proposition has
independent scientific support and is registered with the appropriate evidence
status.

### `BMOPFTools.jl`: executable authority

BMOPFTools is the canonical home for:

- static validation of network structure, terminals, conductors, grounding,
  dimensions, units, references, bounds, and component semantics;
- case analysis and structured `Finding` results with stable finding codes;
- executable scientific contracts and their applicability checks;
- independent solution verification, including residuals, limits, equations,
  balance, and result-dictionary consistency;
- transformation manifests, recovery checks, invariants, metamorphic tests,
  property-based tests, and minimized runnable counterexamples;
- small CI-tested recipes and stable Julia APIs for parsing, analysis, solving,
  verification, and contract checking;
- a generated executable-knowledge export describing available checks without
  duplicating the book's scientific explanations.

BMOPFTools findings must remain useful offline. A finding therefore carries a
concise local explanation and actionable evidence, even when its broader
scientific treatment is linked to the book. Optional metadata may include PSK
IDs, failure class, invalid inferences, possible causes, recommended checks,
counterexample IDs, and documentation references. Existing finding codes and
the `Finding` programmatic contract remain stable.

BMOPFTools must not contain a second claims ledger, general literature review,
misconception retriever, audience answer renderer, or copy of the book corpus.

## Canonical and generated objects

Cross-repository links use a small stable namespace such as `PSK-000001`. PSK
IDs do not replace book claim IDs, misconception IDs, certificate IDs,
counterexample IDs, BMOPFTools finding codes, or Julia API names. They connect
those existing identifier systems.

A canonical PSK object belongs in the book and contains only semantic links and
the minimum fields needed to identify the knowledge object: ID, kind, title,
scientific statement, scope, evidence status, related book identifiers,
executable-contract identifiers, counterexample identifiers, and unresolved
boundaries. Long scientific explanations stay in canonical book prose.

BMOPFTools maintains a small executable registry, not a scientific knowledge
database. It records executable contract IDs, entry points, applicable object
types, finding codes, fixture IDs, output shape, and related PSK IDs. Runtime
evidence remains in findings and contract results. Documentation, API records,
and executable JSONL records are generated or checked against this registry.

The principal generated exports are:

```text
multi-graph-book/generated/scientific_knowledge.jsonl
BMOPFTools.jl/generated/executable_knowledge.jsonl
```

The exact paths may be introduced incrementally, but their semantics are
fixed: the first contains scientific objects and evidence qualifications; the
second contains executable capabilities, applicability domains, and local
source identity. Both carry schema version, repository identity, source path,
source anchor where applicable, source hash, and related PSK IDs.

A federated release or experiment creates a separate pair manifest containing
the immutable revision and export hash of both repositories. Individual source
records do not embed mutually dependent current commit hashes; doing so would
create a circular, permanently stale commit dependency.

## Scientific-contract lifecycle

A scientific contract begins with a proposition broader than a function call.
The book defines its source and target objects, preservation dimensions,
preconditions, domain, observations, decisions, objectives, forgotten
information, recovery map, evidence, and unresolved boundary. BMOPFTools then
implements only the decidable portion.

An executable check reports one of at least four semantic outcomes:

- `passed`: the implemented obligations hold for the supplied instance within
  the declared domain and tolerance;
- `failed`: an implemented obligation is violated, with a reproducible witness;
- `inapplicable`: a declared precondition does not hold, so the check makes no
  preservation claim;
- `indeterminate`: the available model, result, mapping, or numerical evidence
  is insufficient to decide the obligation.

Execution errors and solver termination states are recorded separately from
these contract outcomes. `passed` never means that unimplemented preservation
dimensions hold. `inapplicable` and `indeterminate` are successful refusal
behaviors, not inconvenient failures to hide.

For a transformation check, the normal inputs are the source model, target
model, declared object mapping, contract ID, and requested preservation
dimensions. A target-only heuristic may identify a risk or recommend a
follow-up check, but it cannot certify preservation of information that is no
longer represented.

## First vertical slice: parallel member limits

The first vertical slice is the parallel-branch aggregation/member-rating
case because the book already contains the necessary scientific foundation:
the `parallel-admittance-implies-decision-equivalence` misconception, claims
`TR-PAR-001`, `TR-PAR-002`, and `TR-PAR-003`, executable parallel-branch
certificates, and source/naive/exact-lifted decision comparisons.

The slice introduces one PSK object linking that existing material to a
BMOPFTools executable contract. The BMOPFTools check accepts the source member
lines, target aggregate, and declared mapping. Within its stated fixed-linear
domain it checks terminal-coordinate alignment, reconstruction of member
currents, member and target ratings, and whether the target constraint is an
outer relaxation of the source member-constrained feasible set.

The existing `I.RED.PARALLEL_LINES` finding remains a discovery signal; merely
having parallel lines is neither an error nor evidence that aggregation was
attempted. A distinct contract finding reports loss of member-limit
preservation. Its detail contains the PSK ID, contract ID, affected members,
precondition results, numerical or analytical witness, invalid inference, and
recommended next check.

The primary two-branch witness is checked algebraically so that the scientific
result does not depend on a nonlinear solver. A solved source/naive/exact-lifted
comparison may provide additional numerical evidence, with solver and
optimality status reported honestly. Tests cover failure of the naive summed
rating, preservation with exact lifted member constraints, relabelling
invariance, and refusal outside the supported domain.

## Second vertical slice: neutral, ground, and reference

The second slice tests whether the same federation remains useful for a model-
semantics failure rather than an optimization-preservation failure. Book object
`PSK-000002` links claims `GROUND-SCOPE-001` and `GROUND-SCOPE-002` and the
`ground-neutral-reference-are-one-node` misconception to BMOPFTools contract
`neutral_ground_reference_preservation`.

The initial executable domain compares an explicit one-to-one bus mapping. It
checks identifiable neutral terminals, pairwise neutral continuity, and each
mapped neutral's declared perfect-ground, scalar finite-grounding-shunt, and
voltage-source-reference relations. The minimized counterexample retains the
same simple two-bus graph and neutral labels while removing the neutral-carrying
feeder path and replacing a finite customer grounding relation with a perfect
local ground.

This is intentionally a representation-level contract. A pass does not certify
equal terminal equations, an explicit earth conductor, soil or electrode
models, grounding-asset state, fault current, touch voltage, or protection
operation. Coupled grounding models and missing evidence are refused explicitly
rather than collapsed to scalar assumptions.

## Third vertical slice: solver termination and solution validity

The third slice tests an invalid inference about numerical evidence. Book object
`PSK-000003` links `NUMERICAL-001`, `NUMERICAL-004`, and the
`solver-termination-implies-validated-solution` misconception to BMOPFTools
contract `claimed_solution_validity`.

The initial executable domain treats a claimed-feasible termination status as
an applicability precondition. It requires complete numeric bus-terminal data,
checks the result tree for non-finite values, and independently recomputes
declared bus voltage and angle limits through the existing solution profiler.
The minimized counterexample reports `LOCALLY_SOLVED` while violating a declared
voltage range.

This is intentionally not a complete feasibility or optimality certificate.
Network equations, device limits, load-model residuals, power balance, recovery,
objective guarantees, and solver derivatives remain explicit future contract
dimensions.

The initial three vertical slices cover transformation preservation, model
semantics, and numerical/scientific inference. Shared infrastructure may now be
generalized incrementally, starting with registry-scale inventory and additional
high-consequence PSK links, while each new executable check retains its own
applicability, evidence, counterexample, and refusal semantics.

## Fourth vertical slice: load connection voltage bases

The fourth slice begins that generalization by wrapping an existing package
diagnostic rather than inventing a parallel heuristic. Book object
`PSK-000004` links `LOAD-BASE-001`, `LOAD-CONNECTION-001`, and the
`wye-delta-share-nominal-voltage-base` misconception to BMOPFTools contract
`load_voltage_base_consistency`.

The initial executable domain covers voltage-dependent WYE and DELTA loads
with finite positive nominal anchors and a phase-to-neutral bus base reachable
through BMOPFTools' existing source/transformer voltage-level propagation. It
uses the same connection-coordinate convention and default plausibility band
as `W.LOAD.VNOM_MISMATCH`: WYE is compared with phase-to-neutral voltage;
DELTA is compared with the corresponding line-to-line base. The minimized
counterexample assigns a 230 V phase-to-neutral anchor to a DELTA ZIP load on a
230/398.37 V nominal system.

This is a declaration-consistency contract, not a solved-load or importer
fidelity certificate. A pass does not establish that source or transformer
nominals, terminal maps, load-law coefficients, units, operating voltages,
network equations, or equipment limits are correct. Missing source-reachable
bases or nominal anchors are indeterminate; constant-power and unsupported
connection cases are explicitly inapplicable.

## Fifth vertical slice: adjustable transformer tap domains

The fifth slice applies the federation to a decision variable already supported
by both repositories. Book object `PSK-000005` links `TR-XFMR-005`,
`TR-XFMR-006`, and the
`fixed-tap-snapshot-preserves-adjustable-transformer` misconception to
BMOPFTools contract `transformer_tap_domain_preservation`.

The scientific result is broader than the initial package check. The book
establishes that a scalar ganged tap is preserved by retaining its parameterized
factor, decision identity, and complete continuous or finite domain; replacing
that domain by the start-value singleton is generally an inner restriction. The
recorded transformer-factor and AC-network witnesses show that the restriction
can change the selected tap and objective, without claiming that it always does.

The initial executable domain compares one explicitly mapped two-winding
isolating transformer with a positive continuous `tap_min < tap_max` interval.
Source and target must use the same supported subtype and identical non-tap
declarations. Target bounds that are absent mean a fixed singleton at `tap`, as
defined by the BMOPFTools data model. The check classifies inner restrictions,
outer extensions, shifted overlaps, and disjoint domains and returns a tap
witness admitted by only one side.

A pass establishes only the mapped base-factor declaration, admissibility of
the recorded starts, and equality of the continuous tap interval. Pointwise
transformer equations, tap-dependent leakage or excitation, discrete positions,
per-phase or mechanical coupling, automatic controls, network feasible sets,
objectives, optimal taps, and solver guarantees remain separate obligations.
This separation is intentional: the package contract complements the existing
book certificates instead of reimplementing or weakening them.

## Sixth vertical slice: transformer winding conventions

The sixth slice links book object `PSK-000006`, claims `TR-XFMR-001` and
`TR-XFMR-004`, and the
`transformer-end-swap-is-ordinary-edge-reversal` misconception to BMOPFTools
contract `transformer_winding_convention_preservation`.

The book owns the general science. A transformer winding is a typed port with
an ordered terminal-to-coil incidence, and an exact coordinate action must
transform the incidence and its power-dual current map. The completed fixed
linear factor additionally declares the transfer convention and placement of
leakage, excitation, and internal grounding. Consequently, transformer
orientation is arbitrary only relative to a complete typed transformation; a
bare exchange of endpoint fields is not an equivalence argument.

The initial executable contract is intentionally narrower. It compares one
explicitly mapped, fixed-tap `single_phase`, `wye_delta`, or `delta_wye`
BMOPFTools record with the same subtype. It checks mapped winding-side
identity, ordered terminal-to-coil incidence, positive nominal winding
references, and the fixed effective coil ratio. The minimized fixture swaps
only `bus_from` and `bus_to`, leaving the WYE/DELTA roles and terminal maps
attached to the wrong mapped buses, so the contract reports an incidence
mismatch.

A pass is not a complete transformer-factor certificate. Leakage, excitation,
grounding, limits, adjustable tap domains, controls, network feasible sets,
objectives, and solver evidence remain unassessed. Centre-tap, n-winding,
subtype-changing, and fully typed reversal are outside this first compact
serialization contract. Those boundaries preserve the richer book machinery
instead of replacing it with a field-level heuristic.

## Seventh vertical slice: terminal and decision equivalence

The seventh slice promotes an existing book route rather than inventing a new
retrieval layer. Book object `PSK-000007` links `PRESERVE-001`, the parallel
terminal/feasible-set claims `TR-PAR-001` and `TR-PAR-002`, and misconception
`terminal-equivalence-implies-opf-equivalence` to BMOPFTools contract
`decision_preservation_manifest_completeness`.

The book owns the quantified statement: equivalence is indexed by an
observation family and admissible input set, and equality of an unconstrained
terminal relation does not imply equality of constrained feasible observable
sets. It also owns the broader transformation-certificate vocabulary and the
parallel-member witness showing how a terminal-exact aggregate can be an outer
decision relaxation.

The package complement is a manifest gate, not an equivalence solver. It
applies only when a versioned manifest explicitly claims exact decision
equivalence. The declaration must name source and target identities and close
admissible-domain, terminal, observation, constraint, decision-variable,
objective, and recovery dimensions with either evidence references or a
justified `not_required` disposition. Missing support fails as an evidence gap;
an explicit `unassessed` or `not_preserved` obligation contradicts exactness.
A narrower terminal, inner, outer, or approximate claim is inapplicable rather
than failed.

Even a pass establishes declaration completeness only. Evidence authenticity,
map correctness, equation and feasible-set equality, objective and optimizer
equality, recovery correctness, and solver guarantees remain unassessed. Actual
dimension evidence comes from case-specific contracts and certificates. This
keeps the seventh slice an umbrella route plus narrow executable checks rather
than a generic Boolean `equivalent` flag.

## Eighth vertical slice: Kron boundary exactness and internal recovery

The eighth slice promotes the book's existing Kron and grounding pedagogy into
an executable boundary guardrail. Book object `PSK-000008` links the
observation-indexed preservation definition, the typed and scenario Kron
claims, the existing `kron-reduction-preserves-everything` misconception, and
the tutorial warning that Kron reduction is an assumption rather than a free
simplification. This preserves the book's deterministic context packets,
source-hash binding, unsupported/under-retrieved semantics, and existing
retrieval evaluation; it adds one package check through the same federation
path.

The book owns the mathematical distinction. A Schur complement can reproduce
a declared linear boundary relation, but only under the stated elimination
conditions. For the compact four-wire-to-three-wire case, the eliminated
neutral must be perfectly grounded at every connection point, the target must
match the neutral Schur complement in the declared phase order, and any
internal quantity that matters later must have a recovery map. Finite or
floating grounding is therefore a boundary-condition mismatch even when the
numeric Schur complement happens to match. The tutorial's four-wire example is
the pedagogical counterexample: the reduced model can hide a several-volt
neutral error and cannot recover the internal constraint without retaining the
neutral model.

BMOPFTools owns the narrow contract
`kron_boundary_recovery_preservation` and API
`check_kron_boundary_recovery`. It accepts one mapped, series-only four-
conductor line and a three-conductor target, checks perfect endpoint grounding,
ordered phase alignment, the complex neutral Schur complement, and an explicit
recovery declaration. It reports a grounding-precondition failure separately
from a boundary-relation mismatch, and refuses unsupported shunts, dimensions,
maps, or missing recovery data. A pass is deliberately qualified: it establishes
only the checked boundary relation and recovery obligation. Internal asset
identity, equipment limits, protection quantities, nonlinear/state-dependent
behavior, complete feasible sets, objectives, and solver results remain outside
the contract.

The minimized package fixture is a floating-load-neutral source paired with an
exact Schur target. It must fail on the grounding precondition, while its
grounded companion passes narrowly. This fixture is complementary to the
book's richer running-network, explicit-earth, multi-point, and nonlinear
recovery witnesses; it is not a replacement for them or for the book's
deterministic LLM machinery.

## Ninth vertical slice: positive-sequence collapse applicability

The ninth slice promotes the book's controlled-collapse chapter and its
Fortescue/non-circulant witnesses into a domain guard. Book object
`PSK-000009` links `COLLAPSE-001` and `COLLAPSE-002` to the existing misconception
that transposition alone makes a positive-sequence model exact. The book owns
the invariant-subspace statement: cyclic factors and compatible grounding are
necessary structural conditions, while balanced boundary data, two-terminal
device closure, phase-symmetric decisions, and positive-sequence observations
close the restricted study domain.

BMOPFTools owns the narrow contract
`positive_sequence_collapse_applicability`. It checks a three-conductor source
factor for circulant series and shunt matrices, aligns the declared phase order,
and compares a scalar target with the source positive-sequence eigenvalue. The
caller must explicitly declare the balanced boundary, grounding, device,
decision, and observation guards. Non-circulant factors, failed domain guards,
target relation mismatches, unsupported shapes, and missing declarations are
reported separately. A pass certifies only the restricted positive-sequence
relation; phase-specific, neutral/earth, negative/zero-sequence, protection,
internal-device, complete decision, objective, and solver claims remain
unassessed.

The minimized fixture uses a circulant three-phase line and scalar target, then
deliberately fails one balanced-domain guard in its reproducer. The scientific
contract tests also exercise the positive companion, a non-circulant failure,
an incomplete declaration, and a target mismatch. This keeps the pedagogical
counterexample executable without replacing the book's richer sequence and
four-wire ladder evidence.

## Tenth vertical slice: fixed versus state-dependent equivalents

The tenth slice promotes the book's Ward/Kron and nonlinear-grounding
distinction into an update-provenance guard. Book object `PSK-000010` links the
observation-indexed preservation vocabulary to the recorded state-dependent
grounding probes and the existing misconception that a base-state equivalent
is globally exact. The book owns the scientific boundary: a map calibrated at
one state is local unless the state domain, update law, and relevant recovery or
error obligations are retained.

BMOPFTools owns the declaration contract
`state_dependent_equivalent_provenance`. It requires source and target state
parameter identity, a finite non-singleton domain, aligned base state, and an
explicit target update-rule identifier. A frozen target fails with
`E.CONTRACT.STATE_UPDATE_PROVENANCE_LOSS`; domain or base-state drift are
separate failures, and missing declarations are indeterminate. A pass means
only that the reusable-state declaration is structurally complete. It does not
authenticate the nonlinear update, prove feasible-set or objective equality,
or establish protection or solver equivalence.

The minimized fixture pairs a source varying over `load_scale ∈ [0.8, 1.2]`
with a target frozen at `1.0`; its updating companion passes narrowly. This is
complementary to the book's finite continuation and nonlinear grounding
witnesses, and preserves the deterministic retrieval and refusal machinery.

## Eleventh vertical slice: floating references and singularity

The eleventh slice bundles the book's grounding/reference and numerical-
consequence warnings into a cross-model validation boundary. Book object
`PSK-000011` links the reference and rank claims to the misconception that
successful import or solver termination proves every island is referenced and
nonsingular. The book owns the scientific distinction between a physical or
mathematical voltage reference, connected-island rank, conditioning, and
solver status.

BMOPFTools owns `reference_singularity_validation`. It compares explicitly
mapped `reference_analysis.islands` records, preserving reference incidence and
full-rank status from source to target. A newly unreferenced island and a new
rank deficiency are separate findings; missing or empty evidence is
indeterminate or inapplicable. A pass is only a declaration-level validation
bundle: physical reference-asset identity, equation/Jacobian rank details,
conditioning, complete feasible sets, objectives, and solver guarantees remain
unassessed.

The minimized fixture maps one full-rank referenced island to a target that
loses its reference and one rank. Its exact companion passes the narrow bundle.
This complements existing connectivity, reference, Ybus, and solver
diagnostics rather than replacing them.

## Twelfth vertical slice: terminal/conductor ordering and permutation

The twelfth slice makes typed coordinate-action evidence executable at the
fixed-linear primitive boundary. Book object `PSK-000012` links the terminal
map and coordinate-transformation claims to the misconception that conductor
order is cosmetic. The book owns the general theorem: a relabelling must act
on every typed terminal, phase/sequence coordinate, factor, observation,
constraint, decision, and recovery map that depends on that coordinate.

BMOPFTools owns `terminal_permutation_invariance`. It checks a declared
nonempty one-based bijection, both endpoint terminal maps, and the exact
source row/column permutation of a square series primitive. It reports a
terminal-order mismatch separately from a matrix-relation mismatch. The pass
is deliberately primitive-level evidence only; assets, nonlinear state,
limits, complete feasible sets, objectives, decisions, and solver guarantees
remain unassessed.

The minimized fixture keeps endpoint maps aligned but perturbs one matrix
entry, while its exact companion passes. This is a metamorphic complement to
the book's typed coordinate-action and sequence/coupling material, not a
replacement for a complete network transformation proof.

## Thirteenth vertical slice: complete solved-network feasibility

The thirteenth slice extends the book's numerical-consequence guardrails beyond
solver termination. Book object `PSK-000013` links residual, limit, and recovery
claims to the misconception that `OPTIMAL` or `LOCALLY_SOLVED` is a complete
feasibility certificate. The book owns the scientific distinction between
algorithm status, independently computed residuals, device-limit evidence,
recovery error, and optimality level.

BMOPFTools owns `solved_network_feasibility_validation`. It requires a claimed
solved status and a finite residual witness for equations, KCL, power balance,
device-limit violations, and recovery, comparing each norm with an explicit
tolerance. A pass validates only the supplied witness fields; it does not
recompute the model, authenticate coverage, prove complete feasible-set or
objective equivalence, or establish global optimality.

The minimized fixture retains `OPTIMAL` but fails one power-balance residual;
its exact companion passes. This complements the existing result profiler and
PSK3 status gate rather than replacing solver or equation code.

## Fourteenth vertical slice: unit/base and serialization invariance

The fourteenth slice makes the book's normalization and adapter guardrails
executable at the serialization boundary. Book object `PSK-000014` links
unit/base and provenance claims to the misconception that matching metadata or
a serialized hash proves equivalence. The book owns the scientific semantics
of units, bases, conversion coordinates, and downstream study preservation.

BMOPFTools owns `unit_base_serialization_invariance`. It compares explicit unit
system metadata, a declared base map, and a canonical semantic payload hash,
reporting unit drift, base drift, payload mutation, or missing metadata
separately. A pass binds declared serialization evidence only; it does not
infer units, authenticate hash computation, or prove complete physical or
decision equivalence.

The minimized fixture preserves SI metadata and bases but mutates the semantic
hash; the reordered exact companion passes. This complements `parse_bmopf`,
`write_bmopf`, and source-hash binding without duplicating their I/O logic.

## Federated discovery and context assembly

The existing book service remains the federation point for retrieval. Its
book-only behavior remains valid when no executable export is supplied. With a
pinned BMOPFTools export, corpus generation or index construction adds
executable records while retaining repository and evidence provenance.

The context packet evolves compatibly toward explicit sections such as:

```json
{
  "scientific_basis": [],
  "known_misconceptions": [],
  "counterexamples": [],
  "executable_checks": [],
  "implementation_examples": [],
  "unresolved_boundaries": []
}
```

The existing misconception router continues to trigger mandatory scientific
qualifications. PSK links may then add the corresponding executable contract
records. Contract expansion remains reported separately from ordinary ranker
recall, just as it is today. Retrieval evaluation adds executable-check recall,
counterexample recall, source-repository attribution, and abstention when no
applicable check exists. A vector database or neural reranker is optional and
must outperform the deterministic baseline under the same evidence-preserving
evaluation before it can replace any production path.

Scientific support and runtime evidence remain separate in every packet. A
book claim can be supported while a case-specific check is inapplicable; a
BMOPFTools check can pass while the broader scientific question remains open.
Neither status silently overwrites the other.

## Interfaces and dependency direction

Implementation proceeds from domain interfaces outward:

1. stable Julia validation and contract APIs;
2. structured finding and contract-result serialization;
3. generated executable manifest and small tested recipes;
4. optional JSON CLI operations;
5. thin MCP or PowerMCP-compatible execution adapters.

The book MCP remains the knowledge interface. A future BMOPFTools adapter is an
execution interface and exposes a curated operation set such as case parsing,
analysis, solution verification, contract checking, counterexample execution,
and finding explanation. It must not expose every Julia function or contain
scientific retrieval logic.

## Integrity, CI, and release pairing

Each repository validates its own canonical and generated content without a
live dependency on the other's `main` branch. Local gates include identifier
uniqueness, schema validity, source hashes, generated-file freshness, fixture
existence, documented finding codes, executable contract registration, and
expected counterexample outcomes.

Cross-repository integration uses an explicitly pinned revision or release of
each repository. Its checks verify that referenced claim, misconception, PSK,
finding, contract, and fixture IDs resolve; that source anchors and hashes are
current; and that the federated context packet identifies the exact pair. A
change in either export requires regeneration and re-evaluation of the paired
federated artifact, not a dynamic query against the other repository's latest
branch.

## Agent and contributor workflow

Root `AGENTS.md` files in both repositories will translate this architecture
into local editing rules. Before changing graph representations, network
reductions, conductor maps, grounding, transformer compilation, equivalent
models, bounds, or optimization semantics, an agent identifies the relevant
scientific contract and searches misconceptions, counterexamples, negative
results, and scope boundaries. It then makes the smallest change, runs
ordinary software tests, runs applicable scientific guardrails and minimized
counterexamples, and reports assumptions and unresolved boundaries.

Architectural decisions and rejected approaches belong in a lightweight
development research log. Scientific claims remain in the claims ledger;
ordinary software design choices do not. Failed methods are retained when the
question, setup, failure criterion, evidence, scope, and conditions for
reconsideration are sufficiently specified.

## Change control and anti-goals

Changes to repository ownership, dependency direction, PSK identity, context
status semantics, or the distinction between scientific and runtime evidence
require an explicit update to this document and review in both repositories.
Schema versions may evolve, but consumers must not silently reinterpret old
records.

The integration must not:

- replace the book's deterministic retrieval and evaluation baseline with
  generic RAG infrastructure;
- duplicate claims, misconceptions, or literature prose in BMOPFTools;
- treat a BMOPFTools fixture or successful solve as a theorem;
- make either repository depend on the other's live checkout for ordinary use;
- infer preservation from a target model that cannot represent forgotten
  source information;
- conflate scientific support with executable applicability or pass status;
- begin with a large MCP surface, vector database, benchmark, or generalized
  schema before the three vertical slices establish that the architecture
  works.

Success means an agent proposing a scientifically dangerous modelling change
can retrieve the relevant qualification and contradicting evidence, identify
the precise preservation contract, execute the applicable check on the actual
case, distinguish preserved from lost information, abstain beyond the evidence,
and leave a reproducible trace tied to both repository versions.

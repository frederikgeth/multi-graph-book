# External-review packet map

**Packet date:** 2026-08-17  
**Purpose:** define four bounded review tracks before external contact.  Each
track is a review scope, not a claim that the reviewer must assess the whole
book. The HTML book remains the context source; this file identifies the
minimum packet for each specialist.

## Common instructions

For every assigned claim, the reviewer should:

1. read the listed chapter sections and inspect the cited source or artifact;
2. run the listed reproduction command where practical;
3. check assumptions, coordinate/order conventions, exactness object, and
   stated boundary;
4. record `accept`, `revise`, or `reject` with a short reason; and
5. classify each finding as mathematical, engineering, numerical, semantic,
   editorial, or scope-only.

A passing local test is evidence of reproducibility, not independent review or
global optimality. Empty reviewer fields remain empty until a named reviewer
has completed the assigned track.

## Track A — Graph semantics and formal transformations

**Reviewer profile:** graph transformation, formal methods, compositional
modelling, or mathematical network representations.

**Bounded chapters:**

- `docs/src/foundations/scope-and-thesis.md`
- `docs/src/foundations/preservation-contracts.md`
- `docs/src/foundations/transformation-semantics-register.md`
- `docs/src/foundations/formal-representation-frameworks.md`
- `docs/src/foundations/representation-maps.md`
- `docs/src/foundations/compiled-views-and-graph-surgery.md`
- `docs/src/foundations/cycles-parallelism-radiality.md`
- `docs/src/transformations/certificate-schema-and-composition.md`
- `docs/src/transformations/guarded-normalization.md`

**Claims:** `THESIS-001`, `PRESERVE-001`, `TRANSFORM-SEM-001`,
`ARCH-LENS-001`, `ARCH-VIEW-001`, `ARCH-SURGERY-001`, `ARCH-SURGERY-002`,
`TR-COMP-001`, `TR-GRAPH-001`, `TR-GRAPH-ACTIVE-001`, `TR-GRAPH-002`,
`ARCH-PORT-001`, `ARCH-PORT-002`, `ARCH-CONDUCTOR-002`,
`TRANSFORM-CATALOG-001`.

**Artifacts and figures:**

- `schemas/transformation-certificate.schema.json`
- `experiments/generated/port-factor-architecture.json`
- `experiments/generated/compiled-views-surgery-witness.json`
- `experiments/generated/layer-lens-api-witness.json`
- `experiments/generated/five-bus-cycle-space-analysis.json`
- `experiments/generated/active-radiality-witness.json`
- `experiments/generated/semantic-evaluator-matrix.json`
- map-of-maps, representation-taxonomy, guarded-rule-gate, and
  certificate-composition figures.

**Reproduction:**

```text
julia --project=experiments experiments/test/multigraph_cycle_space.jl
julia --project=experiments experiments/test/active_radiality.jl
julia --project=experiments experiments/test/compiled_views_surgery_witness.jl
julia --project=experiments experiments/test/port_factor_architecture.jl
```

**Questions:**

- Are graph, port--factor, asset, and compiled-view claims kept distinct?
- Does each proposed transformation declare its forgotten information, target
  closure, recovery map, and observation family?
- Are exactness labels attached to the right object rather than pooled across
  connectivity, boundary behaviour, equations, and feasible sets?
- Are the formal-methods citations used as vocabulary or as actual support for
  an electrical theorem?
- Is the proposed certificate composition law stated at the strongest level
  justified by the available definitions and witnesses?

**Out of scope:** physical parameter accuracy, utility data semantics, and
solver performance except where they affect the formal claim boundary.

## Track B — Circuit, multiconductor, and grounding models

**Reviewer profile:** circuit theory, power-system component modelling,
multiconductor lines, grounding, or transformer modelling.

**Bounded chapters:**

- `docs/src/foundations/circuit-formulations-and-lowering.md`
- `docs/src/foundations/earth-ground-models.md`
- `docs/src/foundations/impedance-fidelity-ladder.md`
- `docs/src/foundations/orientation-terminal-power.md`
- `docs/src/transformations/circuit-coordinate-transformations.md`
- `docs/src/transformations/conductor-coordinate-normalization.md`
- `docs/src/transformations/degree-two-series-elimination.md`
- `docs/src/transformations/transformer-winding-coordinate-normalization.md`
- `docs/src/transformations/multiwinding-leakage-reference-compilation.md`
- `docs/src/transformations/multiwinding-terminal-leakage-assembly.md`
- `docs/src/transformations/fixed-linear-transformer-factor-completion.md`
- `docs/src/cases/four-wire-impedance-model-ladder.md`
- `docs/src/cases/australian-carson-reproduction.md`

**Claims:** `FORMULATION-NODAL-001`, `FORMULATION-NODAL-002`,
`FORMULATION-NODAL-003`, `TR-COORD-001`, `TR-SER-001`, `TR-SER-002`,
`TR-SER-003`, `TR-XFMR-001`, `TR-XFMR-002`, `TR-XFMR-003`, `TR-XFMR-004`,
`TR-XFMR-005`, `GROUND-SCOPE-001`, `GROUND-SCOPE-002`, `GROUND-SCOPE-003`,
`GROUND-SCOPE-004`, `IMPEDANCE-LADDER-001`, `PRACTICE-IMPEDANCE-001`,
`AU-CARSON-001`.

**Artifacts and figures:**

- `experiments/generated/circuit-formulation-witness.json`
- `experiments/generated/coordinate-normalization-certificate.json`
- `experiments/generated/degree-two-series-certificate.json`
- `experiments/generated/transformer-winding-normalization-certificate.json`
- `experiments/generated/multiwinding-leakage-compilation-certificate.json`
- `experiments/generated/multiwinding-terminal-assembly-certificate.json`
- `experiments/generated/four-wire-impedance-model-ladder.json`
- `experiments/generated/australian-carson-reproduction.json`
- `experiments/generated/explicit-earth-kron-independent-reproduction.json`

**Reproduction:**

```text
julia --project=experiments experiments/test/circuit_formulation_witness.jl
julia --project=experiments experiments/test/coordinate_normalization.jl
julia --project=experiments experiments/test/series_elimination.jl
julia --project=experiments experiments/test/transformer_winding_normalization.jl
julia --project=experiments experiments/test/four_wire_impedance_model_ladder.jl
julia --project=experiments experiments/test/australian_carson_reproduction.jl
julia --project=experiments experiments/test/explicit_earth_kron.jl
```

**Questions:**

- Are conductor ordering, orientation, dual current maps, and complex-power
  conventions consistent across every coordinate transformation?
- Does the earth-return discussion distinguish reduced-earth impedance factors,
  explicit earth conductors, neutral bonds, and grounding observations?
- Are the series and transformer results exact only under the stated coupling,
  incidence, reference, and limit assumptions?
- Are Fortescue/sequence statements clearly restricted to permutation- or
  sequence-invariant cases rather than used as a general unbalanced-model
  simplification?
- Does the Australian Carson reproduction verify the declared source scope
  without being presented as validation of all engineering adapters?

**Out of scope:** graph-theoretic canonicality, utility workflow adoption, and
global OPF claims.

## Track C — Optimization, feasible sets, and decision preservation

**Reviewer profile:** power-system optimization, OPF, robust constraints,
network reduction, or decision-focused model equivalence.

**Bounded chapters:**

- `docs/src/start/first-failure-parallel-branches.md`
- `docs/src/cases/multiconductor-parallel-ac-decision.md`
- `docs/src/cases/four-wire-parallel-ac-decision.md`
- `docs/src/cases/pi-four-wire-parallel-ac-decision.md`
- `docs/src/transformations/parameterized-transformer-tap-decisions.md`
- `docs/src/cases/transformer-tap-ac-decision.md`
- `docs/src/foundations/load-models-and-decision-dependence.md`
- `docs/src/transformations/kron-ward-opti-kron.md`
- `docs/src/foundations/numerical-consequences.md`

**Claims:** `TR-PAR-001`, `TR-PAR-002`, `TR-PAR-003`, `TR-PAR-004`,
`TR-PAR-005`, `TR-PAR-006`, `TR-PAR-007`, `TR-PAR-JOINT-001`,
`TR-PAR-AC-JOINT-001`, `TR-PAR-STATE-001`, `TR-PAR-SINGULAR-001`,
`TR-XFMR-006`, `TR-XFMR-007`, `TR-XFMR-008`, `TR-XFMR-009`, `TR-XFMR-010`,
`TR-KRON-001`, `TR-KRON-002`, `TR-KRON-003`, `LOAD-DECISION-001`,
`LOAD-CONNECTION-001`, `LOAD-CONTINUATION-001`, `NUMERICAL-001`,
`NUMERICAL-002`, `NUMERICAL-003`.

**Artifacts and figures:**

- `experiments/generated/parallel-branch-certificate.json`
- `experiments/generated/multiconductor-parallel-ac-certificate.json`
- `experiments/generated/four-wire-parallel-ac-certificate.json`
- `experiments/generated/pi-four-wire-parallel-ac-certificate.json`
- `experiments/generated/transformer-tap-ac-decision-certificate.json`
- `experiments/generated/typed-kron-certificate.json`
- `experiments/generated/kron-ward-scenario-comparison.json`
- `experiments/generated/nonlinear-kkt-witness.json`

**Reproduction:**

```text
julia --project=experiments experiments/test/multiconductor_parallel_ac.jl
julia --project=experiments experiments/test/four_wire_parallel_ac.jl
julia --project=experiments experiments/test/pi_four_wire_parallel_ac.jl
julia --project=experiments experiments/test/transformer_tap_ac_decision.jl
julia --project=experiments experiments/test/typed_kron.jl
julia --project=experiments experiments/test/kron_ward_scenario.jl
julia --project=experiments experiments/run_nonlinear_kkt_witness.jl
```

**Questions:**

- Is every exact, inner, outer, or scenario-approximate label attached to a
  declared feasible set, boundary behaviour, equation, or observation sample?
- Do the parallel-member results distinguish constraint pruning from asset
  aggregation and preserve member identities and limits where claimed?
- Are solver outcomes, continuation traces, and local KKT diagnostics kept
  separate from theorem-level or global-optimality claims?
- Do coordinate actions, Kron reduction, transformer taps, and load models
  preserve the decision variables and recovery obligations stated in the text?
- Are singular, state-dependent, jointly coupled, and nonlinear cases refused
  or downgraded where the certificate does not cover them?

**Out of scope:** whether the chosen graph vocabulary is the best general
formalism and whether a utility's data model is operationally deployable.

## Track D — Utility data, engineering practice, and visual language

**Reviewer profile:** utility data models, EMS topology processing, engineering
software, power-system practice, technical communication, or visual language.

**Bounded chapters:**

- `docs/src/foundations/source-to-canonical-model.md`
- `docs/src/foundations/data-model-crosswalk.md`
- `docs/src/foundations/node-breaker-topology-processing.md`
- `docs/src/foundations/rating-semantics.md`
- `docs/src/literature/representation-implementation-record.md`
- `docs/src/start/one-network-five-languages.md`
- `docs/src/start/how-to-read-diagrams-and-equations.md`
- `docs/src/foundations/notation-and-conventions.md`
- `docs/src/foundations/translation-traps.md`

**Claims:** `VOCAB-BRIDGE-001`, `TOPOLOGY-001`, `RATING-001`,
`DATA-XWALK-001`, `PRACTICE-ADAPTER-001`, `PRACTICE-ARCH-001`,
`ARCH-NODAL-001`, `ARCH-SUPPORT-001`, `ARCH-RECOVERY-001`,
`ARCH-RECOVERY-002`, `ARCH-RECOVERY-003`, `ARCH-RECOVERY-004`,
`TR-NEG-001`.

**Artifacts and figures:**

- `experiments/generated/data-model-crosswalk-witness.json`
- `experiments/generated/node-breaker-state-witness.json`
- `experiments/generated/topology-projection-witness.json`
- `experiments/generated/view-source-maps.json`
- `experiments/generated/translation-trap-witnesses.json`
- bus-meaning overlays, topology-projection layers, source-canonical
  pipeline, provenance-lineage, and visual-language figures.

**Reproduction:**

```text
julia --project=experiments experiments/test/data_model_crosswalk.jl
julia --project=experiments experiments/test/node_breaker_state_witness.jl
julia --project=experiments experiments/test/topology_projection_witness.jl
julia --project=experiments experiments/test/public_api.jl
python3 scripts/check_callouts.py
python3 scripts/check_rendered_outputs.py
```

**Questions:**

- Are CIM/CGMES, PowSyBl, PowerModelsDistribution, OpenDSS, and MATPOWER
  described as scoped source or software precedents rather than interchangeable
  semantic standards?
- Does each source-to-canonical adapter expose version, profile, state,
  grounding, rating, and provenance assumptions?
- Are node-breaker, bus-breaker, bus-branch, and topological-node views kept
  distinct from the underlying asset model and from the book's proposed typed
  quotient?
- Do figures and shorthand preserve the same bus, terminal, conductor, state,
  and decision meanings as the equations and claims?
- Can a domain practitioner identify what is an industry convention, what is an
  official software behaviour, and what is an author-derived proposal?

**Out of scope:** proving the mathematical certificates in Tracks A--C.

## Packet assembly and release rule

Each reviewer receives only the relevant track section, its listed chapters,
the cited claims and artifacts, and the common instructions. The full PDF is
available as context but is not the assigned review object. The response form
is [external-review-response-ledger.csv](external-review-response-ledger.csv).

A claim may be labelled **externally reviewed** only after the ledger contains a
named reviewer, date, track, decision, affected claim, issue class, and recorded
disposition. Local reproduction, an automated second coding pass, or an empty
reviewer row cannot satisfy that gate.

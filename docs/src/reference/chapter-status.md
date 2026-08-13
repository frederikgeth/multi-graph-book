# Chapter status

<!-- generated-from claims/claims.toml sha256:3f411f2c1e058141824abb668afa7561c84ee94c2976c8f79a43ec3fd3526eff -->
This page is generated from the claims ledger. It makes the evidence state visible without
requiring readers to inspect TOML or generated JSON files. A chapter with no claim entry is
not automatically unscientific; it is marked as needing explicit scope/status metadata.

| Chapter | Claims | Claim types | Verification | Open issue |
| --- | ---: | --- | --- | --- |
| [Executable running network](../cases/executable-running-network.md) | 2 | empirical | `self-checked` | Add an independent fixture reviewer.; Re-run with an independent solver where possible. |
| [Non-proportional three-phase four-wire parallel case](../cases/four-wire-parallel-ac-decision.md) | 1 | theorem | `self-checked` | TR-PAR-007 covers nonsingular nominal-pi primitives; extend to singular maps, several retained members, state-dependent topology and controls, and obtain an independent global optimality bound where required. |
| [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | 2 | empirical, theorem | `self-checked` | Extend the scalar quadratic-containment idea to non-proportional three-phase four-wire members and reproduce with an independent numerical solver.; Extend from pairwise implications to constraints jointly implied by multiple retained limits, then condition certificates on topology, controls, outages, investments, and non-Euclidean thermal regions. |
| [Four-wire nominal-pi parallel case](../cases/pi-four-wire-parallel-ac-decision.md) | 1 | theorem | `self-checked` | Extend to singular shunted primitives, voltage-dependent shunts, several retained members, topology and control states, and global AC optimality bounds where required. |
| [The running multiconductor network](../cases/running-network.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | 2 | empirical, theorem | `independently-implemented, self-checked` | TR-XFMR-007 independently reproduces the numerical branch search; extend to unbalanced downstream networks, phase-angle controls, independent-phase taps, mechanical coupling, automatic logic, switching costs, and tap-dependent loss parameters.; Reproduce the case with an independently assembled transformer primitive or external power-system tool and establish global or branch-completeness guarantees where required. |
| [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | 2 | theorem | `self-checked` | Extend the executable invariant checks to conductor-terminal incidence and state-indexed multi-terminal factors.; Add active-state radiality certificates with open/closed switches, outages, and multi-terminal compilation choices. |
| [Data-model crosswalk](../foundations/data-model-crosswalk.md) | 1 | practice | `self-checked` | Implement and test version-pinned adapters with round-trip provenance and rating checks. |
| [Earth, neutral, and reference model classes](../foundations/earth-ground-models.md) | 1 | definition | `self-checked` | Add an explicit-earth-conductor fixture and a protection/grounding-asset case. |
| [Formal representation frameworks](../foundations/formal-representation-frameworks.md) | 1 | empirical | `self-checked` | Lift the data witness to evaluated factor relations and independently review the architecture against a non-synthetic asset model. |
| [Node--breaker, bus--breaker, and topology processing](../foundations/node-breaker-topology-processing.md) | 1 | definition | `self-checked` | Add a generated node--breaker fixture with open, closed, and unknown switch states. |
| [Notation and modelling conventions](../foundations/notation-and-conventions.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | 3 | definition, empirical | `self-checked` | Extend the current five-bus structural witness to a pinned running-network benchmark with solver-exported Ybus/Jacobian sparsity, ordering-dependent fill, and recovered decision-margin checks.; Add an independent KKT/Jacobian export and compare ordering-dependent fill and decision margins across source and reduced views.; Connect the same source/aggregate comparison to BMOPFTools checked KKT/DiffOpt diagnostics and solver-exported active-set rows. |
| [Orientation, terminal quantities, and power transfer](../foundations/orientation-terminal-power.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Preservation contracts](../foundations/preservation-contracts.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Rating and limit semantics](../foundations/rating-semantics.md) | 1 | definition | `self-checked` | Map selected utility and software rating fields into the typed limit record. |
| [Representation architecture](../foundations/representation-architecture.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Maps between representation frameworks](../foundations/representation-maps.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Representation taxonomy](../foundations/representation-taxonomy.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Scope and thesis](../foundations/scope-and-thesis.md) | 1 | definition | `self-checked` | — |
| [Translation traps: graphs, circuits, and power-system language](../foundations/translation-traps.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [When the general model collapses](../foundations/when-general-model-collapses.md) | 2 | empirical, theorem | `self-checked` | Add a generated balanced transmission fixture, residual calculation, and independent mathematical review.; Extend the witness to nominal-pi shunts, network assembly, and an independently implemented balanced transmission fixture. |
| [Structure-Preserving Graph Models for Power Networks](../index.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Literature map](../literature/literature-map.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Research agenda](../literature/research-agenda.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [References](../reference/references.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Terminology](../reference/terminology.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | 4 | empirical, theorem | `self-checked` | Add an independent mathematical reviewer.; Molzahn2018 gives an exact scalar AC constraint-pruning test without asset aggregation; a general multiconductor classification remains open.; Establish necessary and sufficient redundancy tests for arbitrary multiconductor limits and for state- or decision-dependent line models.; The multiconductor mechanism is exercised in TR-PAR-004; add an independent reviewer for this linear case. |
| [A five-bus multigraph: identities, cycles, and tree coordinates](../start/five-bus-cycle-spaces.md) | 1 | theorem | `self-checked` | Lift the executable incidence and cycle objects to conductor-terminal graphs, state-conditioned topology decisions, and compiled multi-terminal factors. |
| [One network, many graphs](../start/one-network-many-graphs.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Certificate schema and composition](../transformations/certificate-schema-and-composition.md) | 1 | theorem | `self-checked` | Prove associativity modulo certificate serialization and strengthen compatibility checks beyond object identity. |
| [Circuit coordinate transformations: phase-to-neutral and phase-to-phase](../transformations/circuit-coordinate-transformations.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Conductor-coordinate normalization](../transformations/conductor-coordinate-normalization.md) | 1 | theorem | `self-checked` | Add an independent mathematical reviewer and extend coordinate actions to general input/output tensors. |
| [Degree-two series elimination](../transformations/degree-two-series-elimination.md) | 2 | theorem | `self-checked` | Add an independent mathematical reviewer.; Formalize sufficient physical line-merge guards for selected line models. |
| [Fixed-linear transformer factor completion](../transformations/fixed-linear-transformer-factor-completion.md) | 1 | theorem | `self-checked` | Independently review the completion and test phase-angle controls, tap-dependent leakage, and total-current or apparent-power ratings. |
| [Guarded normalization rules](../transformations/guarded-normalization.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Kron, Ward, and optimized network equivalents](../transformations/kron-ward-opti-kron.md) | 1 | theorem | `unreviewed` | Add executable random-matrix and terminal-permutation tests and obtain an independent mathematical review. |
| [Multiwinding leakage reference compilation](../transformations/multiwinding-leakage-reference-compilation.md) | 1 | theorem | `self-checked` | Add an independent transformer-model review and establish compact serialization contracts that preserve the declared source and compilation references. |
| [Multiwinding terminal leakage assembly](../transformations/multiwinding-terminal-leakage-assembly.md) | 1 | theorem | `self-checked` | Independently review the fixed and parameterized completions and test tap-dependent leakage or excitation models. |
| [Parameterized transformer tap decisions](../transformations/parameterized-transformer-tap-decisions.md) | 1 | theorem | `self-checked` | The first solver-backed network embedding is TR-XFMR-006; extend the contract to phase-angle, independent per-phase, mechanically coupled, and tap-dependent-loss controls. |
| [Projection, compilation, and reduction](../transformations/projection-compilation-reduction.md) | 0 | — | `untracked` | Add chapter-level scope/status metadata |
| [Transformer-winding coordinate normalization](../transformations/transformer-winding-coordinate-normalization.md) | 1 | theorem | `self-checked` | Prove which normalized factors can be serialized back into compact vector-group and delta-roll fields without loss. |

_This file is regenerated during the documentation build._

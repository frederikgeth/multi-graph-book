# Knowledge-base indexes

<!-- generated-from claims/claims.toml sha256:3f411f2c1e058141824abb668afa7561c84ee94c2976c8f79a43ec3fd3526eff -->
This page is generated from `claims/claims.toml` and the JSON artifacts under
`experiments/generated/`. It is the HTML knowledge base's retrieval layer; the curated
PDF route does not attempt to reproduce these indexes as a linear chapter sequence.

**Indexed claims:** 36  
**Indexed chapters:** 25

## Claims by type

### `definition` (5)

| Claim | Chapter | Verification |
| --- | --- | --- |
| `GROUND-SCOPE-001` — Reference, neutral, earth-return, and grounding-asset semantics are distinct model objects; reductions involving them must declare an earth-return class, grounding points, retained observations, and recovery data. | [Earth, neutral, and reference model classes](../foundations/earth-ground-models.md) | `self-checked` |
| `NUMERICAL-001` — Representation and reduction choices have numerical consequences that must be reported separately from electrical preservation: coordinate scaling changes conditioning without changing an invertible solution set, Jacobian dependency graphs need not equal physical graphs, Schur elimination can create fill-in, and decision certificates require residual/error estimates and margins. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `self-checked` |
| `RATING-001` — A power-network rating must identify its constrained asset or terminal, measured quantity and feasible region, duration, ambient/scenario validity, and ownership/provenance before a transformation can claim to preserve it. | [Rating and limit semantics](../foundations/rating-semantics.md) | `self-checked` |
| `THESIS-001` — Representation adequacy is evaluated relative to declared observations, constraints, and decisions. | [Scope and thesis](../foundations/scope-and-thesis.md) | `self-checked` |
| `TOPOLOGY-001` — For a fixed switch state, topological nodes are the connected components of the closed-switch connectivity graph; compiling them into bus--branch buses is a state-conditioned quotient that requires provenance and does not preserve switching decisions by itself. | [Node--breaker, bus--breaker, and topology processing](../foundations/node-breaker-topology-processing.md) | `self-checked` |

### `empirical` (9)

| Claim | Chapter | Verification |
| --- | --- | --- |
| `ARCH-PORT-001` — A minimal executable port--factor bundle instantiated from the running network validates typed port-to-junction and port-to-factor incidence, a three-port multiwinding factor, grounding as an explicit factor, and a many-to-many asset/electrical relation Λ. | [Formal representation frameworks](../foundations/formal-representation-frameworks.md) | `self-checked` |
| `COLLAPSE-002` — The generated Fortescue witness diagonalizes a circulant three-phase impedance matrix and preserves the positive-sequence subspace, while a non-circulant perturbation produces sequence mixing and a positive-subspace residual. | [When the general model collapses](../foundations/when-general-model-collapses.md) | `self-checked` |
| `FIXTURE-001` — Running-network fixture v0.1.0 passes the current BMOPFTools JSON schema and conformance checks without errors or warnings. | [Executable running network](../cases/executable-running-network.md) | `self-checked` |
| `FIXTURE-002` — The v0.1.0 continuous PF and OPF instances terminate locally solved in the recorded environment. | [Executable running network](../cases/executable-running-network.md) | `self-checked` |
| `NUMERICAL-002` — For the pinned running-network fixture, BMOPFTools exports a 20-by-20 passive Ybus with 166 nonzeros; the constant-Z linearized Ybus agrees with it, and realification produces a 40-by-40 current-voltage matrix with 664 nonzeros. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `self-checked` |
| `NUMERICAL-003` — In the pinned nonlinear two-bus parallel-member witness, retaining two explicit member-current laws produces a 6-by-7 residual Jacobian and 13-by-13 KKT pattern, while the summed-current aggregate produces a 4-by-5 Jacobian and 9-by-9 KKT pattern; symbolic fill changes with elimination order in both formulations. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `self-checked` |
| `TR-PAR-003` — In the recorded two-bus maximum-served-load problem, the naive summed-rating aggregate serves 200 MW while the source and exact lifted formulations each serve 110 MW. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `self-checked` |
| `TR-PAR-004` — In the recorded two-conductor AC maximum-served-load case, the source, exact lifted, and certified exact-pruned formulations have objective 0.6138908, while a summed-limit aggregate has objective 1.0630833 and violates a 0.6 p.u. member limit. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `self-checked` |
| `TR-XFMR-007` — A separate damped finite-difference Newton, continuation, and bisection implementation reproduces all three TR-XFMR-006 tap-conditioned high-voltage branch boundaries without an external optimizer; its largest served-fraction difference from JuMP/Ipopt is 3.14e-10, and both methods select tap 0.95. | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `independently-implemented` |

### `practice` (1)

| Claim | Chapter | Verification |
| --- | --- | --- |
| `DATA-XWALK-001` — CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER provide distinct partial correspondences to the book's asset, terminal, topology, factor, state, and rating objects; successful import is not by itself semantic or decision equivalence. | [Data-model crosswalk](../foundations/data-model-crosswalk.md) | `self-checked` |

### `theorem` (21)

| Claim | Chapter | Verification |
| --- | --- | --- |
| `COLLAPSE-001` — Under compatible three-phase terminals, cyclic (circulant) series and shunt matrices, balanced boundary data, sequence-compatible grounding, two-terminal factor closure, phase-symmetric decisions, and positive-sequence observations, the general phase-domain relation restricts exactly to the positive-sequence scalar network. | [When the general model collapses](../foundations/when-general-model-collapses.md) | `self-checked` |
| `GRAPH-CYCLE-001` — The recorded connected five-bus bus--branch multigraph has seven identified lines, incidence rank four, and cycle-space dimension three; collapsing its parallel q/r pair to a simple edge reduces the cycle-space dimension to two, whereas the spanning-tree-plus-chords representation retains all three source dimensions. | [A five-bus multigraph: identities, cycles, and tree coordinates](../start/five-bus-cycle-spaces.md) | `self-checked` |
| `LIT-PAR-001` — For fixed scalar AC pi-line models on common endpoints, a parallel member's current- or apparent-power limit at one terminal is redundant when its normalized terminal-voltage quadratic feasible set contains that of another member; applying the test at both terminals certifies removal of both directional limits without aggregating the line models. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `self-checked` |
| `TR-COMP-001` — Two exact certified transformations compose when the first target is consumed by the second source; constraint maps apply forward and recovery maps apply in reverse order. | [Certificate schema and composition](../transformations/certificate-schema-and-composition.md) | `self-checked` |
| `TR-COORD-001` — A simultaneous permutation of conductor coordinates, terminal pairing, element matrices, and componentwise limits is an exact normalization with an inverse permutation. | [Conductor-coordinate normalization](../transformations/conductor-coordinate-normalization.md) | `self-checked` |
| `TR-GRAPH-001` — For a loopless identified multigraph and its simple endpoint projection, the multigraph cycle rank exceeds the simple-graph cycle rank by the sum over edge fibres of fibre size minus one; the lost dimensions are line-identity cycles supported on parallel fibres. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `self-checked` |
| `TR-GRAPH-002` — An identified line is a multigraph bridge exactly when its simple endpoint edge is a bridge and its parallel fibre is a singleton; consequently the identified multigraph is a forest exactly when its simple projection is a forest and every edge fibre is a singleton. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `self-checked` |
| `TR-KRON-001` — Typed multiconductor Kron reduction commutes with invertible block-diagonal terminal-coordinate changes when currents transform by the power-dual action. | [Kron, Ward, and optimized network equivalents](../transformations/kron-ward-opti-kron.md) | `unreviewed` |
| `TR-PAR-001` — Summed admittance preserves the unconstrained terminal relation of parallel linear branches. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `self-checked` |
| `TR-PAR-002` — Using the sum of member current ratings can create an outer relaxation of the member-constrained feasible set. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `self-checked` |
| `TR-PAR-005` — For fixed linear complex terminal-current maps with centered Euclidean norm limits, one normalized constraint implies another if and only if the retained normalized real quadratic form minus the candidate form is positive semidefinite; applying this pairwise test to every aligned conductor and both terminal ends certifies exact candidate-limit pruning while retaining both member models. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `self-checked` |
| `TR-PAR-006` — For nonsingular fixed series admittances on common multiconductor endpoint coordinates, candidate component currents recover as I_l2=(Y_l2/Y_l1)I_l1, and the exact maximum of candidate component c over all retained component-current discs is sum_k abs(K_ck) Imax_l1k; in the recorded reciprocal non-proportional three-phase four-wire AC case this certifies all l2 limits redundant, the exact-pruned and source objectives agree at 1.1274329, and a summed-limit aggregate reaches 1.8058181 by violating an l1 limit. | [Non-proportional three-phase four-wire parallel case](../cases/four-wire-parallel-ac-decision.md) | `self-checked` |
| `TR-PAR-007` — For fixed nominal-pi multiconductor members whose retained full two-end terminal-current primitive Ar is nonsingular, all candidate terminal currents recover as Ac*inv(Ar) times the retained terminal-current vector, so exact complex-polydisc row norms certify joint implication across both line ends; in the recorded non-proportional four-wire case, pruning eight member-2 limits preserves the 1.1286205 source objective while a same-size summed-limit model reaches 1.8077114 by violating member 1. | [Four-wire nominal-pi parallel case](../cases/pi-four-wire-parallel-ac-decision.md) | `self-checked` |
| `TR-SER-001` — A zero-injection degree-two junction between coordinate-aligned series elements has equivalent impedance Z_l1 + P' Z_l2 P. | [Degree-two series elimination](../transformations/degree-two-series-elimination.md) | `self-checked` |
| `TR-SER-002` — Exact terminal-behaviour closure under degree-two elimination does not by itself establish closure within a homogeneous physical line class. | [Degree-two series elimination](../transformations/degree-two-series-elimination.md) | `self-checked` |
| `TR-XFMR-001` — A transformer winding terminal permutation is an exact typed-factor normalization when its complete terminal-to-coil incidence relation is right-multiplied by the inverse permutation and coil coordinates remain fixed. | [Transformer-winding coordinate normalization](../transformations/transformer-winding-coordinate-normalization.md) | `self-checked` |
| `TR-XFMR-002` — Complete pairwise multiwinding short-circuit impedances compile exactly into a reference-coordinate impedance matrix ZB, from which every pairwise impedance is recoverable; changing the selected reference winding leaves the external winding admittance invariant, and the classical star/T representation is the three-winding special case. | [Multiwinding leakage reference compilation](../transformations/multiwinding-leakage-reference-compilation.md) | `self-checked` |
| `TR-XFMR-003` — Aligned winding connection-incidence factors compose exactly with a multiwinding leakage admittance as Yterminal=A'*(Yw kron I)*A; retaining the coil-current map preserves per-coil winding limits and makes terminal-coordinate and leakage-reference changes explicit coordinate actions. | [Multiwinding terminal leakage assembly](../transformations/multiwinding-terminal-leakage-assembly.md) | `self-checked` |
| `TR-XFMR-004` — A fixed linear transformer completion with declared voltage transfer T, leakage map B=T*A, excitation placement S, and transformer-internal grounding has terminal admittance Ycomplete=B^H*Ycoil*B+S^T*Y0*S+Yground; the power-dual and component-current recovery maps preserve the declared leakage-path limits, while adjustable transfers must remain parameterized decision factors. | [Fixed-linear transformer factor completion](../transformations/fixed-linear-transformer-factor-completion.md) | `self-checked` |
| `TR-XFMR-005` — A continuous or discrete scalar winding tap compiles exactly as a retained parameterized transformer factor when coefficient_xkc(tap)=tap*base_coefficient_xkc and the decision identity and domain are mapped identically; freezing the tap at its start value is generally only an inner restriction, and in the recorded discrete witness it loses the 1.05 optimum and increases the winding-current objective by 671.060 A. | [Parameterized transformer tap decisions](../transformations/parameterized-transformer-tap-decisions.md) | `self-checked` |
| `TR-XFMR-006` — A retained finite scalar transformer tap factor embeds exactly into unchanged multiconductor AC voltage, KCL, power-balance, voltage-limit, and recovered leakage-current constraints by pointwise evaluation; in the recorded 11-terminal WYE/WYE/DELTA case, direct source and parameterized target subproblems agree at all three taps, select 0.95 with served fraction 1.2305865, and freezing the 1.00 start loses 0.0601126 served fraction (0.090169 MW). | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `self-checked` |

## Claims by verification state

| Verification | Claims |
| --- | ---: |
| `independently-implemented` | 1 |
| `self-checked` | 34 |
| `unreviewed` | 1 |

## Unresolved issues

| Claim | Issue |
| --- | --- |
| `ARCH-PORT-001` | Lift the data witness to evaluated factor relations and independently review the architecture against a non-synthetic asset model. |
| `COLLAPSE-001` | Add a generated balanced transmission fixture, residual calculation, and independent mathematical review. |
| `COLLAPSE-002` | Extend the witness to nominal-pi shunts, network assembly, and an independently implemented balanced transmission fixture. |
| `DATA-XWALK-001` | Implement and test version-pinned adapters with round-trip provenance and rating checks. |
| `FIXTURE-001` | Add an independent fixture reviewer. |
| `FIXTURE-002` | Re-run with an independent solver where possible. |
| `GRAPH-CYCLE-001` | Lift the executable incidence and cycle objects to conductor-terminal graphs, state-conditioned topology decisions, and compiled multi-terminal factors. |
| `GROUND-SCOPE-001` | Add an explicit-earth-conductor fixture and a protection/grounding-asset case. |
| `LIT-PAR-001` | Establish necessary and sufficient redundancy tests for arbitrary multiconductor limits and for state- or decision-dependent line models. |
| `NUMERICAL-001` | Extend the current five-bus structural witness to a pinned running-network benchmark with solver-exported Ybus/Jacobian sparsity, ordering-dependent fill, and recovered decision-margin checks. |
| `NUMERICAL-002` | Add an independent KKT/Jacobian export and compare ordering-dependent fill and decision margins across source and reduced views. |
| `NUMERICAL-003` | Connect the same source/aggregate comparison to BMOPFTools checked KKT/DiffOpt diagnostics and solver-exported active-set rows. |
| `RATING-001` | Map selected utility and software rating fields into the typed limit record. |
| `TOPOLOGY-001` | Add a generated node--breaker fixture with open, closed, and unknown switch states. |
| `TR-COMP-001` | Prove associativity modulo certificate serialization and strengthen compatibility checks beyond object identity. |
| `TR-COORD-001` | Add an independent mathematical reviewer and extend coordinate actions to general input/output tensors. |
| `TR-GRAPH-001` | Extend the executable invariant checks to conductor-terminal incidence and state-indexed multi-terminal factors. |
| `TR-GRAPH-002` | Add active-state radiality certificates with open/closed switches, outages, and multi-terminal compilation choices. |
| `TR-KRON-001` | Add executable random-matrix and terminal-permutation tests and obtain an independent mathematical review. |
| `TR-PAR-001` | Add an independent mathematical reviewer. |
| `TR-PAR-002` | Molzahn2018 gives an exact scalar AC constraint-pruning test without asset aggregation; a general multiconductor classification remains open. |
| `TR-PAR-003` | The multiconductor mechanism is exercised in TR-PAR-004; add an independent reviewer for this linear case. |
| `TR-PAR-004` | Extend the scalar quadratic-containment idea to non-proportional three-phase four-wire members and reproduce with an independent numerical solver. |
| `TR-PAR-005` | Extend from pairwise implications to constraints jointly implied by multiple retained limits, then condition certificates on topology, controls, outages, investments, and non-Euclidean thermal regions. |
| `TR-PAR-006` | TR-PAR-007 covers nonsingular nominal-pi primitives; extend to singular maps, several retained members, state-dependent topology and controls, and obtain an independent global optimality bound where required. |
| `TR-PAR-007` | Extend to singular shunted primitives, voltage-dependent shunts, several retained members, topology and control states, and global AC optimality bounds where required. |
| `TR-SER-001` | Add an independent mathematical reviewer. |
| `TR-SER-002` | Formalize sufficient physical line-merge guards for selected line models. |
| `TR-XFMR-001` | Prove which normalized factors can be serialized back into compact vector-group and delta-roll fields without loss. |
| `TR-XFMR-002` | Add an independent transformer-model review and establish compact serialization contracts that preserve the declared source and compilation references. |
| `TR-XFMR-003` | Independently review the fixed and parameterized completions and test tap-dependent leakage or excitation models. |
| `TR-XFMR-004` | Independently review the completion and test phase-angle controls, tap-dependent leakage, and total-current or apparent-power ratings. |
| `TR-XFMR-005` | The first solver-backed network embedding is TR-XFMR-006; extend the contract to phase-angle, independent per-phase, mechanically coupled, and tap-dependent-loss controls. |
| `TR-XFMR-006` | TR-XFMR-007 independently reproduces the numerical branch search; extend to unbalanced downstream networks, phase-angle controls, independent-phase taps, mechanical coupling, automatic logic, switching costs, and tap-dependent loss parameters. |
| `TR-XFMR-007` | Reproduce the case with an independently assembled transformer primitive or external power-system tool and establish global or branch-completeness guarantees where required. |

## Facet indexes

These retrieval facets are provisional and path-derived. They are navigation aids, not
additional verification labels; explicit facet fields can replace them when the claims
schema is normalised.

### `decision-cases` (16)

| Claim | Chapter | Type |
| --- | --- | --- |
| `FIXTURE-001` — Running-network fixture v0.1.0 passes the current BMOPFTools JSON schema and conformance checks without errors or warnings. | [Executable running network](../cases/executable-running-network.md) | `empirical` |
| `FIXTURE-002` — The v0.1.0 continuous PF and OPF instances terminate locally solved in the recorded environment. | [Executable running network](../cases/executable-running-network.md) | `empirical` |
| `TR-PAR-001` — Summed admittance preserves the unconstrained terminal relation of parallel linear branches. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-002` — Using the sum of member current ratings can create an outer relaxation of the member-constrained feasible set. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-003` — In the recorded two-bus maximum-served-load problem, the naive summed-rating aggregate serves 200 MW while the source and exact lifted formulations each serve 110 MW. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `empirical` |
| `TR-PAR-004` — In the recorded two-conductor AC maximum-served-load case, the source, exact lifted, and certified exact-pruned formulations have objective 0.6138908, while a summed-limit aggregate has objective 1.0630833 and violates a 0.6 p.u. member limit. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `empirical` |
| `TR-PAR-005` — For fixed linear complex terminal-current maps with centered Euclidean norm limits, one normalized constraint implies another if and only if the retained normalized real quadratic form minus the candidate form is positive semidefinite; applying this pairwise test to every aligned conductor and both terminal ends certifies exact candidate-limit pruning while retaining both member models. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-006` — For nonsingular fixed series admittances on common multiconductor endpoint coordinates, candidate component currents recover as I_l2=(Y_l2/Y_l1)I_l1, and the exact maximum of candidate component c over all retained component-current discs is sum_k abs(K_ck) Imax_l1k; in the recorded reciprocal non-proportional three-phase four-wire AC case this certifies all l2 limits redundant, the exact-pruned and source objectives agree at 1.1274329, and a summed-limit aggregate reaches 1.8058181 by violating an l1 limit. | [Non-proportional three-phase four-wire parallel case](../cases/four-wire-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-007` — For fixed nominal-pi multiconductor members whose retained full two-end terminal-current primitive Ar is nonsingular, all candidate terminal currents recover as Ac*inv(Ar) times the retained terminal-current vector, so exact complex-polydisc row norms certify joint implication across both line ends; in the recorded non-proportional four-wire case, pruning eight member-2 limits preserves the 1.1286205 source objective while a same-size summed-limit model reaches 1.8077114 by violating member 1. | [Four-wire nominal-pi parallel case](../cases/pi-four-wire-parallel-ac-decision.md) | `theorem` |
| `TR-XFMR-001` — A transformer winding terminal permutation is an exact typed-factor normalization when its complete terminal-to-coil incidence relation is right-multiplied by the inverse permutation and coil coordinates remain fixed. | [Transformer-winding coordinate normalization](../transformations/transformer-winding-coordinate-normalization.md) | `theorem` |
| `TR-XFMR-002` — Complete pairwise multiwinding short-circuit impedances compile exactly into a reference-coordinate impedance matrix ZB, from which every pairwise impedance is recoverable; changing the selected reference winding leaves the external winding admittance invariant, and the classical star/T representation is the three-winding special case. | [Multiwinding leakage reference compilation](../transformations/multiwinding-leakage-reference-compilation.md) | `theorem` |
| `TR-XFMR-003` — Aligned winding connection-incidence factors compose exactly with a multiwinding leakage admittance as Yterminal=A'*(Yw kron I)*A; retaining the coil-current map preserves per-coil winding limits and makes terminal-coordinate and leakage-reference changes explicit coordinate actions. | [Multiwinding terminal leakage assembly](../transformations/multiwinding-terminal-leakage-assembly.md) | `theorem` |
| `TR-XFMR-004` — A fixed linear transformer completion with declared voltage transfer T, leakage map B=T*A, excitation placement S, and transformer-internal grounding has terminal admittance Ycomplete=B^H*Ycoil*B+S^T*Y0*S+Yground; the power-dual and component-current recovery maps preserve the declared leakage-path limits, while adjustable transfers must remain parameterized decision factors. | [Fixed-linear transformer factor completion](../transformations/fixed-linear-transformer-factor-completion.md) | `theorem` |
| `TR-XFMR-005` — A continuous or discrete scalar winding tap compiles exactly as a retained parameterized transformer factor when coefficient_xkc(tap)=tap*base_coefficient_xkc and the decision identity and domain are mapped identically; freezing the tap at its start value is generally only an inner restriction, and in the recorded discrete witness it loses the 1.05 optimum and increases the winding-current objective by 671.060 A. | [Parameterized transformer tap decisions](../transformations/parameterized-transformer-tap-decisions.md) | `theorem` |
| `TR-XFMR-006` — A retained finite scalar transformer tap factor embeds exactly into unchanged multiconductor AC voltage, KCL, power-balance, voltage-limit, and recovered leakage-current constraints by pointwise evaluation; in the recorded 11-terminal WYE/WYE/DELTA case, direct source and parameterized target subproblems agree at all three taps, select 0.95 with served fraction 1.2305865, and freezing the 1.00 start loses 0.0601126 served fraction (0.090169 MW). | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `theorem` |
| `TR-XFMR-007` — A separate damped finite-difference Newton, continuation, and bisection implementation reproduces all three TR-XFMR-006 tap-conditioned high-voltage branch boundaries without an external optimizer; its largest served-fraction difference from JuMP/Ipopt is 3.14e-10, and both methods select tap 0.95. | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `empirical` |

### `graph-and-topology` (10)

| Claim | Chapter | Type |
| --- | --- | --- |
| `GRAPH-CYCLE-001` — The recorded connected five-bus bus--branch multigraph has seven identified lines, incidence rank four, and cycle-space dimension three; collapsing its parallel q/r pair to a simple edge reduces the cycle-space dimension to two, whereas the spanning-tree-plus-chords representation retains all three source dimensions. | [A five-bus multigraph: identities, cycles, and tree coordinates](../start/five-bus-cycle-spaces.md) | `theorem` |
| `TR-GRAPH-001` — For a loopless identified multigraph and its simple endpoint projection, the multigraph cycle rank exceeds the simple-graph cycle rank by the sum over edge fibres of fibre size minus one; the lost dimensions are line-identity cycles supported on parallel fibres. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-GRAPH-002` — An identified line is a multigraph bridge exactly when its simple endpoint edge is a bridge and its parallel fibre is a singleton; consequently the identified multigraph is a forest exactly when its simple projection is a forest and every edge fibre is a singleton. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-PAR-001` — Summed admittance preserves the unconstrained terminal relation of parallel linear branches. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-002` — Using the sum of member current ratings can create an outer relaxation of the member-constrained feasible set. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-003` — In the recorded two-bus maximum-served-load problem, the naive summed-rating aggregate serves 200 MW while the source and exact lifted formulations each serve 110 MW. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `empirical` |
| `TR-PAR-004` — In the recorded two-conductor AC maximum-served-load case, the source, exact lifted, and certified exact-pruned formulations have objective 0.6138908, while a summed-limit aggregate has objective 1.0630833 and violates a 0.6 p.u. member limit. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `empirical` |
| `TR-PAR-005` — For fixed linear complex terminal-current maps with centered Euclidean norm limits, one normalized constraint implies another if and only if the retained normalized real quadratic form minus the candidate form is positive semidefinite; applying this pairwise test to every aligned conductor and both terminal ends certifies exact candidate-limit pruning while retaining both member models. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-006` — For nonsingular fixed series admittances on common multiconductor endpoint coordinates, candidate component currents recover as I_l2=(Y_l2/Y_l1)I_l1, and the exact maximum of candidate component c over all retained component-current discs is sum_k abs(K_ck) Imax_l1k; in the recorded reciprocal non-proportional three-phase four-wire AC case this certifies all l2 limits redundant, the exact-pruned and source objectives agree at 1.1274329, and a summed-limit aggregate reaches 1.8058181 by violating an l1 limit. | [Non-proportional three-phase four-wire parallel case](../cases/four-wire-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-007` — For fixed nominal-pi multiconductor members whose retained full two-end terminal-current primitive Ar is nonsingular, all candidate terminal currents recover as Ac*inv(Ar) times the retained terminal-current vector, so exact complex-polydisc row norms certify joint implication across both line ends; in the recorded non-proportional four-wire case, pruning eight member-2 limits preserves the 1.1286205 source objective while a same-size summed-limit model reaches 1.8077114 by violating member 1. | [Four-wire nominal-pi parallel case](../cases/pi-four-wire-parallel-ac-decision.md) | `theorem` |

### `numerical-evidence` (5)

| Claim | Chapter | Type |
| --- | --- | --- |
| `FIXTURE-001` — Running-network fixture v0.1.0 passes the current BMOPFTools JSON schema and conformance checks without errors or warnings. | [Executable running network](../cases/executable-running-network.md) | `empirical` |
| `FIXTURE-002` — The v0.1.0 continuous PF and OPF instances terminate locally solved in the recorded environment. | [Executable running network](../cases/executable-running-network.md) | `empirical` |
| `NUMERICAL-001` — Representation and reduction choices have numerical consequences that must be reported separately from electrical preservation: coordinate scaling changes conditioning without changing an invertible solution set, Jacobian dependency graphs need not equal physical graphs, Schur elimination can create fill-in, and decision certificates require residual/error estimates and margins. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `definition` |
| `NUMERICAL-002` — For the pinned running-network fixture, BMOPFTools exports a 20-by-20 passive Ybus with 166 nonzeros; the constant-Z linearized Ybus agrees with it, and realification produces a 40-by-40 current-voltage matrix with 664 nonzeros. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `empirical` |
| `NUMERICAL-003` — In the pinned nonlinear two-bus parallel-member witness, retaining two explicit member-current laws produces a 6-by-7 residual Jacobian and 13-by-13 KKT pattern, while the summed-current aggregate produces a 4-by-5 Jacobian and 9-by-9 KKT pattern; symbolic fill changes with elimination order in both formulations. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `empirical` |

### `physical-modelling` (4)

| Claim | Chapter | Type |
| --- | --- | --- |
| `GROUND-SCOPE-001` — Reference, neutral, earth-return, and grounding-asset semantics are distinct model objects; reductions involving them must declare an earth-return class, grounding points, retained observations, and recovery data. | [Earth, neutral, and reference model classes](../foundations/earth-ground-models.md) | `definition` |
| `RATING-001` — A power-network rating must identify its constrained asset or terminal, measured quantity and feasible region, duration, ambient/scenario validity, and ownership/provenance before a transformation can claim to preserve it. | [Rating and limit semantics](../foundations/rating-semantics.md) | `definition` |
| `TR-GRAPH-001` — For a loopless identified multigraph and its simple endpoint projection, the multigraph cycle rank exceeds the simple-graph cycle rank by the sum over edge fibres of fibre size minus one; the lost dimensions are line-identity cycles supported on parallel fibres. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-GRAPH-002` — An identified line is a multigraph bridge exactly when its simple endpoint edge is a bridge and its parallel fibre is a singleton; consequently the identified multigraph is a forest exactly when its simple projection is a forest and every edge fibre is a singleton. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |

### `representation` (13)

| Claim | Chapter | Type |
| --- | --- | --- |
| `ARCH-PORT-001` — A minimal executable port--factor bundle instantiated from the running network validates typed port-to-junction and port-to-factor incidence, a three-port multiwinding factor, grounding as an explicit factor, and a many-to-many asset/electrical relation Λ. | [Formal representation frameworks](../foundations/formal-representation-frameworks.md) | `empirical` |
| `COLLAPSE-001` — Under compatible three-phase terminals, cyclic (circulant) series and shunt matrices, balanced boundary data, sequence-compatible grounding, two-terminal factor closure, phase-symmetric decisions, and positive-sequence observations, the general phase-domain relation restricts exactly to the positive-sequence scalar network. | [When the general model collapses](../foundations/when-general-model-collapses.md) | `theorem` |
| `COLLAPSE-002` — The generated Fortescue witness diagonalizes a circulant three-phase impedance matrix and preserves the positive-sequence subspace, while a non-circulant perturbation produces sequence mixing and a positive-subspace residual. | [When the general model collapses](../foundations/when-general-model-collapses.md) | `empirical` |
| `DATA-XWALK-001` — CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER provide distinct partial correspondences to the book's asset, terminal, topology, factor, state, and rating objects; successful import is not by itself semantic or decision equivalence. | [Data-model crosswalk](../foundations/data-model-crosswalk.md) | `practice` |
| `GROUND-SCOPE-001` — Reference, neutral, earth-return, and grounding-asset semantics are distinct model objects; reductions involving them must declare an earth-return class, grounding points, retained observations, and recovery data. | [Earth, neutral, and reference model classes](../foundations/earth-ground-models.md) | `definition` |
| `NUMERICAL-001` — Representation and reduction choices have numerical consequences that must be reported separately from electrical preservation: coordinate scaling changes conditioning without changing an invertible solution set, Jacobian dependency graphs need not equal physical graphs, Schur elimination can create fill-in, and decision certificates require residual/error estimates and margins. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `definition` |
| `NUMERICAL-002` — For the pinned running-network fixture, BMOPFTools exports a 20-by-20 passive Ybus with 166 nonzeros; the constant-Z linearized Ybus agrees with it, and realification produces a 40-by-40 current-voltage matrix with 664 nonzeros. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `empirical` |
| `NUMERICAL-003` — In the pinned nonlinear two-bus parallel-member witness, retaining two explicit member-current laws produces a 6-by-7 residual Jacobian and 13-by-13 KKT pattern, while the summed-current aggregate produces a 4-by-5 Jacobian and 9-by-9 KKT pattern; symbolic fill changes with elimination order in both formulations. | [Numerical consequences of representation and reduction](../foundations/numerical-consequences.md) | `empirical` |
| `RATING-001` — A power-network rating must identify its constrained asset or terminal, measured quantity and feasible region, duration, ambient/scenario validity, and ownership/provenance before a transformation can claim to preserve it. | [Rating and limit semantics](../foundations/rating-semantics.md) | `definition` |
| `THESIS-001` — Representation adequacy is evaluated relative to declared observations, constraints, and decisions. | [Scope and thesis](../foundations/scope-and-thesis.md) | `definition` |
| `TOPOLOGY-001` — For a fixed switch state, topological nodes are the connected components of the closed-switch connectivity graph; compiling them into bus--branch buses is a state-conditioned quotient that requires provenance and does not preserve switching decisions by itself. | [Node--breaker, bus--breaker, and topology processing](../foundations/node-breaker-topology-processing.md) | `definition` |
| `TR-GRAPH-001` — For a loopless identified multigraph and its simple endpoint projection, the multigraph cycle rank exceeds the simple-graph cycle rank by the sum over edge fibres of fibre size minus one; the lost dimensions are line-identity cycles supported on parallel fibres. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-GRAPH-002` — An identified line is a multigraph bridge exactly when its simple endpoint edge is a bridge and its parallel fibre is a singleton; consequently the identified multigraph is a forest exactly when its simple projection is a forest and every edge fibre is a singleton. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |

### `software-and-data` (4)

| Claim | Chapter | Type |
| --- | --- | --- |
| `ARCH-PORT-001` — A minimal executable port--factor bundle instantiated from the running network validates typed port-to-junction and port-to-factor incidence, a three-port multiwinding factor, grounding as an explicit factor, and a many-to-many asset/electrical relation Λ. | [Formal representation frameworks](../foundations/formal-representation-frameworks.md) | `empirical` |
| `DATA-XWALK-001` — CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER provide distinct partial correspondences to the book's asset, terminal, topology, factor, state, and rating objects; successful import is not by itself semantic or decision equivalence. | [Data-model crosswalk](../foundations/data-model-crosswalk.md) | `practice` |
| `FIXTURE-001` — Running-network fixture v0.1.0 passes the current BMOPFTools JSON schema and conformance checks without errors or warnings. | [Executable running network](../cases/executable-running-network.md) | `empirical` |
| `FIXTURE-002` — The v0.1.0 continuous PF and OPF instances terminate locally solved in the recorded environment. | [Executable running network](../cases/executable-running-network.md) | `empirical` |

### `study-and-literature` (1)

| Claim | Chapter | Type |
| --- | --- | --- |
| `LIT-PAR-001` — For fixed scalar AC pi-line models on common endpoints, a parallel member's current- or apparent-power limit at one terminal is redundant when its normalized terminal-voltage quadratic feasible set contains that of another member; applying the test at both terminals certifies removal of both directional limits without aggregating the line models. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |

### `transformations` (21)

| Claim | Chapter | Type |
| --- | --- | --- |
| `TR-COMP-001` — Two exact certified transformations compose when the first target is consumed by the second source; constraint maps apply forward and recovery maps apply in reverse order. | [Certificate schema and composition](../transformations/certificate-schema-and-composition.md) | `theorem` |
| `TR-COORD-001` — A simultaneous permutation of conductor coordinates, terminal pairing, element matrices, and componentwise limits is an exact normalization with an inverse permutation. | [Conductor-coordinate normalization](../transformations/conductor-coordinate-normalization.md) | `theorem` |
| `TR-GRAPH-001` — For a loopless identified multigraph and its simple endpoint projection, the multigraph cycle rank exceeds the simple-graph cycle rank by the sum over edge fibres of fibre size minus one; the lost dimensions are line-identity cycles supported on parallel fibres. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-GRAPH-002` — An identified line is a multigraph bridge exactly when its simple endpoint edge is a bridge and its parallel fibre is a singleton; consequently the identified multigraph is a forest exactly when its simple projection is a forest and every edge fibre is a singleton. | [Cycles, parallelism, and radial structure](../foundations/cycles-parallelism-radiality.md) | `theorem` |
| `TR-KRON-001` — Typed multiconductor Kron reduction commutes with invertible block-diagonal terminal-coordinate changes when currents transform by the power-dual action. | [Kron, Ward, and optimized network equivalents](../transformations/kron-ward-opti-kron.md) | `theorem` |
| `TR-PAR-001` — Summed admittance preserves the unconstrained terminal relation of parallel linear branches. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-002` — Using the sum of member current ratings can create an outer relaxation of the member-constrained feasible set. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `theorem` |
| `TR-PAR-003` — In the recorded two-bus maximum-served-load problem, the naive summed-rating aggregate serves 200 MW while the source and exact lifted formulations each serve 110 MW. | [A first failure: heterogeneous parallel branches](../start/first-failure-parallel-branches.md) | `empirical` |
| `TR-PAR-004` — In the recorded two-conductor AC maximum-served-load case, the source, exact lifted, and certified exact-pruned formulations have objective 0.6138908, while a summed-limit aggregate has objective 1.0630833 and violates a 0.6 p.u. member limit. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `empirical` |
| `TR-PAR-005` — For fixed linear complex terminal-current maps with centered Euclidean norm limits, one normalized constraint implies another if and only if the retained normalized real quadratic form minus the candidate form is positive semidefinite; applying this pairwise test to every aligned conductor and both terminal ends certifies exact candidate-limit pruning while retaining both member models. | [Multiconductor parallel AC decision case](../cases/multiconductor-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-006` — For nonsingular fixed series admittances on common multiconductor endpoint coordinates, candidate component currents recover as I_l2=(Y_l2/Y_l1)I_l1, and the exact maximum of candidate component c over all retained component-current discs is sum_k abs(K_ck) Imax_l1k; in the recorded reciprocal non-proportional three-phase four-wire AC case this certifies all l2 limits redundant, the exact-pruned and source objectives agree at 1.1274329, and a summed-limit aggregate reaches 1.8058181 by violating an l1 limit. | [Non-proportional three-phase four-wire parallel case](../cases/four-wire-parallel-ac-decision.md) | `theorem` |
| `TR-PAR-007` — For fixed nominal-pi multiconductor members whose retained full two-end terminal-current primitive Ar is nonsingular, all candidate terminal currents recover as Ac*inv(Ar) times the retained terminal-current vector, so exact complex-polydisc row norms certify joint implication across both line ends; in the recorded non-proportional four-wire case, pruning eight member-2 limits preserves the 1.1286205 source objective while a same-size summed-limit model reaches 1.8077114 by violating member 1. | [Four-wire nominal-pi parallel case](../cases/pi-four-wire-parallel-ac-decision.md) | `theorem` |
| `TR-SER-001` — A zero-injection degree-two junction between coordinate-aligned series elements has equivalent impedance Z_l1 + P' Z_l2 P. | [Degree-two series elimination](../transformations/degree-two-series-elimination.md) | `theorem` |
| `TR-SER-002` — Exact terminal-behaviour closure under degree-two elimination does not by itself establish closure within a homogeneous physical line class. | [Degree-two series elimination](../transformations/degree-two-series-elimination.md) | `theorem` |
| `TR-XFMR-001` — A transformer winding terminal permutation is an exact typed-factor normalization when its complete terminal-to-coil incidence relation is right-multiplied by the inverse permutation and coil coordinates remain fixed. | [Transformer-winding coordinate normalization](../transformations/transformer-winding-coordinate-normalization.md) | `theorem` |
| `TR-XFMR-002` — Complete pairwise multiwinding short-circuit impedances compile exactly into a reference-coordinate impedance matrix ZB, from which every pairwise impedance is recoverable; changing the selected reference winding leaves the external winding admittance invariant, and the classical star/T representation is the three-winding special case. | [Multiwinding leakage reference compilation](../transformations/multiwinding-leakage-reference-compilation.md) | `theorem` |
| `TR-XFMR-003` — Aligned winding connection-incidence factors compose exactly with a multiwinding leakage admittance as Yterminal=A'*(Yw kron I)*A; retaining the coil-current map preserves per-coil winding limits and makes terminal-coordinate and leakage-reference changes explicit coordinate actions. | [Multiwinding terminal leakage assembly](../transformations/multiwinding-terminal-leakage-assembly.md) | `theorem` |
| `TR-XFMR-004` — A fixed linear transformer completion with declared voltage transfer T, leakage map B=T*A, excitation placement S, and transformer-internal grounding has terminal admittance Ycomplete=B^H*Ycoil*B+S^T*Y0*S+Yground; the power-dual and component-current recovery maps preserve the declared leakage-path limits, while adjustable transfers must remain parameterized decision factors. | [Fixed-linear transformer factor completion](../transformations/fixed-linear-transformer-factor-completion.md) | `theorem` |
| `TR-XFMR-005` — A continuous or discrete scalar winding tap compiles exactly as a retained parameterized transformer factor when coefficient_xkc(tap)=tap*base_coefficient_xkc and the decision identity and domain are mapped identically; freezing the tap at its start value is generally only an inner restriction, and in the recorded discrete witness it loses the 1.05 optimum and increases the winding-current objective by 671.060 A. | [Parameterized transformer tap decisions](../transformations/parameterized-transformer-tap-decisions.md) | `theorem` |
| `TR-XFMR-006` — A retained finite scalar transformer tap factor embeds exactly into unchanged multiconductor AC voltage, KCL, power-balance, voltage-limit, and recovered leakage-current constraints by pointwise evaluation; in the recorded 11-terminal WYE/WYE/DELTA case, direct source and parameterized target subproblems agree at all three taps, select 0.95 with served fraction 1.2305865, and freezing the 1.00 start loses 0.0601126 served fraction (0.090169 MW). | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `theorem` |
| `TR-XFMR-007` — A separate damped finite-difference Newton, continuation, and bisection implementation reproduces all three TR-XFMR-006 tap-conditioned high-voltage branch boundaries without an external optimizer; its largest served-fraction difference from JuMP/Ipopt is 3.14e-10, and both methods select tap 0.95. | [Transformer tap AC decision case](../cases/transformer-tap-ac-decision.md) | `empirical` |

## Generated artifacts

| Artifact | Evidence summary |
| --- | --- |
| `active-radiality-witness.json` | generated evidence |
| `coordinate-normalization-certificate.json` | `TR-COORD-001` — generated evidence |
| `coordinate-series-composition-certificate.json` | `TR-COMP-001` — generated evidence |
| `degree-two-series-certificate.json` | `TR-SER-001` — generated evidence |
| `five-bus-cycle-space-analysis.json` | `GRAPH-CYCLE-001` — connected loopless scalar series bus-branch multigraph |
| `five-bus-figure-manifest.json` | generated evidence |
| `four-wire-parallel-ac-certificate.json` | `TR-PAR-006` — generated evidence |
| `multiconductor-parallel-ac-certificate.json` | `TR-PAR-004` — generated evidence |
| `multiwinding-leakage-compilation-certificate.json` | `TR-XFMR-002` — generated evidence |
| `multiwinding-terminal-assembly-certificate.json` | `TR-XFMR-003` — generated evidence |
| `nonlinear-kkt-witness.json` | `NUMERICAL-003` — finite-difference nonlinear AC decision Jacobians and symbolic KKT sparsity for a two-bus parallel-member witness |
| `numerical-structure-witness.json` | `NUM-STRUCT-001` — five-bus source topology; structural dependency patterns, not numerical Jacobian entries |
| `parallel-branch-certificate.json` | `TR-PAR-001` — generated evidence |
| `parallel-opf-comparison.json` | `TR-PAR-003` — generated evidence |
| `pi-four-wire-parallel-ac-certificate.json` | `TR-PAR-007` — generated evidence |
| `port-factor-architecture.json` | `ARCH-PORT-001` — data/running-network/v0.1.0.json |
| `positive-sequence-collapse-witness.json` | `COLLAPSE-002` — generated evidence |
| `provenance.json` | generated evidence |
| `summary.json` | generated evidence |
| `transformer-factor-completion-certificate.json` | `TR-XFMR-004` — generated evidence |
| `transformer-tap-ac-decision-certificate.json` | `TR-XFMR-006` — generated evidence |
| `transformer-tap-ac-independent-certificate.json` | `TR-XFMR-007` — generated evidence |
| `transformer-tap-decision-certificate.json` | `TR-XFMR-005` — generated evidence |
| `transformer-winding-normalization-certificate.json` | `TR-XFMR-001` — generated evidence |
| `translation-trap-witnesses.json` | generated evidence |
| `view-source-maps.json` | generated evidence |
| `ybus-jacobian-witness.json` | `NUMERICAL-002` — BMOPFTools passive and constant-Z linearized Ybus for running-network fixture v0.1.0 |

_This file is regenerated during the documentation build._

# Structure-Preserving Graph Models for Power Networks

**Page status:** reader-facing overview and navigation map.

Power-network studies routinely speak of *the network graph*. In fact, several different
structures are being conflated:

1. physical assets and their identities;
2. ordered terminals and conductor connectivity;
3. constitutive relations among terminal variables;
4. operational state, including switch and tap positions;
5. limits, controls, measurements, objectives, and decisions;
6. simplified graphs compiled for particular algorithms.

The book begins with the most general multiconductor case relevant to steady-state power-network
decisions. Buses may have different terminal sets; neutral and ground are explicit; lines may have
full conductor coupling; and transformers may have an arbitrary number of windings. The familiar
balanced transmission graph is treated as an important derived case whose validity follows from
declared symmetry and study assumptions.

The central thesis is:

> A graph transformation for a power network is meaningful only relative to explicit observations,
> constraints, and decisions. Source data should retain typed physical and terminal structure;
> simpler graphs should be derived, traceable views with preservation and recovery contracts.

The book investigates a linked asset/property and hierarchical port--factor architecture as a
candidate common source for these views. It is a proposal to test, not an assumed universal data
model.

## Start with one network

[One network, many graphs](@ref) shows why the same physical system produces different asset,
connectivity, bus--branch, factor, optimization, and sparsity graphs. The
[five-bus multigraph chapter](@ref five-bus-cycle-spaces) then distinguishes a
line-identity cycle basis, simple projection, electrical aggregation, and
spanning-tree coordinates. [A first failure:
heterogeneous parallel branches](@ref first-failure-parallel-branches) then gives the first complete decision-preservation
counterexample. The [Multiconductor parallel AC decision case](@ref multiconductor-parallel-ac-case)
and the further four-wire, nominal-``\pi``, and transformer-tap cases are collected as
solver-backed worked cases after the opening route.
[The running multiconductor network](@ref) specifies the common example used
throughout the book, while the [Executable running network](@ref) provides its versioned BMOPF
realization and six illustrated views plus a checked simple-topology quotient. The
[first positive-sequence collapse](@ref positive-sequence-collapse) then marks the boundary
between the general multiconductor model and a guarded transmission specialization.

The longer solver-backed examples are collected under **Worked decision cases** after this
opening route.

Then read:

1. [Scope and thesis](@ref) for the scientific boundary and decision focus;
2. [Representation taxonomy](@ref representation-taxonomy) for the model families and comparison axes;
3. [Formal representation frameworks](@ref formal-representation-frameworks) for mathematical definitions of the source and derived graph families;
4. [Translation traps: graphs, circuits, and power-system language](@ref translation-traps) for precise replacements for familiar but underspecified phrases;
5. [Orientation, terminal quantities, and power transfer](@ref orientation-terminal-power) for the distinction between topology, reference arrows, terminal signs, operating flow, and loss;
6. [Representation architecture](@ref) for the proposed linked source structures;
7. [Preservation contracts](@ref preservation-contracts) for exact, conservative, relaxed, and approximate maps;
8. [Projection, compilation, and reduction](@ref) for the transformation vocabulary;
9. [Maps between representation frameworks](@ref representation-maps) for morphisms, quotients, compilers, and query-relative expressiveness;
10. [Cycles, parallelism, and radial structure](@ref cycles-parallelism-radiality) for representation-specific cycle spaces, parallel fibres, bridges, leaves, and radiality;
11. [Earth, neutral, and reference model classes](@ref earth-ground-models) for the grounding scope of each reduction;
12. [When the general model collapses](@ref positive-sequence-collapse) for a guarded derivation of the balanced positive-sequence transmission case;
13. [Node--breaker, bus--breaker, and topology processing](@ref node-breaker-topology) for state-conditioned connectivity and switch contraction;
14. [Rating and limit semantics](@ref rating-semantics) for typed quantities, durations, ambient conditions, and preservation obligations;
15. [Data-model crosswalk](@ref data-model-crosswalk) for CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER mappings;
16. [Numerical consequences of representation and reduction](@ref numerical-consequences) for scaling, conditioning, Jacobian structure, fill-in, solver behaviour, and decision margins;
17. [Circuit coordinate transformations](@ref circuit-coordinate-transformations) for phase-to-neutral and phase-to-phase reductions, their grounding and radiality guards, and their recovery maps;
18. [Kron, Ward, and optimized network equivalents](@ref kron-ward-opti-kron) for boundary elimination, external-system realization, and optimized structural selection;
19. [Conductor-coordinate normalization](@ref conductor-coordinate-normalization) for an exact coordinate rewrite;
20. [Transformer-winding coordinate normalization](@ref transformer-winding-normalization) for a delta-safe typed-factor application;
21. [Multiwinding leakage reference compilation](@ref multiwinding-leakage-reference-compilation) for exact pairwise-test compilation;
22. [Multiwinding terminal leakage assembly](@ref multiwinding-terminal-leakage-assembly) for connection-factor composition with recoverable winding limits;
23. [Fixed-linear transformer factor completion](@ref fixed-linear-transformer-factor-completion) for explicit tap/phase operators, excitation, grounding, and the adjustable-control boundary;
24. [Parameterized transformer tap decisions](@ref parameterized-transformer-tap-decisions) for exact continuous/discrete decision retention and the frozen-tap counterexample;
25. [Transformer tap AC decision case](@ref transformer-tap-ac-decision-case) for the first solver-backed network embedding of the retained tap factor;
26. [Degree-two series elimination](@ref degree-two-series-rule) for the first executable guarded reduction;
27. [Certificate schema and composition](@ref certificate-schema-composition) for the shared contract and sequential composition law;
28. [Guarded normalization rules](@ref) for the wider candidate rewrite catalogue.

The [Notation and modelling conventions](@ref) follows the BMOPFTools index discipline:
``\ell ij`` denotes the stored reference orientation and terminal order for
line ``\ell``; it does not assert the operating direction of power. An
element-intrinsic impedance is ``\mathbf Z_\ell``. Multiwinding devices retain device and winding
indices until an explicit compilation creates two-terminal arcs.

## Decision focus

The target is stronger than reproducing voltages. A transformation may also need to preserve or
correctly map:

- conductor and winding limits;
- continuous controls;
- discrete switching, tap, outage, and investment choices;
- feasibility and active constraints;
- objective values and optimal decisions;
- eliminated quantities and source provenance.

Heterogeneous parallel lines provide the first counterexample: aggregate admittance can preserve
terminal current while changing the OPF feasible set, unless every discarded
constraint is separately proved redundant for the declared model and state.

## Claim types and verification

The claims ledger records two separate dimensions. `claim_type` describes what
kind of statement is being made, while `verification` records how far the
current evidence has been checked. The legacy `status` field remains in the
ledger during this migration for compatibility with older certificate tools.

Claim types are:

- **Definition:** terminology adopted consistently in this book.
- **Theorem:** supported by a derivation or authoritative primary source.
- **Empirical:** supported by a recorded computation, experiment, or numerical witness.
- **Practice:** implemented or standardized practice, not necessarily accompanied by a
  general preservation theorem.
- **Proposal:** a design choice advanced and tested by this book.
- **Open:** an unresolved claim, boundary, or research opportunity.

Verification levels are:

- **Unreviewed:** entered for tracking but not yet independently checked;
- **Self-checked:** checked by the repository's derivation, test, or source audit;
- **Independently implemented:** reproduced by a separate implementation path;
- **Externally reviewed:** checked by a reviewer outside the implementing pass.

The current text is an early research draft. The repository quality-control policy separates
verified claims, proposed definitions, implementation evidence, and unresolved work.

## Publication formats

The same Markdown sources generate:

- this navigable HTML knowledge base;
- a [single-file PDF](GraphModelsForPowerSystems.pdf).

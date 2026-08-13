# Structure-Preserving Graph Models for Power Networks

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
heterogeneous parallel branches](@ref) then gives the first complete decision-preservation
counterexample. The [Multiconductor parallel AC decision case](@ref multiconductor-parallel-ac-case)
then retains complex conductor voltages, coupling, voltage bounds, and AC power balance.
The [non-proportional three-phase four-wire case](@ref four-wire-parallel-ac-case)
then certifies jointly implied member limits without proportional matrices or
balanced-network assumptions.
The [four-wire nominal-pi case](@ref pi-four-wire-parallel-ac-case) extends the
certificate to distinct shunt currents and all eight member-end limits.
[The transformer tap AC decision case](@ref transformer-tap-ac-decision-case) embeds the full
11-terminal WYE/WYE/DELTA factor into voltage, neutral-KCL, power-balance, and recovered-current
constraints while retaining its finite tap choice.
[The running multiconductor network](@ref) specifies the common example used
throughout the book, while the [Executable running network](@ref) provides its versioned BMOPF
realization and six illustrated views plus a checked simple-topology quotient.

Then read:

1. [Scope and thesis](@ref) for the scientific boundary and decision focus;
2. [Representation taxonomy](@ref) for the model families and comparison axes;
3. [Formal representation frameworks](@ref formal-representation-frameworks) for mathematical definitions of the source and derived graph families;
4. [Translation traps: graphs, circuits, and power-system language](@ref translation-traps) for precise replacements for familiar but underspecified phrases;
5. [Orientation, terminal quantities, and power transfer](@ref orientation-terminal-power) for the distinction between topology, reference arrows, terminal signs, operating flow, and loss;
6. [Representation architecture](@ref) for the proposed linked source structures;
7. [Preservation contracts](@ref) for exact, conservative, relaxed, and approximate maps;
8. [Projection, compilation, and reduction](@ref) for the transformation vocabulary;
9. [Maps between representation frameworks](@ref representation-maps) for morphisms, quotients, compilers, and query-relative expressiveness;
10. [Cycles, parallelism, and radial structure](@ref cycles-parallelism-radiality) for representation-specific cycle spaces, parallel fibres, bridges, leaves, and radiality;
11. [Circuit coordinate transformations](@ref circuit-coordinate-transformations) for phase-to-neutral and phase-to-phase reductions, their grounding and radiality guards, and their recovery maps;
12. [Kron, Ward, and optimized network equivalents](@ref kron-ward-opti-kron) for boundary elimination, external-system realization, and optimized structural selection;
13. [Conductor-coordinate normalization](@ref conductor-coordinate-normalization) for an exact coordinate rewrite;
14. [Transformer-winding coordinate normalization](@ref transformer-winding-normalization) for a delta-safe typed-factor application;
15. [Multiwinding leakage reference compilation](@ref multiwinding-leakage-reference-compilation) for exact pairwise-test compilation;
16. [Multiwinding terminal leakage assembly](@ref multiwinding-terminal-leakage-assembly) for connection-factor composition with recoverable winding limits;
17. [Fixed-linear transformer factor completion](@ref fixed-linear-transformer-factor-completion) for explicit tap/phase operators, excitation, grounding, and the adjustable-control boundary;
18. [Parameterized transformer tap decisions](@ref parameterized-transformer-tap-decisions) for exact continuous/discrete decision retention and the frozen-tap counterexample;
19. [Transformer tap AC decision case](@ref transformer-tap-ac-decision-case) for the first solver-backed network embedding of the retained tap factor;
20. [Degree-two series elimination](@ref degree-two-series-rule) for the first executable guarded reduction;
21. [Certificate schema and composition](@ref certificate-schema-composition) for the shared contract and sequential composition law;
22. [Guarded normalization rules](@ref) for the wider candidate rewrite catalogue.

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

## Status labels

The text uses five epistemic labels:

- **Definition:** terminology adopted consistently in this book.
- **Established result:** supported by a proof or authoritative primary source.
- **Engineering practice:** implemented or standardized practice, not necessarily accompanied by a
  general preservation theorem.
- **Proposal:** a design choice advanced and tested by this book.
- **Open question:** an unresolved claim, boundary, or research opportunity.

The current text is an early research draft. The repository quality-control policy separates
verified claims, proposed definitions, implementation evidence, and unresolved work.

## Publication formats

The same Markdown sources generate:

- this navigable HTML knowledge base;
- a [single-file PDF](GraphModelsForPowerSystems.pdf).

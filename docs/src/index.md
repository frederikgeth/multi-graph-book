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
connectivity, bus--branch, factor, optimization, and sparsity graphs. [A first failure:
heterogeneous parallel branches](@ref) then gives the first complete decision-preservation
counterexample. [The running multiconductor network](@ref) specifies the common example used
throughout the book, while the [Executable running network](@ref) provides its versioned BMOPF
realization and six generated views.

Then read:

1. [Scope and thesis](@ref) for the scientific boundary and decision focus;
2. [Representation taxonomy](@ref) for the model families and comparison axes;
3. [Representation architecture](@ref) for the proposed linked source structures;
4. [Preservation contracts](@ref) for exact, conservative, relaxed, and approximate maps;
5. [Projection, compilation, and reduction](@ref) for the transformation vocabulary;
6. [Conductor-coordinate normalization](@ref conductor-coordinate-normalization) for an exact coordinate rewrite;
7. [Degree-two series elimination](@ref degree-two-series-rule) for the first executable guarded reduction;
8. [Certificate schema and composition](@ref certificate-schema-composition) for the shared contract and sequential composition law;
9. [Guarded normalization rules](@ref) for the wider candidate rewrite catalogue.

The [Notation and modelling conventions](@ref) follows the BMOPFTools index discipline:
``\ell ij`` denotes line ``\ell`` oriented from bus ``i`` to bus ``j``, while an
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
terminal current while changing the OPF feasible set.

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

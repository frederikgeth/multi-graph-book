# [Notation and modelling conventions](@id reference-notation-conventions)

**Page status:** maintained modelling convention; not a standalone empirical claim.

This page fixes the index discipline and physical conventions used throughout the book. The
starting point is the notation of the BMOPFTools model specification, generalized only where the
book must discuss representations that BMOPFTools does not directly implement.

## Symbols describe semantic ownership

An index appears on a quantity when it identifies the object or oriented attachment that owns that
quantity. Indices are not added merely because an equation is evaluated at an endpoint.

| Symbol | Represents | Typical index |
| --- | --- | --- |
| ``\mathcal B`` | buses or connectivity objects | ``i,j`` |
| ``\mathcal L`` | lines | ``\ell`` |
| ``\mathcal X`` | transformers | ``x`` |
| ``\mathcal W`` | switches | ``w`` |
| ``\mathcal D`` | demands | ``d`` |
| ``\mathcal G`` | generators | ``g`` |
| ``\mathcal H`` | shunts and grounding impedances | ``h`` |
| ``\mathcal F`` | edge ends or flags in the normative multigraph object | ``f`` |
| ``\mathcal P`` | phases | ``p,q`` |
| ``\mathcal N`` | terminal names | ``p,q`` |
| ``\mathbf A`` | oriented incidence matrix | declared bus/edge coordinates |
| ``\mathbf A_\ell`` | full two-end primitive of element ``\ell`` | nominal-``\pi`` terminal-current map |
| ``A_r,A_c`` | retained and candidate current row maps | redundancy certificates |
| ``\mathbf A_\phi,\mathbf A_x`` | factor-incidence maps | conductor/factor assembly |
| ``\mathbf F`` | Fortescue phase-to-sequence transform | ``abc\leftrightarrow012`` |
| ``C_+`` | restriction to the positive-sequence subspace | phase state ``\to`` positive sequence |
| ``E_+`` | embedding of a positive-sequence state | positive sequence ``\to`` phase state |
| ``\sigma`` | declared equipment/topology state; use ``\sigma_e`` for an element state and ``G^\sigma`` for its resolved graph | active/open/closed state, not a nominal-``\pi`` subscript |
| ``\pi`` | projection or quotient map when decorated (for example ``\pi_\sigma``); nominal-``\pi`` is a model-family label | ``\pi_\sigma`` for connectivity quotient; ``\pi`` section for a circuit model |
| ``\alpha`` | scalar decision or model coefficient; qualify the role, such as served-load ``\alpha`` or ZIP ``\alpha_Z`` | ``\alpha`` in an optimization case; ``\alpha_Z,\alpha_I,\alpha_P`` in a load law |
| ``\Lambda`` | asset-to-electrical relation, generally many-to-many rather than a function | ``(a,e)\in\Lambda`` |
| ``\rho`` | a declared realification map, sequence-mixing residual, or fitted proportionality scalar; qualify each use | ``\rho(z)``, ``\rho_+`` or ``\rho^\star`` |
| ``\kappa`` | enumeration map when subscripted by a semantic set, or a condition-number diagnostic | ``\kappa_{\mathcal B}`` versus ``\kappa(\mathbf A)`` |
| ``\Theta`` | admissible family of typed factors or parameters; ``\Theta_\phi`` denotes a factor family | model-class or factor-parameter set |
| ``\eta`` | backward-error, residual, or scenario-validity diagnostic; qualify the source | ``\eta(\widehat x)`` or ``\eta_{\mathrm{asm}}`` |

Identifiers need not be consecutive integers. A data model may use stable strings while the
mathematical model uses the corresponding symbols. When an implementation needs an ordinary
array, introduce an explicit enumeration map, such as

```math
\kappa_{\mathcal B}:\mathcal B\overset{\sim}{\longrightarrow}\{1,\ldots,|\mathcal B|\}.
```

The semantic object is the label-indexed family ``(Y_{ij})_{i,j\in\mathcal B}``; the stored
array is ``[Y]_{\kappa_{\mathcal B}(i),\kappa_{\mathcal B}(j)}``. This book names the semantic
indices before displaying their integer coordinate realization. Integer positions are not
asset identities, and changing the enumeration must not change a claim about the network.

For multiconductor models, bold ``\mathbf Y^{\mathrm N}_{ij}`` denotes a block map between
terminal spaces. It becomes a scalar matrix entry only after the terminal coordinates and bus
enumeration have both been declared. By contrast, ``\mathbf Y_\ell`` is intrinsic data owned by
element ``\ell`` and does not acquire endpoint indices merely because it appears in a nodal
assembly.

## Graph objects and graph-derived counts

The normative finite undirected multigraph is

```math
G=(V,E,\mathcal F,s,p),
```

with two flags in each edge fibre ``p^{-1}(e)``. The complete definition,
including graph loops and matrix conventions, is maintained in [Multigraphs
for expert modelers](@ref multigraphs-for-modelers). Power-system chapters may
specialize ``V`` to buses ``\mathcal B`` and ``E`` to identified lines
``\mathcal L``, but they must not infer that specialization from an
unqualified word such as *network* or *graph*.

For the loopless bus--branch specialization, ``\partial(\ell)`` denotes the
derived unordered endpoint pair and

```math
q:\mathcal L\rightarrow E_{\mathrm s}
```

denotes the simple endpoint projection. The symbol ``q`` is reserved for this
parallel-class quotient in graph-theoretic passages; ``\pi_\sigma`` remains the
state-conditioned connectivity-node quotient used in topology processing.

The following names are not interchangeable:

- ``d_{\mathrm{inc}}`` is incidence degree and counts the two flags of a graph
  loop twice;
- ``d_{\mathrm{nbr}}`` is distinct-neighbour degree in a loopless simple
  projection;
- incident-member count is an engineering count on identified equipment and
  equals ``d_{\mathrm{inc}}`` only in the declared loopless specialization;
- terminal count belongs to a port model; and
- row or block nonzero count belongs to a compiled matrix-support graph.

Likewise, ``B`` denotes a generic signed graph-incidence matrix in the expert
reference chapter, while ``\mathbf A`` remains the preferred power-system
incidence symbol in the engineering chapters. Both use ``-1`` at the selected
tail and ``+1`` at the head unless a reproduced source declares another
convention.

## Oriented element triples

A two-terminal branch is identified independently of its orientation. Its
physical incidence is the unordered endpoint pair ``\partial\ell=\{i,j\}``.
For a line ``\ell`` whose stored reference orientation is from bus ``i`` to
bus ``j``, write

```math
\ell ij \in \mathcal T^{L\rightarrow}
\subseteq \mathcal L\times\mathcal B\times\mathcal B.
```

The opposite terminal arc and the bidirected terminal-arc set are

```math
\mathcal T^{L\leftarrow}
=\{\,\ell ji\mid \ell ij\in\mathcal T^{L\rightarrow}\,\},
\qquad
\mathcal T^L=\mathcal T^{L\rightarrow}\cup\mathcal T^{L\leftarrow}.
```

The triple retains the identity of parallel branches. The arrow is a coordinate
and terminal-order convention; it does not assert the operating direction of
current or active power. Transformer and switch topology sets
``\mathcal T^X`` and ``\mathcal T^W`` use the same pattern when the device is genuinely
two-terminal.

Quantities belonging to an oriented terminal or arc use the triple index:

```math
\mathbf I_{\ell ij},
\qquad
\mathbf S_{\ell ij},
\qquad
\mathbf Y^{\mathrm{sh}}_{\ell ij}.
```

The two terminal quantities need not be negatives: terminal currents can
include local shunts, and the two shunt half-sections may be asymmetric. A
stored-orientation reversal swaps endpoint records; only a declared internal
series-current coordinate has the simple antisymmetry relation. The full
distinction is developed in
[Orientation, terminal quantities, and power transfer](@ref orientation-terminal-power).

## Element-intrinsic quantities

A physical parameter that does not change when the branch orientation is reversed carries only the
element index. For a multiconductor line,

```math
\mathbf Z^{\mathrm s}_\ell
=\mathbf R_\ell+\mathrm j\mathbf X_\ell
```

is the series impedance of line ``\ell``. It is not written
``\mathbf Z_{\ell ij}`` unless the model actually assigns different directional constitutive data.
Likewise, length is ``L_\ell`` and an element-level construction or provenance record belongs to
``\ell``.

This distinction is central to the book:

- ``\ell`` identifies the physical or model element;
- ``\ell ij`` identifies one oriented attachment of that element;
- ``\ell ji`` identifies the opposite attachment;
- terminal maps determine how the element's ordered conductor coordinates meet the endpoint buses.

## Bus terminals and terminal maps

Each bus ``i`` declares an ordered terminal vector

```math
\mathbf N_i=[N_{i,1},\ldots,N_{i,n_i}],
```

for example ``[a,b,c,n]``. Its complex terminal-to-ground voltages form

```math
\mathbf U_i\in\mathbb C^{n_i}.
```

An element does not assume that two buses have identical terminal order or even identical terminal
sets. The ordered terminal maps ``\mathbf N_{\ell i}`` and ``\mathbf N_{\ell j}`` select the bus
terminals to which the ordered conductors of line ``\ell`` attach. Conductor permutations and phase
discontinuities are therefore explicit mappings, not hidden matrix conventions.

For the declared forward orientation, a nominal series relation has the form

```math
\mathbf U_j[\mathbf N_{\ell j}]
=\mathbf U_i[\mathbf N_{\ell i}]
-\mathbf Z^{\mathrm s}_\ell\mathbf I^{\mathrm s}_{\ell ij}.
```

The matrix ``\mathbf Z^{\mathrm s}_\ell`` is full unless a more restrictive model is declared.

## Current and power signs

Terminal currents are defined relative to the terminal at which they enter an element. In the bus
balance, the corresponding contribution is given the sign required by the declared KCL convention.
Every chapter must state that convention before using an unqualified current direction.

For this book, the preferred physical statements use complex terminal vectors. Rectangular real
and imaginary parts are an implementation realization. Per-conductor complex power at an oriented
terminal is

```math
\mathbf S_{\ell ij}
=\mathbf U_i[\mathbf N_{\ell i}]
\circ \mathbf I_{\ell ij}^{*},
```

where ``\circ`` is the Hadamard product and ``(\cdot)^*`` is element-wise conjugation.

The pair ``(\mathbf S_{\ell ij},\mathbf S_{\ell ji})`` consists of terminal
complex-power injections into the element. It is not generally one conserved
edge flow: a series impedance absorbs power even when its end currents are
opposite, and internal nominal-``\pi`` shunts also make the terminal currents
non-antisymmetric. An unqualified phrase such as *power from ``i`` to ``j``*
must therefore identify both the terminal sign convention and the operating
quantity being reported.

## Multi-terminal and multiwinding devices

A genuinely multi-terminal device is not assigned an artificial pair of endpoint buses. A
transformer ``x`` has an ordered winding or port set ``\mathcal K_x``. Its attachment map is

```math
\beta_x:\mathcal K_x\rightarrow\mathcal B,
\qquad
\beta_x(k)=i,
```

and winding ``k`` has its own terminal map ``\mathbf N_{xk}``, connection, reference voltage,
current variables, limits, and provenance. Pairwise short-circuit data may be indexed by winding
pairs, while a reconstructed winding-star or primitive admittance remains owned by ``x``.

Only an explicit compilation may replace ``x`` by two-terminal elements and virtual internal buses.
The generated arcs then receive their own identities and triples, together with a map back to
``(x,k)`` and to any generated internal object.

In this book, *winding* counts a transformer port or voltage-level connection unless a passage
explicitly refers to physical coils.

## Nodal attachments

A nodal element uses an element--bus pair, such as

```math
di\in\mathcal C^D,
\qquad
gi\in\mathcal C^G,
\qquad
hi\in\mathcal C^H.
```

Its ordered terminal or connection map is recorded separately. A load attached at bus ``i`` is not
therefore assumed to be three-phase, wye-connected, or phase-to-neutral.

## Compound nodal operator

The scalar-to-matrix transition is a change in coordinate space, not a change
of graph vocabulary. A scalar branch law uses ``i_{\ell ij}=y_\ell(v_i-v_j)``;
the multiconductor analogue uses ordered vectors and a matrix primitive. The
translation bridge and its diagram-reading checklist are given in [How to read
power-network diagrams and equations](@ref how-to-read-diagrams-and-equations).

The assembled linear current--voltage operator on a declared ordered set of
retained junction coordinates is

```math
\mathbf I=\mathbf Y^{\mathrm N}\mathbf U.
```

The superscript ``\mathrm N`` means *nodal* and does not imply a scalar,
positive-sequence, or simple-graph model. Conventional ``\mathbf
Y_{\mathrm{bus}}`` and `Ybus` are retained as aliases when reproducing software
interfaces or established scalar bus-matrix language, but every use must state
the coordinate order and model class. A reduced image is distinguished as
``\widehat{\mathbf Y}`` or ``\mathbf Y_{\mathrm K}``; it is not silently
overwritten onto the source operator.

## Ground, neutral, and reference

The following are distinct:

- a voltage reference used to remove gauge freedom;
- the physical earth or an earth-return model;
- a neutral conductor;
- a perfectly grounded terminal;
- a grounding impedance or admittance;
- the elimination of a neutral variable by a declared reduction.

No chapter may use *ground* as an unqualified synonym for all of them. Perfectly grounded terminals
have fixed voltage. Impedance grounding is an explicit shunt or factor. A neutral conductor remains
a network conductor unless an admissible transformation eliminates it.

## Parameters, variables, and sets

The mathematical prose distinguishes:

- ordinary italic lower-case symbols for scalars;
- bold symbols for vectors and matrices;
- calligraphic symbols for sets;
- roman subscripts or superscripts for descriptive roles such as ``\mathrm{sh}`` or
  ``\mathrm{ref}``;
- a superscript ``*`` for complex conjugation and ``\mathrm H`` for conjugate transpose.

The HTML may use colour to distinguish real and complex quantities or parameters and variables,
following BMOPFTools. No definition may depend on colour: typography, prose, and context must remain
complete in monochrome PDF output.

The same rule applies to generated figures. Titles, labels, line styles, panel
placement, and captions carry the interpretation; colour only provides a
secondary visual cue. In matrix-pattern figures, filled cells mean nonzeros
and the panel title identifies the matrix or formulation. In the running
network multiview, ``x_1^*`` is labelled as a compiled star so its orange
styling is not the sole indication of compilation.

## Units and coordinate systems

Foundational physical equations use SI units. A per-unit system, sequence transform, conductor
permutation, or real rectangular realization is a declared coordinate transformation. Its bases,
ordering, orientation, and inverse or recovery map belong in the transformation record.

Equality of raw arrays is not evidence of physical equality when their terminal order, units,
reference direction, or base differ.

## Decision notation

A model ``M`` defines both equations and an admissible set ``\mathcal F_M``. A decision problem is
written abstractly as

```math
\min_{z\in\mathcal F_M}\; f_M(z),
```

where ``z`` may include network states, continuous controls, and discrete decisions. A
transformation is not decision preserving merely because it reproduces selected voltages. Its
contract must state the relationship between source and target feasible sets, objectives, active
constraints, and optimal decisions.

## Local deviations

A chapter may introduce specialized notation when that notation makes a derivation substantially
clearer. It must provide a local symbol table and an explicit map to this contract. Silent changes
of current direction, terminal order, impedance base, or winding meaning are not permitted.

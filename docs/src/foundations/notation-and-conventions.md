# Notation and modelling conventions

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
| ``\mathcal P`` | phases | ``p,q`` |
| ``\mathcal N`` | terminal names | ``p,q`` |

Identifiers need not be consecutive integers. A data model may use stable strings while the
mathematical model uses the corresponding symbols.

## Oriented element triples

A two-terminal branch is identified independently of its orientation. For a line ``\ell`` whose
declared forward direction is from bus ``i`` to bus ``j``, write

```math
\ell ij \in \mathcal T^{L\rightarrow}
\subseteq \mathcal L\times\mathcal B\times\mathcal B.
```

The reverse orientation and the bidirectional topology set are

```math
\mathcal T^{L\leftarrow}
=\{\,\ell ji\mid \ell ij\in\mathcal T^{L\rightarrow}\,\},
\qquad
\mathcal T^L=\mathcal T^{L\rightarrow}\cup\mathcal T^{L\leftarrow}.
```

The triple retains the identity of parallel branches. Transformer and switch topology sets
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

The forward and reverse quantities need not be equal: terminal currents include local shunts, and
the two shunt half-sections may be asymmetric.

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


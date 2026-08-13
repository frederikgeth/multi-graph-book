# [Fixed-linear transformer factor completion](@id fixed-linear-transformer-factor-completion)

The leakage factor is only one part of a transformer model. A linear phasor
model may also contain fixed ideal voltage transfers, a no-load excitation
branch, and transformer-internal neutral grounding. These components can be
assembled exactly, but only after their placement, coordinates, and control
status have been declared.

This chapter completes the fixed-linear factor. Here *complete* means complete
for the declared linear steady-state components. Saturation, frequency
dependence, thermal state, protection, and adjustable controls are not thereby
eliminated or approximated.

## Serialization contract

For transformer ``x``, winding ``k`` at bus ``i`` retains:

- its stable winding identity and position ``k``;
- ordered terminal labels ``\mathbf N_{xk}`` and labelled coil coordinates
  ``\mathcal C_{xk}``;
- the connection incidence ``\mathbf A_{xk}``;
- the source impedance-test reference and selected leakage-compilation
  reference;
- a declared voltage-transfer mode, coefficient convention, and decision
  identity when adjustable;
- the placement and coordinates of every excitation or grounding factor.

The executable JSON contract uses the versioned convention

```math
V^{\mathrm{leak}}_{xkc}
=a_{xkc}V^{\mathrm{coil}}_{xkc},
\qquad c\in\mathcal C_{xk}.
```

Thus ``a_{xkc}`` is not an unqualified `tap` field whose direction must be
guessed. An adapter may map a package's tap convention into ``a_{xkc}``, but it
must record that map. The running contract is stored separately from the
canonical BMOPFTools fixture because its excitation and grounding values are
illustrative, not nameplate data.

## Power-dual voltage transfer

Let ``\mathbf A_x`` be the aligned block connection matrix from `TR-XFMR-003`
and let

```math
\mathbf T_x
=\operatorname{blkdiag}
\left(
\operatorname{diag}(\mathbf a_{x1}),\ldots,
\operatorname{diag}(\mathbf a_{xn_x})
\right).
```

The connected-coil and leakage-coordinate voltages are

```math
\mathbf V_x^{\mathrm{coil}}=\mathbf A_x\mathbf U_x,
\qquad
\mathbf V_x^{\mathrm{leak}}
=\mathbf T_x\mathbf A_x\mathbf U_x.
```

A voltage map does not determine the same current map. Complex-power
preservation requires the conjugate-transpose dual:

```math
\mathbf I_x^{\mathrm{w,leak}}
=\mathbf T_x^{\mathrm H}\mathbf I_x^{\mathrm{leak}}.
```

Indeed,

```math
(\mathbf V_x^{\mathrm{coil}})^{\mathrm H}
 \mathbf I_x^{\mathrm{w,leak}}
=(\mathbf T_x\mathbf V_x^{\mathrm{coil}})^{\mathrm H}
 \mathbf I_x^{\mathrm{leak}}.
```

This distinction is invisible for a real unit coefficient. It is essential for
an off-nominal magnitude or an explicitly declared phase-shifting transfer.
Connection-induced vector-group displacement should remain in the real winding
incidences—such as the declared delta roll—rather than being duplicated in
``\mathbf T_x``.

With ``\mathbf Y_x^{\mathrm{coil}}`` from the leakage assembly, define

```math
\begin{aligned}
\mathbf B_x&=\mathbf T_x\mathbf A_x,\\
\mathbf I_x^{\mathrm{leak}}
&=\mathbf Y_x^{\mathrm{coil}}\mathbf B_x\mathbf U_x.
\end{aligned}
```

The leakage contribution at transformer terminals is therefore

```math
\mathbf Y_x^{\mathrm{series}}
=\mathbf B_x^{\mathrm H}
 \mathbf Y_x^{\mathrm{coil}}
 \mathbf B_x.
```

A complex phase-shifting transfer need not produce a complex-symmetric nodal
matrix. The correctness condition here is the declared voltage/current dual
and its complex-power identity, not symmetry copied from the real-incidence
special case.

## Excitation and core loss

Let winding ``k_0`` carry the explicitly placed excitation branch. The real
selection-incidence matrix ``\mathbf S_x`` maps terminal voltages to its
aligned coil voltages, and ``\mathbf Y_x^0`` is its labelled coil admittance:

```math
\mathbf V_x^0=\mathbf S_x\mathbf U_x,
\qquad
\mathbf I_x^0=\mathbf Y_x^0\mathbf V_x^0.
```

The implementation accepts a full reciprocal matrix ``\mathbf Y_x^0`` rather
than assuming diagonal phases. Its Hermitian part must be positive
semidefinite within tolerance, so the shunt cannot generate real power. A
diagonal ``G_x^0+\mathrm jB_x^0`` is the common core-loss and magnetising
special case.

Placement is part of the contract. The executable example follows the
BMOPFTools/OpenDSS convention of placing the branch across winding 2's coils,
but the book-level compiler does not infer that placement from an array
position.

## Transformer-internal grounding

For each declared transformer-internal grounding branch ``g``, let ``y_g`` be
its passive terminal-to-earth admittance and ``\mathbf e_g`` select the
qualified terminal ``(x,k,N)``. Then

```math
\mathbf Y_x^{\mathrm{ground}}
=\sum_g y_g\mathbf e_g\mathbf e_g^{\mathsf T}.
```

This factor is distinct from a neutral conductor, a voltage reference, and an
external bus grounding. The compiler rejects an object whose scope is
`external_bus`: absorbing it would change asset ownership and could invalidate
later grounding, protection, or topology decisions.

## Completed fixed-linear factor

The terminal current is the sum of the three retained contributions,

```math
\mathbf I_x
=\mathbf B_x^{\mathrm H}\mathbf I_x^{\mathrm{leak}}
 +\mathbf S_x^{\mathsf T}\mathbf I_x^0
 +\mathbf Y_x^{\mathrm{ground}}\mathbf U_x,
```

and hence

```math
\boxed{
\mathbf Y_x^{\mathrm{complete}}
=\mathbf B_x^{\mathrm H}\mathbf Y_x^{\mathrm{coil}}\mathbf B_x
 +\mathbf S_x^{\mathsf T}\mathbf Y_x^0\mathbf S_x
 +\mathbf Y_x^{\mathrm{ground}}
}.
```

The target retains maps for leakage-coil current, winding-side leakage current,
excitation current, and internal-ground current. A leakage-path coil limit is
therefore enforced on

```math
\left|
[\mathbf T_x^{\mathrm H}\mathbf Y_x^{\mathrm{coil}}
  \mathbf T_x\mathbf A_x\mathbf U_x]_{xkc}
\right|
\leq \overline i^{\mathrm{leak}}_{xkc}.
```

If a source instead defines a rating on total terminal current or apparent
power, that semantic must be declared separately and applied to the
corresponding recovered sum. The compiler does not silently reinterpret a
leakage-path rating.

## Adjustable taps are a different target

For a tap decision ``t_x`` or discrete position ``d_x``, the relation is

```math
\mathbf V_x^{\mathrm{leak}}
=\mathbf T_x(t_x,d_x)\mathbf A_x\mathbf U_x,
\qquad
\mathbf I_x^{\mathrm{w,leak}}
=\mathbf T_x(t_x,d_x)^{\mathrm H}\mathbf I_x^{\mathrm{leak}}.
```

This is a parameterized factor in the decision model, not one fixed admittance
matrix. Replacing ``t_x`` by its start value changes the feasible set and loses
the tap decision. The static compiler therefore returns the structured guard
`adjustable_winding_transfer_requires_factorized_decision_model` for both
continuous and discrete modes. The serialization still retains the mode and
decision identity so a later optimization compiler can implement the correct
factor.

## Executable evidence

The illustrative completion of the running WYE/WYE/DELTA transformer has 11
external terminals, nine leakage-coil coordinates, a three-coordinate
excitation branch on winding 2, and one internal neutral-ground branch. It
records:

- component-current recovery residual ``9.38\times10^{-14}\ \mathrm A``;
- complex-power residual ``1.13\times10^{-13}\ \mathrm{VA}``; and
- difference ``2.96\times10^{-17}\ \mathrm S`` from the independently
  constructed `BMOPFTools.nwinding_yprim` after removing the separately added
  internal-ground branch, which that implementation does not stamp for the
  n-winding subtype.

The tests also use nonuniform real tap coefficients and a complex fixed phase
transfer, reorder labelled transfer coordinates, and reject active shunts,
missing grounding terminals, external bus grounding, and adjustable controls.
The machine-readable result is certificate `TR-XFMR-004`.

## Model boundary

`TR-XFMR-004` is exact for the declared fixed linear phasor factor. It is not a
claim about saturation, harmonics, frequency-dependent core behavior, thermal
state, inrush, protection, mechanical tap dynamics, or uncertainty. Those are
additional factors and states. [Parameterized transformer tap decisions](@ref
parameterized-transformer-tap-decisions) provides the continuous/discrete
continuation that preserves feasible sets and decision identities rather than
evaluating one fixed snapshot.

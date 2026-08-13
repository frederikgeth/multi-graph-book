# [Non-proportional three-phase four-wire parallel case](@id four-wire-parallel-ac-case)

**Page status:** guarded AC decision case with self-checked and independently
reproduced numerical evidence; broader global claims remain open.

This case reuses the canonical member-versus-aggregate distinction from
[the first scalar counterexample](@ref first-failure-parallel-branches); its
new content is the non-proportional four-wire current map and joint quadratic
containment certificate.

The preceding phase--neutral example deliberately used proportional member
matrices. This case removes that simplification while retaining the book's
general baseline: ordered ``(a,b,c,n)`` conductors, full mutual coupling, an
explicit neutral return, unbalanced constant-power loading, individual member
limits, and a decision objective.

## Reciprocal non-proportional members

Two series-only members ``\ell_1ij`` and ``\ell_2ij`` share buses ``i`` and
``j``. Their full impedance matrices are complex symmetric and have positive
resistive and reactive diagonals. The second matrix is not a scalar multiple
of the first: after fitting the best complex scalar ``\rho``, the infinity-norm
residual is

```math
\|\mathbf Y_{\ell_2}-\rho\mathbf Y_{\ell_1}\|_\infty=0.3663.
```

Both members follow

```math
\mathbf I_{\ell i j}=\mathbf Y_\ell(\mathbf U_i-\mathbf U_j),
```

with component limits ``|I_{\ell i j,c}|\le0.72`` p.u. at both ends. A balanced
four-wire slack supplies an unbalanced wye load with phase directions

```math
(s_a,s_b,s_c)=
(0.70+0.14\mathrm j,\ 0.55+0.12\mathrm j,\ 0.42+0.09\mathrm j),
```

all multiplied by the served-load decision ``\alpha``. Each phase-to-neutral
voltage magnitude lies in ``[0.88,1.05]`` p.u.; neutral KCL is explicit.

## Joint componentwise redundancy certificate

Because ``\mathbf Y_{\ell_1}`` is nonsingular, the common voltage drop can be
eliminated between the member laws:

```math
\mathbf I_{\ell_2 i j}=\mathbf K\mathbf I_{\ell_1 i j},\qquad
\mathbf K=\mathbf Y_{\ell_2}\mathbf Y_{\ell_1}^{-1}.
```

For retained component discs
``|I_{\ell_1 i j,k}|\le I^{\max}_{\ell_1,k}``, the exact worst-case magnitude
of candidate component ``c`` is

```math
\max |I_{\ell_2 i j,c}|=
\sum_k |K_{ck}|I^{\max}_{\ell_1,k}.
```

The equality is constructive: the independent complex currents can choose
phases that align every term in row ``c``. Nonsingularity ensures that every
retained current vector corresponds to a voltage drop. Thus the row-norm test
is necessary and sufficient for each candidate component to be implied
jointly by all retained component limits.

For ``(a,b,c,n)``, the certified worst cases are respectively
``(0.1773,0.1710,0.1647,0.1636)`` p.u., all well below ``0.72`` p.u. Since a
series-only reverse-end current changes only sign, the same proof covers
``\ell ji``. The target can remove all four ``\ell_2`` component constraints
while retaining its line law, identity, recovered currents, and possible use
by other observations.

This extends the one-constraint PSD result in `TR-PAR-005`. It does not yet
cover singular retained maps, shunt currents, limits implied jointly by several
different retained members, or topology- and decision-dependent parameters.
The [four-wire nominal-pi case](@ref pi-four-wire-parallel-ac-case) next adds
distinct from/to shunt currents and certifies the full stacked terminal map.

## Decision results

| Formulation | Served fraction | Phase-``a`` voltage | Largest ``\ell_1`` loading | Largest ``\ell_2`` loading | Variables / constraints |
|:--|--:|--:|--:|--:|--:|
| source | 1.1274329 | 0.9394441 | 1.0000000 | 0.1898951 | 9 / 23 |
| exact lifted | 1.1274329 | 0.9394441 | 1.0000000 | 0.1898951 | 9 / 23 |
| exact pruned | 1.1274329 | 0.9394441 | 1.0000000 | 0.1898951 | 9 / 19 |
| naive summed-limit aggregate | 1.8058181 | 0.8952127 | 1.6807715 | 0.3192597 | 9 / 19 |

The exact-pruned target removes four constraints and agrees with the source to
``1.7\times10^{-14}`` in objective value. The naive target has the same model
size but serves 60% more of the load direction by violating the binding
``\ell_1`` phase-``a`` constraint. Again, size does not determine fidelity.

The unbalanced solution has neutral voltage ``0.02796`` p.u.; this is not a
balanced transmission case with a cosmetic fourth coordinate. All four
conductors participate in the coupled member recovery and redundancy proof.

## Independent checks

Three checks use different seams:

1. JuMP and Ipopt solve the source, lifted, pruned, and naive nonlinear models.
2. A LinearAlgebra-only finite-difference Newton continuation and bisection
   reproduces the source boundary at ``1.1274329171``, within
   ``1.4\times10^{-8}`` of Ipopt, with power-flow residual below
   ``5\times10^{-16}``.
3. BMOPFTools' public `line_yprim` reconstructs each ordered four-wire primitive
   from the stored impedance entries and matches the direct admittance blocks
   to ``10^{-12}``.

Together these establish claim `TR-PAR-006`; they do not constitute a global
optimality proof for an arbitrary nonconvex AC OPF.

Run:

```sh
julia --project=experiments experiments/run_four_wire_parallel_ac.jl
julia --project=experiments experiments/test/four_wire_parallel_ac.jl
```

The generated certificate is
`experiments/generated/four-wire-parallel-ac-certificate.json`.

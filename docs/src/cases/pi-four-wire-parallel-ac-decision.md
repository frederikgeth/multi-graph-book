# [Four-wire nominal-pi parallel case](@id pi-four-wire-parallel-ac-case)

The series-only four-wire case uses the same current magnitude at opposite
member ends. A nominal-``\pi`` line removes that shortcut: shunt current depends
on the local terminal voltage, and ``\mathbf I_{\ell i j}`` is generally not
``-\mathbf I_{\ell j i}``. Redundancy must therefore be certified on the full
two-end primitive, as in the scalar setting of [Molzahn2018](@cite).

## Full terminal-current map

For series admittance ``\mathbf Y_\ell`` and end shunts
``\mathbf Y^{\mathrm{sh}}_{\ell,i}`` and
``\mathbf Y^{\mathrm{sh}}_{\ell,j}``, define

```math
\begin{bmatrix}
\mathbf I_{\ell i j}\\
\mathbf I_{\ell j i}
\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
\mathbf Y_\ell+\mathbf Y^{\mathrm{sh}}_{\ell,i}&-\mathbf Y_\ell\\
-\mathbf Y_\ell&\mathbf Y_\ell+\mathbf Y^{\mathrm{sh}}_{\ell,j}
\end{bmatrix}}_{\mathbf A_\ell}
\begin{bmatrix}
\mathbf U_i\\
\mathbf U_j
\end{bmatrix}.
```

The experiment adds unequal diagonal charging blocks at the two ends of both
reciprocal, non-proportional ``(a,b,c,n)`` members from `TR-PAR-006`. The
retained primitive ``\mathbf A_{\ell_1}`` is nonsingular, with condition number
``2922.9``. Hence

```math
\begin{bmatrix}
\mathbf I_{\ell_2 i j}\\
\mathbf I_{\ell_2 j i}
\end{bmatrix}
=\mathbf A_{\ell_2}\mathbf A_{\ell_1}^{-1}
\begin{bmatrix}
\mathbf I_{\ell_1 i j}\\
\mathbf I_{\ell_1 j i}
\end{bmatrix}.
```

Applying the complex-polydisc row norm to this eight-dimensional recovery map
gives an exact worst-case candidate magnitude no larger than ``0.17793`` p.u.
for any of the eight ``ij`` or ``ji`` components, below the ``0.72`` p.u.
rating. All member-2 terminal limits are therefore jointly implied by the full
set of member-1 terminal limits.

The invertibility guard matters. The series-only full primitive is singular
because a common endpoint-voltage shift produces no series current; that case
uses the reduced voltage-drop coordinate of `TR-PAR-006`. Nominal-``\pi``
shunts make absolute terminal voltage observable, so silently applying the
series recovery would omit charging current.

## AC decision comparison

The load directions, explicit neutral KCL, phase-to-neutral voltage bounds,
and served-load objective are retained from the preceding four-wire case.
Receiving-bus power uses the negative ``ji`` terminal current, including the
receiving-end shunt.

| Formulation | Served fraction | Phase-``a`` voltage | Largest ``\ell_1`` loading | Largest ``\ell_2`` loading | Variables / constraints |
|:--|--:|--:|--:|--:|--:|
| source | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 31 |
| exact lifted | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 31 |
| exact pruned | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 23 |
| naive summed-limit aggregate | 1.8077114 | 0.8961512 | 1.6807809 | 0.3192479 | 9 / 23 |

The exact-pruned target deletes eight constraints and agrees with the source to
``1.2\times10^{-13}`` in objective value. The same-size naive formulation
serves substantially more load by violating the binding member-1 limit.

## Independent checks and scope

BMOPFTools' `line_yprim` reconstructs both complete nominal-``\pi`` primitives
from their series and from/to shunt entries and matches the direct matrices to
``10^{-12}``. A separate finite-difference Newton continuation and bisection
reproduces the source boundary at ``1.1286205634``, within
``1.4\times10^{-8}`` of Ipopt, with residual below ``4\times10^{-15}``.

This establishes claim `TR-PAR-007` for fixed nominal-``\pi`` members whose
retained full primitive is nonsingular. It does not cover singular shunted
maps, voltage-dependent shunts, tap or switching states, or implication by
constraints distributed across several retained members.

Run:

```sh
julia --project=experiments experiments/run_pi_four_wire_parallel_ac.jl
julia --project=experiments experiments/test/pi_four_wire_parallel_ac.jl
```

The generated certificate is
`experiments/generated/pi-four-wire-parallel-ac-certificate.json`.

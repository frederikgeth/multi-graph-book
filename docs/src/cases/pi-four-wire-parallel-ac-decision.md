# [Four-wire nominal-pi parallel case](@id pi-four-wire-parallel-ac-case)

**Page status:** guarded nominal-``\pi`` decision case with executable
certificates; singular shunted refusal and state/voltage-dependent
recomputation are explicit, while global extensions remain open.

This is the nominal-``\pi`` extension of the canonical parallel-member failure
in [the first scalar counterexample](@ref first-failure-parallel-branches).
Only the additional shunt-current observations and both-end limit contract are
new here.

The shared certificate geometry and decision-gap plate are introduced in the
[multiconductor parallel case](@ref multiconductor-parallel-ac-case); the
nominal-``\pi`` chapter then adds the full two-end primitive and its refusal
and recomputation guards.

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

The certificate records the retained-map condition number, a normalized
backward error for the recovery solve, and a relative margin for every deleted
limit. It rejects a map that is too ill-conditioned or a limit whose margin is
numerically ambiguous. The result is exact for the nominal matrices and
centered complex discs; uncertainty in those matrices requires a separate
robustness analysis.

For reproducibility, the implementation rejects a retained map when its
2-norm condition number exceeds ``\kappa_{\max}=10^8``; it also rejects a
candidate row when its relative margin is below
``\varepsilon_{\mathrm{margin}}=10^{-8}``. These are numerical certification
guards, not physical operating limits. The present fixture has
``\kappa_2(\mathbf A_{\ell_1})=2922.9``, comfortably inside the declared
conditioning bound.

### Guarded extensions: singular, jointly retained, and state-dependent

The companion witness
`experiments/generated/guarded-parallel-reduction-witness.json` makes three
boundaries executable:

| Situation | Witnessed treatment | Classification |
| --- | --- | --- |
| series-only full terminal map | reject the singular full ``[\mathbf I_{ij};\mathbf I_{ji}]`` recovery map, then use the endpoint-voltage-drop coordinate | guarded exact reduction in the reduced coordinate |
| candidate constrained by several retained members | sum the exact support contributions ``\sum_k\lvert K_{ck}\rvert\bar I_k`` over all retained discs | jointly implied when the declared candidate rating contains the sum |
| state-dependent admittance/control | recompute the recovery map at each declared state; the base map is not reused off-state | decision-conditioned map required |

`TR-PAR-JOINT-001` records the scope of the middle row: the support sum is an
exact linear-disc implication when every retained limit is imposed together.
The generated witness now uses three retained discs. It is not yet a full
nonlinear AC result for several retained members.

#### Jointly retained constraints (`TR-PAR-JOINT-001`, `TR-PAR-AC-JOINT-001`)

A separate three-member AC probe crosses this linear certificate into the
nonlinear network model. It sets ``I_{\ell_3}=0.10I_{\ell_1}+0.10I_{\ell_2}``,
assigns member 3 a ``0.15`` p.u. component limit, and obtains a joint support
bound of ``0.144`` p.u. The source and exact-pruned formulations both solve at
served fraction ``1.2401762`` (gap below ``7\times10^{-14}``). This is claim
`TR-PAR-AC-JOINT-001`: a fixed-map, locally solved AC witness, not a global
nonlinear optimality theorem.

The same certificate includes an independent finite-difference damped-Newton
continuation and bisection check of the source boundary. It brackets the
boundary within ``6.0\times10^{-9}`` served-fraction units, with power-flow
residual below ``1.1\times10^{-15}``; its boundary differs from the Ipopt
source solve by about ``1.3\times10^{-8}``. This is an independent numerical
reproduction of the declared branch, not a proof of global AC optimality.

The same three-member certificate now includes `TR-PAR-STATE-001`, a finite
four-state admittance envelope. At the base, higher-admittance,
lower-admittance, and phase-selective unbalanced states, the member maps, joint
support certificate, and source and exact-pruned AC formulations are rebuilt.
Pruning remains exact in all four local solves, while the optimal served value
changes across states. The state rows also carry independent boundary checks.
This is finite state-dependent evidence, not a global control-policy or
nonlinear optimality guarantee.
The companion `three-member-state-envelope-independent-reproduction.json`
reconstructs all four state boundaries with a separate standard-library
Newton/bisection implementation.

This does not certify a singular shunted primitive or arbitrary AC control
policy. It records the guard and the correct next representation, rather than
treating a pseudoinverse or a frozen nominal map as an exact rewrite.

#### Singular-map refusal (`TR-PAR-SINGULAR-001`)

The generated nominal-``\pi`` certificate now includes singular-map refusal
probes. One constructs a rank-deficient neutral series map with zero endpoint
shunts; a second retains a nonzero from-end neutral shunt while leaving the
to-end neutral shunt absent. Both verify that the full two-end recovery matrix
is singular after realification and that the redundancy evaluator refuses it.
The fallback is an endpoint-voltage or factor-coordinate formulation; this is
a refusal witness, not a pseudoinverse-based reduction.

For the series-only singular fixture, the certificate also demonstrates the
valid reduced-coordinate fallback. Writing ``\Delta\mathbf U=\mathbf U_i-
\mathbf U_j`` gives ``\mathbf I_{\ell_1}=\mathbf Y_{\ell_1}\Delta\mathbf U`` and
``\mathbf I_{\ell_2}=\mathbf Y_{\ell_2}\Delta\mathbf U``; the declared neutral
rows are zero and are retained as an explicit invariant. The reduced recovery
map is therefore exact on the endpoint-voltage-drop coordinate even though the
full two-end terminal map remains rank deficient. This is a scoped series-only
result: it does not use a pseudoinverse and does not extend to singular shunted
maps or a global nonlinear AC theorem.
This scoped executable result is claim `TR-PAR-SINGULAR-001`.

#### State-conditioned maps (`TR-PAR-STATE-001`)

The same certificate includes scoped state-conditioned map probes: changing
the endpoint shunts changes the nominal-π primitive, so the base-state map is
rejected off-state and the shifted map is recomputed. A voltage-dependent
shunt probe makes the stronger point that the map changes with terminal
voltage, not merely with a separately declared state. These records provide
the local guard needed for a control/state-dependent study; they do not
provide a global robust AC bound or an optimizer-independent equivalence
theorem.

The certificate now also solves the two declared shunt states with their own
maps. The served-fraction boundary changes from ``1.1286205497`` in the base
state to ``1.1285736287`` after the shunt shift. Re-running the exact-pruned
formulation at the shifted state agrees with its shifted source formulation to
``4.5\times10^{-14}``. Thus the probe demonstrates a state-conditioned
full-AC decision calculation and exact pruning after recomputation; it does not
justify reusing the base map or claim a global control policy theorem.

The generated evidence now evaluates a finite three-state envelope: the base
state, the shifted state above, and a reverse shunt shift. Each state rebuilds
its nominal-``\pi`` map, rechecks the joint limit certificate, and solves both
the source and exact-pruned AC formulations. All three states are locally
solved, with maximum source/pruned objective gap below ``1.2\times10^{-13}``.
This is finite declared-state evidence, not a bound over a continuous control
or uncertainty set.

The finite envelope is summarized once here; the map and both local nonlinear
solves are rebuilt for every row.

| Declared state | From/to shunt scales | Map certified | Source served fraction | Pruned served fraction | Objective gap |
|:--|:--:|:--:|--:|--:|--:|
| base | 1.00 / 1.00 | yes | 1.1286205497 | 1.1286205497 | ``1.2\times10^{-13}`` |
| shifted_shunt | 1.35 / 0.70 | yes | 1.1285736287 | 1.1285736287 | ``4.5\times10^{-14}`` |
| reverse_shift | 0.75 / 1.25 | yes | 1.1286586199 | 1.1286586199 | ``1.1\times10^{-13}`` |

## AC decision comparison

The load directions, explicit neutral KCL, phase-to-neutral voltage bounds,
and served-load objective are retained from the preceding four-wire case.
Receiving-bus power uses the negative ``ji`` terminal current, including the
receiving-end shunt.

| Formulation | Served fraction | Phase-``a`` voltage | Largest ``\ell_1`` loading | Largest ``\ell_2`` loading (fraction of 0.72 p.u. rating) | Variables / constraints |
|:--|--:|--:|--:|--:|--:|
| source | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 31 |
| exact lifted | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 31 |
| exact pruned | 1.1286205 | 0.9404444 | 1.0000000 | 0.1898792 | 9 / 23 |
| naive summed-limit aggregate | 1.8077114 | 0.8961512 | 1.6807809 | 0.3192479 | 9 / 23 |

The exact-pruned target deletes eight constraints and agrees with the source to
``1.2\times10^{-13}`` in objective value. The same-size naive formulation
serves substantially more load by violating the binding member-1 limit.
The certified worst-case currents are absolute p.u. magnitudes; the loading
columns are current divided by the corresponding 0.72 p.u. rating.

## Independent checks and scope

BMOPFTools' `line_yprim` reconstructs both complete nominal-``\pi`` primitives
from their series and from/to shunt entries and matches the direct matrices to
``10^{-12}``. A separate finite-difference Newton continuation and bisection
reproduces the source boundary at ``1.1286205634``, within
``1.4\times10^{-8}`` of Ipopt, with residual below ``4\times10^{-15}``.

This establishes claim `TR-PAR-007` for fixed nominal-``\pi`` members whose
retained full primitive is nonsingular. The accompanying refusal and
recomputation probes expose, but do not solve, singular shunted maps,
voltage-dependent shunts, tap or switching states, or implication by
constraints distributed across several retained members.

Run:

```sh
julia --project=experiments experiments/run_pi_four_wire_parallel_ac.jl
julia --project=experiments experiments/test/pi_four_wire_parallel_ac.jl
```

The generated certificate is
`experiments/generated/pi-four-wire-parallel-ac-certificate.json`.

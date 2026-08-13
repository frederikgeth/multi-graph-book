# [Multiconductor parallel AC decision case](@id multiconductor-parallel-ac-case)

The scalar parallel example shows the feasible-set mechanism with almost no
algebra. This case retains complex conductor voltages, mutual impedance,
phase-to-neutral power, voltage bounds, and nonlinear AC power balance. Its
purpose is to test whether the same representation failure changes an AC
decision optimum.

## Source model

Two buses ``i`` and ``j`` have ordered conductor set ``(a,n)``. The sending
voltage is fixed at

```math
\mathbf U_i=(1,0)^{\mathsf T}\ \mathrm{p.u.}
```

and two parallel members satisfy

```math
\mathbf I_{\ell i j}
=\mathbf Y_\ell(\mathbf U_i-\mathbf U_j),
\qquad \ell\in\{1,2\}.
```

The full, coupled series impedances are

```math
\mathbf Z_{\ell_1}=
\begin{bmatrix}
0.04+0.08\mathrm j&0.01+0.02\mathrm j\\
0.01+0.02\mathrm j&0.04+0.08\mathrm j
\end{bmatrix},
\qquad
\mathbf Z_{\ell_2}=10\mathbf Z_{\ell_1}.
```

Every member and conductor has limit
``|I_{\ell i j,c}|\le0.6`` p.u. Receiving-end conservation requires

```math
\sum_{\ell}I_{\ell i j,a}
+\sum_{\ell}I_{\ell i j,n}=0.
```

The decision ``\alpha\ge0`` scales a constant-power direction across phase and
neutral:

```math
S_j=\alpha(1+0.2\mathrm j)
=(U_{j,a}-U_{j,n})
 \left(\sum_\ell I_{\ell i j,a}\right)^{\!*}.
```

The phase-to-neutral voltage magnitude is restricted to ``[0.70,1.05]`` p.u.,
and the objective maximizes ``\alpha``.

## Three formulations

The **source** formulation retains each ``\mathbf I_{\ell i j}`` as a variable
and enforces every member limit. The **naive aggregate** uses

```math
\mathbf Y_{\mathrm{eq}}=\mathbf Y_{\ell_1}+\mathbf Y_{\ell_2}
```

and assigns each aggregate conductor the summed limit ``1.2`` p.u. The
**exact lifted aggregate** uses the same aggregate terminal relation but
recovers

```math
\mathbf I_{\ell i j}
=\mathbf Y_\ell(\mathbf U_i-\mathbf U_j)
```

inside the target model and applies the original ``0.6`` p.u. limits.

## Results

| Formulation | Served fraction | Receiving voltage magnitude | Largest recovered member current | Variables / constraints |
|:--|--:|--:|--:|--:|
| source members | 0.6138908 | 0.9485579 | 0.6000000 | 13 / 19 |
| naive aggregate | 1.0630833 | 0.9034471 | 1.0909091 | 5 / 9 |
| exact lifted aggregate | 0.6138908 | 0.9485579 | 0.6000000 | 5 / 11 |

The naive target serves about 73% more load than the source by violating the
stronger member's current limit. The exact lifted formulation reproduces the
source optimum while using the aggregate current relation and six fewer
explicit current variables in this implementation. This is claim
`TR-PAR-004`.

## Solver-independent check

For the chosen proportional matrices, a phase-to-neutral current sees loop
impedances

```math
z_\ell=Z_{\ell,aa}+Z_{\ell,nn}-Z_{\ell,an}-Z_{\ell,na}.
```

The equivalent loop impedance is
``z=0.05454545+0.10909091\mathrm j`` p.u. If ``C`` is the limiting total-current
magnitude, ``s=1+0.2\mathrm j``, and ``v`` is the receiving voltage magnitude,
then

```math
1=v^2+2Cv\frac{\Re(z)\Re(s)+\Im(z)\Im(s)}{|s|}+|z|^2C^2,
\qquad
\alpha=\frac{Cv}{|s|}.
```

The source member limit gives ``C=0.66`` p.u.; the summed aggregate gives
``C=1.2`` p.u. The served-power derivative on the high-voltage branch remains
positive at both limits, so each current cap is binding. The positive quadratic
roots reproduce both Ipopt objectives to better than ``10^{-7}``.

## Scope and reproducibility

This is a deliberately minimal nonlinear AC case, not a three-phase benchmark.
It includes conductor coupling and an explicit return path, but uses
proportional member matrices and one scalable load direction so that a closed
form check remains possible. The next extension should break that
proportionality, add three phases plus neutral, and compare active constraints
and decisions in a larger BMOPFTools case.

Run:

```sh
julia --project=experiments experiments/run_multiconductor_parallel_ac.jl
julia --project=experiments experiments/test/multiconductor_parallel_ac.jl
```

The generated AC certificate contains all three solutions, recovered member
currents, model sizes, residuals, and closed-form differences.

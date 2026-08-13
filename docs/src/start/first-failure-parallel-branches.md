# A first failure: heterogeneous parallel branches

## The tempting replacement

Consider two scalar resistive branches ``\ell_1 i j`` and ``\ell_2 i j`` with
intrinsic impedances

```math
Z_{\ell_1}=0.1\ \Omega,\qquad Z_{\ell_2}=1.0\ \Omega,
```

and member current limits

```math
I^{\max}_{\ell_1}=I^{\max}_{\ell_2}=100\ \mathrm{A}.
```

Writing ``\Delta U=U_i-U_j`` and ``Y_{\ell}=Z_{\ell}^{-1}``, the terminal
currents are

```math
I_{\ell_k i j}=Y_{\ell_k}\Delta U,\qquad k\in\{1,2\}.
```

Replacing the pair by one branch with

```math
Y_{\mathrm{eq}}=Y_{\ell_1}+Y_{\ell_2}=11\ \mathrm{S}
```

is exact for the unconstrained total terminal-current relation. It does not
follow that the replacement is exact for a decision problem with member limits.

## The feasible sets differ

The source model requires both inequalities

```math
|Y_{\ell_1}\Delta U|\le I^{\max}_{\ell_1},\qquad
|Y_{\ell_2}\Delta U|\le I^{\max}_{\ell_2}.
```

Hence its admissible voltage-drop magnitude is

```math
|\Delta U|\le
\min\left\{\frac{I^{\max}_{\ell_1}}{|Y_{\ell_1}|},
            \frac{I^{\max}_{\ell_2}}{|Y_{\ell_2}|}\right\}
=10\ \mathrm{V}.
```

A common aggregate construction assigns the equivalent branch the summed
rating, ``I^{\max}_{\mathrm{eq}}=200\ \mathrm{A}``. It admits

```math
|\Delta U|\le \frac{200}{11}=18.18\ \mathrm{V}.
```

At the witness ``\Delta U=15\ \mathrm{V}``, the equivalent branch carries
``165\ \mathrm{A}`` and satisfies its aggregate limit. Recovery gives

```math
I_{\ell_1 i j}=150\ \mathrm{A},\qquad
I_{\ell_2 i j}=15\ \mathrm{A},
```

so the source violates the ``\ell_1`` limit. The target feasible set is
therefore an outer relaxation of the source feasible set.

## Preservation contract

| Contract field | Value |
| --- | --- |
| source | two identified parallel branches with individual limits |
| target | one equivalent branch with summed admittance and rating |
| preconditions | common endpoints and voltage coordinates; linear branch laws |
| preserves | unconstrained total terminal current as a function of ``\Delta U`` |
| does not preserve | the member-constrained feasible set |
| forgets | member identity and independent outage, maintenance, or investment state |
| recovery | ``I_{\ell_k i j}=Y_{\ell_k}\Delta U`` if member admittances remain available |
| classification | outer/relaxed for this rating construction |

This counterexample does not say that parallel aggregation is never useful. It
says that an aggregate rating needs its own derivation relative to the intended
observation or decision set. Choosing a tighter equivalent limit can reproduce
this one scalar voltage-drop bound, but it still does not recreate independent
member states or arbitrary member-wise constraints.

## Multiconductor form

For multiconductor branches,

```math
\mathbf I_{\ell_k i j}=\mathbf Y_{\ell_k}\Delta\mathbf U,
```

and the source feasible set is the intersection of the inverse images of every
member constraint set:

```math
\mathcal D_{\mathrm{src}}=
\bigcap_k\left\{\Delta\mathbf U:
\mathbf Y_{\ell_k}\Delta\mathbf U\in\mathcal C_{\ell_k}\right\}.
```

The summed terminal map
``\mathbf Y_{\mathrm{eq}}=\sum_k\mathbf Y_{\ell_k}`` does not, by itself,
encode that intersection. Mutual coupling and per-conductor limits make a
single conventional rating still less likely to be an exact representation.

The generation script emits the numerical witness and its machine-readable
contract as claim `TR-PAR-001`.

## A decision problem exposes the gap

The same mechanism changes an optimum in a two-bus maximum-served-load model.
Let the parallel members have

```math
(b_{\ell_1},b_{\ell_2})=(1000,100)\ \mathrm{MW/rad},\qquad
(F^{\max}_{\ell_1},F^{\max}_{\ell_2})=(100,100)\ \mathrm{MW},
```

with ``F_{\ell i j}=b_\ell\delta_{ij}``, nonnegative
``\delta_{ij}``, and served power equal to total flow. The source model keeps
both member laws and both limits. The naïve target uses
``b_{\mathrm{eq}}=1100`` MW/rad and
``F^{\max}_{\mathrm{eq}}=200`` MW.

| Formulation | Maximum served power | ``\delta_{ij}`` | Active restriction |
|:--|--:|--:|:--|
| source members | 110 MW | 0.1 rad | ``F_{\ell_1 i j}\le100`` MW |
| naïve aggregate | 200 MW | ``2/11`` rad | summed 200 MW rating |
| aggregate relation with exact lifted member constraints | 110 MW | 0.1 rad | recovered ``F_{\ell_1 i j}\le100`` MW |

The exact lifted formulation retains

```math
F_{\ell i j}=b_\ell\delta_{ij},\qquad
F_{\ell i j}\le F^{\max}_\ell \quad\text{for every }\ell,
```

alongside the aggregate terminal relation. It therefore reproduces the source
feasible set and optimum without pretending that a summed scalar rating is
exact. This computed comparison is claim `TR-PAR-003`. JuMP and Ipopt produce
the machine-readable result in
`experiments/generated/parallel-opf-comparison.json`; the analytic values above
also provide a solver-independent check.

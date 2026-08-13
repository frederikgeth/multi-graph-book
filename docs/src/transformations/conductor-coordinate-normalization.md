# [Conductor-coordinate normalization](@id conductor-coordinate-normalization)

Conductor order is representation, not physics. It is nevertheless part of
the meaning of every vector, matrix, and componentwise constraint. A rewrite
that changes an order without changing all dependent objects is therefore a
model error, not a harmless formatting operation.

## Rule

Consider an element ``\ell i j`` with source conductor order
``\gamma_\ell=(n,a)`` and a requested order
``\widehat\gamma_\ell=(a,n)``. Let ``\mathbf P_\ell`` be the unique
permutation for which

```math
\widehat{\mathbf x}_{\ell i j}
=\mathbf P_\ell\mathbf x_{\ell i j}.
```

Intrinsic element data retain only the element index. In particular, the
coordinate-normalized impedance is

```math
\widehat{\mathbf Z}_\ell
=\mathbf P_\ell\mathbf Z_\ell\mathbf P_\ell^{\mathsf T},
```

and a vector of componentwise limits becomes

```math
\widehat{\mathbf I}^{\max}_\ell
=\mathbf P_\ell\mathbf I^{\max}_\ell.
```

The terminal map at ``j`` is reordered by preserving each original
from--to conductor pairing. Thus a coordinate position can move, but conductor
identity cannot silently change.

## Exactness and inverse

A permutation matrix satisfies
``\mathbf P_\ell^{-1}=\mathbf P_\ell^{\mathsf T}``. Hence every normalized
state and every transformed intrinsic matrix has a unique recovery:

```math
\mathbf x_{\ell i j}
=\mathbf P_\ell^{\mathsf T}\widehat{\mathbf x}_{\ell i j},
\qquad
\mathbf Z_\ell
=\mathbf P_\ell^{\mathsf T}\widehat{\mathbf Z}_\ell\mathbf P_\ell.
```

The rule is therefore an exact normalization (`TR-COORD-001`). It forgets no
declared source semantics. This statement depends on permuting every indexed
quantity consistently; permuting only ``\mathbf Z_\ell`` or only a terminal
list is not the same rule.

## Guards and rejection

The executable rule requires:

- unique conductor labels in both orders;
- equal source and requested conductor sets;
- equal arity; and
- preservation of the original paired terminal map.

A missing, duplicated, or new conductor label produces a structured rejection.
The implementation does not guess whether, for example, `g` and `n` are
interchangeable.

## Executable example

For the order reversal used by the running series example,

```math
\mathbf P_\ell=
\begin{bmatrix}0&1\\1&0\end{bmatrix}.
```

The rule moves limits ``(80,110)`` A in order ``(n,a)`` to ``(110,80)`` A in
order ``(a,n)`` and permutes both axes of ``\mathbf Z_\ell``. Run:

```sh
julia experiments/test/coordinate_normalization.jl
julia --project=experiments experiments/run_coordinate_series_composition.jl
```

The machine-readable result is
`experiments/generated/coordinate-normalization-certificate.json`. The next
chapter composes this normalization with degree-two series elimination.

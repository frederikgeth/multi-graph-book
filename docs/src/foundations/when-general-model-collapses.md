# [When the general model collapses](@id positive-sequence-collapse)

The general multiconductor, multi-terminal model is a baseline for preserving
meaning. It is not a claim that every study needs all of that structure. This
chapter gives a positive derivation of the familiar balanced positive-sequence
bus--branch model and lists the assumptions that make the collapse admissible.

## The balanced invariant subspace

Let a three-phase two-terminal factor use the phase order ``(a,b,c)`` and the
Fortescue matrix ``A``

```math
\mathbf v_{abc}=A\mathbf v_{012},
\qquad
A=\begin{bmatrix}1&1&1\\1&a^2&a\\1&a&a^2\end{bmatrix},
\qquad a=e^{\mathrm j2\pi/3}.
```

The positive-sequence subspace is

```math
\mathcal V_+=\{A[0,V_1,0]^{\mathsf T}:V_1\in\mathbb C\}.
```

An exactly balanced operating point has phase voltages and currents in this
subspace, with the corresponding phase shifts. Balance is a restriction on
the admissible state and injections; it is not created by drawing one edge per
bus pair.

## Factor-level assumptions

Consider a linear series or nominal-``\pi`` factor with phase-domain relation
``\mathbf i=\mathbf Y\mathbf v``. A sufficient exact-collapse contract is:

1. **compatible phase sets:** every retained terminal has the same ordered
   three-phase set, with no unresolved neutral or earth port;
2. **cyclic symmetry:** each series and shunt matrix commutes with the cyclic
   phase permutation, equivalently it is circulant in the declared phase
   coordinates;
3. **balanced boundary data:** sources, injections, and measurements are
   restricted to ``\mathcal V_+``;
4. **sequence-compatible grounding:** zero- and negative-sequence return paths
   are either absent from the study or represented by fixed factors whose
   constraints are not queried;
5. **two-terminal closure:** each device is already a two-terminal factor, or
   a multi-terminal device has an explicitly verified positive-sequence
   compilation;
6. **decision symmetry:** controls are common to all phases, and limits,
   costs, and admissible states are invariant under the same phase symmetry;
7. **observation restriction:** the study does not ask for phase-specific,
   neutral-to-ground, negative-sequence, zero-sequence, or internal winding
   quantities.

Under these assumptions, ``A^{-1}\mathbf Y A`` is diagonal in sequence
coordinates, and the positive-sequence block is invariant:

```math
\mathbf Y_{012}=A^{-1}\mathbf Y_{abc}A
=\operatorname{diag}(Y_0,Y_1,Y_2),
\qquad
I_1=Y_1V_1.
```

For a nominal-``\pi`` factor, the same statement applies to the series and
shunt blocks separately. The positive-sequence network is therefore a derived
two-terminal scalar complex network with one voltage and current per bus/arc,
provided the factor library and decision constraints close under the
restriction.

The generated witness
`experiments/generated/positive-sequence-collapse-witness.json` diagonalizes
one circulant impedance matrix to numerical precision and records a
non-circulant perturbation that mixes sequences. It is a factor-level witness,
not yet a complete balanced transmission network or a global decision
equivalence test.

## Network-level derivation

Let ``C_+`` restrict a general model to the positive-sequence subspace and let
``E_+`` embed a positive-sequence state into phase coordinates. Under the
factor, boundary, and decision assumptions above,

```math
\mathcal F_{+}=C_+(\mathcal F_{abc}),
\qquad
E_+(\mathcal F_{+})\subseteq\mathcal F_{abc},
```

and the declared observations factor as

```math
h_{abc}\circ E_+=\widehat h_+.
```

Thus the positive-sequence model is exact for the restricted observation
family ``H_+``. It is not exact for the unrestricted phase-domain feasible set
unless every feasible phase-domain point is balanced, which is a much stronger
statement.

For an approximately balanced model, define the residual of a phase-domain
state ``v`` by

```math
\rho_+(\mathbf v)=\left\|\mathbf v-E_+C_+\mathbf v\right\|.
```

This is a coordinate residual, not a decision-error bound. A voltage residual
must be propagated through the factor equations and constraints before it can
support an engineering approximation claim.

## What collapses, and what does not

| General object | Positive-sequence image | Required qualification |
| --- | --- | --- |
| three phase voltages/currents | one complex sequence variable | only balanced states are represented |
| circulant series and shunt matrices | scalar ``Y_1`` blocks | non-circulant coupling produces sequence mixing |
| identical phase limits and common controls | one sequence limit/control | phase-specific constraints are outside the image |
| two-terminal factor | oriented bus--branch arc | multi-terminal devices need a verified compiler |
| neutral/earth factor | omitted or externally resolved | grounding and zero-sequence questions are forgotten |
| phase-specific measurements | aggregate sequence observation | not preserved by the quotient |

The running fixture intentionally fails several guards: it has four-wire lines,
an explicit grounded neutral, nonuniform terminal sets, a phase permutation,
unbalanced loads, full coupled matrices, and a three-winding transformer. It is
therefore a test of the general model, not a balanced positive-sequence witness.
The transmission specialization must be a separately declared fixture or a
parameterized subcase with its own residual and checks.

!!! warning "Power-system shorthand"
    “Use a positive-sequence model” is a modelling decision with assumptions,
    not a graph-theoretic simplification. State the balance, transposition,
    grounding, equipment, limit, and observation assumptions before treating
    the resulting bus--branch graph as exact.

## Decision consequence

The positive-sequence collapse is exact for a restricted decision problem when
the feasible-set inclusion, recovery embedding, and observation factorization
above hold. If a contingency opens one phase, a relay observes zero sequence,
a transformer has phase-dependent taps, or a conductor limit becomes active,
the decision domain has left ``\mathcal F_+``. The general port--factor model or
an explicitly guarded intermediate model is then required.

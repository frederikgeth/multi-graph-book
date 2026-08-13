# [Kron, Ward, and optimized network equivalents](@id kron-ward-opti-kron)

## Three different questions

Kron reduction, Ward equivalents, and Opti-KRON are related, but they do not
make the same modelling choice:

```math
\boxed{
\begin{aligned}
\text{Kron: }&\text{which linear boundary relation results from elimination?}\\
\text{Ward: }&\text{how is the eliminated external system represented at the boundary?}\\
\text{Opti-KRON: }&\text{which nodes or clusters should be retained under an error objective?}
\end{aligned}}
```

All three require a declared source model, boundary, injection model, and
observation contract. None is inherently an asset-preserving transformation.

## Linear Kron reduction

Partition a linear nodal relation into retained boundary variables ``B`` and
eliminated internal variables ``I``:

```math
\begin{bmatrix}
\mathbf i_B\\
\mathbf i_I
\end{bmatrix}
=
\begin{bmatrix}
\mathbf Y_{BB}&\mathbf Y_{BI}\\
\mathbf Y_{IB}&\mathbf Y_{II}
\end{bmatrix}
\begin{bmatrix}
\mathbf v_B\\
\mathbf v_I
\end{bmatrix}.
```

**Proposition.** If ``\mathbf Y_{II}`` is invertible and ``\mathbf i_I`` is
fixed, then eliminating ``\mathbf v_I`` gives the exact affine boundary
relation

```math
\mathbf i_B
=\mathbf Y_{\mathrm K}\mathbf v_B
+\mathbf K_I\mathbf i_I,
```

where

```math
\mathbf Y_{\mathrm K}
=\mathbf Y_{BB}
-\mathbf Y_{BI}\mathbf Y_{II}^{-1}\mathbf Y_{IB},
\qquad
\mathbf K_I
=\mathbf Y_{BI}\mathbf Y_{II}^{-1}.
```

The eliminated voltages are recovered by

```math
\mathbf v_I
=\mathbf Y_{II}^{-1}
(\mathbf i_I-\mathbf Y_{IB}\mathbf v_B).
```

**Proof.** Solve the internal block equation for ``\mathbf v_I`` and
substitute it into the boundary block equation.

For zero internal injection this becomes

```math
\mathbf i_B=\mathbf Y_{\mathrm K}\mathbf v_B.
```

This is exact equality of a selected linear terminal relation. Schur
elimination can create dense coupling among neighbours of eliminated nodes,
and the resulting entries need not correspond to physical lines. Dörfler and
Bullo analyze the graph and loopy-Laplacian properties of this operation
[DorflerBullo2013](@cite). Closure inside a more restrictive dynamic or device
class requires additional physical assumptions [CaliskanTabuada2014](@cite).

Kron reduction does not by itself preserve:

- eliminated asset identity or topology;
- internal branch currents and limits unless recovery is retained;
- switching, outage, maintenance, or investment decisions;
- protection and failure dependencies;
- sparsity;
- nonlinear constant-power behaviour over arbitrary operating points.

The Schur complement first produces a reduced multiport relation. Realizing
that relation as a permitted collection of bus--branch devices is a separate
synthesis or compilation problem.

## Typed multiconductor Kron reduction

In the multiconductor case, the symbols ``B`` and ``I`` denote direct sums of
typed terminal-coordinate spaces, not merely lists of scalar buses. Let

```math
\mathcal V_B=\bigoplus_{k\in B}\mathbb C^{n_k},
\qquad
\mathcal V_I=\bigoplus_{k\in I}\mathbb C^{n_k}.
```

Each port voltage is first aligned with its junction by its terminal map. If
``\mathbf N_q`` maps the ordered junction voltage into the ordered coordinates
of port ``q``, then

```math
\mathbf v_q=\mathbf N_q\mathbf U_{j(q)},
\qquad
\mathbf I_{j(q)}\mathrel{+}=
\mathbf N_q^{\mathsf H}\mathbf i_q.
```

The conjugate transpose in the current map is the power-dual action: it makes
``\mathbf v_q^{\mathsf H}\mathbf i_q`` agree with the corresponding junction
power pairing. The assembled nodal blocks in the preceding section are formed
only after these terminal maps have been applied. Consequently every product
``\mathbf Y_{BI}\mathbf Y_{II}^{-1}\mathbf Y_{IB}`` is a typed map
``\mathcal V_B\rightarrow\mathcal V_B``.

**Proposition (typed coordinate-covariant Kron reduction).** Suppose the
assembled linear multiconductor relation has
``\mathbf Y_{II}:\mathcal V_I\rightarrow\mathcal V_I`` invertible. Let
``\mathbf T_B`` and ``\mathbf T_I`` be invertible, block-diagonal changes of
retained and internal terminal coordinates, with

```math
\mathbf v_B=\mathbf T_B\widetilde{\mathbf v}_B,
\qquad
\mathbf v_I=\mathbf T_I\widetilde{\mathbf v}_I,
\qquad
\widetilde{\mathbf i}_B=\mathbf T_B^{\mathsf H}\mathbf i_B,
\qquad
\widetilde{\mathbf i}_I=\mathbf T_I^{\mathsf H}\mathbf i_I.
```

Then Kron reduction before or after the coordinate change gives the same
boundary relation. Specifically,

```math
\widetilde{\mathbf Y}_{\mathrm K}
=
\mathbf T_B^{\mathsf H}\mathbf Y_{\mathrm K}\mathbf T_B,
```

and the affine internal-injection term transforms as

```math
\widetilde{\mathbf K}_I\widetilde{\mathbf i}_I
=
\mathbf T_B^{\mathsf H}\mathbf K_I\mathbf i_I.
```

The recovered internal voltage is coordinate consistent:

```math
\widetilde{\mathbf v}_I
=
\mathbf T_I^{-1}\mathbf Y_{II}^{-1}
(\mathbf i_I-\mathbf Y_{IB}\mathbf v_B).
```

**Proof.** The transformed blocks are

```math
\widetilde{\mathbf Y}_{XY}
=\mathbf T_X^{\mathsf H}\mathbf Y_{XY}\mathbf T_Y,
\qquad X,Y\in\{B,I\}.
```

Using

```math
(\mathbf T_I^{\mathsf H}\mathbf Y_{II}\mathbf T_I)^{-1}
=\mathbf T_I^{-1}\mathbf Y_{II}^{-1}\mathbf T_I^{-\mathsf H}
```

in the transformed Schur complement cancels the internal coordinate maps and
leaves ``\mathbf T_B^{\mathsf H}\mathbf Y_{\mathrm K}\mathbf T_B``. The same
substitution proves the affine and recovery identities.

The proposition covers phase permutations and other invertible port-coordinate
actions. A sequence-coordinate statement needs its transform convention
declared: with the usual non-unitary Fortescue matrix ``A``, applying the same
voltage and current coordinates gives the similarity action
``A^{-1}\mathbf Y A``; the power-dual convention above gives the congruence
action ``A^{\mathsf H}\mathbf Y A``. These coincide only under additional
normalization assumptions. Neither convention justifies dropping a conductor,
identifying a neutral with earth, or aggregating phases: those maps are not
invertible coordinate changes and require separate preservation claims.

**Corollary (reciprocity is convention-relative).** If a nodal matrix is
complex symmetric in physical coordinates, a real coordinate congruence
``T^{\mathsf T}\mathbf YT`` preserves complex symmetry. The power-dual action
``T^{\mathsf H}\mathbf YT`` preserves it when ``T`` is real (or under other
explicit compatibility conditions), but not for an arbitrary complex ``T``.
Hermitian structure and complex symmetry are therefore distinct properties;
the certificate must record which one is required and which coordinate action
is being used.

## Realizability is a second theorem

The reduced matrix always defines a general linear factor on the retained
ports. It need not define a conventional collection of lines. Realizability is
therefore relative to a target device library.

!!! warning "Power-system shorthand"
    A nonzero off-diagonal block in a reduced admittance is a boundary coupling,
    not automatically a physical line. Any line--shunt realization is a second
    construction whose asset meaning, limits, states, and provenance must be
    declared separately.

For a useful baseline, suppose all retained junctions use the same ordered
``c``-conductor coordinates and the target library permits:

1. one reciprocal full-matrix series primitive between any pair of retained
   junctions; and
2. one full-matrix shunt primitive at every retained junction.

Write the reduced admittance in ``c\times c`` blocks
``\mathbf Y^{\mathrm K}_{pq}``.

**Proposition (direct line--shunt realization).** If every off-diagonal block
obeys

```math
\mathbf Y^{\mathrm K}_{pq}
=\mathbf Y^{\mathrm K}_{qp}
=(\mathbf Y^{\mathrm K}_{pq})^{\mathsf T},
```

then the reduced relation has the exact complete-graph realization

```math
\mathbf Y^{\mathrm s}_{pq}=-\mathbf Y^{\mathrm K}_{pq},
\qquad
\mathbf Y^{\mathrm{sh}}_p
=\mathbf Y^{\mathrm K}_{pp}
-\sum_{q\ne p}\mathbf Y^{\mathrm s}_{pq}.
```

**Proof.** A reciprocal series primitive contributes
``-\mathbf Y^{\mathrm s}_{pq}`` to both off-diagonal blocks and
``\mathbf Y^{\mathrm s}_{pq}`` to both corresponding diagonal blocks.
Summing all pairwise stamps reproduces every off-diagonal block. The residual
shunt definition then reproduces each diagonal block. Thus the proposition is
an exact stamping identity in a library that permits full ``c\times c``
reciprocal blocks; it is not a claim that a smaller physical line library is
closed under Kron reduction. For ``N`` retained junctions the construction
uses ``N(N-1)/2`` pairwise series blocks plus ``N`` shunts.

This is an algebraic realization, not yet a physical line realization. A
passive line--shunt library imposes additional conditions such as

```math
\operatorname{He}(\mathbf Y^{\mathrm s}_{pq})\succeq0,
\qquad
\operatorname{He}(\mathbf Y^{\mathrm{sh}}_p)\succeq0,
```

along with its reciprocity, frequency, grounding, and parameterization rules.
A restricted diagonal or sequence-decoupled library imposes stronger closure
conditions. Ideal-transformer terminal maps can realize a broader class of
off-diagonal blocks, but then transformer ratios, winding coordinates,
grounding, and provenance become part of the target certificate. If none of
these libraries closes, retaining ``\mathbf Y_{\mathrm K}`` as one general
multiport factor is still exact.

Internal current and limit recovery is yet another layer. If a source branch
current has the affine form

```math
\mathbf I_\ell
=\mathbf A_{\ell B}\mathbf v_B
+\mathbf A_{\ell I}\mathbf v_I,
```

substitution of the voltage recovery map gives an exact affine boundary map
for ``\mathbf I_\ell``. Keeping that map permits source limits to be checked;
discarding it does not make limits on artificial reduced branches equivalent.

## Ward equivalents

The affine term

```math
\mathbf K_I\mathbf i_I
```

shows what a network equivalent must do when the eliminated region has
nonzero injections. A Ward-type equivalent combines the reduced boundary
admittance with equivalent boundary injections, shunts, or sources intended to
represent the external system in a power-flow study. Ward's original
construction explicitly approximates suppressed loads and generation as
constant currents, retains the tie terminals, replaces the eliminated network
by a boundary mesh, and places equivalent injections at those terminals
[Ward1949](@cite).

For a linear fixed-current source model, the affine relation above is exact.
For a constant-power AC model, however,

```math
\mathbf i_I(\mathbf v_I)
=\left(\mathbf S_I\oslash\mathbf v_I\right)^*,
```

where ``\oslash`` denotes componentwise division. The internal injection is
then voltage dependent, so replacing it by a fixed boundary source is not a
global exact reduction of the nonlinear feasible relation. Its validity must
instead be tied to an operating point, linearization, iteration, or scenario
domain.

The term *extended Ward* is not just another name for that base construction.
Monticelli and coauthors build an external equivalent for static security from
a single estimated operating state, address boundary-bus designation, and
discuss treatment of external shunts and generator-outage studies
[Monticelli1979](@cite). A Ward--PV construction instead retains external
generator buses after load-node elimination; the reduced Ward--PV model then
aggregates selected coherent generator groups [Machowski1988](@cite). These
targets preserve different state and control structure.

The resulting source taxonomy is:

- **classical Ward:** constant-current approximation followed by external-bus
  elimination and boundary-mesh/injection realization;
- **operating-state extended Ward:** a base-state-calibrated external
  equivalent with extra boundary, shunt, and contingency treatment;
- **Ward--PV:** retention of selected generator/PV structure before any
  subsequent coherent aggregation;
- **nonlinear or iterative Ward-type methods:** later constructions that
  update or fit the boundary source model over operating points and must state
  their own domain.

These are historically related, not mathematically interchangeable. In
particular, the exact affine result for fixed currents does not make a
base-state-calibrated AC equivalent globally exact for constant-power or
voltage-controlled devices.

## Opti-KRON

Opti-KRON adds a structural selection problem around a Kron-based electrical
reduction. An assignment matrix maps original nodes to retained supernodes;
the selection trades the degree of reduction against reproduction error for
declared voltage observations and operating scenarios. The three-phase work
also constrains phase availability and connectivity [Mokhtari2027](@cite).
A related extension identifies nodes to restore so that the final reduced
network recovers radiality [MokhtariRadial2025](@cite).

It is useful to factor the method conceptually as

```math
\text{optimized structural assignment}
+\text{Kron-based electrical reduction}
+\text{scenario observation metric}.
```

The Schur-complement step can be exact for its retained linear boundary
relation while the supernode representation of eliminated voltages is
approximate. The combined method is therefore not classified simply as
*exact Kron reduction*. Its certificate must record at least:

- the retained-node and assignment decision spaces;
- phase and connectivity guards;
- the operating scenarios used to evaluate voltage error;
- the voltage observation norm and bound;
- any radiality restoration;
- the source injections and controls represented in those scenarios;
- whether source constraints and decisions can be recovered.

Low voltage error over a scenario set does not alone prove equality of AC OPF
feasible sets, active limits, discrete decisions, or objective values. Those
are additional observation families requiring their own evidence.

!!! warning "Decision-model consequence"
    Scenario voltage accuracy answers one observation question. It is not a
    surrogate theorem for feasibility, active-limit, objective, or discrete
    decision accuracy.

## Classification in the book's transformation language

The classification depends on the complete construction, not on whether its
name contains *Kron*:

- **Zero-injection linear Kron:** from a linear nodal or multiport relation to
  its boundary relation. This is exact behavioural reduction; physical
  realization and internal constraints are not automatic.
- **Fixed-current affine Kron:** from a linear relation with fixed internal
  injections to an affine boundary relation. This is exact behavioural
  reduction for that source model, not for arbitrary voltage-dependent
  injections.
- **Ward equivalent:** from an external-system study model to a boundary
  network with equivalent injections. It may be exact, local, or approximate
  depending on the injection model; there is no assumed universal definition
  across Ward variants.
- **Opti-KRON:** from scenario data and a candidate topology to a selected
  reduced network. This is mixed structural optimization and scenario
  approximation; general decision equivalence is not automatic.
- **Radiality restoration:** from a nonradial reduced topology to one with
  selected nodes restored. This is structural postprocessing under its stated
  rule, not electrical or decision equivalence by itself.

These distinctions place each method relative to a preservation contract
before relating it to the book's local rewrite rules.

## Relation to local transformations

The guarded degree-two series rule is a special zero-injection elimination for
which the reduced relation remains inside a declared series-element family.
A star--mesh transformation is another local Schur-complement realization.
Parallel primitive summation is different: it combines factors sharing a
boundary but eliminates no bus. Redundant-limit removal is different again: it
is exact presolve on the constraints while the physical members remain.

This separation prevents every operation involving a smaller network from
being called Kron reduction.

## Open research boundary

The current evidence leaves four implementation questions open:

1. executable realizability tests for selected line, shunt, transformer, and
   general-factor libraries;
2. recovery and constraint maps for internal currents, powers, and losses;
3. an executable small example comparing exact Kron, a Ward operating-point
   equivalent, and an Opti-KRON-style scenario approximation;
4. a decision experiment measuring feasibility, active constraints, and
   objective error in addition to voltage error.

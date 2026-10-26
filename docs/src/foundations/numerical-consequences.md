# [Numerical consequences of representation and reduction](@id numerical-consequences)

**Page status:** generated structural, linearized, symbolic KKT, and
package-level solver-diagnostics crosswalk witnesses; solver-internal
nonlinear exports remain future work.

## A graph choice is also a numerical choice

Two representations can describe the same declared electrical behaviour while
producing very different numerical problems. A quotient may reduce the number
of variables but worsen scaling; a Kron reduction may preserve a boundary
relation but introduce dense couplings; a factor model may expose physical
structure while a bus--branch compiler produces a smaller, more familiar
Jacobian. These are computational consequences, not afterthoughts.

The relevant comparison is therefore not only

```math
\text{same terminal map?}
```

but also

```math
\text{same feasible observations, with what conditioning, sparsity, and recovery cost?}
```

The statements below concern a declared operating point, coordinate system,
and solver tolerance. They do not claim that one representation is uniformly
better.

The federated `PSK-000011` guard makes one practical boundary executable:
`reference_singularity_validation` compares mapped connected-island reference
incidence and rank declarations before accepting a transformed model. A
successful import or solver termination is not an independent certificate of
full rank. The package pass remains declaration-level evidence; equation,
Jacobian, conditioning, and solver-specific checks still belong to the study.

!!! note "Vocabulary bridge"
    Electrical loss is power absorbed by a device model. Information loss is
    a failure of recovery under a representation map. An optimization or ML
    loss is an objective function. The shared word does not make these
    quantities comparable, and reducing one need not reduce either of the
    others.

## Scaling and conditioning

Let a linearized or linear subproblem be

```math
\mathbf A x = b.
```

Changing units or terminal coordinates is represented by nonsingular maps
``x=\mathbf D_x\widetilde x`` and ``b=\mathbf D_b\widetilde b``. The
coefficient matrix becomes

```math
\widetilde{\mathbf A}
 = \mathbf D_b^{-1}\mathbf A\mathbf D_x.
```

The coordinate map bijectively relates the two solution sets. For nonsingular
``\mathbf A`` and an induced matrix norm, the condition number can change:

```math
\kappa(\widetilde{\mathbf A})
 = \|\mathbf D_b^{-1}\mathbf A\mathbf D_x\|
   \|\mathbf D_x^{-1}\mathbf A^{-1}\mathbf D_b\|.
```

This is why per-unit coordinates are a numerical convention as well as a
reporting convention. A declared base scales voltage, current, power, and
impedance together; it does not erase poor physical conditioning, singular
topology, or an omitted conductor. A coordinate transformation is safe to call
an exact rewrite only when its inverse and its power-dual action are retained,
as in [the coordinate-transformation chapter](@ref circuit-coordinate-transformations).

!!! warning "Circuit-theory trap"
    A dimensionless or per-unit matrix is not automatically well conditioned.
    The conditioning claim must name the norm, the bases, and the operating
    domain. A small residual in badly scaled coordinates can coexist with a
    large error in a physical voltage, current, or decision.

For a computed solution ``\widehat x`` define the residual
``r=b-\mathbf A\widehat x``. A backward-error measure is, for example,

```math
\eta(\widehat x)
 = \frac{\|r\|}{\|\mathbf A\|\,\|\widehat x\|+\|b\|}.
```

For nonsingular ``\mathbf A``, nonzero exact solution ``x``, and the same vector
norm and its induced matrix norm throughout, put
``\theta=\kappa(\mathbf A)\eta(\widehat x)``. If ``\theta<1``, an explicit bound is

```math
\frac{\|\widehat x-x\|}{\|x\|}
 \le \frac{2\theta}{1-\theta}.
```

To see the factor of two, use ``\widehat x-x=-\mathbf A^{-1}r`` and
``\|b\|\le\|\mathbf A\|\|x\|``. The relative error ``\delta`` then satisfies
``\delta\le\theta(2+\delta)``. This bound concerns the stated linear system;
it does not certify a nonlinear solution or the physical input data. The
[LAPACK error-analysis discussion](https://www.netlib.org/lapack/lug/node81.html)
also distinguishes normwise and componentwise backward error. Record both
residual/backward-error information and conditioning, with their norms and
scaling, rather than relying only on solver termination.

## Choose a model against a constraint margin

The [parallel-member lesson](@ref first-failure-parallel-branches) derives an
exact aggregate for fixed data. Now suppose the total nonnegative current
``J`` is prescribed, both members are rated 100 A, the second conductance is
1 S, and the first is known only to lie in ``[8,12]`` S. The nominal first
conductance is 10 S. These are declared interval assumptions for a resistive
teaching case, not measured equipment uncertainty or a probability model.

For conductance ``g`` expressed numerically in siemens, current division is

```math
I_1(J,g)=\frac{g}{g+1}J,\qquad I_2(J,g)=\frac{1}{g+1}J.
```

Compare three choices: solve the two nominal member relations; use their
exact nominal aggregate cap of 110 A with recovery; or require both member
limits for every conductance in the interval. The first two describe the
same nominal feasible set. Neither settles the uncertain-data question.

Because ``I_1`` increases with ``g`` and ``I_2`` decreases, their worst values
occur at opposite interval endpoints. Thus the exact robust cap in this
local model is

```math
J\le\min\{100(13/12),100(9)\}=325/3\ \mathrm A.
```

At 99 A, the nominal first-member current is 90 A; the worst member current
is ``1188/13`` A, leaving ``112/13`` A of margin. At 109 A, the nominal
model still accepts, but the worst member current is ``1308/13`` A and
exceeds its rating by ``8/13`` A. The same uncertainty that was harmless for
the first decision changes the second decision's feasibility classification.

A precise nominal computation cannot remove an uncertain input. Compare the
possible observation error with the source constraint margin. Here the nominal
aggregate is defensible for a stated nominal question; the interval requirement
needs the robust cap. This is a proof over the full declared interval using
monotonicity, not a claim based only on sampled scenarios. Other coupled or
nonlinear models need their own worst-case argument.

```sh
python3 experiments/lessons/model_choice.py
python3 experiments/lessons/model_choice.py --check
python3 experiments/lessons/model_choice.py --benchmark
```

The first two commands use rational arithmetic. The optional local timing
comparison uses floating-point arithmetic for nominal explicit, nominal
aggregate, and interval-robust evaluations. Each measured call includes its
cap/current calculation, limit checks, and current recovery; imports and I/O
are excluded. It reports the median of seven batches of 10,000 calls. This is
a tiny algebraic microbenchmark with no PF solver: use it to learn to count
recovery work, not to rank network formulations. Timings are printed for the
actual machine and are not stored as universal performance evidence.

**Transfer exercise.** Narrow the interval to ``[9,11]`` S. Derive the new
robust cap and decide whether 109 A is admissible. The cap is ``1200/11`` A,
so it is admissible under this interval. State which changed assumption made
that conclusion possible. Do not report it as evidence for the original
``[8,12]`` S interval.

## Jacobians: physical topology is not matrix sparsity

For a nonlinear decision model ``F(y,u)=0``, Newton or interior-point methods
use a Jacobian such as

```math
\mathbf J = \frac{\partial F}{\partial y}.
```

The physical graph predicts some nonzeros, but the Jacobian graph is a graph of
variable--equation dependence. A single multi-terminal factor can create a
dense block between all of its ports. A nominal-``\pi`` element can couple
endpoint voltages through series terms and endpoint currents through shunts.
Constraint rows for limits, controls, and recovery variables add edges that
have no corresponding physical line. Conversely, a physical asset may be
absent from a particular Jacobian block when its state is fixed or its
equation has been eliminated.

Write ``G_phys`` for a chosen physical incidence graph and ``G_J`` for the
bipartite Jacobian graph. In general there is no equality
``G_phys=G_J``. The useful statement is a declared dependency map

```math
\delta:\; (\text{factor},\text{terminal},\text{constraint})
\longmapsto (\text{equation rows},\text{variables}),
```

from which ``G_J`` is generated. This map is the numerical analogue of source
provenance: it explains why a fill-in or a dense block exists.

The five-bus structural witness makes the distinction concrete. Its source has
seven line identities but only six edges after simple projection because ``q``
and ``r`` are parallel. Eliminating ``j`` then adds the ``i``--``l`` fill edge
to the projected pattern. The fill argument and the dependency argument are
shown separately so that a reader does not confuse a Schur-complement edge
with a numerical derivative. The conceptual pair now appears in the
[formulation and lowering chapter](@ref circuit-formulations-and-lowering);
this chapter retains the executed witnesses and their fixture-specific
counts.

The data and checks are recorded in
`experiments/generated/numerical-structure-witness.json`; the renderer is
`experiments/generate_numerical_structure_views.py`. This separation is
intentional: both structural views can be checked without pretending that
either is a solver-exported Jacobian.

Fill is not inevitable. The
[two-level topology chapter](@ref two-level-topology-and-nodal-projection)
proves a positive structural case: dense two-terminal conductor stamps over a
bus-level tree form a chordal scalar-support graph, and eliminating leaf-bus
coordinate blocks inward is a perfect elimination order with zero symbolic
fill. The warning here concerns arbitrary orderings, meshes, reductions, and
factor libraries; it should not hide structure that a declared model makes
exploitable.

The numerical witness now carries a crosswalk to
`experiments/generated/five-bus-typed-kron-witness.json`. That crosswalk uses
the non-pendant ``\ell`` elimination, whose fill edges are ``j-m`` and
``k-m``, and records the small boundary residual together with the recovered
``u``-branch limit observation. This ties the Schur-complement example to the
numerical-structure discussion without conflating fill edges with physical
assets or solver-private factorization output.

## A pinned numerical export

The running fixture provides a second, numerical witness through BMOPFTools'
passive and constant-``Z`` linearized ``Y``-bus exporters. In the exporter's
node order, the passive matrix has 20 rows and 166 nonzeros. The constant-``Z``
linearized matrix agrees with that passive matrix for this fixture. Realifying
the complex current relation gives a 40-by-40 real matrix with 664 nonzeros.
This is a coordinate embedding, not a promise that every complex invariant is
preserved: the complex Ybus is transpose-symmetric to numerical precision,
whereas the realified current-Jacobian embedding has a large transpose
residual. That residual is expected for a nonzero imaginary part: the block
matrix ``\mathcal R(Y)`` with diagonal blocks ``\Re Y`` and off-diagonal blocks
``-\Im Y`` and ``\Im Y`` is generally not symmetric. This is not a
round-off failure. Realification preserves the coordinate support and the
current relation, but symmetry claims must be stated in the representation in
which they are checked (the witness residual is approximately ``448.79``):

```math
\begin{bmatrix}\Re I\\ \Im I\end{bmatrix}
=
\begin{bmatrix}
\Re Y&-\Im Y\\
\Im Y& \Re Y
\end{bmatrix}
\begin{bmatrix}\Re V\\ \Im V\end{bmatrix}.
```

![Generated passive Ybus and realified current-Jacobian patterns.](../assets/ybus-jacobian-witness.png)

The ordinary 2-norm condition estimates are approximately
``2.49\times10^{17}`` (unscaled) and ``2.36\times10^{16}`` (after simple
row/column equilibration). Because both matrices are numerically rank
deficient (rank 18 of 20 at the witness tolerance), those finite values should
not be read as meaningful condition numbers: they are dominated by singular
values below the modelling tolerance. The witness therefore also reports the
rank-aware effective estimates ``\kappa_{\mathrm{eff}}=\sigma_1/\sigma_{18}``
and its equilibrated counterpart. These are diagnostic, not universal
constants: they depend on units, scaling, norm, rank tolerance, and the
chosen fixture. Pure row and column permutations preserve singular values,
so they preserve the exact 2-norm condition number and a ratio of the same
selected singular values. Ordering can change sparse-factorization fill,
pivoting behavior, runtime, and floating-point estimation details; these are
algorithmic effects, not a change in the exact spectral condition number.
For this export the effective estimates are approximately
``6.50\times10^8`` and ``1.13\times10^7`` after equilibration. A solver must
account for reference and grounding structure rather than treating any of
these numbers as a graph invariant.

The complete export, including node order, nonzero entries, checks, and the
linearization convention, is recorded in
`experiments/generated/ybus-jacobian-witness.json`. Its generator and renderer are:

```text
experiments/run_ybus_jacobian_witness.jl
experiments/render_ybus_jacobian_view.py
```

This is a pinned
linear current/Jacobian witness; it is not yet a nonlinear OPF KKT Jacobian or
an independent-solver comparison.

## Nonlinear decision Jacobian and KKT fill

The next witness adds the nonlinear term that makes the parallel-line warning
decision relevant. For a fixed complex endpoint voltage ``U`` and member
currents ``I_1,I_2``, the residual includes

```math
S(U,I_1,I_2)-\alpha S_0
  = U(I_1+I_2)^*-\alpha S_0.
```

The source formulation retains two explicit current laws and two current
vectors. The aggregate formulation replaces them by one summed current law.
At the recorded operating point both residuals are exactly zero, but their
finite-difference Jacobians and KKT patterns differ:

For avoidance of a common counting error, the source witness has two complex
member-current coordinates, represented as four real variables, in addition to
the three retained real coordinates. It therefore has seven real source
variables; the aggregate witness has five real variables. The reduction removes
two real variables (one complex current), not eight. The source KKT system has
13 rows and columns because it adds six residual/constraint multipliers; that
KKT dimension is a different count from the number of primal variables.

![Nonlinear source and aggregate KKT sparsity and fill witness.](../assets/nonlinear-kkt-witness.png)

| formulation | residual Jacobian | KKT dimension | natural fill | constraints-first fill |
| --- | ---: | ---: | ---: | ---: |
| two explicit members | ``6\times7`` (26 nonzeros) | 13 | 15 | 21 |
| summed member current | ``4\times5`` (16 nonzeros) | 9 | 6 | 10 |

The fill counts are symbolic graph counts, not floating-point factorization
times. They show why an ordering is part of a numerical certificate: the same
KKT graph has different fill under different elimination orders. The source
and aggregate models also have different graphs, so a smaller KKT system does
not by itself establish decision equivalence.

The complete finite-difference and symbolic-fill artifact is
`experiments/generated/nonlinear-kkt-witness.json`, regenerated by
`experiments/run_nonlinear_kkt_witness.jl` and
`experiments/render_nonlinear_kkt_view.py`. It is deliberately labelled a
nonlinear decision witness rather than a solver-internal Ipopt KKT export. A
package-level crosswalk now binds it to the BMOPFTools Ybus witness, while
actual solver-internal factorization diagnostics remain a separate boundary.

### Package-level diagnostics crosswalk

The generated `solver-diagnostics-crosswalk.json` composes the two witnesses
without pretending that either is a production solver export. It retains the
physical node/terminal order, the BMOPFTools passive and constant-``Z`` Ybus,
the realified current Jacobian, the finite-difference nonlinear residual
Jacobian, and the symbolic KKT graph under two declared orders. In the source
formulation, for example, the natural and constraints-first orders produce
different fill counts, so the crosswalk records ordering as part of the
diagnostic identity.

The crosswalk also exercises the public
`BMOPFTools.opf_checked_kkt_factorization` callback on a staged OPF context. The
probe accepts a regular matrix and rejects a near-singular one. This is a
checked callback boundary. A minimal parameterized OPF now passes that callback
through DiffOpt: the forward sensitivity agrees with a central finite
difference to the recorded tolerance, and the KKT diagnostic is accepted. The
adapter also captures the matrix passed to the callback, recording its
dimension and nonzero count, alongside the JuMP variable and constraint order
used to account for its rows and columns. Four additional callback rows remain
outside that declared JuMP block, so they are retained as an explicit
DiffOpt/solver-internal boundary rather than silently assigned a physical
label. The crosswalk still records
`solver_internal_kkt_export = false` because solver-provided row labels,
scaling, linear-solver choice, pivot or inertia data, and factorization
statistics are not yet exported as a source/target comparison.

The same witness records BMOPFTools' differentiability report: inequality
counts, active, near-active, weakly-active, and violated labels, minimum
inactive slack, and qualifications. In this deliberately unconstrained
fixture the inequality count is zero. The report's `ready` flag is state
provenance for the selected local solve, not a proof of LICQ, strict
complementarity, second-order sufficiency, global optimality, or branch
stability.

The crosswalk now also builds a regular JuMP mirror and records its native
affine/quadratic variable-support count alongside a separate
`JuMP.NLPEvaluator` view. This gives an executable constraint-row/nonzero
summary for the model-level derivative graph (23 supported variable entries in
the current 19-row fixture), while leaving
`native_nlp_export_is_solver_internal = false`: it is not Ipopt's private KKT
ordering, pivoting, inertia, or factorization export.

For a deliberately narrow parallel-line fixture, the crosswalk also compares a
two-member source against a single 0.25 Ω equivalent member. The tested voltage
sensitivity is preserved, while the captured KKT matrix grows for the explicit
source. The native JuMP support count changes as well, so the distinction is
visible before any solver-private factorization. This is evidence that an exact
electrical scalar equivalent can still change solver structure; it is not a
general AC or multiconductor reduction certificate.

### Numerical evidence boundary

The three numerical artifacts answer different questions and should not be
collapsed into one solver claim:

| Artifact | What is measured | What it does not establish |
| --- | --- | --- |
| structural witness | incidence, dependency, and symbolic fill edges | numerical derivative values or solver performance |
| `Ybus`/Jacobian witness | pinned passive and constant-``Z`` matrix patterns, rank, and conditioning diagnostics | nonlinear OPF sensitivities, active-set stability, or factorization timings |
| nonlinear KKT witness | finite-difference residual structure and symbolic fill under two declared orders | Ipopt's internal derivative graph, linear-solver pivoting, or global optimality |
| solver-diagnostics crosswalk | shared node/order provenance, a checked-KKT callback probe, a DiffOpt sensitivity cross-check, and JuMP ordering metadata | an exported source/target solver KKT comparison, solver-native row labels, or ordering/factorization metadata |

An actual solver diagnostic would need to bind the exported derivative rows and
columns to the source/target variable order, record scaling and tolerances,
identify the linear solver and ordering, and retain the factorization or
inertia report. Until that export exists, the chapter's KKT language is a
symbolic comparison, not an implementation claim about a production solver.

## Elimination and fill-in

Partition a sparse matrix by retained variables ``B`` and eliminated variables
``I``. The Schur complement is

```math
\mathbf S
 = \mathbf A_{BB}
   -\mathbf A_{BI}\mathbf A_{II}^{-1}\mathbf A_{IB}.
```

Even when ``\mathbf A`` is sparse, ``\mathbf S`` can be dense on the neighbours
of ``I``. In the symbolic graph, eliminating a vertex connects its remaining
neighbours into a clique. The extra nonzeros are **fill-in**. The same
mechanism appears in [Kron reduction](@ref kron-ward-opti-kron): preserving a
boundary relation does not preserve sparsity, asset identity, or the cost of a
subsequent solve.

The order of elimination matters. For a fixed matrix, two orders can have the
same exact Schur complement but different intermediate fill, memory use, and
factorization time. A certificate that reports a reduction should therefore
record at least:

| numerical field | required meaning |
| --- | --- |
| `ordering` | symbolic elimination or factorization order |
| `nnz_input`, `nnz_factor`, `nnz_fill` | structural nonzero counts under that order |
| `rank_guard` | rank/invertibility test for eliminated blocks |
| `conditioning` | estimate for the retained and eliminated solves |
| `recovery_cost` | work/storage needed to reconstruct omitted variables |

These fields are properties of a compiled numerical problem, not of a simple
graph in isolation.

## [A coverage table before a feasibility verdict](@id verification-coverage-lesson)

**Predict.** Two independent feeders each have a 10 V ideal source, a 1 Ω
series resistor and a 1 S shunt to earth at the receiving terminal. In each
feeder, the receiving voltage is 5 V and the line current is 5 A. If the two
reported source currents change to 6 A and 4 A, does checking total power detect
the corruption?

For either feeder, direct substitution gives

```math
10-5=1\cdot5,\qquad I_{\mathrm{shunt}}=1\cdot5=5\ \mathrm A.
```

The source supplies 50 W; the line and shunt each absorb 25 W. With two feeders,
the original source total is 100 W. The corrupted source currents still give
``10\cdot6+10\cdot4=100`` W, so aggregate power agrees. But the signed KCL
residuals at the two source terminals, taking outgoing current as positive,
are ``5-6=-1`` A and ``5-4=1`` A. Each violates a ``10^{-6}`` A acceptance
tolerance. Updating the reported source powers to 60 W and 40 W does not repair
those local equations.

This is a concrete use of claims `NUMERICAL-004` and `NUMERICAL-005`: a supplied
residual bundle and a solver status cannot replace recomputation with explicit
coverage. The [zero-voltage lesson](@ref zero-voltage-kcl) gives a second
failure mechanism: at an exactly grounded terminal a missing 1 A earth reaction
can be invisible even to *local* power balance. A perfect ground fixes voltage;
its reaction current must still be accounted for in a current audit.

### What was evaluated, and what was reconstructed?

For an inline series-line model, an evaluator can read the authored matrix
entries and check

```math
r_V=V_f-V_t-ZI_f,\qquad r_{I,\mathrm{line}}=I_f+I_t,
\qquad r_{I,b}=\sum_{\text{outgoing devices}}I-\sum_{\text{injections}}I.
```

These are distinct observations with distinct units and tolerances. The receiving
terminal map determines where ``I_t`` enters KCL, even when result rows use the
sending conductor's label. A limit check must evaluate ``|I_f|``, ``|I_t|`` and
any declared ``|V_f\overline{I_f}|`` / ``|V_t\overline{I_t}|`` bounds at their
respective endpoints. Equality with a bound passes within the declared tolerance;
a negative or malformed declared rating is not a zero limit violation.
An absent optional rating means no such constraint was declared.

For a shunt with no independently supplied current, computing ``I=YV`` constructs
a contribution to KCL. Reporting ``I-YV=0`` as an independent successful test
would merely compare the calculation with itself. Label it **reconstructed**.
A missing source current instead makes the affected audit **unassessed**; no
residual has been measured. These categories should survive JSON serialization.

### Package candidate and the running-network boundary

The package-owned `audit_linear_solution` candidate implements this small domain
without calling the model builder, `line_yprim`, Ybus, or the result profiler.
It shares the native SI input schema, result labels and arithmetic libraries.
That is independent equation evaluation, not independent parsing, a second
physical model, or measurement validation. The candidate's exact local revision
is recorded in `experiments/integration/linear-audit-candidate.json`; it is
**not included in the published integration pin** and is not exposed by MCP.
The companion is `experiments/lessons/verify_linear_coverage.jl`, with execution
instructions in the repository's `experiments/integration/README.md`.

The analytic tiny circuit and its native-coordinate solve pass; the
cancelling-current mutation fails, and removing a required current returns an
indeterminate result. The companion also records a solve using default per-unit
scaling, evaluated at the **same physical tolerances**. In the local candidate
run, that solver reported `LOCALLY_SOLVED`, but the two receiving-node KCL
residuals were about ``4.72\times10^{-4}`` A, exceeding the ``10^{-6}`` A audit
tolerance. The native-coordinate solve passed without relaxing the audit.
This is a diagnostic observation for this tiny case and environment, not a claim
that per-unit scaling is generally worse. The companion records the comparison
without requiring every future solver run to fail the same way. On the running
network, the candidate produces the following bounded coverage:

| Running-network obligation | Candidate evidence |
| --- | --- |
| Four coupled series-line voltage/current relations | Eight directly evaluated equation checks |
| Both-end line current limits | 30 conductor-end checks; not transformer or switch ratings |
| Line loss identity | Four checks from terminal currents and voltages |
| Two fixed earth shunts | Current contributions reconstructed directly from entries |
| Two declared perfect grounds | Zero-voltage conditions checked; reported ground reactions consumed |
| Loads, generator, switch and n-winding transformer | Device equations unassessed |
| Source with neutral return; bus voltage bounds | Unassessed in this first domain |
| 26 bus-terminal KCL rows and network power | Unassessed because current contributions are incomplete |
| Objective, optimality and physical adequacy | Not established |

The audit contains 42 unassessed rows. That number counts obligations, not 42
missing devices or 42 independent experiments. The implementation conservatively
suppresses every KCL verdict when any device current contribution is unassessed;
local line checks remain available. A later implementation may propagate missing
coverage by incidence, but must first demonstrate that its incidence inventory
is complete. A failed evaluated check must also remain visible when other rows
are unassessed.

### Extending coverage without changing the older API

The separate candidate `audit_solution` adds default-role source neutral returns
and signed per-phase source P/Q limits,
implicit source grounding, WYE/`SINGLE_PHASE`/DELTA constant-power load equations,
fixed ideal switches, bounded WYE/`SINGLE_PHASE` and cyclic DELTA generator injections/coil limits,
bus and branch angle/magnitude bounds, three-phase sequence/VUF limits and
bounded transformer equations. It retains recognized generator/source prices and
transformer `s_rating` as declarations, without turning them into physical limits
or objective certificates. The component sections below describe how that
coverage was added; their intermediate counts precede the final cost-scope trace.

The same default running-network result now has **zero unassessed rows** but
**three failed generator active-power upper bounds**. Their excess is about
0.00997 W each, above the unchanged 1e-6 W audit tolerance. All 26 terminal KCL
rows and aggregate power pass. A separate tighter native solve of the unchanged
input passes the scoped electrical audit. Both results and solver settings are
retained by the companion. The [cost-scope lesson](@ref generator-cost-scope-audit)
explains why the recognized price declaration opens these checks without
certifying the selected objective, objective value, optimality or custom model.
The 42-row table above remains the older `audit_linear_solution` coverage.

Source-return and device-terminal currents are reconstructed from explicit
connection maps; each earth reaction is consumed once. The switch has a checked
closed-voltage relation and four conductor current caps. The winding-list
transformer has checked coil equations, leakage and current caps; `s_rating`
remains metadata. The running voltage declarations have 28 phase-earth rows,
four neutral-earth caps and six phase-pair bounds. No input fields or nonzero
residuals are removed to obtain coverage. The
[delta coil lesson](@ref delta-coil-current-lesson) explains why successful KCL
still does not replace individual device equations.

### A switch needs a state law and a conductor limit

A fixed closed ideal switch requires equal voltages at its ordered endpoint
pairs; its nonzero current is determined by the surrounding circuit. A fixed
open switch instead requires zero current, with no voltage equality. The package
checks both domains against small native solves, including an open switch
between separately supplied 10 V and 7 V sides. Missing reported open-switch
current remains missing evidence; the checker does not fill in a passing zero.

The companion's closed two-wire fixture uses different endpoint labels and a
10 V, ``10+2\mathrm j`` VA load. The phase current is ``1-0.2\mathrm j`` A,
with its opposite returning through the neutral. At zero neutral voltage,
neutral apparent power is zero. Changing only the neutral current rating from
1.1 A to 0.5 A therefore creates a violation of approximately 0.5198 A while all
KCL rows, aggregate power and the neutral's zero apparent-power limit still
pass. This is the [zero-voltage current/power distinction](@ref zero-voltage-kcl)
applied to a conductor limit. Changing the limit does not change the supplied
operating point; it changes whether that point is admissible.

The switch result reports one current per from-side conductor. The to-side
current is its reconstructed opposite, with the to-side terminal map retained;
this is not a second independent current measurement. The candidate checks
finite nonnegative rating arrays in that order. Malformed or infinite ratings,
unknown controls and unrepresented device semantics remain unassessed. The
scope is static supplied-state verification, not switching optimization,
interruption physics or protection coordination.

**Transfer exercise.** Keep the two equal-voltage source currents at 6 A and 4 A,
but remove the second source's current field. Can the evaluator report zero
aggregate error because the first source is present? **Check your reasoning:**
no. A required term is unknown. The aggregate residual is null and its coverage
is unassessed; it cannot be computed by substituting zero. Finish the supported
model inventory before interpreting a small norm as feasibility evidence.

The [solution-multiplicity lesson](@ref unintended-solution-multiplicity)
separates additional admissible circuit roots, continuous current modes and
spurious roots introduced by a lost equation. It also distinguishes local
optima from the globally preferred branch.

## Solver behaviour and decision margins

For a constrained decision problem, solver behaviour is part of the evidence
but not the preservation theorem. A reduced model may converge faster because
it has fewer variables, or slower because it has denser and more ill-conditioned
blocks. A feasible point can also be numerically ambiguous when a constraint
margin is comparable with the estimated forward error.

A termination label such as `LOCALLY_SOLVED` or `OPTIMAL` records what the
algorithm reports under a particular solver interface and tolerance. It is not
an independent recomputation of the returned primal point. A scientific use of
that result must separately name and check the relevant evidence: finite
numeric values, model equations, declared bounds, device and network residuals,
recovery obligations, and the level of optimality actually supported. Missing
checks remain missing even when the status string sounds successful.

Start with the [zero-voltage KCL lesson](@ref zero-voltage-kcl) before using a
small power-balance residual as feasibility evidence. At each terminal,
``r_S=V\overline{r_I}`` loses its current information at zero voltage and scales
it by ``|V|`` elsewhere; a total-network power sum can additionally hide
opposite nodal errors. The running-network verification script checks line
recovery and package profile quantities, but does not thereby supply an
independent all-device nodal KCL audit.

This separation also works in the other direction. A status that does not
claim feasibility is not evidence that a candidate primal point passed an
independent validator, and a narrowly validated primal point does not upgrade a
local solver result into a global optimum. Status, primal validation, and
optimality evidence are distinct fields of a solution certificate.

For a scalar inequality ``g_k(y,u)\le 0``, define the signed margin

```math
m_k = -g_k(\widehat y,\widehat u).
```

If ``e_k`` is a declared bound or estimate for the error in that constraint,
classify the result as:

```math
\begin{array}{ll}
\text{certified feasible} & m_k>e_k,\\
\text{numerically ambiguous} & |m_k|\le e_k,\\
\text{certified violated} & m_k<-e_k.
\end{array}
```

This is deliberately stronger than reporting ``g_k\le 0`` at printed
precision. The same classification applies to decision comparisons: if two
objectives or tap choices differ by less than the propagated numerical error,
the certificate should not claim a unique optimum.

!!! warning "Decision-model consequence"
    A reduction that preserves a boundary voltage to tolerance may still change
    the active member limit, the selected switch state, or the winning discrete
    decision. Record the decision margin and the recovery error for every
    claimed decision-preservation result.

## What a transformation certificate should expose

The numerical fields extend the general [preservation contract](@ref preservation-contracts):

```math
\mathcal N = (
\text{coordinates},\text{scaling},\kappa,\eta,\text{dependency graph},
\text{ordering},\text{fill},\text{recovery cost},\text{decision margins}
).
```

An exact electrical map may therefore be computationally unattractive, while
an approximate map may be useful if its error and decision domain are explicit.
The running network's six generated views should eventually carry this record
alongside their source maps; the current fixture records the source maps and
solver outcomes but does not yet claim a complete cross-solver conditioning
study.

## Scope and open work

This chapter gives definitions and reporting requirements, not a universal
solver benchmark. The next executable tranche should compare the running
multiconductor network and its five-bus quotient under a pinned ordering and
coordinate convention, report ``Y``/Jacobian sparsity and fill-in, and test
whether recovered current and rating margins remain decisive after reduction.


### [Generator dispatch and voltage-bound applicability](@id generator-voltage-audit)

A reported dispatch inside a power box is not enough: recompute power using the
correct connection voltage and supplied current. The local candidate companion
now includes a package-owned 10 V example with a ``10+2\mathrm j`` VA load,
``4+1\mathrm j`` VA generator injection and ``6+1\mathrm j`` VA source injection.
The currents are respectively ``1-0.2\mathrm j``, ``0.4-0.1\mathrm j`` and
``0.6-0.1\mathrm j`` A. Their signs and explicit neutral returns close KCL.
Equal lower/upper generator P/Q bounds fix the native comparison point; this
example does not claim to optimize dispatch or generation cost.

**Predict.** If a result reports 3 W but voltage and current imply 4 W, can a
3 W upper bound be certified? No. The independent evaluation detects both the
1 W report discrepancy and the 1 W bound violation. The report is evidence to
check, not a substitute for the defining power relation.

| Changed evidence or declaration | Expected result | What remains checked |
|:--|:--|:--|
| Original analytic and native points | Passed within this small supported model | Powers, limits, voltages and KCL |
| Forged 3 W report and 3 W upper bound | Failed | Recomputed power is 4 W |
| Return-current cap tightened to 0.4 A | Failed | KCL and aggregate power still pass |
| Generator current omitted | Indeterminate | KCL and aggregate power unassessed |
| 9 V upper bound declared at the 10 V source terminal | Indeterminate | Native bound application is skipped; source equation still checked |

The phase and return current magnitudes are ``\sqrt{0.17}≈0.4123`` A. A 0.5 A
phase cap passes while a 0.4 A return cap fails. With multiple WYE phases the
return magnitude is ``|\sum_k I_k|``, not ``\sum_k|I_k|`` and not any individual
phase magnitude. For example, two in-phase 1 A injections give a 2 A return;
opposite injections cancel. At zero coil voltage a power identity can still
hide nonzero current, so current limits and KCL remain separate checks.

For the finite native WYE/`SINGLE_PHASE` domain, generator power uses the explicitly
mapped coil voltage. Omitting the neutral from a WYE generator map does not
borrow the bus neutral. A two-terminal `SINGLE_PHASE` generator uses its ordered
pair, which may also be phase-to-phase. The later DELTA-generator section
extends this scope: the load's two-terminal DELTA convention must not be copied
into another device family without checking that family's executable contract.

Bus-voltage limits ask a different coordinate question. The supported
`v_min/v_max` arrays bound phase-to-**earth** magnitude in non-neutral terminal
declaration order. Moving the neutral changes a phase-neutral generator power
without changing the phase's earth voltage. Tests use such a perturbed candidate
to distinguish those observations; the separate switch-voltage check rejects
that candidate. An unchanged bus-bound result is not a certificate for it.

The native builder skips ordinary bus bounds at source-fixed and perfectly
grounded terminals. The candidate records those bound obligations as
**unassessed**, even if their declarations happen to agree with the source.
For the 10 V source and 9 V upper bound, a native source equation does not enforce
the declared bound. This slice does not silently label it passed, reinterpret the
bound as phase-to-neutral, or remove its array index. Other bound families,
nonfinite/malformed arrays, malformed generator prices/controllers and unsupported transformer checks
retain explicit coverage limits. Known current contributions remain usable when
only limit/report evidence is missing; missing currents cannot be filled in from
power by dividing by voltage.

Reproduce the example through `experiments/lessons/verify_linear_coverage.jl`
using the exact clean local candidate environment in
`experiments/integration/README.md`. The output contains native inputs/results,
all mutation verdicts, candidate revision/tree and fixture/example/environment
hashes. The published package pin and execution MCP surface have not changed.
This is an implementation comparison and a small teaching witness, not independent
scientific review or a complete running-network feasibility certificate.

**Transfer exercise.** With total real current 2 A and two phase currents each
1 A, replace the return limit by 1.5 A. Both phase caps of 1 A pass; the return
fails by 0.5 A. Reverse the second phase current: the return then passes, but
local KCL must be reevaluated against the surrounding circuit. A generator-only
rating check does not establish a network solution.


### [Transformer series currents are not all terminal currents](@id fixed-transformer-audit)

The next local candidate slice covers one explicit terminal pair on each side
of the native `single_phase` transformer, with fixed tap, finite leakage and
secondary excitation. It complements the [transformer-port lesson](@ref ideal-transformer-port-lesson)
by checking supplied native current observations as well as equations. It does
not by itself cover the running network's `n_winding` device; the later
winding-list and rating-metadata slices supply that distinct coverage.

Let ``U_f,U_t`` be oriented coil voltages and ``I_f,I_t`` the supplied series
currents, both positive into their winding. For this native tap convention,

```math
N_0=V_{\mathrm{nom},f}/V_{\mathrm{nom},t},\qquad
N=N_0\tau,\qquad Z'=Z_t+Z_f/N_0^2,
```

```math
U_f-NU_t=N^2Z'I_f,\qquad NI_f+I_t=0.
```

The fixed multiplier ``\tau`` changes the effective ratio **and** the
from-referred leakage ``N^2Z'``. Replacing that leakage with ``Z_f+N^2Z_t``
agrees at ``\tau=1`` but generally differs away from it. This is a declared
parameterization of the implemented equivalent circuit, not a universal law
for every transformer tap or leakage model. Zero leakage is handled directly
as an ideal voltage relation; no small impedance is inserted.

The excitation admittance ``Y`` lies across the secondary coil. Consequently,

```math
I_{t,\mathrm{terminal}}=I_t+YU_t,\qquad
S_{\mathrm{terminal}}=U_f\overline{I_f}
 +U_t\overline{I_t+YU_t}
 =Z'|I_t|^2+\overline Y|U_t|^2.
```

The last equality follows from the voltage and current relations and is
checked separately. The signed terminal returns enter KCL. The excitation
current is reconstructed from ``Y,U_t``; this is not an independent excitation
measurement. Native `fr/1`, `to/1` currents and their `cm` values refer to the
**series** currents, while `i_max_to` bounds the secondary **terminal** current.
The positive nameplate `s_rating` bounds from-coil apparent power.

**Predict.** Does a reported secondary `cm` above `i_max_to` necessarily violate
the implemented terminal-current limit? It does not: the two fields can describe
different observations when excitation is present.

The fixture uses SI values ``N_0=2``, ``\tau=5/4``,
``Z_f=1/2+\mathrm j/4`` Ω, ``Z_t=1/8+\mathrm j/16`` Ω and
``Y=1/20-\mathrm j/40`` S. It gives ``Z'=1/4+\mathrm j/8`` Ω and the exact
operating point

| Quantity | Value |
|:--|:--|
| Primary coil voltage | ``685/64+5\mathrm j/32`` V |
| Secondary coil voltage | 4 V |
| Primary series current | ``0.4-0.1\mathrm j`` A |
| Secondary series current | ``-1+0.25\mathrm j`` A |
| Excitation current | ``0.2-0.1\mathrm j`` A |
| Secondary terminal current | ``-0.8+0.15\mathrm j`` A |
| Load power | ``3.2+0.6\mathrm j`` VA |
| Transformer loss | ``341/320+341\mathrm j/640`` VA |

The secondary series magnitude is approximately 1.031 A; the terminal magnitude
is approximately 0.814 A. A 0.9 A terminal cap passes. Tightening only that cap
to 0.8 A fails while KCL and aggregate power remain satisfied. Replacing the
series-current report with the terminal current instead fails current coupling
and KCL. The distinction concerns the specific equivalent-circuit observation;
it does not, by itself, identify all physical winding hot spots or thermal limits.

The package-owned example also retains a missing series current and an
adjustable-tap declaration as indeterminate cases. Internal grounding, larger
winding maps, other transformer subtypes, alternate excitation encodings and
internal per-unit coordinate fields remain outside this slice. A two-terminal
map containing a neutral uses that neutral as the return regardless of its
array position; a map with two phase terminals uses their declared orientation.
Tests distinguish consistent relabelling from reversing only one physical coil.

Run the same source-bound `verify_linear_coverage.jl` companion using the local
candidate environment in `experiments/integration/README.md`. It includes
`examples/fixed_transformer_audit.jl`, the analytic fixture (checked numerically with explicit tolerances), a native
solve and the mutation evidence. It retains solver and primal status and gates
acceptance on the independent audit. The successful native point is not a proof
of uniqueness, global optimality, or general transformer coverage. The published
package pin and execution MCP route remain unchanged.

**Transfer exercise.** Set both leakage impedances and excitation to zero,
retain ``N=2.5`` and the same 4 V load point. The primary voltage becomes 10 V,
primary current ``0.32-0.06\mathrm j`` A, and loss zero. Omitting those zero-valued
optional fields gives the same native default model. Now restore excitation
without updating the reported currents: the old ideal solution must be checked
again against the restored current and power relations.

### [Coupled winding leakage and the observation being rated](@id winding-list-audit)

The [preceding two-port example](@ref fixed-transformer-audit) does not determine
the rating semantics of a winding-list model. The next local candidate checks
two or three WYE windings with one phase-neutral coil each, fixed nominal
ratios, explicit pairwise short-circuit reactances, and excitation on winding 2.
It uses the native `n_winding` equations, independently evaluated in SI units.
This smaller witness does not by itself assess the running network's
multiphase arrangement; the later slices address incidence and rating metadata
separately. Other unsupported declarations remain explicit obligations.

Let ``U_k`` denote phase-minus-neutral coil voltage and ``I_k`` bare coil
current, positive **into** the transformer at every winding. Define

```math
N_k=V_{\mathrm{nom},k}/V_{\mathrm{nom},1},\qquad
j_k=N_k I_k,\qquad R_k=r_k/N_k^2.
```

Here ``r_k`` is in ohms on winding ``k``'s own voltage base; the supplied
pairwise ``X_{ab}`` values are already referred to winding 1. With
``Z_{ab}=R_a+R_b+\mathrm jX_{ab}``, form the coupled matrix

```math
(Z_B)_{ii}=Z_{1,i+1},\qquad
(Z_B)_{ij}=\tfrac12(Z_{1,i+1}+Z_{1,j+1}-Z_{i+1,j+1})\quad(i\ne j).
```

The current and voltage equations are

```math
\sum_{k=1}^{n}j_k=0,\qquad
U_1-U_k/N_k=-(Z_Bj_{2:n})_{k-1}\quad(k=2,\ldots,n).
```

The minus sign follows from using inward currents on **all** ports. For two
windings, ``j_2=-I_1`` turns it into the familiar positive source-current
voltage drop. For three windings, the nonreference currents are coupled through
the off-diagonal term. Replacing this matrix by independent two-port branches
generally changes the equations. Reordering windings requires reordering their
pairwise data, ratios and result labels; excitation attached to winding 2 also
makes its position part of the declared model.

The package fixture chooses ``N=(1,1/2,1/4)``,
``r=(1/4,1/16,1/64)`` Ω and
``(X_{12},X_{13},X_{23})=(1/2,3/4,3/4)`` Ω, giving

```math
Z_B=\begin{bmatrix}
1/2+\mathrm j/2 & 1/4+\mathrm j/4\\
1/4+\mathrm j/4 & 1/2+3\mathrm j/4
\end{bmatrix}\ \Omega.
```

With ``Y=1/32-\mathrm j/64`` S on winding 2, the analytic point is:

| Winding | Coil voltage (V) | Bare coil current (A) |
|:--|:--|:--|
| 1 | 10 | ``0.625-0.15625\mathrm j`` |
| 2 | ``4.82421875-0.10546875\mathrm j`` | ``-1+0.25\mathrm j`` |
| 3 | ``2.439453125-0.04296875\mathrm j`` | ``-0.5+0.125\mathrm j`` |

Winding 2's terminal current is
``I_2+YU_2=-0.85089111328125+0.17132568359375\mathrm j`` A.
Its magnitude is approximately 0.868 A, whereas ``|I_2|≈1.031`` A.
**Predict:** would a 0.95 A limit pass? In this native winding-list model,
per-winding scalar `i_max` bounds the **bare coil** current, so it fails.
A terminal-current reading below 0.95 A cannot certify that coil rating.
Similarly, per-winding scalar `s_max` bounds ``|U_k\overline{I_k}|`` for this
single-coil slice. These are different observation contracts from the preceding
`single_phase` secondary terminal-current cap. Neither convention alone
identifies every physical thermal hot spot.

Terminal power supplies an additional consistency check:

```math
\sum_k U_k\overline{I_{k,\mathrm{terminal}}}
 =j_{2:n}^{\mathrm H}Z_Bj_{2:n}+\overline Y|U_2|^2,
\qquad
\Re(j_{2:n}^{\mathrm H}Z_Bj_{2:n})=\sum_k r_k|I_k|^2.
```

The total loss at the fixture point is approximately
``0.901948+0.542283\mathrm j`` VA. The example checks both these identities,
individual voltage equations, ampere-turn balance, reported magnitudes/powers,
ratings and local KCL. A plausible aggregate loss cannot repair a wrong winding
current, voltage referral, or local balance.

Run `experiments/lessons/verify_linear_coverage.jl` with the exact clean local
candidate described in `experiments/integration/README.md`. It invokes the
package-owned `examples/winding_list_audit.jl`, binds its fixture and source
hashes, and retains the native solve alongside analytic and mutation evidence.
Wrong referral and replacing a bare-coil report by terminal current fail.
Missing coil current or pairwise reactance stays **indeterminate**, with network
KCL/power unassessed. Explicit zero reactances remain valid at the ideal boundary;
omitted entries do not become measured zeros. The successful solve establishes
neither uniqueness nor global optimality. Published integration and execution
MCP availability remain unchanged.

**Transfer exercise.** For lossless pairwise reactances
``X_{12}=X_{13}=3`` Ω and ``X_{23}=10`` Ω, the reactance matrix is

```math
\begin{bmatrix}3&-2\\-2&3\end{bmatrix},
```

with eigenvalues 1 and 5 Ω.
Its equivalent reference star arm is negative, yet this matrix is positive
definite. A negative star arm is not a negative diagonal reactance. Conversely,
positive diagonal entries alone do not establish positive semidefiniteness.
The candidate's point audit does not certify magnetic realisability: passing
circuit residuals and checking the admissibility of constitutive data are
separate obligations. The package's input analysis provides the separate
matrix diagnostic. Multiphase/DELTA windings, taps, internal grounding and
internal per-unit fields remain outside this audit slice.

### [An adequate winding total can hide an overloaded phase](@id multiphase-winding-audit)

The next local candidate extends the [winding-list audit](@ref winding-list-audit)
to matched one-, two-, and three-phase WYE windings. This is an extension of a
specific executable model: each winding has an explicit neutral, and the coil
counts agree. The native model pairs coils by position in their phase lists,
after removing the neutral. A terminal label identifies a local terminal; it
does not automatically define a cross-winding phase correspondence.

For coil position ``p``, the same current and voltage equations hold separately:

```math
\sum_k N_k I_{kp}=0,\qquad
U_{1p}-U_{kp}/N_k=-(Z_Bj_{2:n,p})_{k-1}.
```

The model does not add mutual leakage between different phase positions.
Excitation acts across each winding-2 coil. Its phase terminal currents and
neutral return, oriented out of the bus into the transformer, are

```math
T_{kp}=I_{kp}+\mathbf{1}_{k=2}YU_{2p},\qquad
T_{k,n}=-\sum_{p=1}^{m}T_{kp}.
```

Losses sum the preceding per-coil identities over ``p``. The neutral is the
negative **complex sum**, not the sum of magnitudes. Opposite current errors in
two phases can leave this neutral sum unchanged while violating their individual
ampere-turn equations and local phase KCL. Likewise, a winding neutral current
is not an earth-reaction measurement. The computational fixture has nonzero
neutral currents and separately supplied zero earth reactions.

**Predict.** A winding has a 12 VA rating, with three coil powers whose
magnitudes sum to less than 12 VA. Is it necessarily compliant with the native
winding-list limit? No: this implementation allocates equal shares,

```math
|U_{kp}\overline{I_{kp}}|\le S_{k,\max}/m\quad\text{for every }p.
```

That constraint bounds each **bare coil** before excitation is added to its
terminal current. It differs from either aggregate constraint
``|\sum_p U_{kp}\overline{I_{kp}}|\le S_{k,\max}`` or
``\sum_p|U_{kp}\overline{I_{kp}}|\le S_{k,\max}``.
Satisfying every allocated share implies both aggregate bounds; the converse
fails in general. This allocation rule describes the implemented limit, not a
universal thermal-rating rule for all physical transformers.

The package-owned `multiphase-winding.json` fixture retains the preceding
three-winding ratios, leakage matrix and excitation. Its source voltages are
``(10,-5-8\mathrm j,-5+8\mathrm j)`` V, and winding-2 bare currents are
``(-1+0.25\mathrm j,0.5+0.25\mathrm j,0.25-0.5\mathrm j)`` A.
Winding-3 currents are half these values; winding-1 currents are ``-5/8``
times them. Each set satisfies ampere-turn balance for ``N=(1,1/2,1/4)``.

| Coil position | Winding-2 voltage (V) | Apparent-power magnitude (VA) | Allocated 4 VA cap |
|:--|:--|--:|:--|
| 1 | ``4.82421875-0.10546875\mathrm j`` | 4.973879 | Fails |
| 2 | ``-2.46484375-3.89453125\mathrm j`` | 2.576506 | Passes |
| 3 | ``-2.39453125+3.96484375\mathrm j`` | 2.589267 | Passes |

The sum of magnitudes is approximately 10.139652 VA. Tightening only the winding
rating from 30 VA to 12 VA leaves equations, KCL and aggregate power balance
satisfied, but fails coil 1's limit. The native result's per-coil `s_max` must
also report the divided cap: 10 VA at the baseline, 4 VA in the tighter case.
Reporting 30 VA for every coil is a separate report-consistency error.

At the analytic point, the winding-2 neutral current is approximately
``0.251648+0.000549\mathrm j`` A and total transformer loss is approximately
``2.338756+1.314397\mathrm j`` VA. The native solve reproduces the voltages and
losses and passes the independent audit. That is evidence for this supplied
point, not uniqueness or global optimality. The neutral-current observation is
marked **reconstructed**; the audit does not invent a neutral-current limit or
an independent neutral measurement.

Use the same `verify_linear_coverage.jl` companion and exact local candidate
environment in `experiments/integration/README.md`. It invokes
`examples/multiphase_winding_audit.jl` and retains the analytic/native points,
unequal-phase overload, wrong cap report, phase-order corruption, missing coil
current and missing earth reaction. Tests also cover a two-phase case with exact
neutral cancellation and consistent phase permutations. Missing a required coil
current leaves network KCL/power **unassessed**. The next section extends the
incidence to DELTA; the separate rating-metadata trace below addresses
`s_rating`. Unmatched coil counts, taps and internal coordinates remain outside
the supported domain. This intermediate slice alone left the running network
indeterminate; the final price-scope trace below records its current verdicts.

**Transfer exercise.** For this point, the smallest equally allocated total
rating is ``3\max_p|S_{2p}|≈14.921637`` VA, rather than the 10.139652 VA sum.
At that rating coil 1 is exactly on its boundary. For two coils, repeat the
allocation using division by two, even if their currents cancel in the neutral.
Zero neutral current does not imply zero coil power or spare phase capacity.


### [DELTA line currents cannot reveal internal circulation](@id delta-winding-audit)

The [coil-incidence lesson](@ref delta-coil-current-lesson) distinguishes a
coil current from its terminal observation. The next local package candidate
applies that distinction to two/three-winding transformers. A supported DELTA
winding has exactly three distinct phase terminals and no neutral in its map;
other devices at the same bus may still use a neutral. Its ordered phases and
rotation define the directed coil pairs. For phase order ``(a,b,c)``, rotation
``+1`` gives ``(a,b),(b,c),(c,a)``; rotation ``-1`` gives
``(a,c),(b,a),(c,b)``. These are conventions relative to the declared order,
not standalone vector-group labels.

Let ``D`` have one row per coil, with +1 at its first terminal and -1 at its
second. The voltage/current pairing is

```math
U=Dv,\qquad I_{\mathrm{port}}=I_{\mathrm{coil}}+I_{\mathrm{exc}},\qquad
I_{\mathrm{line}}=D^{\mathsf T}I_{\mathrm{port}},\qquad
v^{\mathsf T}\overline{I_{\mathrm{line}}}
=U^{\mathsf T}\overline{I_{\mathrm{port}}}.
```

Excitation is present only on winding 2 in this native model. The independent
audit enumerates the pairs directly, then evaluates the same per-coil leakage
and ampere-turn equations as before. It reconstructs bus line currents with the
power-dual incidence and marks them **reconstructed**, without a residual or an
independent-measurement claim. WYE neutral-return rules do not apply to DELTA.

**Predict:** if the bare coil current is ``0.5-0.25\mathrm j`` A but the line
current at a is ``0.875-0.375\mathrm j`` A, does a native 0.6 A winding
`i_max` pass? In this implementation it does: that limit bounds each **bare
coil**, whose magnitude is approximately 0.559 A, rather than the approximately
0.952 A line current. The package-owned `delta-winding.json` fixture supplies
this finite-leakage DELTA/WYE point, with rotation -1, winding-2 excitation,
explicit internal currents and SI voltage/current reports. A native solve
agrees with the analytic point and passes the independent audit. The scalar
`s_max/3` allocation uses actual line-to-line coil voltage for DELTA.

Now consider the separate **ideal zero-leakage, zero-excitation** DELTA/DELTA
boundary. Both windings have equal nominal ratio, identical terminal voltages,
and the same rotation. A constant current on every coil lies in the kernel of
``D^{\mathsf T}``. Compare these two supplied internal states:

| Observation or check | Zero internal current | -1 A on each winding-1 coil; +1 A on each winding-2 coil |
|:--|:--|:--|
| Terminal voltages | Same supplied voltages | Same supplied voltages |
| Line currents at all six phase terminals | Zero | Zero |
| Per-coil ampere-turn and ideal voltage equations | Pass | Pass |
| Terminal KCL and total power | Pass | Pass |
| Six bare-coil limits of 0.75 A | Pass | Each fails by 0.25 A |

The two states have identical terminal observations but different coil-loading
verdicts. Even complete line-current measurements cannot recover this internal
circulation without additional information. The witness uses an ideal boundary:
adding positive winding resistance makes this particular circulating point
violate the voltage equation. It does not establish arbitrary circulation with
strictly passive leakage, magnetic realisability, or which state a solver selects.

**Inspect:** `examples/delta_winding_audit.jl`, invoked by the source-bound
`verify_linear_coverage.jl` companion, retains the finite analytic/native point,
rotation corruption, missing coil current, refused neutral-bearing map, both
ideal states and the six rating violations. Tests also construct mixed and
all-DELTA two/three-winding points from independent star-arm laws, exercise
excitation on DELTA winding 2, and distinguish consistent reindexing from a
changed connection. Missing an internal current suppresses network KCL/power
certification even when line currents could appear to close.

Neutral-bearing DELTA remains explicitly **unassessed**. Inspection of the
complete native build path found that validation rejects a DELTA map containing
a neutral before constraints are stamped; a rejection test records that boundary.
This audit
accepts only the three-terminal closed incidence above. Two-terminal DELTA,
unmatched coils, taps and internal coordinates also remain unassessed. The
rating-metadata trace below handles `s_rating` separately. Before the final
price-scope trace, the running network retained 28 unassessed obligations. The published package pin and execution
MCP surface are unchanged.

**Transfer exercise.** Cyclically reorder every winding's coil positions and
its current reports together: the verdict should remain unchanged. Then change
only `delta_roll` while keeping phase order and reports fixed: which coil voltage
and line-current equations change? Finally, explain why neither summing terminal
power nor setting an unavailable coil current to zero can certify its rating.


### [A retained rating field may declare no loading limit](@id winding-rating-metadata)

The [per-coil allocation example](@ref multiphase-winding-audit) required an
explicit loading constraint. A rating field can instead serve as an impedance
conversion base, a retained nameplate, or a native loading cap. Its name and
presence alone do not establish which role reaches the solved model.

For the native `n_winding` path reviewed here, top-level and per-winding
`s_rating` are **power-base/nameplate metadata**. Each winding's optional
`s_max` separately declares the total apparent-power cap, allocated equally
among its coils. This differs from the earlier `single_phase` recipe, whose
`s_rating` actually creates a from-coil loading constraint. A package-wide
"all transformer nameplates are enforced" inference is therefore unsafe.

The conversion trace also matters. PowerIO 0.11.6 converts source kVA into
winding rating metadata. Its BMOPF schema-0.1.0 emission retains the winding-list
record under `extras`; BMOPFTools restores it during normalization and preserves
the ratings without inventing `s_max`. Conversion uses rating bases to turn
percentages into ohms, with a package-owned correction for the imported winding
resistance convention. Once the supplied SI coefficients are fixed, editing
rating metadata alone does **not** rederive their ohmic values. The direct SI
audit evaluates those coefficients; it does not authenticate the earlier
conversion or infer an omitted equipment limit.

**Predict:** can a native solution pass while coil apparent power exceeds
`s_rating`? The package-owned `rating-metadata.json` witness uses the preceding
finite DELTA/WYE point with deliberately small rating metadata and separate
60 VA winding caps:

| Declaration or observation | Supplied value | Native role |
|:--|:--|:--|
| Top-level `s_rating` | 0.25 VA | Retained power-base metadata |
| Winding-1 / winding-2 `s_rating` | 0.5 / 0.75 VA | Retained winding nameplates |
| Each winding's `s_max` | 60 VA | 20 VA cap per coil |
| Tightened winding-2 `s_max` | 12 VA | 4 VA cap per coil; two supplied coils fail |

The baseline passes the native constraints and independent audit in SI,
system-base per-unit, and unequal local-base coordinates. That result says
nothing about the physical acceptability of exceeding the declared nameplates.
Changing only the rating metadata leaves the independently evaluated SI
electrical rows unchanged. In the local-base run, the native working top-level
rating is divided by winding 1's 100 VA power base, while the two winding caps
use their own 100 VA and 25 VA bases. This bookkeeping does not turn a retained
field into a constraint. Internal working dictionaries are outside the SI
audit's input domain.

**Inspect:** `examples/winding_rating_metadata.jl`, invoked by the exact-candidate
`verify_linear_coverage.jl` companion, preserves these points and the tightened
OPF/PF attempts. The latter return local infeasibility and fail the independent
point audit; the status alone is not a global infeasibility certificate. The
current native PF recipe retains nested winding `i_max`/`s_max`, so it also
retains this winding-list loading limit. A general "PF removes every operational
limit" inference would be wrong for this path.

A valid metadata observation has status **declared**, no residual, and
`enforced_as_limit=false`. It is not a passed equipment limit or an independent
nameplate measurement. Malformed metadata remains **unassessed**, while known
currents and checked violations remain visible. Missing an internal coil current
still suppresses network KCL/power; metadata cannot recover it.

The running-network input is retained intact. Its transformer equations,
incidence and declared current caps now pass; top-level `s_rating` is recorded
as metadata. Before the price-scope extension below, the audit retained 28
unassessed obligations: generator cost was outside scope and prevented a complete
current inventory. Physical adequacy, objectives,
external review, published integration and execution MCP exposure remain
separate obligations.

**Transfer exercise.** Identify which fields in an imported transformer were
used to convert percentage data, which are retained declarations, and which
actually register loading constraints. Then explain why adding `s_max` is a
modeling decision requiring evidence about the intended rating and observation,
rather than a repair justified merely by the existence of `s_rating`.


### [Phase-to-neutral bounds require the neutral phasor](@id phase-neutral-voltage-audit)

The preceding examples distinguish phase-to-earth voltage from device-current
observations. The next independent audit adds
finite `vpn_min`/`vpn_max` arrays for the actual phase-minus-neutral voltage.
These arrays have one entry per phase in the full bus declaration order,
excluding its default-role n/N neutral. They do not bound phase-to-earth voltage,
and a missing neutral role is not permission to substitute earth.

Consider a 10 V source with a 1 Ω phase conductor and a 1 Ω neutral conductor.
At the supplied 8 W load point, phase current is 1 A toward the load and neutral
current is -1 A in the same source-to-load orientation. Direct conductor drops
therefore give

```math
V_{q,x}=10-1\times1=9\ \mathrm V,\qquad
V_{q,n}=0-1\times(-1)=1\ \mathrm V,\qquad
U_{q,xn}=V_{q,x}-V_{q,n}=8\ \mathrm V.
```

**Predict:** would a 9 V phase-to-earth result establish compliance with a
phase-neutral lower bound of 8.25 V? It would not. The package-owned
`phase-neutral-voltage.json` fixture separates the observations:

| Quantity or obligation | Supplied value or bounds | Independent result |
|:--|:--|:--|
| Phase-to-earth voltage | 9 V, bounds 8.5–9.5 V | Pass |
| Neutral-to-earth voltage | 1 V | Required supplied state; no neutral limit inferred |
| Phase-to-neutral voltage | 8 V, bounds 7.5–8.5 V | Pass |
| Tightened PN lower bound | 8.25 V | Fail by 0.25 V |
| Tightened PN upper bound | 7.75 V | Fail by 0.25 V |
| Local KCL and total power at either bound mutation | Same supplied currents/voltages | Pass |

Source power is 10 W, the load consumes 8 W and the two conductor losses sum to
2 W. Closing that power balance does not erase either voltage-limit violation.
The native SI and system-base per-unit solves reproduce the supplied voltages
and pass the independent audit. A limited native attempt is retained with its
local termination and failed point audit; local infeasibility alone is not a
global infeasibility certificate, and a successful solve does not prove uniqueness.

For supplied complex voltages, the checked quantity is

```math
m_p=|V_p-V_n|,\qquad
e_{p,\min}=\max(0,\underline v_{pn,p}-m_p),\qquad
e_{p,\max}=\max(0,m_p-\overline v_{pn,p}).
```

Violations and tolerances are in **V**, not V². At the 8.25 V lower bound, the
squared-constraint violation is 4.0625 V² while the magnitude violation is
0.25 V; those numbers cannot share an unqualified tolerance. Subtract the
phasors before taking a magnitude: ``|V_p-V_n|`` generally differs from
``|V_p|-|V_n|``. A common shift of both phasors preserves this voltage
observation; separate source, grounding or earth-connected equations may forbid
that shift in the surrounding network.

A grounded neutral has its own obligation. A separately consistent fixture
changes the load to 9 W at 9 V, sets neutral-conductor current to zero and
supplies the corresponding earth reactions. It passes the native solve and
independent audit. The native builder may substitute zero for an ideal grounded
neutral in its bound expression. The audit instead uses the supplied neutral
phasor in the original voltage difference and checks grounding separately.
An inconsistent ground report is therefore a failed grounding obligation;
a missing neutral report stays unknown even when the neutral was declared
grounded. It is never filled in as zero.

**Inspect:** `examples/phase_neutral_voltage_audit.jl`, invoked by the exact
candidate `verify_linear_coverage.jl` companion, retains the analytic/native
points, both bound violations, grounded case, missing neutral, malformed array
and a source-fixed bound. Each checked PN row identifies its neutral reference,
full phase index, observed magnitude and bound. Tests also cover an unbalanced
three-phase circuit, consistent declaration reordering, upper-case neutral
labels, exact zero/equality boundaries and complex common shifts.

The native builder skips a grounded or source-fixed **phase** without shifting
later array indices. The audit leaves that phase's declared bound **unassessed**;
it does not report compliance merely because a source supplied its voltage.
A grounded **neutral** does not itself skip an applicable phase bound. When the
first phase is skipped, the next phase still uses bound entry 2. Tests inspect
native constraint identities as the object under test, while the independent
evaluator constructs neither observations nor residuals from those constraints.

Full finite nonnegative arrays and a supported neutral role are required.
Malformed or nonfinite bounds, conversion overflow/underflow and unknown
applicability remain **unassessed**, while otherwise known current contributions
and checked violations stay visible. Missing required neutral voltage suppresses
network KCL/power certification. Neutral-to-earth limits are covered below;
phase-to-phase, bus-angle, sequence and branch-end angle limits also follow. The
existing running network has no PN-bound declarations, so this family adds no
checks there. The cost-scope section gives its latest coverage and verdict. The published integration pin and execution MCP
surface are unchanged.

**Transfer exercise.** For ``V_p=4+6\mathrm j`` V and ``V_n=1+2\mathrm j`` V,
compute the phase-neutral magnitude and compare it with subtracting their
magnitudes. Then place a skipped grounded phase before this phase in
`terminal_names`: explain why its bound uses entry 2, and why deleting the
neutral result cannot be repaired by a grounding label or solver status.


### [Neutral-to-earth voltage does not determine neutral current](@id neutral-earth-voltage-audit)

A neutral-to-earth magnitude cap observes a different quantity from the
phase-to-neutral bounds above. The next candidate audit accepts an applicable
finite nonnegative scalar `vn_max` and evaluates

```math
m_n=|V_n|,\qquad e_n=\max(0,m_n-\overline v_n).
```

The reference is the model's earth coordinate. This voltage alone does not
establish a neutral-conductor current, earth-return path, electrode state,
touch voltage or protection adequacy.

**Predict:** does a neutral phasor whose real and imaginary components are both
within ±1 V comply with a 1 V magnitude cap? Consider a 10 V source, 1 Ω phase
and 2 Ω neutral conductors, with phase current ``0.5-0.25\mathrm j`` A toward
the load and the opposite current in the neutral. Direct conductor drops give

```math
V_{q,x}=9.5+0.25\mathrm j\ \mathrm V,\qquad
V_{q,n}=1-0.5\mathrm j\ \mathrm V,\qquad
U_{q,xn}=8.5+0.75\mathrm j\ \mathrm V.
```

The load consumes ``4.0625+2.5\mathrm j`` VA, the source supplies
``5+2.5\mathrm j`` VA and the two conductors dissipate 0.9375 W.
The package-owned `neutral-earth-voltage.json` witness separates the checks:

| Observation or obligation | Supplied value or bound | Independent result |
|:--|:--|:--|
| Neutral magnitude | ``\sqrt{1.25}\approx1.118034`` V | From complex neutral state |
| Scalar neutral cap | 1.5 V | Pass |
| Tightened neutral cap | 1 V | Fail by about 0.118034 V |
| Componentwise box | Real 1 V, imaginary −0.5 V | Both within ±1 V; insufficient for the cap |
| Phase/PN bounds, KCL and power at the bound mutation | Same supplied point | Pass |

Violations and tolerances are in **V**. The positive native cap is represented
by a normalized quadratic inequality; at a 1 V cap its excess is 0.25,
dimensionless. That solver expression and the 0.118034 V physical magnitude
excess require different tolerances. The independent evaluator uses the supplied
rectangular state and its own phasor norm, rather than a native residual or a
reported magnitude. Native SI and per-unit solves reproduce the scoped point.
A tightened native attempt is retained with local infeasibility and a failed
point audit; the termination alone is not a global infeasibility certificate.

Now replace the neutral conductor by 4 Ω and add a 0.25 S neutral-earth shunt.
At the same neutral voltage, load power and source power, the neutral-conductor
current magnitude falls from ``\sqrt{0.3125}\approx0.559017`` A to
``\sqrt{0.078125}\approx0.279508`` A. The shunt carries the remaining return
current. Its current is reconstructed from the declared admittance and supplied
voltage, not independently measured. Both analytic and native finite-grounding
points pass their scoped audits. A neutral-voltage observation therefore cannot
stand in for a conductor-current rating or recover an omitted return path.

**Inspect:** `examples/neutral_earth_voltage_audit.jl`, invoked by the exact clean
candidate `verify_linear_coverage.jl` companion, retains these points, both
cap violations, malformed data, missing state and explicit/source-ground cases.
The native builder omits this bound at an explicitly perfectly grounded neutral
or an implicitly grounded source-bus neutral. The latter rule also applies when
the source terminal map omits that bus neutral. Such declared caps remain
**unassessed**, with no invented zero residual; their separate grounding voltage
checks still apply. Consistent native grounded cases solve successfully while
retaining incomplete audit coverage. A finite grounding shunt does not trigger
that skip. Even a zero voltage cap does not allocate the free earth-reaction
current of a perfect-ground declaration: a voltage constraint is not a new
current path.

Missing/ambiguous/custom neutral roles, malformed scalars and missing neutral
state remain unknown. Missing required state suppresses KCL/power certification;
bad limit data preserves otherwise known currents and checked violations.
Tests cover complex norms, zero/equality and V-unit tolerance, Float64 range,
uppercase neutrals and native constraint incidence. Native builders are the
test subjects, not the independent audit's oracle.

Four running-network neutral caps now pass, reducing unassessed obligations
from 33 to 29 at this stage without deleting input fields. Phase-to-phase limits
follow below. At that stage generator cost was still outside scope, preventing
complete KCL/power checks; the final cost-scope section revisits them.
The published integration pin, PSK implementation statuses, physical adequacy
and execution MCP exposure remain separate.

**Transfer exercise.** Give the neutral-voltage and neutral-conductor-current
magnitudes for both return circuits above. Explain which additional model and
state data distinguish them, why a finite shunt does not skip `vn_max`, and why
a successful source-grounded solve does not turn its skipped cap into a passed
limit.


### [Phase-to-phase bounds preserve the full pair index](@id phase-phase-voltage-audit)

A phase-to-phase magnitude is the norm of a complex voltage difference. It
requires both phase phasors; neither a neutral report nor a balanced-system
conversion factor can replace them. The candidate audit now evaluates applicable
finite nonnegative `vpp_min`/`vpp_max` arrays:

```math
m_{ij}=|V_i-V_j|,\qquad
e_{ij,\min}=\max(0,\underline v_{pp,ij}-m_{ij}),\qquad
e_{ij,\max}=\max(0,m_{ij}-\overline v_{pp,ij}).
```

**Predict:** take source phases 10 V and ``10\mathrm j`` V connected through
two 1 Ω conductors to a two-terminal DELTA load. A supplied load-coil current
of 1 A from x to y gives load phases ``V_x=9`` V and ``V_y=1+10\mathrm j`` V.
The source supplies ``10-10\mathrm j`` VA; the load consumes ``8-10\mathrm j`` VA
and the conductors dissipate 2 W. Would subtracting the phase magnitudes recover
the voltage seen by this load?

| Quantity or obligation | Supplied value or bounds | Independent result |
|:--|:--|:--|
| Complex phase difference | ``8-10\mathrm j`` V | Magnitude ``\sqrt{164}\approx12.806248`` V |
| Difference of phase magnitudes | ``9-\sqrt{101}`` V | Different observation |
| Phase-pair bounds | [12,13] V | Pass |
| Tightened lower bound | 13 V | Fail by about 0.193752 V |
| Tightened upper bound | 12.5 V | Fail by about 0.306248 V |
| Phase-earth bounds, local KCL and total power at either bound mutation | Same supplied point | Pass |

Residuals and tolerances are **V**. At the 12.5 V upper bound, the native
squared-constraint excess is 7.75 V², while the independent magnitude excess is
about 0.306248 V. A tolerance must name its quantity and units. This synthetic
unbalanced two-phase circuit also supplies no ``\sqrt{3}`` conversion rule.
Native SI and per-unit points pass their scoped audits. The tightened native
attempt has local infeasibility and a failed point audit; the termination alone
is not a global infeasibility certificate.

Array position is part of the declaration. For phases `[a,b,c]`, pair entries
1, 2 and 3 mean `(a,b)`, `(a,c)` and `(b,c)`. The list excludes a supported n/N
neutral when present, and otherwise retains all phases in declaration order.
A pair touching a perfectly grounded or source-fixed phase is skipped by the
native builder but still consumes its index. The independent audit leaves its
bound **unassessed**, with no zero residual invented. If phase a is skipped,
`(b,c)` still uses entry 3. Reordering phases therefore requires the corresponding
pair-array permutation, not just a permutation of phase entries. A grounded
neutral does not skip phase pairs; neither does a finite grounding shunt.

**Inspect:** `examples/phase_phase_voltage_audit.jl` and its
`phase-phase-voltage.json` fixture, invoked by the exact clean candidate
`verify_linear_coverage.jl` companion, retain the analytic/native points,
bound violations, skipped first phases, malformed arrays and missing endpoint
state. Consistent native grounded/source-fixed cases solve while retaining
incomplete audit coverage. Tests inspect native constraint identities and cross
terms as subjects, without using builder expressions as the evaluator's oracle.
They also cover three-phase pair permutations, consistent relabeling, common
phasor shifts, exact zero/equality and V-unit tolerance, forged magnitudes and
Float64 range. A common shift preserves this pair observation; separate absolute
source, grounding or earth-connected equations may forbid it.

Fewer than two phases, custom or ambiguous roles, malformed arrays and missing
endpoint state remain unknown. A neutral is not required for this observation;
a missing declared neutral state nevertheless prevents complete network
KCL/power certification. Bad limit data preserves otherwise known currents
and checked violations. Each checked row names its terminal pair, phase indices,
full pair index, observed magnitude and bound.

The running network now has six checked phase-pair bounds at bus i6. Unknown
rows fall from 29 to 28: the two unsupported fields previously shared one
field-coverage row. Generator cost was still outside scope at that stage, so
KCL/power remained incomplete until the price-scope trace. Bus-angle, sequence and branch-end angle
limits follow below; objectives, physical adequacy, PSK implementation statuses,
published integration and execution MCP remain separate obligations.

**Transfer exercise.** Reorder `[a,b,c]` to `[c,a,b]` and map each old pair entry
to its new position. Then ground c: identify the surviving pair and its full
array index. Explain why a solver status, a neutral voltage or one phase
magnitude cannot fill in a missing endpoint phasor.


### [Centered bus angles need two nonzero phasors](@id bus-angle-voltage-audit)

An intra-bus angle bound observes a direction, not a voltage magnitude. For
phase indices ``i<j`` in the full declaration order, the candidate audit uses

```math
\Delta_{ij}=\phi_j-\phi_i,\qquad
d_{ij}=\arg\left(\frac{V_j}{|V_j|}\overline{\left(\frac{V_i}{|V_i|}\right)}
                  e^{-\mathrm j\Delta_{ij}}\right)\in(-\pi,\pi].
```

The optional `va_nom` array supplies ``\phi`` for all phases, excluding a
supported n/N neutral when present. Without it the offset is zero; a nominal
balanced arrangement is not inferred. Both `va_diff_min` and `va_diff_max`
are scalar bounds in **rad**, shared by applicable pairs. The native formulation
requires an ordered window strictly inside ``(-\pi/2,\pi/2)``. The independent
checks report ``\max(0,\underline d-d_{ij})`` and
``\max(0,d_{ij}-\overline d)`` with a separate `angle_tol` in rad.

**Predict:** reuse the load phases 9 V and ``1+10\mathrm j`` V above. Their raw
second-minus-first angle is ``\arctan(10)\approx1.47112767`` rad. With nominal
angles ``[0,\pi/2]``, the centered deviation is instead
``-\arctan(0.1)\approx-0.09966865`` rad. Which quantity does a declared centered
window constrain?

| Observation or obligation | Supplied value or window | Independent result |
|:--|:--|:--|
| Centered deviation | About −0.09966865 rad | From both complex phase states |
| Centered window | [−0.15,0.05] rad | Pass |
| Tightened lower bound | −0.05 rad | Fail by about 0.04966865 rad |
| Tightened upper bound | −0.12 rad | Fail by about 0.02033135 rad |
| Magnitude bounds, KCL and power at either mutation | Same supplied circuit | Pass |
| Explicit raw window with no nominal array | [1.4,1.5] rad | Pass, for a different declared observation |

A 2.8 rad common rotation of all voltages and currents preserves this circuit,
its powers and the centered deviation. Individual phase angles cross the branch
cut: subtracting their principal reports without circular reduction can introduce
a full turn. The evaluator normalizes each endpoint separately and takes the
principal argument of the centered product. This also avoids overflowing or
underflowing the raw product of two available nonzero voltage phasors. It uses
phase-to-earth directions, not phase-minus-neutral directions. A common voltage
translation generally changes the angle observation, even though it preserves
a phase-pair voltage difference.

Zero is a distinct boundary. A separate no-load point has one receiving phase
at 10 V and the other at zero. Its line/source currents are zero and KCL/power
pass. Native bilinear angle rows also vanish, satisfying their closure; the
angle of the zero endpoint is nevertheless undefined. The audit records the
pair **unassessed**, with no invented zero deviation. Small nonzero supplied
phasors have defined numerical directions; this check does not establish their
robustness to measurement or numerical perturbations. Native SI bilinear
residuals have V² units; per-unit rows use working coordinates. Neither is an
angular excess in rad, so they cannot share an unqualified angular tolerance.

**Inspect:** `examples/bus_angle_voltage_audit.jl` and
`bus-angle-voltage.json`, invoked by the exact clean candidate companion, retain
these points, both violations, absent nominal data, common rotation, malformed
windows and missing state. Native SI, per-unit and rotated points pass their
scoped audits. A tightened native attempt returns local infeasibility and fails
the point audit; termination alone is not a global infeasibility certificate.
Native primal-point and constraint-identity inspections are test subjects,
not observations reused by the independent evaluator.

Grounded/source-fixed phase pairs remain **unassessed**. Skipping a first phase
preserves full nominal indices: the remaining pair uses entries 2 and 3.
Finite grounding does not skip a phase; a grounded neutral is excluded from
phase enumeration. Consistent native skipped-phase cases solve while retaining
incomplete audit acceptance. Reversing pair direction negates the centered
angle and reverses an asymmetric window. Noncyclic phase swaps require matching
nominal-array permutations; cyclic symmetry can preserve nominal offsets modulo
full turns. Equal window endpoints are supported: native equality plus a
half-plane guard excludes the nonzero antipodal ray, which the independent
principal-angle check rejects directly.

Missing required endpoints, one-sided/reversed/singular windows, malformed
nominal arrays and unrepresentable data stay unknown. Known currents and checked
violations remain visible; missing required state suppresses complete KCL/power
certification. Standalone `va_nom` and custom roles remain outside this bus-angle slice;
sequence and branch-end angle limits follow below. The running network declares no bus-angle
window, so this family did not change the 28 then-unassessed obligations. The
final cost-scope section gives its latest verdict. Published integration, PSK statuses, execution MCP, objective and
physical adequacy remain separate.

**Transfer exercise.** Reverse the two phases in the asymmetric centered window
above. Give the new nominal order, deviation and bound endpoints. Then set one
endpoint voltage to zero and explain why successful bilinear rows or `atan(0,0)`
cannot supply its missing direction.


### [Sequence-voltage magnitudes are not a VUF ratio](@id sequence-voltage-audit)

Sequence bounds observe a linear combination of three phase phasors, followed
by a magnitude. In full declaration order, let ``\alpha=e^{2\pi\mathrm j/3}``:

```math
V_0=\frac{u_1+u_2+u_3}{3},\qquad
V_1=\frac{u_1+\alpha u_2+\alpha^2u_3}{3},\qquad
V_2=\frac{u_1+\alpha^2u_2+\alpha u_3}{3}.
```

Here ``u`` is phase-minus-neutral voltage when the declared default-role n/N
neutral floats, and phase-to-earth voltage when the neutral is absent or
perfectly grounded, including implicit source-bus grounding. The native
transform includes **all three phases**, even grounded or source-fixed ones.
These limits therefore have different applicability from the individual-phase
bounds above. Phase labels do not authenticate a physical phase arrangement;
this transform follows the full declared order. A cyclic permutation preserves
magnitudes, while exchanging two phases swaps positive and negative sequences
in this convention.

**Predict:** does an absolute negative-sequence cap establish a voltage-unbalance
ratio? The package-owned four-wire `sequence-voltage.json` circuit has 1 Ω per
phase and neutral conductor. At its supplied load point, the neutral is
``1-0.5\mathrm j`` V and the phase-neutral sequence phasors are
``V_1=10`` V, ``V_2=1`` V and ``V_0=0.5+0.25\mathrm j`` V. The independent
forward transform checks these observations from rectangular terminal states.

| Observation or obligation | Supplied value or bound | Independent result |
|:--|:--|:--|
| Positive magnitude | 10 V, interval [9.5,10.5] V | Pass |
| Negative magnitude | 1 V, cap 1.25 V | Pass |
| Zero magnitude | ``\sqrt{0.3125}\approx0.559017`` V, cap 0.75 V | Pass |
| VUF fraction | 0.1, cap 0.125 | Pass |
| Tightened positive lower/upper bound | 10.25 V / 9.75 V | Each fails by 0.25 V |
| Tightened negative / zero cap | 0.75 V / 0.4 V | Fail by 0.25 V / about 0.159017 V |
| Tightened VUF cap | 0.08 | Fail by 0.02, dimensionless |
| KCL and total power at each bound mutation | Same supplied circuit | Pass |

A consistent second circuit point reduces only the positive-sequence phasor to
5 V and updates the source references and specified powers. Negative sequence
stays 1 V, satisfying the same absolute cap, but VUF rises to 0.2. Its positive
bounds are adjusted to [4.5,5.5] V so this distinct ratio failure remains visible.
An absolute cap and a ratio limit cannot substitute for each other when the
positive-sequence magnitude varies.

The independent magnitude violations use **V** and `voltage_tol`. VUF is the
fraction ``|V_2|/|V_1|``, not a percent-valued field, and uses a separate
**dimensionless** `vuf_tol`. The ratio is assessed only for
``|V_1|>\texttt{vuf\_voltage\_floor}``; that configurable floor defaults to
``10^{-6}`` V, independently of `voltage_tol`. Below or at the floor, the row
reports the sequence magnitudes and floor but leaves observed ratio and residual
null. Other magnitude limits still receive their own results. A known positive
lower-bound violation remains failed even when the ratio is unknown.

This is a necessary boundary of the observation. The native constraint
``|V_2|^2\leq u^2|V_1|^2`` can pass at the all-zero origin, where the ratio is
undefined. The independent audit refuses to report ratio compliance there.
It does not assess native polynomial feasibility outside its stated ratio
domain. Native SI squared residuals are V² and per-unit rows use working
coordinates; neither supplies a dimensionless ratio excess or its tolerance.
The floor is a declared numerical domain, not a physical unbalance standard or
an uncertainty bound.

Reference choice also matters. At the floating-neutral point, the mean of the
**earth-referenced** phases is ``1.5-0.25\mathrm j`` V, with magnitude about
1.520691 V. Using it would fold neutral displacement into the zero component
instead of checking the specified phase-neutral observation. A separate
consistent grounded-neutral circuit uses earth input and passes. A bad grounded
neutral report fails grounding separately; its earth-referenced sequence
observation is not silently changed to subtract that bad report. Missing a
floating neutral prevents the transform. Known earth-reference phase data can
still support that observation while missing other declared state prevents
complete KCL/power certification. No missing neutral report is filled in as zero.

**Inspect:** `examples/sequence_voltage_audit.jl`, invoked by the exact clean
candidate companion, retains all bound mutations, the low-positive point,
malformed data, missing neutral and native SI/per-unit/grounded witnesses. The
permitted low-positive native point has a separate relaxed ratio cap. A tightened
native VUF attempt has local infeasibility and a failed point audit; termination
alone is not a global infeasibility certificate. Native expression/incidence
and zero-origin primal inspections are subjects, never the independent oracle.

Tests cover exactly three full phases, source/ground applicability, cyclic and
reversing permutations, neutral reference/fallback, scalar zero/equality and
unit-specific tolerances, denominator-floor refusal/configuration, malformed
limits and missing state. Known currents and checked violations survive bad
limit data. The running input declares no sequence or VUF bound; adding this
family did not change the 28 then-unassessed obligations. The cost-scope section
gives the latest verdict. Branch-end
angle limits follow below. Objectives, physical phase-order measurement and
adequacy, published integration, PSK statuses and execution MCP remain separate.

**Transfer exercise.** Keep negative sequence at 1 V and change positive sequence
from 10 V to 5 V. Give the two VUF fractions and identify which obligations a
1.25 V negative cap establishes. Then set both sequence magnitudes to zero:
explain why a successful cross-multiplied inequality cannot supply the ratio.


### [Branch-end angles follow the mapped conductor direction](@id branch-angle-voltage-audit)

A branch angle compares two ends of the **same mapped conductor**. It is not
the centered second-minus-first intra-bus angle above. For conductor index ``k``,
the independent audit observes

```math
d_k=\arg\left(\frac{V_{\mathrm{from},k}}{|V_{\mathrm{from},k}|}
             \overline{\left(\frac{V_{\mathrm{to},k}}{|V_{\mathrm{to},k}|}\right)}\right)
\in(-\pi,\pi].
```

The direction is ``\theta_{\mathrm{from},k}-\theta_{\mathrm{to},k}``, with no
nominal-angle offset. Each line's scalar `va_diff_min`/`va_diff_max` window
applies to every positional pair in its explicit from/to terminal maps. Those
maps must be nonempty, unique and equally long. Neither sorted labels nor
prefix truncation can recover an undeclared conductor correspondence.

**Predict:** the two-conductor DELTA circuit already used above has source
phases 10 V and ``10\mathrm j`` V, receiving phases 9 V and
``1+10\mathrm j`` V, and 1 Ω per conductor. What is the second conductor's
signed branch angle?

| Observation or obligation | Supplied value or window | Independent result |
|:--|:--|:--|
| First mapped conductor | ``0-0`` rad | Zero |
| Second mapped conductor | ``\pi/2-\arctan(10)=\arctan(0.1)`` rad | About +0.09966865 rad |
| Branch window | [−0.02,0.12] rad | Both pass |
| Tightened lower bound | 0.02 rad | First conductor fails by 0.02 rad |
| Tightened upper bound | 0.08 rad | Second conductor fails by about 0.01966865 rad |
| Line equations/current ratings, bus magnitude bounds, KCL and power at either mutation | Same supplied circuit | Pass |

The positive sign differs from the earlier centered bus deviation for this
circuit. Angular violations use **rad** and the separate `angle_tol`; the native
sine/cosine-scaled SI rows have V² units, while per-unit rows use working
coordinates. Their residuals cannot supply an angular tolerance. Both scalar
endpoints must be finite, ordered and strictly inside ``(-\pi/2,\pi/2)``.
Equal endpoints are supported: the native equality plus half-plane guard
excludes the nonzero antipodal ray, which the independent principal angle
rejects directly.

Direction is part of a branch declaration. Reverse the branch and its endpoint
maps, reverse the supplied endpoint currents/result labels, and replace
``[\underline d,\overline d]`` by ``[-\overline d,-\underline d]``. The same
circuit then passes with the opposite signed deviation. Keeping the old
asymmetric window can change the result. A consistent conductor permutation
also permutes both maps and their data; it does not sort phases by name.

A 1.62 rad common rotation of voltages and currents crosses the individual-angle
branch cut while preserving the circuit and branch observations. The evaluator
normalizes each nonzero endpoint before multiplication and takes the principal
argument. This avoids raw voltage-product under/overflow and unwrapped
subtraction errors. It uses supplied earth-referenced voltages; neither a bus
nominal reference nor a phase-neutral substitution defines this branch quantity.

Zero endpoints remain a distinct boundary. Native rows are registered for
**all conductors**, including neutrals and source/ground endpoints. A separate
explicit-neutral circuit has zero source-neutral voltage and a floating
receiving neutral. Native solving succeeds, but that conductor's angle remains
**unassessed**, with no invented residual. Its other conductor angle, line
equations, currents, KCL and power still pass. At an all-zero branch point,
native primal constraints also pass without defining either endpoint direction.
A grounding label or successful homogeneous inequality cannot supply an angle.

**Inspect:** `examples/branch_angle_voltage_audit.jl` and
`branch-angle-voltage.json`, invoked by the exact clean candidate companion,
retain both violations, common rotation, complete reversal, missing state,
one-sided data, neutral and zero endpoints. Native SI/per-unit/rotated/reversed
points pass their scoped audits. The tightened native attempt has local
infeasibility and a failed point audit; termination alone is not a global
infeasibility certificate. Native semantic keys, domain guard and zero-origin
primal inspection are test subjects, never the independent oracle.

Bad angular data does not erase known inline-series current contributions or
checked current-rating violations. Missing required endpoint state suppresses
complete KCL/power certification but need not erase a different conductor's
angle observation. Supplied endpoint angles can also be checked while a separate
line equation model is unsupported; those observations cannot certify its
currents or equations. The older linear-only API retains its refusal of
line-angle declarations. Tests cover positional mapping, asymmetric reversal,
principal cuts, normalization, equality/zero/tolerance, neutral/ground incidence,
malformed windows/maps and partial state.

The running network declares no branch-angle bounds, so adding this family
did not change the 28 then-unassessed obligations. The final price-scope trace
below gives its latest verdict. Physical adequacy,
objectives, broader device/role coverage, published integration, PSK statuses
and execution MCP remain separate obligations.

**Transfer exercise.** Reverse a branch whose window is [−0.02,0.12] rad.
Give its new window and the sign of each conductor observation. Then delete
only the second receiving voltage: identify which angular observation remains
available and why complete line/KCL certification is still unavailable.


### [A generator price is not an objective certificate](@id generator-cost-scope-audit)

A generator price declaration has a different role from an electrical limit.
In the bounded native generator form it is a full finite signed vector,
one coefficient per declared coil. A two-terminal `SINGLE_PHASE` device has one
coil price, including when its terminal order is reversed. A WYE neutral has
no separate price. Scalars, polynomial-shaped objects, wrong or extra lengths,
nulls, Booleans and unrepresentable values remain unassessed rather than being
reinterpreted as another cost model.

The native default generator contribution is

```math
C_g=\sum_k c_{g,k}\frac{P^{\mathrm{inj}}_{g,k}}{1000},\qquad
P^{\mathrm{inj}}_{g,k}=\Re\left(U_{g,k}\overline{I_{g,k}}\right).
```

With power in W and price in currency/kWh, ``C_g`` is a **rate in currency/hour**.
It is linear in active power, although bilinear in IVR voltage/current variables.
A positive coefficient penalizes its injection contribution; a negative one
rewards it within the selected minimization objective. Other terms and network
constraints can alter actual dispatch. Zero direct cost alone establishes
neither a feasible flat direction nor dispatch non-uniqueness.

The native cost-expression constructor adds no variables or constraints.
Generator apparent-power limits already create auxiliaries independently of
price. Per-unit working prices are multiplied by the local power base to cancel
power scaling; this is coordinate bookkeeping, not a changed tariff. A staged
caller can omit the objective, replace it, combine snapshots or apply explicit
duration weights. A network/result pair alone does not identify that choice.

The independent audit therefore retains valid prices with status **declared**,
null residual and `enforced_as_physical_limit=false`. This is not a passed
objective or an economic-validity finding. Signed/zero prices are recognized;
malformed prices remain unknown while otherwise known currents, KCL and limit
violations remain available. Missing required current or state still prevents
complete electrical checks. Generator active/reactive/apparent-power rows name
**W**, **var** and **VA** respectively, with unchanged numerical tolerances.

The output `objective_scope` explicitly leaves objective selection, reported
objective consistency, objective evaluation, custom constraints and local/global
optimality unchecked. Finite price metadata also does not certify numerical
objective applicability under arbitrary scaling or coefficient providers. The
candidate result-field description now says **reported objective value**; an
objective field alone is not an optimality or feasibility certificate.

**Predict:** a 10 V ideal-switch circuit supplies a ``10+2\mathrm j`` VA load
with a generator fixed at ``4+1\mathrm j`` VA. What can an electrical audit tell
from the same physical point under these known recipe choices?

| Explicit recipe | Recorded objective | Electrical point evidence |
|:--|:--|:--|
| Default price +0.25 currency/kWh | +0.001 currency/hour | Pass |
| Default price −0.25 currency/kWh | −0.001 currency/hour | Pass |
| Zero price at fixed dispatch | 0 | Pass; no feasible-flat-direction claim |
| Caller-selected constant objective | 123 in caller-defined units | Same fixed point passes |
| Explicitly hold the snapshot for two hours | 0.002 currency | Same fixed point passes; duration is an extra assumption |
| Supplied result with an invented `objective=999` | Unverified | Electrical pass does not validate this field |

In this particular circuit, with an unpriced source, Q fixed at 1 var and P
allowed in [3,5] W, the per-unit positive/negative-price solves select the
respective P limits. These native observations do not establish global optimality
for a general network. Only the known recipe supplies the values and units in
the table; the standalone feasibility audit does not infer it.

**Inspect:** `examples/generator_cost_scope.jl` and `generator-cost.json`, invoked
by the exact clean candidate companion, retain these price, recipe, malformed-
data and missing-current witnesses. Tests inspect native expression values,
indexing and unchanged variable/constraint counts as subjects; the declaration
audit does not call the native cost builder as its oracle. The public native
objective construction stage precedes KCL finalization.

The native SI attempts are preserved honestly. From the voltage-only start,
Ipopt reports a restoration failure and the returned point fails the electrical
audit. With a full supplied-primal start it still reports a restoration failure,
but its returned point passes electrical checks and has the expected rate.
Per-unit, no-objective, zero-price and custom-constant recipes solve and pass.
Solver success, a valid supplied point and selected-objective assessment are
three separate observations; neither failure nor success can substitute for
the other checks.

The running example makes the distinction consequential. Its retained generator
prices ``[-0.08,-0.08,-0.08]`` are now recognized without deleting any field.
Previously that declaration prevented a complete current inventory. It now
opens all 26 KCL checks and aggregate power, which pass, and exposes three
active-power upper-bound violations in the original default solver result.

| Running result, same input and audit tolerances | Unknown rows | Failed electrical checks |
|:--|--:|:--|
| Retained default solve | 0 | Three p_max excesses, about 0.00997 W each |
| Separate tighter solve | 0 | None; scoped electrical point audit passes |

The absolute audit tolerance remains 1e-6 W. The separate solve uses
`tol=1e-10`, `constr_viol_tol=1e-12`, `acceptable_iter=0` and
`bound_relax_factor=0`; both results and solver options are retained. No audit
tolerance is loosened and no input constraint or price is removed. Default
solver behavior is a recorded diagnostic, not a requirement that every future
backend reproduce the same violation.

A **passed** result here means the explicitly supported electrical supplied-point
obligations hold at the stated tolerances. It does not establish unrestricted
native/custom-model feasibility, a selected objective, stationarity, local/global
optimality, physical adequacy, economic correctness or external review. The
DELTA generator and voltage-source price scopes follow below; other device/controller
scopes, IBR price applicability, published
integration, PSK statuses and execution MCP remain separate.

**Transfer exercise.** Give the rate and explicit two-hour cost for 4 W injection
at price +0.25 currency/kWh. Then explain why `objective=123`, solver success,
a zero price or a tiny active-power excess cannot independently settle the
selected objective, uniqueness, or electrical compliance.


### [DELTA generator limits live on coils](@id delta-generator-injection-audit)

The [DELTA circulation lesson](@ref delta-coil-current-lesson) applies to
injections as well as consumption. The local candidate now audits bounded
DELTA generators using their own native indexing: two or three distinct
non-neutral terminals in declared cyclic order. A reported current at a
terminal key need not be the current injected into that terminal.

**Predict:** for coil currents ``I=(0.3-0.1\mathrm j,-0.2+0.15\mathrm j,
0.1+0.05\mathrm j)`` A, does a second entry `i_max=0.3` bound the current in
the second coil or the current injected at the second terminal?

For ordered terminals ``(x,y,z)``, the pairs are ``x\to y``, ``y\to z`` and
``z\to x``. In the native result, `generator.g.x.crg/cig` stores ``I_1``,
the injection coil current paired with ``U_1=V_x-V_y``. Independently evaluate

```math
S_k=U_k\overline{I_k},\qquad
J_k=I_k-I_{k-1},\qquad
\sum_k S_k=\sum_k V_k\overline{J_k},
```

with cyclic indices. Here ``J_k`` is terminal injection; outgoing-current KCL
uses ``-J_k``. The final identity follows from incidence, so it does not replace
individual coil observations or limits. The audit labels terminal currents
**reconstructed**, retaining explicit pairs and both injection/outgoing signs.
It does not invent an independent line-current measurement.

The native generator's `i_max[k]` bounds ``|I_k|``. Its `s_max[k]` bounds
``|S_k|`` directly; no total rating is divided among coils. This array rule is
separate from the earlier winding-list transformer's equal allocation of a
single winding `s_max`. Generator P/Q bounds and required `pg/qg` reports also
refer to each coil. Signed injections and absorption are allowed by the
corresponding declared bounds. Residuals use A, W, var and VA with the existing
absolute current/power tolerances.

**Inspect:** the source/switch/load fixture uses
``V=(10,10\mathrm j,-6-8\mathrm j)`` V, giving:

| Coil | Voltage difference (V) | Injection current (A) | Injection power (VA) | Current cap (A) | Apparent-power cap (VA) |
|:--|:--|:--|:--|--:|--:|
| ``x\to y`` | ``10-10\mathrm j`` | ``0.3-0.1\mathrm j`` | ``4-2\mathrm j`` | 0.35 | 6 |
| ``y\to z`` | ``6+18\mathrm j`` | ``-0.2+0.15\mathrm j`` | ``1.5-4.5\mathrm j`` | 0.30 | 6 |
| ``z\to x`` | ``-16-8\mathrm j`` | ``0.1+0.05\mathrm j`` | ``-2`` | 0.20 | 3 |

All coil limits pass. The reconstructed terminal injections are
``(0.2-0.15\mathrm j,-0.5+0.25\mathrm j,0.3-0.1\mathrm j)`` A. At terminal y,
``|J_y|\approx0.559`` A exceeds the numerical second-coil cap, while the
second coil carries only 0.25 A. Applying the declared coil cap to that terminal
current would falsely reject this native operating point. No terminal-line
rating is inferred from the coil array.

Now add the same ``0.5+0.2\mathrm j`` A to every coil. Incidence removes the
common increment, so terminal injections, KCL and aggregate generator power
``3.5-6.5\mathrm j`` VA are unchanged. Individual coil powers become
``(7-9\mathrm j,8.1+3.3\mathrm j,-11.6-0.8\mathrm j)`` VA. All three original
current caps and all three apparent-power caps fail, while honest updated
`pg/qg` reports, KCL and aggregate power pass. This is a six-limit violation,
not missing evidence. Internal circulation cannot be reconstructed from those
terminal observations alone.

At a separate zero-voltage point, equal nonzero coil currents give zero terminal
injection and zero coil power. Zero apparent-power caps therefore pass even
though the current caps fail. Inspection of the native primal constraints also
rejects those currents. A zero power report is neither a zero-current observation
nor spare current capacity.

The package's `delta_generator_audit.jl` and `delta-generator.json`, invoked by
the source-bound book companion, retain analytic/native points, circulation,
forged reports, missing internal observations and malformed ratings. Native SI,
per-unit, consistently reversed-coil and two-terminal comparisons fix the
recorded coil dispatch and pass. A separate tighter-current-cap attempt reports
`LOCALLY_INFEASIBLE` and returns a point that fails the independent audit. Both
statuses are retained; this solver observation is not a global infeasibility
certificate or a robustness claim.

Cyclic reordering must move coil-indexed bounds, prices and reports with the
coils. Reversing the cycle reverses each matched coil's voltage and current;
its complex power keeps the same sign. Changing terminal order alone does not
perform that transformation. Per-unit evaluation returns to original SI coil
voltages and currents; an earth-voltage magnitude or a generic square-root-of-
three factor cannot replace an actual ordered voltage difference.

There are two applicability distinctions to keep visible:

- The native **two-terminal DELTA generator has two opposed coils**, one at
  each cyclic position. A two-terminal DELTA load and a two-terminal
  `SINGLE_PHASE` generator each have one coil. The separate three-terminal
  data-model arity checker still warns on the native two-terminal generator
  form. Matching native equations does not establish specification conformance
  or a physical three-phase winding interpretation.
- A neutral-bearing DELTA generator map remains **unassessed**. The current
  native generator builder constructs it, while its conformance checker emits
  `E.SPEC.DELTA_HAS_NEUTRAL`. The audit records that disagreement and refuses
  the map. It neither changes native construction nor applies WYE neutral-return
  rules to make coverage pass. One/four-terminal cycles, custom roles and
  controllers remain outside this bounded audit.

Missing a required coil current or voltage suppresses complete network KCL/power
certification. Known observations and violations on other coils remain visible;
a missing `pg/qg` report does not erase otherwise known current or limit checks.
Malformed extra/prefix rating entries remain unknown without hiding a separate
known violation. Finite signed coil prices remain **declared** metadata;
objective selection/value, local/global optimality, physical realizability and
unrestricted native/custom-model feasibility are separate obligations.

The running network's generator is WYE, so this extension leaves its recorded
default three-`p_max` failure, zero unknowns and separate tighter electrical pass
unchanged. Published integration, PSK implementation statuses and execution MCP
remain separate.

**Transfer exercise.** Derive the three terminal injections from the baseline
coil currents. Then add a common complex increment and identify which
observations stay unchanged, which ratings must be rechecked, and why terminal
measurements cannot supply a missing internal coil current.


### [A source price does not change its voltage reference](@id source-price-reference-audit)

A native voltage source uses two indexing and reference conventions at once.
Its `v_magnitude/v_angle` entries specify **absolute terminal-to-earth phasors**
in full source-map order. Its current, P/Q and price entries follow only the
**non-neutral source-map order**. Neither order is inherited from the bus list.
Recognizing the price vector must not discard or reinterpret the source's
reference and grounding obligations.

**Predict:** a bus lists ``(n,a,b)``, while its source map is ``(b,n,a)``.
The reference magnitudes are ``(10,0,10)`` V at ``(\pi/2,0,0)`` rad. There are
two prices ``(0.4,0.1)`` currency/kWh. Which price belongs to phase a, and what
voltage reference enters its priced power?

Independently decoding that source gives phase order ``(b,a)`` and map positions
``(1,3)``. The neutral has no price/current slot. For these supported native
WYE/`SINGLE_PHASE` sources,

```math
S_k=(V_{t_k}-V_n)\overline{I_k},\qquad
C_s=\sum_k c_k\frac{\Re(S_k)}{1000}.
```

If the bus has no neutral, use earth in place of ``V_n``. If a declared bus
neutral exists but is **omitted from the source map**, the native source still
uses it for power and current return, and grounds it at zero. This differs
from an unmapped-neutral WYE load/generator's earth-reference rule. The price
metadata retains the phase order, original map positions, phase/reference
pairs and whether the neutral was mapped. The audit uses supplied neutral
state in P/Q evaluation; grounding is checked separately, so missing state
is not replaced by a passing zero.

Positive source active power is injection into the network, interpreted here
as import; negative power is export. The same signed coefficient multiplies
either sign. A positive coefficient therefore credits negative injection in
that expression. This is not a separate buy/sell tariff. With P in W and price
in currency/kWh, the snapshot expression is a **rate in currency/hour**. Energy
cost needs an explicit duration assumption. Valid fixed source references make
these source-power terms linear in the source currents; they do not make the
whole network model linear.

**Inspect:** `source_price_audit.jl` and `source-price.json`, invoked by the
exact clean candidate companion, retain this unbalanced computational point:

| Source phase order | Earth voltage (V) | Injected current (A) | Injected power (VA) | Price (currency/kWh) | Known rate contribution (currency/hour) |
|:--|:--|:--|:--|--:|--:|
| b, map position 1 | ``10\mathrm j`` | ``0.2-0.3\mathrm j`` | ``-3+2\mathrm j`` | 0.4 | -0.0012 |
| a, map position 3 | ``10`` | ``0.6-0.1\mathrm j`` | ``6+1\mathrm j`` | 0.1 | +0.0006 |

The net import is 3 W, but the known default rate is **-0.0006 currency/hour**
under these declared phase prices. This is a signed numerical witness with
negative active demand on one load phase, not an inference about asset identity
or economically adequate pricing. A neutral-first map ``(n,a,b)`` needs prices
``(0.1,0.4)`` to keep the same phase-price assignment. Leaving the old prices
in that reordered map gives **+0.0021 currency/hour**, while the same electrical
point still passes. An electrical audit cannot recover which tariff mapping
the caller intended.

Several reference cases must remain distinct:

| Source declaration | Reference obligation | Price/current obligation |
|:--|:--|:--|
| Full ``(b,n,a)`` map | Three absolute phasors, including neutral | Two entries, ordered b then a |
| Map ``(b,a)`` with bus neutral n | Two absolute phase phasors; separate implicit neutral ground | Two entries, each using bus n for power/return |
| Map ``(b,a,n)`` with two reference entries | Omitted trailing n is known grounded zero | Two phase entries; no neutral price |
| Prefix omitting an explicitly grounded phase | Omitted suffix must already be known zero | Grounded phase still keeps its price/current slot |
| Explicit empty reference prefix | Allowed only when every mapped terminal is known grounded zero | Phase slots remain; missing arrays are not an empty prefix |
| Prefix omitting a free phase | Reference remains unassessed; native construction rejects it | No phase phasor is inferred |
| Two-phase `SINGLE_PHASE` source without neutral | Two absolute phase references | Two earth-referenced currents/prices |

The final case does **not** use the one-coil convention of a two-terminal
`SINGLE_PHASE` generator. Its source currents ``(0.3-0.1\mathrm j,
-0.3+0.1\mathrm j)`` A at ``(10,10\mathrm j)`` V have powers
``(3+\mathrm j,1-3\mathrm j)`` VA. Prices ``(0.1,0.2)`` give a known rate of
0.0005 currency/hour. A one-entry price vector remains unknown to the audit
and the native default expression cannot consume its missing second entry.

Absolute source references and phase-neutral powers are also different tests.
A common voltage translation can preserve all supplied phase-neutral powers
and KCL while violating the source's absolute phasors and neutral ground. In
a separate displaced-neutral witness, the authored source reference itself
sets ``V_n=1`` V: its supplied absolute reference equation, honest P/Q reports,
KCL and aggregate power pass, but the independent neutral-ground boundary
fails. Native construction rejects that conflicting reference. Neither price
metadata nor balanced power legitimizes the nonzero source neutral.

Source neutral return injection is ``-\sum_k I_k``. The separately supplied
earth-reaction current is another term, even when the neutral voltage is zero.
The audit reconstructs the return, consumes a shared source-bus ground reaction
once, and leaves a missing earth reaction unknown. Two overlapping ideal
sources can satisfy the same references and external current balance while
redistributing their currents. Two recorded splits both pass electrically,
but their known default expression values differ. The fixture does not optimize
that allocation; electrical acceptance establishes neither intended allocation
nor objective well-posedness.

Native SI/per-unit, neutral-omitted, trailing-prefix, neutral-first, earth and
two-phase `SINGLE_PHASE` comparisons solve and pass. Reversing the price signs,
omitting the objective, or selecting a caller-constant123 objective retains
separate recipe and electrical evidence. Per-unit working prices multiply the
local power base and cancel power scaling; they are not revised tariffs.
Native expression tests confirm that `generation_cost` adds no variables or
constraints and does not select the objective. They inspect the implementation
as a subject; the independent audit does not call it as an oracle.

Recognized full finite signed price vectors have status **declared**, null
residual/tolerance and `enforced_as_physical_limit=false`. Scalar, partial,
extra/neutral-priced, Boolean, nonfinite and unrepresentable declarations remain
unknown while known source equations, currents, reports and KCL remain checked.
Malformed reference arrays likewise leave known current incidence available;
the reference equation stays unassessed. A missing required phase current,
neutral state or earth reaction suppresses complete network KCL/power checks.
Known other-phase report failures survive. Optional supplied `ps/qs` reports
are checked in W/var with unchanged tolerances.

The next section adds source P/Q limits. Unsupported source current/apparent-
power ratings or controller fields, custom terminal roles and DELTA sources
remain outside this bounded extension. It certifies no
tariff, selected objective, reported objective consistency, local/global
optimality, physical grounding adequacy or unrestricted native/custom-model
feasibility. The running input has no source price, so its recorded default
three generator `p_max` violations/zero unknowns and separate tighter electrical
pass are unchanged. Published integration, PSK statuses and execution MCP
remain separate.

**Transfer exercise.** Reorder ``(b,n,a)`` to ``(n,a,b)`` while preserving the
physical phase tariffs. Write the new reference and price arrays, then explain
why a correct cost rate cannot establish the omitted phase reference, neutral
earth-reaction current, source allocation or selected-objective guarantee.


### [Source P/Q limits apply to signed phase injections](@id source-pq-limit-audit)

A voltage source can fix its voltage reference while having a constrained
power exchange. The local candidate now independently checks authored
`p_min/p_max/q_min/q_max` for its bounded `WYE`/`SINGLE_PHASE` source domain.
It recomputes power from the supplied voltage/current state:

```math
S_k=(V_{t_k}-V_n)\overline{I_k},\qquad
P_k=\Re(S_k),\quad Q_k=\Im(S_k),
```

with earth in place of ``V_n`` when no bus neutral exists. An unmapped bus
neutral still supplies the source's power reference and return. The limits
follow non-neutral **source-map order**, even if the neutral appears between
phases in the full reference array. Source-fixed and grounded phases keep
their P/Q slots. The earlier voltage-bound skip rules do not apply to this
source-power family.

**Predict:** phase powers in source order ``(b,a)`` are ``(-3+2\mathrm j,
6+\mathrm j)`` VA. Upper P bounds ``(-2,5.5)`` W sum to 3.5 W, while net P is
3 W. Does that establish source-bound compliance?

The actual constraints are independent signed boxes:

```math
p_k^{\min}\le P_k\le p_k^{\max},\qquad
q_k^{\min}\le Q_k\le q_k^{\max}.
```

For example, upper-P excess is ``\max(0,P_k-p_k^{\max})`` and lower-P
excess is ``\max(0,p_k^{\min}-P_k)``. P residuals and `power_tol` use W;
Q residuals use var with the same numeric tolerance setting. These are
absolute violations in original SI coordinates, not relative percentages,
per-unit residuals or price-weighted penalties.

Positive P is injection into the network (import), and negative P is export.
A lower bound ``p^{\min}=-2.5`` W therefore rejects ``P=-3`` W by 0.5 W:
there is too much export for that lower bound. An upper bound ``p^{\max}=-3.5``
W would require more export than ``P=-3`` provides and also fails by 0.5 W.
There is no absolute-value or import/export sign flip. Positive Q is reactive
injection; negative Q is absorption under the declared complex-power convention.

**Inspect:** `source_pq_audit.jl` and `source-pq.json` extend the source-price
point with these full phase bounds. The bus order remains ``(n,a,b)`` and the
source map remains ``(b,n,a)``:

| Phase | Full map position | P (W) | Q (var) | P interval (W) | Q interval (var) |
|:--|--:|--:|--:|:--|:--|
| b | 1 | -3 | 2 | [-4,-2] | [1,3] |
| a | 3 | 6 | 1 | [5,7] | [0.5,1.5] |

All baseline rows pass. Tightening only phase a's upper P bound to 5.5 W
creates one 0.5 W violation, despite the passing summed comparison in the
prediction. Tightening phase b's upper Q bound to 1.5 var creates one 0.5 var
violation even though total Q equals the summed upper bound of 3 var. Lower
P/export and lower Q examples retain the same distinction. No aggregate
comparison or neutral-current observation replaces an individual phase bound.
A separate two-phase `SINGLE_PHASE` source without a neutral checks negative
Q absorption with two independently indexed source terms.

Optional `ps/qs` reports are a separate consistency check. A forged in-range
`ps=5.5` cannot hide a recomputed 6 W injection: the report and limit each
fail by 0.5 W. Missing optional reports leave known current-derived limits
available. Missing a required phase current instead leaves that phase's
power/limits unknown, preserves known other-phase failures, and suppresses
complete network KCL/power certification. The checker never inverts a reported
power to replace the missing current.

Declaration applicability is also explicit:

| Limit declaration | Bounded audit meaning |
|:--|:--|
| Field absent | No authored bound for that field; no limit row invented |
| Explicit empty array | Declared empty-limit metadata; no numeric residual or zero constraint |
| Full finite signed phase vector | Each phase checked at its original non-neutral index |
| Nonempty prefix, extra/neutral entry, scalar, bad type or unrepresentable value | Field unassessed; other known fields and current incidence remain checked |

An empty row has null residual/tolerance and `enforced_as_limit=false`. It does
not claim that any phase satisfies a zero bound. This source empty-vector rule
is distinct from the generator audit's stricter full-array declaration domain.
No field is deleted, padded or trimmed to obtain complete coverage.

The native builder is permissive about nonempty lengths: a prefix stamps only
its available first phase entries, and extra entries are ignored. Static
indexing diagnoses both with `W.INT.DIM_MISMATCH`. The source-bound companion
retains successful native prefix/extra solves whose bounded point audits stay
**indeterminate**, rather than silently assigning missing entries or accepting
an unexplained extra declaration. Native semantic-row inspection shows one
upper-P row for a one-entry prefix and two rows for a full vector with an
ignored extra entry. Four full vectors on two phases add eight native
constraints and no variables; empty and absent vectors add none.

Native SI/per-unit, consistently reordered, neutral-omitted, trailing-neutral,
earth-reference, two-phase `SINGLE_PHASE` and empty-limit comparisons solve and
pass their scoped audits. Consistent reordering moves P/Q arrays together
with the source reference, price and current indexing. Leaving the old bound
order can invalidate the same electrical point. Separate tighter P and Q
attempts report `LOCALLY_INFEASIBLE` and return points failing the independent
audit. Both outcomes are retained; this is no global infeasibility,
optimality or initialization-robustness certificate. Native constraints and
per-unit recovery are test subjects, not the independent evaluator's oracle.

At a separate point with every phase-to-reference voltage zero, nonzero
source currents pass zero P/Q boxes. A positive lower P bound then fails.
Native primal inspection confirms both supplied-point observations. Thus even
complete P/Q-box compliance is not a conductor-current or apparent-power
rating certificate. No physical grid/ground adequacy, selected objective,
controller/custom-role domain or unrestricted native/custom-model feasibility
is inferred. Unsupported source current/apparent-power declarations remain
unassessed.

The running input has no source P/Q bounds. Its retained default three
generator `p_max` violations/zero unknowns and separate tighter electrical pass
therefore remain unchanged. Published integration, PSK implementation statuses
and execution MCP remain separate.

**Transfer exercise.** For the table's operating point, choose a bound that
rejects excess export on b while leaving import on a admissible. Then preserve
those physical phase limits under source-map reordering, and explain why a
passing total-P comparison, an in-range report, an empty array or a zero-power
observation cannot replace the phase and current evidence.


### [IBR currents depend on the admitted topology](@id ibr-injection-audit)

An inverter label alone does not identify the voltage/current pairing or its
terminal-current incidence. The local candidate adds independent supplied-point
checks for a bounded AC-only slice. Its three admitted topologies have distinct
observations and current caps:

| Admitted topology | Power voltage and supplied current | Reconstructed injections and current cap |
|:--|:--|:--|
| `SINGLE_PHASE`: exactly two distinct endpoints | One ordered pair, ``U=V_{t_1}-V_{t_2}``, one `cri/cii` current ``I`` | ``(+I,-I)``; one shared current capped by the minimum of one/two `i_max` entries |
| `FOUR_LEG`: one to three phases plus an explicitly mapped default-role neutral | One ``V_\phi-V_n`` and current per phase, in map order after removing n | Phase injections ``I_\phi``, neutral ``-\sum I_\phi``; phase caps and optional final neutral cap |
| `THREE_LEG`: exactly three distinct non-neutral endpoints | One supplied current per cyclic coil, ``U_k=V_{t_k}-V_{t_{k+1}}`` | Terminal injection ``J_k=I_k-I_{k-1}``; `i_max` caps coils, without an inferred terminal-current rating |

The default-role neutral may occur anywhere in a four-leg map. Reversing the
single-phase pair negates its current while preserving its physical terminal
injections and power. A cyclic reordering or reversal must transform every coil
observation and parameter slot consistently. Reconstructed returns and terminal
currents are derived quantities, not independent measurements.

**Predict:** a three-leg point passes terminal KCL. Add the same complex
``h`` to every supplied cyclic coil current. Which observations change, and
which ratings must be checked again?

The independently evaluated powers are

```math
S_k=U_k\overline{I_k},\qquad P_k=\Re(S_k),\quad Q_k=\Im(S_k).
```

For the cyclic model,

```math
(I_k+h)-(I_{k-1}+h)=J_k,\qquad
\sum_k U_k=0,\qquad
\sum_k U_k\overline{(I_k+h)}=\sum_k S_k.
```

Thus terminal KCL and total injected complex power cannot reveal this internal
circulation. Individual coil powers and current magnitudes can change. In the
minimized three-leg fixture, adding ``h=0.5+0.2\mathrm j`` A preserves all
reconstructed terminal injections, terminal KCL and aggregate power while
violating three coil current and three coil apparent-power caps. The base
point also has a terminal current larger than the corresponding coil cap;
that cap is attached to the coil quantity, so it is satisfied. A terminal-current
rating would be a different obligation.

Two other fixture observations separate the current-cap rules:

| Point | Authored cap change | Independent supplied-point outcome |
|:--|:--|:--|
| Single pair current ``0.4-0.1\mathrm j`` A | `i_max=[0.5,0.3]` A | Shared magnitude ``\sqrt{0.17}`` A exceeds 0.3 A; no separate return-current constraint is inferred |
| Four-leg map `[n,z,x,y]`, phase-current sum ``0.3+0.1\mathrm j`` A | Final neutral cap 0.2 A | Neutral-return magnitude ``\sqrt{0.1}`` A exceeds the cap while all phase caps pass |

The audit checks full finite signed `p_min/p_max/q_min/q_max` in W/var and
nonnegative `s_max/i_max` in VA/A. Residuals are absolute SI excesses under
`power_tol` or `current_tol`, not squared or per-unit magnitudes. Absent or
explicit empty arrays author no native bound; empty arrays yield declared
no-bound rows. Nonempty arrays must match the admitted branch/current domain.
Optional reported `pg/qg` are separate consistency checks, never the limit
oracle. A malformed array preserves independently known other limits and
current contributions. A missing required current or voltage preserves known
other branch failures but suppresses complete network KCL/power certification.
No division by voltage or reconstruction from reported power is used. At zero
voltage, nonzero cyclic current can pass zero P/Q/S caps while violating I caps.

The package example `examples/ibr_injection_audit.jl` and fixture
`test/data/linear_audit/ibr-injection.json` are included by the source-bound book
companion. Analytic points pass for all three admitted topologies. Separate
controlled native comparisons fix their dispatch, seed the full primal state
and pass their scoped audits in SI and per-unit coordinates; the reversed
single pair also passes. Attempts with the tighter shared/neutral caps retain
their solver statuses, returned points and independent audits. In this locked
run both report `LOCALLY_INFEASIBLE`; their returned-point audits fail one and
four checks respectively. These are local outcomes, without a global
infeasibility, unique-dispatch or initialization certificate.
Floating-neutral, map-permutation, missing-observation, zero-voltage and
malformed-declaration tests exercise the package's bounded evaluator. Native
construction, extraction, auxiliary variables and coordinate recovery are test
subjects; the audit uses none as its equation oracle.

Topology applicability remains a separate question. Native construction accepts
a single-phase ignored terminal suffix, a four-leg map omitting its neutral
(with earth reference), other cyclic three-leg arities, and extra single-phase
current entries. The bounded audit refuses those declarations. Static conformance
and native construction remain distinct: a reduced-phase four-leg case may
receive an arity warning even within the stated native audit slice. This work
checks the **current native cyclic equations** for `THREE_LEG`; the broader
physical topology review in package issue #95 remains unresolved. Agreement
with these equations cannot settle that physical model question.

Authored filters (`r_filter`, `x_filter`, `b_filter_shunt`), internal/grid-forming
voltage fields, controller profiles, `p_avail`, prices, custom roles and DC
coupling remain unassessed, including explicit zero/false filter declarations.
The native filter-boundary comparison has unchanged variable/constraint counts
with these fields present. Ignoring them is not evidence that a filter is ideal
or adequate, so the audit refuses the declaration. False `dc_link_coupled` is
admitted as the uncoupled default. Recognized `prime_mover` enum values are
metadata without PV, battery-dynamics or STATCOM physical guarantees. Native
power-flow construction omits `s_max` capability circles; supplied-point cap
compliance does not establish that a chosen native problem enforced them.
Selected objectives, custom constraints and local/global optimality remain
outside the electrical point audit.

The running input contains no IBR. Its retained default three generator
`p_max` failures with zero unknowns, all 26 passing KCL rows and passing aggregate
power, and its separate tighter electrical pass remain unchanged. Published
integration, PSK implementation statuses and execution MCP remain separate.

**Transfer exercise.** For each topology, state the meaning of a supplied
`cri/cii`, write its ordered power voltage and reconstruct the terminal
injections. Then decide which extra evidence is needed for a physical
terminal-current rating, a filter model or a DC-coupled energy guarantee.

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

The separate candidate `audit_solution` now adds default-role source neutral
returns, implicit source grounding and WYE/SINGLE_PHASE/DELTA constant-power
load equations, fixed ideal switches, a bounded WYE/SINGLE_PHASE generator
domain, ordinary phase-to-earth and explicit-neutral phase-to-neutral voltage
bounds, applicable scalar neutral-to-earth caps, fixed single-coil transformers,
and matched WYE/DELTA winding-list equations with explicit rating-metadata
semantics. The same running-network result now has **29 unassessed rows**
(33 before the neutral-to-earth audit below):
11 local power equations across five loads and the source voltage relation are
now evaluated. Source-return and load-terminal currents are reconstructed from
their connection maps; each explicit or implicit earth reaction is consumed once.
The switch now has a checked closed-voltage relation and four conductor current
limits; its opposite endpoint currents are reconstructed from the supplied
from-side currents. The 42-row table above remains the coverage of
`audit_linear_solution`.

The extended verdict is still **indeterminate**. The running-network generator
has a cost field outside this audit slice; phase-to-phase voltage
limits also remain unassessed. The winding-list transformer now has checked
coil equations, leakage, current caps and reconstructed terminal incidence. Its
`s_rating` is retained as metadata, not an added apparent-power limit. The 28 ordinary
phase-to-earth voltage-bound rows and four neutral-to-earth caps are now checked. All 26
terminal KCL rows and aggregate power remain unassessed because required current
contributions are still missing. The companion records both APIs on the same solved point;
no zeros are supplied to close the remaining obligations. The
[delta coil lesson](@ref delta-coil-current-lesson) explains why successful KCL
would still not replace the individual load equations.

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

For the finite native WYE/SINGLE_PHASE domain, generator power uses the explicitly
mapped coil voltage. Omitting the neutral from a WYE generator map does not
borrow the bus neutral. A two-terminal SINGLE_PHASE generator uses its ordered
pair, which may also be phase-to-phase. DELTA generators remain outside this
slice: the load's two-terminal DELTA convention must not be copied into another
device family without checking that family's executable contract.

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
nonfinite/malformed arrays, generator costs/controllers and unsupported transformer checks
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
the supported domain. The running network remains indeterminate.

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
rating-metadata trace below handles `s_rating` separately; the current running
network retains 29 unassessed obligations. The published package pin and execution
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
as metadata. The audit has 29 unassessed obligations and remains
**indeterminate** because other declarations, including generator cost and
unsupported voltage families, remain open. Physical adequacy, objectives,
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
phase-to-phase, angle and sequence limits remain separate audit work. The existing running network has no
PN-bound declarations, so its 29 unassessed obligations remain unchanged. The
published integration pin and execution MCP surface are unchanged.

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
from 33 to 29 without deleting input fields. Generator cost, phase-to-phase
limits and incomplete KCL/power coverage still make the result **indeterminate**.
The published integration pin, PSK implementation statuses, physical adequacy
and execution MCP exposure remain separate.

**Transfer exercise.** Give the neutral-voltage and neutral-conductor-current
magnitudes for both return circuits above. Explain which additional model and
state data distinguish them, why a finite shunt does not skip `vn_max`, and why
a successful source-grounded solve does not turn its skipped cap into a passed
limit.

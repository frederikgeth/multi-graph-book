# [IBR power-factor, Volt-var and Volt-watt controls](@id ibr-pf-control-audit)

**Page status:** self-checked control equations and examples for a local development candidate; physical controller validation remains open.

An inverter-based resource (IBR) may have both a control law and capability
limits. Can a supplied point satisfy them together? Work from the declared
equations and check each obligation. A solver label or reported power cannot
settle that intersection.

The code examples require the local candidate identified in
`experiments/integration/linear-audit-candidate.json`. The published integration
does not provide these audit APIs. The [workbook environment
table](@ref running-case-evidence-generations) gives the separate execution routes.
The evaluator checks equations under the `PSK-000013` boundary; it does not
validate physical controller behavior or the selected objective. Its calculations
do not use the native model builder or reported powers as their oracle.

## Two declarations, two mathematical objects

Constant PF fixes a signed relationship between injected P and Q. Minimum PF
bounds a generation-only operating envelope. Neither replaces authored P/Q/I/S
capability limits.

**Predict:** an IBR injects P = 4 W under constant PF 0.8, with minimum PF 0.8
and `q_min=-2` var. Can its controller satisfy the case simply by clipping Q
to −2 var?

Use RMS phasors. Positive P and Q denote injection into the network. For each
admitted ordered voltage/current pair, the audit recomputes

```math
S_k=U_k\overline{I_k}=P_k+\mathrm jQ_k.
```

It does not recover current by dividing reported power by voltage. The PF audit
covers two-endpoint `SINGLE_PHASE`, explicit-neutral `FOUR_LEG`,
and exactly three cyclic-coil `THREE_LEG` connections. Constant and minimum PF
are checked per branch. Volt-var and Volt-watt, separately or together, apply
only to the single-pair and explicit-neutral four-leg models. In a cyclic model,
coil current differs from reconstructed terminal current; the physical adequacy
of the `THREE_LEG` convention remains unresolved.

The following JSON blocks are network-field excerpts; the runnable fixture
supplies the complete bus and device data. A pure constant-PF declaration is:

```json
"control_profile": {
  "pf": {"power_factor": {"pf": 0.8}}
}
```

The IBR refers to it with `"control_profile":"pf"`. For a finite signed target
``f`` satisfying ``0<|f|\le1``, define

```math
a=|f|,\qquad b=\sqrt{(1-a)(1+a)}.
```

The native equality and independent weighted residual are

```math
\operatorname{sign}(f)aQ_k+bP_k=0,\qquad
r_k^{\mathrm{constant}}=
\left|\operatorname{sign}(f)aQ_k+bP_k\right|.
```

This signed target convention belongs to the declared controller, not to every
data format. At positive P, positive f absorbs reactive power (negative Q),
while negative f reverses that sign. Both signed unity targets require Q = 0. The equality alone
also admits the signed absorption extension with negative P; it does not impose
generation direction. No tangent or `acos` evaluation is needed, including near
zero targets.

For ``0<m\le1`` and ``c=\sqrt{(1-m)(1+m)}``, the native constraints are

```math
P_k\ge0,\qquad mQ_k\le cP_k,\qquad -mQ_k\le cP_k.
```

The corresponding independent residuals are

```math
r_k^{\mathrm{generation}}=\max(0,-P_k),\quad
r_k^{+}=\max(0,mQ_k-cP_k),\quad
r_k^{-}=\max(0,-mQ_k-cP_k).
```

Generation residuals use W; constant and weighted reactive residuals use VA.
All use the absolute SI `power_tol` setting. The checks use the actual injected
power computed from supplied V/I, not `p_max`, nameplate power, available PV
power or optional reported `pg/qg`.

## Capability is an intersection

For P = 4 W and f = 0.8, the constant-PF equality gives Q = −3 var. That point
also lies on the m = 0.8 minimum-PF boundary. It violates `q_min=-2` by 1 var.
Clipping Q to −2 at P = 4 would violate the constant-PF equality instead.

| Supplied point or native comparison | Observation |
|:--|:--|
| P = 4 W, Q = −3 var, f = m = 0.8 | Both controls pass; `q_min=-2` fails by 1 var |
| P = 4 W, Q = +3 var, f = +0.8 | Constant-PF weighted excess is 4.8 VA; the minimum envelope itself permits either Q sign |
| Minimum-only P = 0 W, Q = 1 var, m = 0.8 | Upper weighted excess is 0.8 VA |
| Native maximum-P comparison with f = m = 0.8 and `q_min=-2` | P = 8/3 W and Q = −2 var at the Q-cap intersection |

Native supplied-point inspection confirms the Q-cap violation at the first
point. A separate fixed-P conflict attempt retains its termination, primal and
raw statuses, returned point and independent audit. It is not a global
infeasibility certificate. The maximum-P comparison is a bounded native recipe,
not a general selected-objective or optimality check.

These are per-branch constraints. In a four-leg minimum-only fixture, ordered
powers P = [1,10,10] W and Q = [3,0,0] var have aggregate PF
``21/\sqrt{21^2+3^2}>0.8``. The first phase still violates its own upper envelope
by 1.8 VA. Reordering the map moves that violation with its physical phase;
neutral position does not create or remove a PF slot. Signed single-pair reversal
preserves its power and control obligations when its current is negated.

## Zero power and small coefficients

At P = Q = 0, both the equality and envelope are satisfied. A PF quotient there
is undefined; the audit assigns none. At unity minimum PF, Q must be zero, and
the separate P ≥ 0 row still matters: negative P with zero Q can satisfy both
reactive rows while failing generation direction.

A fixed absolute weighted tolerance does not certify a PF ratio. For example,
at m = ``10^{-20}``, P = 0 W and Q = 1 var, the upper weighted excess is only
``10^{-20}`` VA. It passes the default ``10^{-6}`` VA tolerance but fails at
``10^{-22}`` VA. Exact envelope membership would require Q = 0 at P = 0, yet
finite-tolerance weighted checks alone do not establish that exact property.
Tiny constant-PF targets have the same distinction: bounded coefficients avoid
tangent overflow but do not make a fixed residual tolerance scale-free.

The independent audit evaluates the stated native constraints without division
by P or apparent power. It does not substitute the existing reported-P/Q
profiler's special zero-P rule or relative tolerance. These are different
numerical checks with explicit obligations, not interchangeable PF certificates.

## Applicability and missing evidence

Minimum PF is a separate package-owned policy in the schema's extras namespace:

```json
"extras": {
  "bmopftools": {
    "minimum_power_factor": {
      "schema": "bmopftools.minimum_power_factor/v1",
      "ibr": {
        "i": {"pf_min": 0.8, "direction": "generation", "scope": "per_coil"}
      }
    }
  }
}
```

The admitted profile contains only `power_factor`, whose object contains only
`pf`. The minimum-policy wrapper and per-IBR requests have exactly the fields
shown above. Targets must be finite, nonzero and representable in Float64;
constant targets may have either sign and minimum targets are positive.
Minimum-policy applicability additionally requires full finite nonnegative
`p_min`, and `p_max` if present, plus a compatible constant target
``|f|\ge m``. A constant target below the requested minimum is rejected by native
construction; its bounded audit reports unknown policy applicability rather than
inventing a constructed constraint or a numerical feasibility failure. The point P = Q = 0
still satisfies both weighted laws even for such targets.
The construction policy is therefore stricter than algebraic intersection;
additional bounds would be needed to exclude that point.

Unresolved/null references, empty/extra profiles, PF/droop mixtures, malformed policies,
unknown targets and unused invalid profiles remain visible as unassessed control
declarations. Known V/I powers, capability checks and current incidence survive
those control-only unknowns. A valid constant equality can still be evaluated
when a separate minimum request is malformed. Unrelated extras namespaces or
package fields remain unsupported and suppress complete network KCL/power;
they are not accepted through the new policy path.

Missing required branch current or voltage leaves its control residual unknown,
while known failures on other branches survive. Complete network KCL/power is
suppressed when current/state contributions cannot be established. Optional P/Q
reports are separate consistency checks: forging Q cannot repair a control
failure computed from the supplied voltage and current.

The package-owned `examples/ibr_pf_audit.jl` and fixture
`test/data/linear_audit/ibr-pf.json` supply the source-bound computational route.
In the locked run, the six controlled SI/per-unit cases solve and pass their
scoped audits. The fixed-P/Q-cap conflict reports `LOCALLY_INFEASIBLE` and its
returned-point audit fails one check with zero unknowns. These are local recipe
observations, without a global infeasibility or initialization guarantee.
The examples include analytic points, native SI/per-unit attempts, signed/unity/zero
boundaries, hard-Q capability intersection, per-coil and partial-observation
witnesses, and native primal inspection. Adding constant PF plus minimum PF adds
four native constraints per branch and no variables. Native helpers, role/index
resolvers, control decoders and reported-power profilers are not used as the
independent audit's oracle.

Filters, internal/grid-forming voltages and DC dynamics need other models.
The running network contains no IBR, so its audit does not exercise these
controllers; use the dedicated fixtures above.

**Transfer exercise.** Distinguish a constant-PF equality, a generation-only
minimum envelope and an authored Q cap. Construct a per-phase violation hidden
by an aggregate check, then explain what a weighted residual pass at tiny m can
and cannot establish about an actual PF ratio.


## [Volt-var: requested graph and assumed smooth model](@id ibr-volt-var-audit)

A Volt-var law links reactive injection to a measured voltage. Here it uses a
pure `volt_var` profile on `SINGLE_PHASE` or explicit-neutral `FOUR_LEG`. Check
the voltage monitor, static curve, Q capability and minimum-PF envelope
separately. The supplied result does not reveal the solver's smoothing recipe.

### State the graph and normalization first

A bounded profile has four positive, finite, strictly increasing breakpoints
``x_1<x_2<x_3<x_4`` in **SI volts**, and
`q_limits=[q_absorb,q_inject]` with ``q_{\mathrm{absorb}}\le0\le q_{\mathrm{inject}}``.
Only `q_unit=VA_FRACTION` and `q_ref=VAR_MAX` are admitted. Despite that reference
label, native normalization uses **each branch's `s_max`**, not `q_max`, total
three-phase power, available P or a measured reactive capability. Fractions
alone do not establish a rating guarantee; P/Q/I/S caps remain separate.

The requested graph is constant at ``q_{\mathrm{inject}}`` below ``x_1``, falls
linearly to zero at ``x_2``, stays zero through ``x_3``, falls linearly to
``q_{\mathrm{absorb}}`` at ``x_4`` and stays there above ``x_4``. Multiplication by
the branch's ``S_{\max,k}`` produces its requested PWL target in var.

**Predict:** at U = 9 V, breakpoints [8,9,11,12] V, fractions [−0.6,0.44] and
`S_max=20` VA, the requested target is Q = 0. Does that establish the reactive
equality imposed by a smoothed native model?

The first supported model assumption is the native `user_defined` softplus
encoding with an explicit positive relative width ``\rho``. In physical volts,

```math
\epsilon=\rho\frac{x_1+x_2+x_3+x_4}{4},\qquad
s_\epsilon(z)=\epsilon\log(1+\exp(z/\epsilon)).
```

The declared static smooth target is

```math
\begin{aligned}
Q_k^{\mathrm{model}}&=S_{\max,k}q_{\mathrm{inject}}\\
&\quad-\frac{S_{\max,k}q_{\mathrm{inject}}}{x_2-x_1}
 [s_\epsilon(U-x_1)-s_\epsilon(U-x_2)]\\
&\quad+\frac{S_{\max,k}q_{\mathrm{absorb}}}{x_4-x_3}
 [s_\epsilon(U-x_3)-s_\epsilon(U-x_4)].
\end{aligned}
```

For the prediction's point and ``\rho=0.02``, ``\epsilon=0.2`` V and the
smoothed target is approximately **1.208 var**. A supplied point on the requested
Q = 0 graph fails that smooth equality, despite valid voltage/current balance.
The requested graph and the smooth model are different obligations. Smoothing
can change the response on either side of the zero band; no conservative-Q-cap
or one-sided target guarantee is inferred.

### Make the model assumption explicit

The network and supplied result do not establish the native build's global
`volt_var_watt_eps`, softplus mode or later coefficient updates. The Julia audit
therefore requires a separate declaration before assessing smooth equality:

```julia
audit_solution(net, result; volt_var_model=Dict(
    "schema" => "bmopftools.audit.volt_var_model/v1",
    "softplus" => "user_defined",
    "volt_var_watt_eps" => 0.02))
```

This is an **unauthenticated assumption**, not a recovered build certificate.
A profile alone does not silently select the default native width. Omitting or
malforming the declaration leaves the smooth equality unassessed while retaining
known capability checks, current incidence and the requested PWL diagnostic.
A recipe placed in the supplied result or a successful solver label is not used
as authority. The fixed-linear API does not certify these controller assumptions.

Each numerical row exposes monitored V, the requested PWL target, assumed smooth
target, smoothing width in V, target difference, base VA, VI-derived Q and an
absolute var residual under `power_tol`. `build_recipe_authenticated` and
`live_coefficient_updates_checked` remain false. Selected/reported objective and
optimality flags retain the earlier boundary.

The independent evaluator derives these equations without the native curve,
smoothing, role/index or profiler helpers. High-precision scalar arithmetic
reduces cancellation in the declared static formula; finite coefficient and
operator-argument checks refuse unsupported representation ranges. This is not
a general floating-point/backend, derivative-range or convergence certificate.
Builtin and Swish modes, exact-PWL build recipes and live coefficient providers
remain outside this first slice. A native mode name is not interchangeable with
another mathematical surrogate.

### Voltage references and averaging have their own incidence

| Topology/reference | Monitored physical voltage |
|:--|:--|
| `SINGLE_PHASE`, PN or PP | Magnitude of its ordered endpoint difference |
| `SINGLE_PHASE`, PG | Magnitude of its first endpoint's earth/frame phasor |
| `FOUR_LEG`, PN | Each phase minus its explicitly mapped neutral |
| `FOUR_LEG`, PG | Each phase's earth/frame phasor |
| `FOUR_LEG`, PP | Each phase minus the next phase cyclically, after removing the neutral from map order |

The six admitted reference values combine PN/PG/PP with `PER_PHASE` or
`AVERAGED`. An omitted profile reference has the documented `PN_PER_PHASE`
default, recorded as a default. Invalid references stay unassessed; native
warning-and-fallback paths are not accepted as the authored control.

For averaged control, the monitor is **the mean of the magnitudes**, not the
magnitude of the mean phasor. Each branch still uses its own `s_max`; the ratings
are not averaged. An explicit IBR `voltage_aggregation=AVERAGE` or `PER_PHASE`
overrides the profile's aggregation. A single pair has only one magnitude, so
averaging does not create a new voltage reference. The four-leg one-phase PP
fallback to PG is refused, and native `THREE_LEG` droop skipping is not a checked
Volt-var law. The physical adequacy of the cyclic `THREE_LEG` model remains unresolved.

The floating-neutral witness makes the distinction visible: a single pair has
PN magnitude 9 V but first-endpoint PG magnitude ``\sqrt{12^2+4^2}`` V.
They legitimately demand different Q. Four-leg cases test all six references,
non-last neutral position, arithmetic magnitude averaging and both legacy
overrides. Native supplied-primal inspections agree for those constructed
floating-neutral cases. Missing one monitored phase leaves an averaged monitor
unknown; no partial mean is substituted. In per-phase mode, known other phase
observations and failures survive.

### Hard limits and minimum PF remain intersected

The healthy single-pair point has P = 4 W and Q approximately 1.208 var under
the declared smooth law. Setting `q_max=0.2` var rejects the point even though
its droop equality passes. Lowering actual P to 0.2 W also makes that Q violate
the generation-only minimum-PF 0.8 envelope. Available power, `p_max` or nominal
rating cannot replace that curtailed P in the minimum-PF check.

The model does not clip Q to either bound. The source-bound recipe retains
native fixed-voltage Q-cap and minimum-PF conflict attempts, with termination,
primal/raw status, returned points and independent audits. In the locked run,
both conflict attempts report `LOCALLY_INFEASIBLE`; their returned audits fail
two and one checks respectively with zero unknowns. Those local outcomes
are not global infeasibility or unrestricted controller-feasibility certificates.

Changing a reported `qg` does not repair or break a control equality computed
from supplied V/I; the report gets its separate consistency check. Missing
current can leave the monitor and requested graph known while the Q residual
stays unknown. Missing voltage/current contributions still suppress complete
network KCL/power. Malformed control declarations preserve known hard-limit
violations rather than dropping fields or returning zero residuals.

At zero voltage, a finite nonzero supplied current gives Q = 0. This low-voltage
curve still requests approximately 8.8 var, so its equality fails. No current is
recovered by dividing that target by zero voltage, and no clipping or zero-Q
fallback is invented.

### Computational scope

`examples/ibr_volt_var_audit.jl` and `test/data/linear_audit/ibr-volt-var.json`
provide the package-owned route included by the book's source-bound companion.
It compares analytic points, native SI/per-unit solves under the declared
smoothing recipe, requested-PWL versus smooth points, floating-reference primal
inspections, aggregation overrides and retained capability/minimum-PF conflicts.
Scaling voltage and breakpoints together also checks the physical smoothing
width transformation; it is not an all-asset network-equivalence claim.

The [combined audit](@ref ibr-droop-composition-audit) adds Volt-watt without
replacing these obligations. PF/droop mixtures, unsupported references, units
and topologies, filters and DC dynamics remain outside this model. A native
warning that skips a declaration does not establish compliance with it.

**Transfer exercise.** Distinguish requested PWL response, assumed smoothed
response, reported Q and actual VI-derived Q. Then change averaging or curtail P
without relaxing a Q cap or minimum-PF policy, and identify which observations,
model assumptions and failure evidence must be retained.


## [Volt-watt: a cap with a declared normalization base](@id ibr-volt-watt-audit)

Volt-var fixes Q under an assumed model; Volt-watt limits P from above. A point
below the cap may comply. It need not sit on the curve, and curtailment is not
an equality to available power.

**Predict:** a single-pair converter has Smax = 20 VA, authored `p_max=10` W,
scalar `p_avail=1` W and actual P = 4 W. With no availability-based controller,
does that scalar alone reject P = 4 W?

The candidate admits pure `volt_watt` profiles on the same `SINGLE_PHASE` and
explicit-neutral `FOUR_LEG` domains as Volt-var. The declaration is:

```json
"control_profile": {
  "vw": {"volt_watt": {
    "breakpoints": [9.0, 11.0], "p_limits": [0.2, 1.0],
    "p_unit": "VA_FRACTION", "p_ref": "S_MAX",
    "voltage_reference": "PN_PER_PHASE"
  }}
}
```

The IBR references `"control_profile":"vw"`. Two finite positive strictly
increasing knots are SI volts. Fractions are finite, nonnegative and ordered
`[low,high]`; the audit does not invent an upper limit of one. The requested
clamped graph is

```math
C_{\mathrm{PWL},k}(U)=B_k\begin{cases}
p_{\mathrm{high}},&U\le u_1,\\
p_{\mathrm{high}}+(p_{\mathrm{low}}-p_{\mathrm{high}})
\dfrac{U-u_1}{u_2-u_1},&u_1<U<u_2,\\
p_{\mathrm{low}},&U\ge u_2.
\end{cases}
```

The default `p_unit="VA_FRACTION"` is the admitted unit convention. The base
must be explicit and complete for its selected reference:

| `p_ref` | Normalization base for branch k | Separate obligation |
|:--|:--|:--|
| `S_MAX` (default) | `s_max[k]`, in VA | Branch apparent-power cap remains hard. |
| `P_MAX` | `p_max[k]`, in W | Authored active-power box still applies. |
| `P_AVAILABLE` | Scalar `p_avail` divided by non-neutral mapped-terminal count, in W | This normalization does not author a direct availability cap. |

Missing, prefix, extra, negative or nonfinite bases remain unassessed. Native
zero fallbacks for missing normalization data do not establish compliance with
the intended declaration. Empty or absent `p_max` still means no authored P box
in the injection audit; it cannot supply a `P_MAX` normalization base.

### Requested graph, assumed smooth cap and hard box

The six PN/PG/PP per-phase/averaged monitors and legacy aggregation precedence
are the same as in [Volt-var](@ref ibr-volt-var-audit). There is no partial
average on missing observations and no inferred one-phase PP fallback or
`THREE_LEG` droop. An independent static softplus cap requires:

```julia
audit_solution(net, result; volt_watt_model=Dict(
    "schema" => "bmopftools.audit.volt_watt_model/v1",
    "softplus" => "user_defined",
    "volt_var_watt_eps" => 0.02))
```

Let the relative width be rho, epsilon = rho times the mean of the two SI knots,
and let s be the softplus hinge defined above. The assumed cap and residual are

```math
\begin{aligned}
C_{\epsilon,k}(U)&=B_kp_{\mathrm{high}}\\
&\quad+\frac{B_k(p_{\mathrm{low}}-p_{\mathrm{high}})}{u_2-u_1}
\bigl[s_\epsilon(U-u_1)-s_\epsilon(U-u_2)\bigr],\\
r_k&=\max(0,P_k-C_{\epsilon,k}(U_k)).
\end{aligned}
```

The residual has units W under absolute `power_tol`. The independent P comes
from supplied ordered V/I. Each row retains the requested PWL cap, assumed
smooth cap, physical smoothing width, selected base, observed P and effective
upper cap. With a known authored `p_max`, that last cap is the minimum of the
box and smooth curve. A malformed box leaves the intersection unknown while
the independently known curve can still pass or fail. Hard lower P, Q/I/S and
actual-P minimum-PF checks remain separate.

For the declaration above with base 20 VA and epsilon = 0.2 V:

| Monitor U | Requested PWL cap | Assumed smooth cap | Controlled point |
|:--|--:|--:|:--|
| 9 V | 20 W | approximately 18.891 W | P = 20 W passes the PWL cap but fails the smooth cap. |
| 11 V | 4 W | approximately 5.109 W | P = 5 W passes the smooth cap but exceeds the PWL cap. |

At U = 9 V, P = 4 W passes below the cap. Tightening `p_max` to 3 W rejects
that point despite a passing curve row. A separate native maximum-P comparison
returns approximately 3 W under that hard box. With `P_MAX` and the original
10 W box, the corresponding native comparison reaches approximately 9.446 W.
The comparison fixes P through an added constraint on the public power
expression, preserving the original `p_max`; changing the box to fix dispatch
would change a `P_MAX`-normalized model.

The recipe is an unauthenticated assumption. A result's `modeled_volt_watt`
coefficient rows and reported cap are comparison data, not the independent
oracle. Omitting or rejecting the recipe leaves smooth-cap compliance unknown
while preserving requested PWL diagnostics, known boxes and current incidence.
Mathematical high-precision hinge evaluation and finite-range guards do not
certify backend arithmetic, derivatives or convergence. The native constructor
has one global smoothing width; differing declared widths for separately used
Volt-var and Volt-watt families create an unknown compatibility obligation,
while preserving their individually assessed assumed equations.

### Availability is an input declaration with provenance

**Resolve the prediction:** scalar `p_avail=1` W alone does not enforce P <= 1 W.
The metadata-only P = 4 W case passes both the independent audit and a controlled
native solve with the 10 W box. The audit records the scalar but does not
authenticate a resource fact, PV model or energy guarantee over time.
Its presence also does not establish a particular augmentation recipe.

The native `P_AVAILABLE` divisor counts non-neutral mapped terminals. One
phase-neutral pair has divisor one; one phase-to-phase `SINGLE_PHASE` coil has
divisor two. The same scalar 12 W therefore produces bases 12 W and 6 W in
those cases. At U = 9 V with the example fractions and width, P = 8 W passes
the phase-neutral cap and fails the phase-to-phase cap. This is an indexing
applicability observation about the candidate implementation, not a physical
allocation rule inferred from coil count.

Three-phase `FOUR_LEG` uses divisor three even with its neutral first in the
map. The scalar 12 W produces [4,4,4] W bases. An explicit augmentation can
instead derive a missing `p_max` proportionally to `s_max`: ratings [20,12,10]
VA give approximately [5.714,3.429,2.857] W. Scenario operations can scale
availability and write new boxes subject to equipment/authored ceilings. Those
are distinct transformations; this audit does not call them or invent missing
P limits. Audit the resulting network and retain its transformation provenance
separately. Native SI/per-unit comparisons preserve the scalar in W and divide
by the local power base once.

`examples/ibr_volt_watt_audit.jl` and `test/data/linear_audit/ibr-volt-watt.json`
are included by the source-bound companion. They compare all three bases in
SI/per-unit, floating-reference primal points, both smooth corners, hard-box
intersection, metadata-only availability and the phase-pair divisor. Malformed
curves/bases, forged coefficient rows and partial observations preserve known
failure evidence. PF/droop mixtures,
`THREE_LEG` droop, unsupported native warning/fallback paths, builtin/Swish/live
updates, filters/internal voltages and physical availability/DC dynamics remain
outside this model.

**Transfer exercise.** Change a scalar availability declaration without changing
an authored P box, then change the curve from `S_MAX` to `P_AVAILABLE`. Explain
which cap changes. Repeat with a phase-to-phase pair and with an explicitly
augmented network, retaining the distinct base, divisor and provenance.


## [Combined droop: intersected obligations and monitor applicability](@id ibr-droop-composition-audit)

A profile containing exactly both `volt_var` and `volt_watt` now composes the
bounded single-pair and explicit-neutral four-leg audits. The two subobjects
retain their own knots, fractions, reference and normalization. Volt-var imposes
its assumed Q equality; Volt-watt adds its assumed P upper cap. Neither law
replaces a hard capability limit or applicable minimum-PF envelope.

**Predict:** at fixed U = 9 V, the earlier Volt-var law requests approximately
Q = 1.208 var. A `P_AVAILABLE`-based Volt-watt cap permits approximately
0.970 W. Can a generation-only minimum PF of 0.8 be met by curtailing P further?

For a fixed monitored state, write the assumed family responses as Q = q(U) and
P <= c(U). With minimum PF m strictly between zero and one, its weighted
inequalities require

```math
P\ge\frac{m|q(U)|}{\sqrt{1-m^2}},\qquad P\ge0.
```

If an apparent-power cap is present and ``|q(U)|\le S_{\max}``, it additionally
requires

```math
P\le\sqrt{S_{\max}^2-q(U)^2}.
```

The available P interval must also intersect the authored P box and c(U).
If ``|q(U)|>S_{\max}``, that circle cannot admit the requested Q. At m = 1,
minimum PF instead requires Q = 0 and P >= 0; the divided expression above is
inapplicable. These are fixed-state branch implications, not a sufficient
network-feasibility test. Individual and shared-return current caps, other
branches, KCL and the rest of the network still apply. The implementation checks
the original weighted residuals and supplied V/I; it does not use this divided
formula as its oracle or assign a PF quotient at zero power.

**Resolve the prediction:** Q approximately 1.208 var requires P at least
approximately 1.611 W under that minimum PF. A 0.970 W upper cap cannot meet it
at this voltage under the declared models. A supplied P = 0.5 W point passes
both droop rows and fails the minimum-PF upper inequality. Further curtailment
does not fix the reactive demand. The native fixed-P conflict attempt retains
its local solver status and returned-point audit; it is not a global solver
infeasibility certificate.

The companion also retains a Q-box conflict and an apparent-power-circle
conflict. In the latter, `s_max=4` VA reduces the Volt-var normalization target
to approximately 0.242 var, while a `P_MAX`-normalized Volt-watt cap still admits
P = 4 W. The apparent power exceeds 4 VA even though both control rows pass.
The controller is not clipped to the circle. Actual P, Q and ordered current
observations remain separate from reported `pg`/`qg` fields.

### Separate model assumptions and partial evidence

Both earlier Julia keywords are required independently for their respective
smooth-law residuals. The native build has one relative `volt_var_watt_eps`, so
those declared relative widths must agree. The physical widths need not agree:
Volt-var knots [8,9,11,12] V have mean 10 V, while Volt-watt knots [9,13] V have
mean 11 V. A shared relative width 0.02 gives epsilon values 0.2 V and 0.22 V.
Using one physical epsilon for both would describe a different pair of laws.

A missing or unsupported family recipe leaves that law unknown while retaining
the other known law, requested-graph diagnostic, hard limits and current
incidence. An unequal pair of declared relative widths adds an unknown global
compatibility obligation; it does not erase the individually evaluated assumed
responses. The declarations still do not authenticate an actual build or live
coefficient updates.

The combined profile decoder likewise retains a known family when the other
family's curve or selected normalization base is malformed. The incomplete
combination and its minimum-PF applicability stay unknown; known other-family
failures and electrical contributions survive. A mixture containing
`power_factor` or extra profile fields remains unassessed. Native PF priority or
a warning that skips a requested curve is not a compliance argument.

### Native monitor sharing retains controller-specific inputs

Each family independently selects PN, PG or PP, and per-phase or averaged
monitoring. Equal references can share native magnitude variables; different
quantities need distinct observations. Sharing a static profile ID does not make
two devices share voltage state, rating, availability, terminal order or local
coordinate bases.

The earlier candidate's duplicate-key failure came from caching physical
magnitudes by aggregation (review R2). The repaired candidate shares magnitude
definitions while registering each controller's input: Volt-var `PN_PER_PHASE`
can use individual magnitudes while Volt-watt `PN_AVERAGED` uses their mean.
Sharing an observation does not identify the laws.

| Reference combination | Candidate native observation | Independent audit scope |
|:--|:--|:--|
| Same quantity, same effective averaging | Shared monitor objects in the controlled build | Both declared-law residuals remain separate. |
| Different quantities | Distinct monitor objects | Each law uses its own physical observation. |
| Four-leg, same quantity, different effective averaging | Shared magnitude variables, separate controller inputs | Each law retains its own aggregation; hard limits and KCL remain independent. |
| A valid legacy override unifies averaging | Shared monitors build in the controlled case | Both laws use the common overridden averaging. |
| Single pair with differing averaging requests | Aggregation is moot | PG uses the first endpoint; PN/PP use the pair difference. |

The package route `examples/ibr_droop_composition_audit.jl` with fixture
`test/data/linear_audit/ibr-droop-composition.json` builds all 36 reference pairs
per bounded topology. It also compares all three P bases in SI/per-unit, legacy
overrides, missing recipes, capability/PF conflicts and device-specific bases.
Unbalanced floating-neutral tests check individual and mean inputs and unique
magnitude definitions in both coordinate systems. These repair the recorded
constructor boundary; residuals still do not authenticate a build or recipe.
Native objects are comparison evidence, never the independent evaluator's oracle.

Parameterized/live providers and profile caches, physical controller/filter/DC
adequacy, `THREE_LEG` droop, selected objectives and optimality remain outside
this audit.

**Transfer exercise.** Change one curve's voltage reference, then override
averaging. Identify the changed observation, residual and build applicability.
Explain why passing controls alone certify neither capability, network
feasibility nor an authenticated build.

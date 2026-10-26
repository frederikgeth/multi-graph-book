# [IBR power-factor and Volt-var controls](@id ibr-pf-control-audit)

**Page status:** self-checked local candidate control-equation and applicability witnesses; no general controller, physical-model, PF-ratio accuracy or optimality certificate.

This lesson extends the local candidate's [IBR injection audit](numerical-consequences.md#ibr-injection-audit).
Its evidence is a supplied-point equation check under the `PSK-000013`
verification boundary. Native construction, reported powers and solver status
are comparison subjects. They are not the independent evaluator's oracle.
The [IBR price declaration boundary](numerical-consequences.md#ibr-price-scope-audit)
also remains in force: electrical control checks do not select or verify an
objective.

## Two declarations, two mathematical objects

Constant PF fixes a signed relationship between injected P and Q. Minimum PF
bounds a generation-only operating envelope. Neither replaces authored P/Q/I/S
capability limits.

**Predict:** an IBR injects P = 4 W under constant PF 0.8, with minimum PF 0.8
and `q_min=-2` var. Can its controller satisfy the case simply by clipping Q
to −2 var?

For the ordered voltage/current pair admitted by the topology, the independent
audit recomputes

```math
S_k=U_k\overline{I_k}=P_k+\mathrm jQ_k.
```

It does not recover current by dividing reported power by voltage. The bounded
slice admits the existing two-endpoint `SINGLE_PHASE`, explicit-neutral
`FOUR_LEG`, and exactly three cyclic-coil `THREE_LEG` domains. Every control
below applies to each ordered branch. A coil current and reconstructed terminal
current remain different observations in the cyclic model; physical
`THREE_LEG` review #95 is unresolved.

A pure constant-PF declaration has exactly this structure:

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

At positive P, positive f absorbs reactive power (negative Q), while negative f
reverses that sign. Both signed unity targets require Q = 0. The equality alone
also admits the signed absorption extension with negative P; it does not impose
generation direction. No tangent or `acos` evaluation is needed, including near
zero targets.

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

The admitted profile contains only `power_factor`, whose object contains only
`pf`. The minimum-policy wrapper and per-IBR requests have exactly the fields
shown above. Targets must be finite, nonzero and representable in Float64;
constant targets may have either sign and minimum targets are positive.
Minimum-policy applicability additionally requires full finite nonnegative
`p_min`, and `p_max` if present, plus a compatible constant target
``|f|\ge m``. A constant target below the requested minimum is rejected by native
construction; its bounded audit reports unknown policy applicability rather than
inventing a constructed constraint or a numerical feasibility failure.

Unresolved/null references, empty/extra/mixed profiles, droop, malformed policies,
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

Filters, internal/grid-forming voltages, other droop/availability/DC dynamics, physical
model adequacy, arbitrary custom constraints and selected-objective/optimality
verification remain separate. The running input has no IBR: its retained default
three generator-bound failures with zero unknowns, all 26 passing KCL rows and
aggregate power, and its separate tighter electrical pass are unchanged. The
published integration pin, PSK implementation statuses and execution MCP are
unchanged by this local candidate.

**Transfer exercise.** Distinguish a constant-PF equality, a generation-only
minimum envelope and an authored Q cap. Construct a per-phase violation hidden
by an aggregate check, then explain what a weighted residual pass at tiny m can
and cannot establish about an actual PF ratio.


## [Volt-var: requested graph and assumed smooth model](@id ibr-volt-var-audit)

The next local candidate slice admits a pure `volt_var` profile on the existing
`SINGLE_PHASE` or explicit-neutral `FOUR_LEG` topology. It independently checks
the voltage monitor, static curve, hard Q capability and applicable minimum-PF
envelope. It does not infer the solver's smoothing recipe from a supplied result.

### State the graph and normalization first

A bounded profile has four positive, finite, strictly increasing breakpoints
``x_1<x_2<x_3<x_4`` in **SI volts**, and
`q_limits=[q_absorb,q_inject]` with ``q_{\rm absorb}\le0\le q_{\rm inject}``.
Only `q_unit=VA_FRACTION` and `q_ref=VAR_MAX` are admitted. Despite that reference
label, native normalization uses **each branch's `s_max`**, not `q_max`, total
three-phase power, available P or a measured reactive capability. Fractions
alone do not establish a rating guarantee; P/Q/I/S caps remain separate.

The requested graph is constant at ``q_{\rm inject}`` below ``x_1``, falls
linearly to zero at ``x_2``, stays zero through ``x_3``, falls linearly to
``q_{\rm absorb}`` at ``x_4`` and stays there above ``x_4``. Multiplication by
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
Q_k^{\rm model}=S_{\max,k}q_{\rm inject}
-\frac{S_{\max,k}q_{\rm inject}}{x_2-x_1}
 [s_\epsilon(U-x_1)-s_\epsilon(U-x_2)]
+\frac{S_{\max,k}q_{\rm absorb}}{x_4-x_3}
 [s_\epsilon(U-x_3)-s_\epsilon(U-x_4)].
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
Volt-var law. Physical `THREE_LEG` review #95 remains unresolved.

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

Only pure Volt-var profiles are newly admitted. Mixed PF/Volt-var or Volt-watt
profiles, unsupported references/units/bases/arities, ignored native controls,
filters/internal voltages, availability/DC dynamics and physical control adequacy
remain outside. In particular, a native warning that skips a declaration does
not establish compliance with it. The running input has no IBR; its retained
three default generator-bound failures/zero unknowns, all 26 passing KCL rows and
aggregate power, and separate tighter electrical pass remain unchanged. Published
integration, PSK implementation statuses and execution MCP remain separate.

**Transfer exercise.** Distinguish requested PWL response, assumed smoothed
response, reported Q and actual VI-derived Q. Then change averaging or curtail P
without relaxing a Q cap or minimum-PF policy, and identify which observations,
model assumptions and failure evidence must be retained.

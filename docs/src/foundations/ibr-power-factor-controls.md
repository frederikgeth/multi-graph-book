# [IBR power-factor controls and applicability](@id ibr-pf-control-audit)

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

Filters, internal/grid-forming voltages, droop/availability/DC dynamics, physical
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

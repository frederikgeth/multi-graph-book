# Pinned BMOPFTools integration

This environment checks the current reviewed package/book pairing. It is separate
from the September replay in `../reproduction/review-2026-09-06` and from the
unlocked developer environment in `../Project.toml`.

`profile.json` records an immutable package commit and tree, Julia version, and
hashes of the Project and Manifest. The Manifest pins transitive dependencies;
BMOPFTools is obtained from its repository URL at that commit, never from a
mutable sibling path. Julia must match the profile's version. Ordinary book-only
retrieval checks these files without installing Julia or contacting the package.

From the book root, with a clean BMOPFTools Git checkout at the profile revision:

```bash
python3 scripts/check_bmopf_integration.py --check-profile
python3 scripts/check_bmopf_integration.py --bmopf-root ../BMOPFTools.jl
```

The second command creates a new temporary results directory. Use `--output` to
choose a new directory outside the repository. It checks package export freshness
and the live federation, instantiates this environment without changing its lock,
runs package-owned scientific contracts, controlled properties, export/recipe,
execution and MCP tests, then solves the book's running-network verification
lesson. The package checkout and installed package tree must match the lock.
It also runs the scalar transformer port companion against the package, checking
finite and zero leakage, representation-threshold changes, terminal currents,
power, shunts, nominal-voltage rejection and free common modes. Its evidence is
saved as `transformer-ports.json` in the run directory.
The parameter-reuse companion writes `parameter-reuse.json`: fresh and reused
SI conductance circuits through zero, deliberately deleted terms, a structural
edit requiring rebuilding, and a retained infeasible scenario followed by
recovery. It uses the public staging and `resolve_opf!` APIs at the published
pin. A separate unrefreshed nonlinear cache probe is diagnostic evidence for
the recorded versions; reproducing its failure is not an acceptance criterion.
The multiplicity companion writes `solution-multiplicity.json`, recording
branch-isolating intervals, both-end apparent-power versus current constraints,
all multistart attempts, a neutral minimum-norm selection, and original-law
checks on spurious power-balance roots. Its exact Python artifact is checked
separately; solver observations do not establish root completeness or stability.
These scalar JuMP models use this lock but do not validate native BMOPFTools
device implementations.
Its log, `run.json`, and `verification.json` retain the exact package and book
identities, environment hashes, book dirty state, commands and outcome.
The runner sets `JULIA_LOAD_PATH` to this locked environment and `@stdlib`,
including for recipe subprocesses that choose the package root as their active
project. A sibling developer Manifest or global Julia environment cannot supply
dependencies to those recipes.

A successful integration run is bounded evidence. The verification lesson checks
the package profile and four line-current recoveries, detects an altered voltage,
and requires the complete-feasibility gate to remain `indeterminate`. It does not
supply an independent all-device KCL audit, global optimality, or model adequacy.
The integration does not run the full BMOPFTools test suite.

The `pinned-bmopf-integration` workflow obtains the declared commit rather than
upstream `main`, runs the same command, and uploads the run evidence. The tested
book revision is recorded at run time; embedding its own containing commit into
generated book files would create a circular identity. The pair instead binds
book content hashes, the immutable package revision, and this profile's hash.

To upgrade deliberately, review the new package sources and docs, change the
Project's source revision, resolve its Manifest with the selected Julia version,
and update the profile's revision, tree, version and environment hashes. Then run
`scripts/regenerate_all.py --bmopf-root <clean-reviewed-checkout>`, inspect the
generated diff, and run both deterministic and live integration gates. Never
refresh the historical replay files as a side effect of an integration upgrade.

## Local direct-audit candidate (separate from the pin)

`linear-audit-candidate.json` identifies the local package commit that implements
`audit_linear_solution` and the separate `audit_solution` extension. It is not a published package release, a change to
`profile.json`, or an MCP capability. The package branch is
`codex/coverage-aware-feasibility`; its worktree created for this development is
`tmp/BMOPFTools-feasibility` under the book. The Git branch/commit belongs to the
sibling BMOPFTools repository; the book does not vendor its implementation.
Until that branch is published, a fresh remote clone cannot fetch the candidate.

With that exact clean candidate checkout available, copy the reviewed environment
to a temporary directory and change only its package source. From the book root:

```sh
MGB_AUDIT_ENV=$(mktemp -d)
cp experiments/integration/Project.toml "$MGB_AUDIT_ENV/Project.toml"
cp experiments/integration/Manifest.toml "$MGB_AUDIT_ENV/Manifest.toml"
julia --startup-file=no --project="$MGB_AUDIT_ENV" -e \
  'using Pkg,TOML; p=Base.active_project(); d=TOML.parsefile(p);
   delete!(d["sources"],"BMOPFTools"); open(io->TOML.print(io,d),p,"w");
   Pkg.develop(path=ARGS[1])' "$PWD/tmp/BMOPFTools-feasibility"
julia --startup-file=no --project="$MGB_AUDIT_ENV" \
  experiments/lessons/verify_linear_coverage.jl "$MGB_AUDIT_ENV/coverage.json"
```

Use a different package path if the same candidate commit has been checked out
elsewhere. The companion checks the installed package's exact Git revision and
clean state, runs the tiny analytic, native-coordinate solve, corrupted and missing-data
cases, records a default per-unit solve as a diagnostic comparison at the same
physical tolerances, then solves and audits the running network. It records the candidate identity, environment and
source hashes, full running-network input/result, and all coverage rows. It now
retains both the default running solve and a separate tighter solve at unchanged
audit tolerances. In this recorded run the default point has zero unknown rows
and three generator p_max violations, approximately 0.00997 W each against a
1e-6 W tolerance. The tighter point passes its supported electrical obligations.
Default solver behavior is diagnostic; future backends need not reproduce those
violations. Neither point establishes selected-objective correctness, custom
constraints or optimality. This companion is not in the published-pin CI job;
package tests cover the evaluator on its own branch.
Do not substitute zero residuals to promote it into the legacy witness contract.

Next promotion requires completing/reviewing the desired device coverage,
publishing the package commit, deliberately updating the ordinary integration
pin and regenerating the federated pair. The native default-role source-neutral return and constant-power loads are now
covered by the extended API, together with fixed ideal switches, bounded
WYE/SINGLE_PHASE generator injections/limits, applicable phase-to-earth bus
voltage bounds, explicit-neutral phase-to-neutral vpn_min/vpn_max arrays, applicable scalar neutral-to-earth vn_max, phase-to-phase vpp_min/vpp_max arrays, centered intra-bus and mapped branch-end angle windows and three-phase sequence/VUF bounds, and fixed single-coil single_phase transformers with legacy
secondary excitation, plus two/three-winding WYE transformers with matched one-to-three phase-neutral coils and
explicit pairwise leakage, plus matched three-terminal DELTA winding incidence/rotation.
Full finite signed generator price vectors are recognized as declarations, with
no physical-limit residual or objective certificate. DELTA generators,
controllers, other cost forms, transformer variants/limits outside that narrow
slice, voltage-dependent loads, other voltage families and selected-objective
evaluation remain open. Source-fixed/grounded bus-bound declarations are
explicitly unassessed because the native builder skips their application.

The companion also runs the package's `neutral-and-delta.json` analytic fixture,
a native solve of it, a delta circulating-current corruption, and missing implicit
earth-reaction evidence. It applies both APIs to the same running-network result:
the original linear audit retains 42 unassessed rows. The connected extension
now recognizes the generator's intact signed price declaration and has zero
unknown rows, with 11 load power equations, source relations, the closed switch
voltage relation, four switch current limits, 28 phase-to-earth voltage-bound
rows, four neutral-to-earth caps, six phase-pair limits and the mixed WYE/DELTA
transformer equations, incidence, current limits and declared rating metadata.
All 26 KCL rows and aggregate power pass. The default point fails the three
p_max checks described above; the separate tighter point passes. The original
linear API remains indeterminate. Custom terminal conventions and unrecognized semantic
fields are explicitly outside the current extension's supported domain.
The `fixed-switch.json` companion verifies a native solve and a neutral-current
overload invisible to power checks, and retains missing switch current as unknown.


The separate `experiments/lessons/verify_native_multiplicity.jl` companion uses
that same exact clean candidate environment. It runs the package-owned
`examples/constant_power_roots.jl`, checks its SI input against the book's exact
rational witness at explicit 1 V/1 A bases, and records source/environment hashes,
all attempted native solves and independent equation-audit evidence:

```sh
julia --startup-file=no --project="$MGB_AUDIT_ENV" \
  experiments/lessons/verify_native_multiplicity.jl "$MGB_AUDIT_ENV/native-multiplicity.json"
```

The example isolates each known branch under native line current or both-end
power limits. A low-voltage result passes the emitted power-limited model but
fails the intended current-limited model. Experimental real-voltage intervals
are checked outside the audit and do not add general bus-voltage-bound coverage.
Multistart observations are diagnostic, including failures; different starts
of auxiliary variables can change which branch a local solver selects.
This does not change the published integration pin or expose candidate audits
through MCP.

The `verify_neutral_shunt_multiplicity.jl` companion adds the package-owned
`neutral_shunt_roots.jl` example in the same candidate environment:

```sh
python3 experiments/lessons/neutral_shunt_multiplicity.py --check
julia --startup-file=no --project="$MGB_AUDIT_ENV" \
  experiments/lessons/verify_neutral_shunt_multiplicity.jl "$MGB_AUDIT_ENV/neutral-shunts.json"
```

It binds the exact SI witness to native coupled series conductors and separate
dense shunt factors, checks both roots and audits the declared endpoint ratings.
Source, series, composite-cut and load-coil currents remain separate observations.
Aggregate-power caps are postprocessed comparisons, not new native constraints;
shunt currents are reconstructed. Neither native internal pi-shunt coverage nor
an MCP capability is introduced. The published pin remains separate.


The same companion also runs `examples/generator_voltage_audit.jl` and its
`generator-voltage.json` fixture. It compares the analytic 10 V, 4 W + 1 var
fixed generator injection with a native solve, then retains a forged power report,
return-current overload, missing current and skipped source-voltage bound as
separate evidence. The package fixture, example and companion are source-bound
in the output. It uses the existing candidate environment and command above;
no package API is reimplemented in the book.


The companion also runs `examples/fixed_transformer_audit.jl` with
`fixed-transformer.json`: a nonunit fixed tap, finite complex leakage and
secondary excitation distinguish reported series currents from terminal currents.
It checks a native solve, current/loss identities, a tighter terminal cap,
series/terminal confusion, missing series current and unsupported adjustable tap.
The single-coil transformer example does not itself assess the running network's
mixed WYE/DELTA device; the later winding-list and metadata slices add that
distinct coverage. The final generator-price trace below completes the supported
running current inventory; earlier transformer slices alone left 28 unknown rows.


The companion additionally runs `examples/winding_list_audit.jl` and
`winding-list.json`: a three-winding, single-coil WYE case with nonunit nominal
ratios, coupled leakage and winding-2 excitation. Its native per-winding scalar
limits apply to bare coil currents/powers. A 0.95 A cap fails although the
corresponding terminal-current magnitude is below that cap. The companion checks
analytic/native agreement, complex loss, wrong referral, coil/terminal confusion,
missing current and missing pairwise data. It retains the original running-network
coverage refusal, candidate-only evidence status and source/hash binding. Taps,
DELTA windings, unmatched coil counts and internal coordinates remain outside this slice.


The companion now also runs `examples/multiphase_winding_audit.jl` with
`multiphase-winding.json`. Three unbalanced WYE phases distinguish total winding
power from native equal per-coil s_max allocation: a 12 VA cap fails one 4.974 VA
coil despite the sum of coil magnitudes being about 10.140 VA. It checks native
and analytic results, allocated cap reports, phase-order corruption, neutral
reconstruction and missing coil/earth-reaction observations. Multiphase evidence
uses explicit coil-indexed rows; the original one-coil row IDs remain stable.
The separate rating-metadata example below resolves the native top-level
nameplate role without inferring physical nameplate compliance.


The companion also invokes `examples/delta_winding_audit.jl` and binds
`delta-winding.json`. A finite-leakage DELTA/WYE fixture checks declared phase
order, rotation, coil-to-line current reconstruction and native SI agreement.
A separate ideal equal-ratio DELTA/DELTA boundary has zero terminal line currents
but ±1 A internal circulation: all six 0.75 A coil caps fail while equations,
KCL and power pass. The output retains both zero and nonzero internal states,
wrong rotation, missing internal current and a neutral-bearing-map refusal.
Native build validation rejects DELTA maps carrying a neutral; that boundary is
covered by package tests. The audit requires internal coil observations and
uses s_max/3 at actual line-to-line coil voltage. Two-terminal DELTA, unmatched
coils, taps and internal coordinates remain unassessed. The separate metadata
trace handles `s_rating`; before the generator-price trace, the running network
still had 28 unknown rows. The published
integration pin, PSK implementation statuses and execution MCP remain unchanged.


The companion additionally runs `examples/winding_rating_metadata.jl` with
`rating-metadata.json` and binds the conversion witness
`test/data/pf_comparison/pf_3wdg_unequal_kva.dss`. Finite positive top-level and
winding `s_rating` values are retained with status `declared`, no residual and
`enforced_as_limit=false`. Explicit winding `s_max/nph` constraints remain
separate. The deliberately low metadata values do not prevent the native SI,
classic, unequal local-base or PF witness from passing; this is native-model
evidence, not physical nameplate acceptability. Tightened OPF/PF limits, invalid
metadata and missing internal currents remain in the output with their distinct
statuses. Package tests trace raw PowerIO 0.11.6 emission under `extras`,
normalization, unequal-kVA resistance repair and rating/cap serialization.
The audit does not authenticate that upstream conversion.

The current running input is retained intact: transformer equations/current
caps are checked and its top-level rating is declared metadata. At this stage,
generator cost still suppressed complete network KCL/power certification. The
later generator-price trace recognizes that declaration and records the default
failed and tighter passed electrical points without dropping fields. No published
integration pin, PSK implementation status or execution MCP change is included.


The same companion runs `examples/phase_neutral_voltage_audit.jl` and binds
`phase-neutral-voltage.json`. Its 10 V, two-conductor SI witness has a 9 V load
phase and 1 V neutral: phase-neutral voltage is 8 V. Tightened PN lower/upper
bounds fail by 0.25 V while KCL and power pass. The example retains native SI,
per-unit, grounded-neutral and limited attempts, plus missing-neutral,
source-fixed and malformed-bound evidence. Grounding is checked separately;
missing neutral voltage is never reconstructed as zero. PN rows retain their
full phase-array index and reference terminal, including when an earlier phase
is skipped by native applicability. Required bounds are finite nonnegative
full-length arrays in the original non-neutral bus order.

Package tests cover skipped grounded/source phases, three-phase reorderings,
complex phasor subtraction and Float64 representability boundaries. Other
voltage families remain open. The running input has no vpn_min/vpn_max fields,
so this PN slice adds no running obligations. The generator-price trace below
records the current default and tighter running verdicts.
Published integration, PSK implementation statuses and execution MCP stay separate.


The companion also runs `examples/neutral_earth_voltage_audit.jl` and binds
`neutral-earth-voltage.json`. A complex neutral voltage of `1-0.5im` V has
magnitude about 1.118034 V; a 1 V scalar `vn_max` therefore fails even though
both rectangular components fit a ±1 V box. Independent phase/PN, KCL and
power checks still pass at that supplied point. A finite 0.25 S grounding
shunt with a 4 ohm neutral preserves that voltage and the source/load powers
while halving the neutral-conductor current compared with the 2 ohm case.
The shunt current is reconstructed; voltage is not a conductor-current rating.
Native SI/per-unit and finite-grounding solves pass their scoped audits.

The native builder omits `vn_max` at explicit perfect neutral grounds and
implicit source-bus neutral grounds, including when the source map omits that
neutral. Those declarations remain unassessed with null residuals; separate
grounding checks still apply. Consistent native perfect/source-ground cases
solve successfully but do not have complete audit acceptance. Finite shunts do
not trigger this skip. A zero voltage cap does not add a free earth-reaction
current path. Malformed scalar data and missing neutral state remain unknown;
missing state suppresses KCL/power certification. Four intact running-network
caps reduced unknown obligations from 33 to 29 at that stage, before the final
generator-price trace. The published pin, PSK statuses and execution MCP remain unchanged.


The companion additionally binds `examples/phase_phase_voltage_audit.jl` and
`phase-phase-voltage.json`. Source phases 10 V and 10im V feed a two-terminal
DELTA load through two 1 ohm conductors. The load phases 9 V and `1+10im` V
have difference `8-10im` V, magnitude sqrt(164) ≈ 12.806248 V. Bounds [12,13] V
pass; tightened lower/upper limits fail while phase-earth, KCL and power pass.
The audit uses the phasor difference, with V-unit residuals and tolerances.

Arrays enumerate all unordered pairs in full declared phase order, excluding
a supported n/N neutral when present. A neutral is not required. Pairs touching
grounded/source-fixed phases remain unassessed and consume their pair index;
an applicable third pair still uses entry 3 after two skips. Native SI/per-unit
points pass; skipped-phase solves retain incomplete audit acceptance. Missing
endpoint state and malformed arrays stay unknown. Grounded neutrals and finite
shunts do not skip these phase pairs. Tests cover complex norms, array
permutations, relabeling, exact boundary/tolerance and native constraint incidence.
Six running limits pass; at that stage unknown rows fell 29 -> 28 because both
declared fields formerly shared one field-coverage row. Generator price was
still outside the audit until the later trace below. Objective/adequacy,
published integration, PSK status and execution MCP promotion remain separate.


The companion additionally binds `examples/bus_angle_voltage_audit.jl` and
`bus-angle-voltage.json`. Both scalar va_diff endpoints must be finite, ordered
and strictly within (-pi/2,pi/2). Optional full-phase va_nom centers second-minus-
first earth-phasor angles; absence means zero offset. Principal centered
violations and the separate angle_tol are rad. Zero endpoints stay unassessed
even though native bilinear rows can vanish there. Standalone nominal metadata
and custom roles remain outside this bus-angle slice. Missing endpoint state suppresses KCL/power certification.

The same load phases 9 and 1+10im V have raw difference atan(10), centered on
[0,pi/2] to -atan(0.1) ≈ -0.09966865 rad. Window [-0.15,0.05] passes; lower
-0.05 or upper -0.12 fails while magnitude, KCL and power pass. Native SI,
per-unit and common-rotation/branch-cut witnesses pass. The zero-endpoint point
retains valid KCL/power but no angle compliance. Native primal inspection checks
that distinction without providing the independent evaluator's oracle. Skipped
first phases retain nominal indices (2,3); native skipped cases solve with
incomplete audit acceptance. Tests cover direction reversal, cyclic symmetry,
noncyclic reorderings, equal windows/antipodal exclusion, malformed data and
Float64 range. The running input declares no bus-angle windows or va_nom, so
this angle slice adds no running obligations. The later generator-price trace
records the current verdicts. The published pin, PSK statuses and execution MCP are unchanged.


The companion additionally binds `examples/sequence_voltage_audit.jl` and
`sequence-voltage.json`. All three phases in declaration order enter the
independently evaluated Fortescue transform, including grounded/source-fixed
phases. Floating neutral selects supplied phase-neutral input; absent or perfect
neutral (including implicit source grounding) selects earth input. No missing
neutral state is invented. Missing required state still suppresses KCL/power.

Magnitude limits vpos_min/max, vneg_max and vzero_max use V; vuf_max bounds the
fraction |Vnegative|/|Vpositive| with separate dimensionless vuf_tol. Both vuf_tol
and the separate denominator floor vuf_voltage_floor default to 1e-6, with the
latter in V. At/below the floor, observed ratio/residual are null; magnitude
limits remain independently checked. Native cross-multiplied feasibility at the
all-zero point does not define a ratio. This audit makes no polynomial-feasibility
claim outside its ratio domain.

The four-wire 1 ohm circuit has load sequence phasors 10 V, 1 V and 0.5+0.25im V,
floating neutral 1-0.5im V and VUF 0.1. Tightened bounds each fail with KCL/power
still passing. A consistent 5 V positive/1 V negative point passes the same
negative cap but has VUF 0.2. Native SI/per-unit, grounded-neutral and permitted
low-positive points pass; the tightened native VUF attempt and failed point
audit are retained with local infeasibility, not a global certificate. Tests
cover full source/ground phase incidence, phase-order reversal/cyclic symmetry,
zero/floor refusal, scalar/unit boundaries and malformed/missing data. The
running input declares no sequence/VUF bound, so this slice adds no running
obligations. The generator-price trace below records the current verdicts. The published pin, PSK statuses and execution MCP
stay separate.


The companion additionally binds `examples/branch_angle_voltage_audit.jl` and
`branch-angle-voltage.json`. Branch va_diff windows use paired finite scalar
endpoints in (-pi/2,pi/2), but observe principal theta_from-theta_to, with no
nominal offset. Every positional mapped conductor is included, including
neutral and source/ground endpoints. Maps must be explicit, unique, nonempty
and equally long. No truncation or guessed label matching is used. Angular
excess uses angle_tol in rad, independently of line-equation voltage_tol.

The two-conductor DELTA point has angles 0 and +atan(0.1) ≈ +0.09966865 rad.
Window [-0.02,0.12] passes; lower 0.02 and upper 0.08 each produce one violation
while line equations, magnitude limits, KCL and power pass. Common rotation
crosses a principal-angle cut without changing the circuit. Reversing the branch
also reverses maps/currents/result labels and maps [lo,hi] to [-hi,-lo]. Native
SI/per-unit/rotated/reversed points pass. The native neutral witness solves but
retains an undefined source-neutral endpoint angle; a separate zero-origin
primal inspection likewise does not define an angle. Native rows are subjects,
not the independent oracle.

Malformed angle data preserves known inline-series currents and ratings; known
violations take precedence over angle uncertainty. Missing endpoint state
suppresses full KCL/power but can leave other conductor angles checked. Endpoint
angle observations do not certify an unsupported line equation model. The older
linear-only API still refuses line-angle declarations. The running lines have
none, so this slice adds no running obligations. The generator-price trace below
records the current verdicts. Published pin, PSK status
and execution MCP stay separate.


The companion now binds `examples/generator_cost_scope.jl` and
`generator-cost.json`. A full finite signed linear price vector has one entry
per WYE/SINGLE_PHASE coil, excluding a WYE neutral. Its declaration is recorded
with `status="declared"`, null residual and
`enforced_as_physical_limit=false`. Malformed prices remain unknown while
otherwise known generator currents, electrical limits and KCL remain assessed.
Generator active/reactive/apparent-power rows use W/var/VA respectively, without
changing numeric tolerances. Source/IBR price applicability remains separate.

Native tests trace default cost `sum(cost[k]*P_injected_W[k]/1000)`, in
currency/hour for currency/kWh prices, with no variables or constraints added
by the expression constructor. Per-unit coefficients compensate power scaling.
An explicit two-hour weight changes the rate to an energy cost; a caller can
omit or replace the objective. The independent audit neither invokes that
constructor nor evaluates or validates a supplied objective. Its explicit
`objective_scope` leaves selection, reported value, custom constraints and
local/global optimality unchecked.

At fixed 4 W + 1 var dispatch, known positive/negative price recipes produce
+0.001/-0.001 currency/hour; zero, constant-123 and explicit two-hour recipes
retain their distinct scope. With P in [3,5] W and an unpriced source, native
per-unit positive/negative prices select the respective endpoints. A forged
reported objective remains unverified. The two unsuccessful native SI attempts
are retained: the voltage-only start returns a failed electrical point, while
the full supplied-primal start returns a passing point despite a restoration
failure. Successful per-unit, zero-price, no-objective and custom-constant
recipes are recorded separately from these attempts.

The running generator's intact `[-0.08,-0.08,-0.08]` prices now permit all 26
KCL rows and aggregate power to be checked; these pass. The default result's
three p_max violations remain failed at 1e-6 W tolerance. A separate solve uses
`tol=1e-10`, `constr_viol_tol=1e-12`, `acceptable_iter=0` and
`bound_relax_factor=0` with identical input and audit tolerances, and passes.
Both solver recipes/results and their audits are retained in the source-bound
output. This is supported electrical supplied-point evidence, not unrestricted
native/custom-model feasibility, economic adequacy or an objective certificate.
The published pin, PSK implementation statuses and execution MCP remain unchanged.

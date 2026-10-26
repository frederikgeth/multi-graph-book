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
WYE/SINGLE_PHASE and bounded cyclic DELTA generator injections/coil limits, applicable phase-to-earth bus
voltage bounds, explicit-neutral phase-to-neutral vpn_min/vpn_max arrays, applicable scalar neutral-to-earth vn_max, phase-to-phase vpp_min/vpp_max arrays, centered intra-bus and mapped branch-end angle windows and three-phase sequence/VUF bounds, and fixed single-coil single_phase transformers with legacy
secondary excitation, plus two/three-winding WYE transformers with matched one-to-three phase-neutral coils and
explicit pairwise leakage, plus matched three-terminal DELTA winding incidence/rotation.
Full finite signed generator and voltage-source price vectors are recognized as declarations, with
no physical-limit residual or objective certificate. Other generator topologies,
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
changing numeric tolerances. Source price applicability is added below; IBR price
applicability remains separate.

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


The companion also binds `examples/delta_generator_audit.jl` and
`delta-generator.json`. Two/three distinct non-neutral terminals form cyclic
injection coils. Result `crg/cig` at terminal-map key k is coil current I[k];
terminal injection is J[k]=I[k]-I[k-1], and the outgoing KCL contribution is
-J[k]. Explicit reconstruction metadata is not an independent terminal-current
measurement. Native `i_max` and `s_max` entries bound individual coils, with no
terminal-line, neutral-return or equal-allocation inference. P/Q/S rows use
W/var/VA; coil current limits use A. Two-terminal DELTA generators have two
opposed coils, unlike the single coil of a two-terminal DELTA load. This native
indexing does not remove the separate data-model three-terminal arity warning.

At the unbalanced analytic point, the second terminal injection has magnitude
about .559 A despite a .3 A second-coil cap; the actual second coil carries
.25 A and passes. Adding .5+.2im A to every coil leaves terminal currents, KCL
and aggregate generator power unchanged, but fails all three original current
and all three apparent-power coil limits. Honest updated power reports still
pass. Missing internal current cannot be recovered from terminal observations;
other known coil checks survive while KCL/power remain unassessed. A separate
known violation takes precedence over a malformed extra current-rating entry.

Native SI, per-unit, reversed-coil and two-terminal comparisons fix the recorded
coil dispatch and pass. The tighter-coil-cap native attempt is retained with
`LOCALLY_INFEASIBLE` and a failed returned-point audit; it is not a global
infeasibility certificate. Neutral-bearing DELTA maps remain unassessed: the
native generator builder currently constructs them, while spec conformance emits
`E.SPEC.DELTA_HAS_NEUTRAL`. No native construction behavior changes here.
Generator prices remain declarations and selected objective/optimality remains
unchecked. The running generator is WYE, so its default three-p_max failure,
zero unknowns and separate tighter electrical pass are unchanged. Published
integration, PSK implementation statuses and execution MCP remain unchanged.


The companion additionally binds `examples/source_price_audit.jl` and
`source-price.json`. WYE/SINGLE_PHASE source prices are full finite signed
vectors in NON-NEUTRAL source-map order. Voltage references instead follow
full terminal-map order and specify absolute earth phasors. A matching prefix
may omit only a suffix of explicitly grounded terminals or the implicitly
zero-grounded source-bus neutral. Omitted grounded phases retain their price
and current slots. Source current/apparent-power ratings, controllers, custom roles and
DELTA sources remain outside this bounded extension; source P/Q limits follow below.

An unmapped bus neutral still supplies the source return and power reference;
without one, power uses earth. The source-neutral return and separate earth
reaction remain distinct, with shared source-ground evidence consumed once.
A two-phase SINGLE_PHASE source has TWO reference/current/price terms, unlike
the one-coil SINGLE_PHASE generator. Source ps/qs report residuals now name
W/var, with unchanged tolerances. Optional reports are checked when present.

The analytic/native witness has bus order [n,a,b], source map [b,n,a], three
voltage entries and only two prices [.4,.1] currency/kWh. Phase b exports 3 W,
phase a imports 6 W, and the known default rate is -.0006 currency/hour. The
same electrical point passes after consistently reordering references and
prices. Reordering the map but leaving the old price order gives +.0021 instead;
the standalone point audit does not infer intended tariff mapping or validate
that reported objective. SI/per-unit, absent/mapped/trailing-neutral, earth,
two-phase SINGLE_PHASE, negative-price, omitted-objective and constant123
native recipes are retained with separate electrical acceptance.

Bad price shape/type/range leaves the declaration unknown without hiding known
reference, report, current, KCL or power evidence. Malformed voltage-reference
arrays likewise leave known current incidence checked while their equation
remains unassessed. Required missing current/state/earth reaction suppresses
complete KCL/power certification. Grounded-phase and all-zero reference suffixes
have explicit analytic/native-construction evidence; omitted free phase
references remain unknown and native construction rejects them. An authored
nonzero neutral reference can match the supplied source equation and P/Q but
fails the separate ground boundary; native construction rejects that input.
Two overlapping-source current splits pass electrically while their known
expression values differ. No allocation, economic adequacy, objective selection,
reported-value consistency, well-posedness or optimality is inferred.
The running input has no source price, so its default three generator p_max
violations/zero unknowns and separate tighter electrical pass are unchanged.
The published pin, PSK statuses and execution MCP remain unchanged.


The companion also binds `examples/source_pq_audit.jl` and `source-pq.json`.
Signed p_min/p_max and q_min/q_max bound independently recomputed phase
injections in W/var, in non-neutral source-map order. Bus-neutral fallback,
earth reference, grounded phase entries and two-phase SINGLE_PHASE indexing
retain the source conventions above. Optional ps/qs reports do not supply the
limit value. New rows retain original phase/map indices, reference pairs,
observed injection, bound and sense at unchanged absolute power tolerances.

Absent fields author no bound. Explicit empty vectors are recorded as declared
empty-limit metadata, null residual/tolerance and enforced_as_limit=false;
they add no zero or aggregate constraint. Nonempty vectors must be full finite
signed phase arrays. Scalar, partial, extra/neutral-slot, invalid type and range
failures remain unknown without erasing known other-field/phase failures or
current incidence. Missing required current/state still suppresses KCL/power.
The native builder accepts prefixes and ignores extra entries while static
indexing diagnoses them. Successful native prefix/extra solves are retained
with indeterminate point audits; no data is padded or discarded to pass.

The unbalanced source-price point has phase powers [-3+2im,6+1im] VA in map
[b,n,a]. Tightening phase a's p_max to 5.5 W fails by .5 W although net P=3 W
fits the summed cap 3.5 W. Tightening phase b's q_max to 1.5 var fails by .5 var
although total Q=3 var fits the summed cap. Signed lower/export and reactive
absorption cases, in-range forged reports, malformed prices and missing other-
phase observations remain separate evidence. At zero phase-to-reference
voltage, nonzero current passes zero P/Q boxes; a positive lower bound fails.
Native primal inspection confirms these points without a current-rating claim.

Native SI/per-unit, reordered, unmapped/trailing neutral, earth, two-phase
SINGLE_PHASE and empty-limit solves pass. Two tighter P/Q attempts report local
infeasibility and their returned points fail the audit; no global certificate
is claimed. Four full two-phase vectors add eight native constraints and no
variables; empty and absent vectors add none. Native row inspection and the
reused controlled source-price solve recipe are subjects, not audit oracles.
Source current/apparent-power ratings, physical grid/grounding adequacy,
controllers/custom roles, selected objectives and optimality remain separate.
The running input has no source P/Q bounds, so its default three generator
p_max failures/zero unknowns and separate tighter electrical pass are unchanged.
Published integration, PSK statuses and execution MCP remain unchanged.


The candidate also adds the bounded AC-only IBR injection/current-incidence
example `examples/ibr_injection_audit.jl` and analytic fixture
`test/data/linear_audit/ibr-injection.json`, run by `verify_linear_coverage.jl`.
Its explicit topology domain is: two-endpoint SINGLE_PHASE; one-to-three-phase
FOUR_LEG with a mapped default-role neutral; exactly three cyclic non-neutral
THREE_LEG coils. It independently computes ordered U*conj(I), signed P/Q boxes,
branch I/S caps, shared single-pair minimum current cap and optional four-leg
neutral-return cap. Cyclic coil currents and terminal differences remain
separate observations. Internal circulation can violate all three I/S coil
caps without changing terminal KCL or total power. Reported P/Q is optional
consistency evidence. Missing observations suppress complete KCL/power while
known other violations survive; malformed full arrays do not erase currents.

Controlled native SI/per-unit and reversed single-pair comparisons fix the
analytic dispatch and seed its full primal state. Tighter shared/neutral-cap
attempts retain failure evidence. Native construction also accepts maps/extra
entries refused by the bounded audit. Filter fields leave native model shape
unchanged but remain audit refusals. The current native THREE_LEG cyclic model
is not a resolution of physical review #95. Filters/internal/grid-forming
voltages, controllers, availability, custom roles, DC coupling/dynamics
and objective/optimality remain outside this slice. A false dc_link_coupled is
the uncoupled default; recognized prime_mover values are metadata only. Native
power-flow construction omits s_max circles; declared-cap compliance does not
certify which problem was built. The running input has no IBR; its default
three generator-bound failures/zero unknowns and separate tighter pass persist.
Published pin, PSK statuses, historical replay and execution MCP are unchanged.


The bounded IBR price extension recognizes full finite signed branch prices
as declaration metadata, retaining ordered pairs/map positions and false
selected/reported-objective, objective-value and optimality flags. Absent cost
authors no declaration; empty/scalar/null/prefix/extra/Boolean/nonfinite/range-
invalid data remains unknown without erasing known electrical evidence.
`examples/ibr_price_scope.jl` and `test/data/linear_audit/ibr-price.json` add
native expression/recipe comparisons to the source-bound companion. Single,
four-leg and cyclic three-leg rate values .001/-.00045/-.0005 currency/hour
agree in SI/per-unit; price scaling uses the local AC power base. Expression
construction adds no variables/constraints and does not select an objective.
Consistent reordering moves prices; unmoved four-leg prices yield -.00095.
Cyclic circulation changes nonuniform rate to -.0044 with unchanged terminal
power and six retained coil failures; uniform .1 prices yield .00035 before/after.
Default/feasibility/custom-123/two-hour recipes remain separate observations,
without selected-objective or optimality certification. Malformed native
construction boundaries, physical THREE_LEG review #95 and filter/control/DC
refusals remain explicit. Running-network/default/tighter evidence and published
integration, PSK statuses, historical replay and execution MCP remain unchanged.

The fully seeded single-pair SI positive/negative/two-hour attempts retain
OTHER_ERROR/Restoration_Failed and INFEASIBLE_POINT statuses with passing
returned electrical audits; they remain unaccepted solver attempts. Separate
per-unit counterparts solve and pass. No initialization-robustness claim.


The constant/minimum-PF extension adds `examples/ibr_pf_audit.jl` and
`test/data/linear_audit/ibr-pf.json` to the source-bound companion, with a focused
lesson at `docs/src/foundations/ibr-power-factor-controls.md`. The new audit
independently decodes pure signed constant-PF profiles and the exact package v1
generation/per_coil minimum policy; it does not call native policy/role/index
helpers or use reported P/Q. Constant equality, generation direction and both
weighted reactive inequalities are separate per-branch obligations, composed
with hard P/Q/I/S caps. Minimum applicability requires full nonnegative p_min,
p_max if present, and compatible constant target. Malformed controls preserve
known electrical evidence; unrelated extras remain unsupported and suppress KCL.
No PF quotient is formed at zero; tiny coefficients expose fixed absolute
weighted-tolerance limits. Native profiling has a separate reported-P/Q/zero-P
policy. Adding both controls adds four constraints per branch, no variables.

Analytic and controlled native SI/PU cases pass in this locked run. With f=m=.8,
P4/Q-3 passes controls but q_min=-2 fails by1var. Separate native maximum-P with
that cap yields P8/3/Q-2; the fixed-P conflict attempt reports local infeasibility
and its returned-point audit fails, without a global claim. Aggregate PF hides
a first-coil 1.8VA violation at P=[1,10,10],Q=[3,0,0]. Missing state, forged Q,
zero/unity/signed targets, map changes and tiny coefficients retain scope.
Droop, filters/internal voltages, availability/DC dynamics, physical THREE_LEG
realization, selected objectives and optimality remain outside. Running-network,
published pin/PSK statuses, historical replay and execution MCP remain unchanged.


The Volt-var extension adds `examples/ibr_volt_var_audit.jl` and
`test/data/linear_audit/ibr-volt-var.json` to the source-bound companion. It
admits pure SINGLE_PHASE/explicit-neutral FOUR_LEG profiles with positive ordered
SI breakpoints, VA_FRACTION/VAR_MAX (each branch s_max), six PN/PG/PP monitors,
mean magnitudes and strict legacy aggregation overrides. The Julia
volt_var_model keyword requires an explicit static user_defined-softplus recipe
and relative volt_var_watt_eps for equality assessment. This is an assumption,
not authenticated build metadata; missing recipes preserve known current/limit
evidence and report requested PWL targets separately. Builtin/Swish/live updates,
PWL build recipes, mixed controls and native fallback/THREE_LEG skip stay outside.

The breakpoint point U9V, knots[8,9,11,12]V, q_limits[-.6,.44], s_max20VA,
relative width.02 has requested Q0 but smoothed Q1.2080118var. Source-bound SI/PU,
floating-reference primal and aggregation comparisons preserve that distinction.
Hard q_max=.2var and curtailed-P=.2W/minimum-PF=.8 conflicts remain independent;
native attempts are locally infeasible with returned audits failed2/failed1,
without a global claim. Missing terminal decoding now continues to later known
phase observations/failures, while complete network certification stays
suppressed. No native curve/index/role/smoothing or profiler helper is the
independent oracle. Mathematical target evaluation does not certify backend
range/convergence or physical/controller adequacy. Running-network default/tighter,
published pin/PSK statuses, historical replay and execution MCP remain unchanged.


The Volt-watt/availability extension adds `examples/ibr_volt_watt_audit.jl` and
`test/data/linear_audit/ibr-volt-watt.json`. Pure SINGLE_PHASE/explicit-neutral
FOUR_LEG curves use two positive increasing SI knots, nonnegative ordered
p_limits=[low,high], VA_FRACTION and S_MAX/P_MAX/P_AVAILABLE bases. Six references,
mean magnitudes and legacy overrides share the independently decoded geometry.
An explicit volt_watt_model/v1 static user_defined-softplus assumption is needed
for a one-sided W excess over the cap. Requested PWL, assumed smooth and the
intersection with a known authored p_max remain distinct. Supplied modeled
coefficient rows are not the independent oracle; missing recipes preserve known
current/box evidence. Native comparisons fix dispatch after build without
rewriting p_max, preserving P_MAX normalization. Both curve corners, hard-box
intersection, native SI/PU and floating-reference points retain these boundaries.

Finite nonnegative scalar p_avail is metadata, not a direct cap, authenticated
resource/weather fact or time/energy guarantee. P_AVAILABLE divides it by
non-neutral mapped terminal count: a phase-neutral pair uses one, a single
phase-to-phase coil two, a three-phase four-leg device three. Explicit
augmentation may instead derive missing p_max proportionally to s_max. The
companion retains that transformation and manifest separately; the audit never
invokes augmentation or writes inferred P limits. A metadata-only p_avail1W /
actualP4W comparison passes with p_max10W. Original scalar W availability stays
unscaled during SI-to-PU input conversion and is normalized once by the native
constructor. Separate used VV/VW family assumptions with unequal global widths
produce an unknown compatibility obligation while known assumed equations remain
assessed. Malformed legacy aggregation retains known current/P-box failures.
Mixed controllers, THREE_LEG droop, builtin/Swish/live updates, physical
availability, filters/DC, selected objectives and optimality remain outside.
Running-network/default/tighter, published pin/PSK states, historical replay and
execution MCP remain unchanged.

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
source hashes, full running-network input/result, and all coverage rows. The
running-network verdict must remain **indeterminate**. This companion is not in
the published-pin CI job; package tests cover the evaluator on its own branch.
Do not substitute zero residuals to promote it into the legacy witness contract.

Next promotion requires completing/reviewing the desired device coverage,
publishing the package commit, deliberately updating the ordinary integration
pin and regenerating the federated pair. The native default-role source-neutral return and constant-power loads are now
covered by the extended API, together with fixed ideal switches, bounded
WYE/SINGLE_PHASE generator injections/limits, applicable phase-to-earth bus
voltage bounds and fixed single-coil single_phase transformers with legacy
secondary excitation, plus two/three-winding WYE transformers with matched one-to-three phase-neutral coils and
explicit pairwise leakage. DELTA generators, generator costs/controllers, transformer
variants/limits outside that narrow slice, voltage-dependent loads, other voltage families and objective
evaluation remain open. Source-fixed/grounded bus-bound declarations are
explicitly unassessed because the native builder skips their application.

The companion also runs the package's `neutral-and-delta.json` analytic fixture,
a native solve of it, a delta circulating-current corruption, and missing implicit
earth-reaction evidence. It applies both APIs to the same running-network result:
the original linear audit retains 42 unassessed rows; the connected extension
reduces this to 34, with 11 load power equations, source relations, the closed
switch voltage relation, four switch current limits and 28 phase-to-earth
voltage-bound rows evaluated. The running generator still contains an unsupported
cost field; this slice does not discard it to manufacture full KCL coverage.
Both remain indeterminate. Custom terminal conventions and unrecognized semantic
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
The bounded transformer slices do not assess the running network's multiphase
WYE/DELTA `n_winding` transformer, so that example remains indeterminate with 34 unassessed rows.


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
The running network still has unassessed DELTA/top-level nameplate semantics.

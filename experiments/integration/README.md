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
covered by the extended API. Switches, generators, transformer equations/limits,
voltage-dependent loads, bus voltage bounds and objective remain open.

The companion also runs the package's `neutral-and-delta.json` analytic fixture,
a native solve of it, a delta circulating-current corruption, and missing implicit
earth-reaction evidence. It applies both APIs to the same running-network result:
the original linear audit retains 42 unassessed rows; the source/load extension
reduces this to 36, with 11 load power equations and source relations evaluated.
Both remain indeterminate. Custom terminal conventions and unrecognized semantic
fields are explicitly outside the current extension's supported domain.

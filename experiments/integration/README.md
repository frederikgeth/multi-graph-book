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

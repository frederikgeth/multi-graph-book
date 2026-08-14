# GraphModelsForPowerNetworks

This is the dependency-light package candidate for the reusable core of the
book. It provides multigraph primitives, typed linear Kron reduction, typed
state-space and unit objects, and transformation-certificate contracts.

The solver-backed demonstrations and BMOPFTools integration remain in the
repository's `experiments/` project. That separation keeps the package API
portable while preserving executable evidence for the knowledge base.

Run the package tests from this directory with:

```julia
using Pkg
Pkg.test()
```

The package is currently version `0.1.0`; publication and compatibility
promises remain a later release step.

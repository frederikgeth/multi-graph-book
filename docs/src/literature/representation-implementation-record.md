# [Representation implementation record](@id representation-implementation-record)

**Page status:** research and software record; implementation coverage is
evidence about the current repository, not a claim that the architecture is
complete.

The mathematical architecture is defined normatively in [Formal
representation frameworks](@ref formal-representation-frameworks). This page
records the engineering status of the small executable facade and its fixture
coverage so that package maturity is not confused with representation theory.

## Public transformation API boundary

The reusable facade in
`experiments/src/GraphModelsForPowerNetworks.jl` currently exports a small,
dependency-light surface: identified multigraph primitives, incidence and
cycle-space queries, simple projection, typed linear Kron operations,
coordinate and recovery maps, unit conversion, boundary projections, and
structural certificate validation. Solver-backed AC cases, generated figures,
literature adapters, and BMOPFTools integration remain experimental evidence,
not package-stability promises.

The generated `experiments/generated/public-api-manifest.json` is the checked
record of that boundary. Promotion to a standalone package should wait until
the state-space and unit types, conversion contracts, and recovery semantics
are versioned. Otherwise a representation change could silently alter the
meaning of a reduction while leaving the Julia method names unchanged.

## Fixture coverage and evidence status

`experiments/generated/fixture-coverage-matrix.json` keeps coverage separate
from API existence. It distinguishes direct fixture evidence, related evidence,
and explicit ``not_yet_tested`` rows for the running network, five-bus
cycle-space example, and multiwinding transformer. A certificate on a
synthetic fixture is therefore not silently promoted to validation of a
canonical network fixture.

The multiwinding fixture records two cycle views: its native factor--port
incidence is a star with cycle rank zero, while a derived clique compilation
has cycle rank one. The latter is a view choice, not a new electrical loop.
Likewise, active radiality for the isolated transformer contract remains
``not_yet_tested`` because no switching or energized-state domain is declared.

The matrix distinguishes typed map families as well. The running-network
state-space/unit witness is direct evidence for its declaration and conversion
contract; the multiwinding entry is related evidence because it is not a
separate state-space instantiation. Winding-terminal normalization is direct
for the serialized ``x1`` transformer contract but only related to the running
network as a whole. Parameterized transformer control is tracked separately
from fixed transformer compilation and has direct evidence in the retained-tap
AC certificate.

## Current research boundary

These records establish a reproducible implementation inventory. They do not
establish categorical composition, universal factor evaluation, complete
schema coverage, or package API stability. Those remain research tasks and are
kept separate from the normative definitions and the generated transformation
certificates.

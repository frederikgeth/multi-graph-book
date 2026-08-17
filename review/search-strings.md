# Search strings

These are portable logical forms. Database-specific translations must preserve
the concepts while recording changes to field names, wildcards, proximity
operators, and query limits.

## Core representation and transformation query

```text
("power system*" OR "power network*" OR "electrical network*" OR
 "distribution network*" OR "transmission network*")
AND
(graph OR topology OR representation OR model OR terminal OR port OR
 hypergraph OR "node breaker" OR "bus branch")
AND
(reduc* OR equivalen* OR aggregat* OR simplif* OR transform* OR compil* OR
 normaliz* OR canonical* OR rewrite* OR "Kron reduction" OR "Ward equivalent")
```

## Decision and constraint preservation

```text
("power system*" OR "power network*")
AND
(reduc* OR equivalen* OR aggregat* OR projection)
AND
(constraint* OR limit* OR feasible OR optim* OR decision* OR contingency OR
 switching OR investment OR recover* OR lifting OR provenance)
```

## Multiconductor, grounding, and device detail

```text
("distribution network*" OR "power network*")
AND
(multiphase OR multiconductor OR unbalanced OR neutral OR grounding OR
 multiwinding OR "multi-terminal" OR transformer)
AND
(reduc* OR transform* OR compil* OR equivalen* OR topology OR representation)
```

## Circuit and formal-method foundations

```text
("electrical network*" OR circuit*)
AND
("graph transformation" OR rewriting OR cospan* OR corelation* OR
 "port-Hamiltonian" OR "black box" OR compositional OR "inverse network")
AND
(equivalen* OR behavio* OR recover* OR eliminat* OR normal-form OR closure)
```

## Graph-model and formulation landscape

```text
("power network*" OR "power system*" OR "electrical network*" OR circuit*)
AND
(multigraph OR hypergraph OR "factor graph" OR "port graph" OR
 "port-Hamiltonian" OR "bond graph" OR "node-breaker" OR "bus-branch" OR
 "modified nodal" OR "sparse tableau" OR "branch-current")
AND
(representation OR formulation OR topology OR interconnection OR
 equivalen* OR compil* OR transform*)
```

Use this family to separate mathematical formulation precedents from power
system reduction papers. Code the source and target as equation/graph objects,
record whether the result is behavioral or decision-preserving, and mark
utility identity, phase/neutral, grounding, and provenance scope explicitly.

## Targeted method families

Run separate narrower searches for:

- `Kron`, `Ward`, `REI`, Schur complement, and network equivalents;
- feeder reduction, phase aggregation, and spatial clustering;
- switch contraction, topology processing, node--breaker, and bus--branch;
- star--mesh, `Y`--`Delta`, transformer realization, and grounding extraction;
- sparsification, spectral reduction, and graph coarsening;
- CIM/CGMES, OpenDSS, PowerModelsDistribution, and related official model
  conversion or reduction procedures.

For each database, save the exact executed query, fields, dates, filters,
result count, export format, and checksum of the raw export. Do not silently
replace a previous search; create a dated run.

# Search run: multiphase formulations and practical reductions

**Page status:** generated search-run record.

**Protocol:** 0.2.0  
**Run date:** 2026-08-16  
**Purpose:** close the next scoped coverage gap identified in the roadmap: the
multiphase OPF formulation precedents and practical feeder/transmission
reduction records that sit between abstract Kron theory and software topology
processing.

## Records added

The pass added seven included, single-coded records to the canonical matrix:

- `EV-0022` and `EV-0023` — Gan--Low chordal and multiphase convex/linear
  formulation records;
- `EV-0024` — Caliskan--Tabuada generalized Kron reduction;
- `EV-0025` — Coppo--Bignucolo--Turri multiphase transformer construction;
- `EV-0026` — Pecenak et al. multiphase feeder reduction;
- `EV-0027` — Sistermanns et al. feature- and structure-preserving transmission
  reduction;
- `EV-0028` — the journal Opti-KRON record, kept distinct from the radiality
  preprint already coded as `EV-0003`.

## Coding decisions

The Gan--Low records are coded as formulation/relaxation precedents rather than
as physical asset reductions. The chordal result is an outer feasible-set
relaxation for its declared class; the companion record contains multiple
approximation regimes and is therefore left `unclassified` rather than given a
single exactness label. The practical feeder and transmission records are coded
as scenario-approximate observation studies. None is treated as a universal
multiconductor, neutral-preserving, or decision-preserving equivalence.

## Limits

This is targeted citation chasing from the verified bibliography, not a database
export or independent second coding. The new rows remain `single_coded`; the
matrix still cannot support PRISMA-style flow counts or claims of exhaustive
coverage. As a screening-control exercise, the same pass records `Nanopass2005`
as `EV-0029` with `exclude / wrong_domain`: it is retained as a compiler
analogy in the bibliography but has no explicit power-network mapping.

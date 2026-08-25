# [Search run: coupled multi-voltage corridors](@id search-run-2026-08-25-coupled-multivoltage-corridors)

**Protocol:** 0.2.0  
**Run date:** 2026-08-25  
**Purpose:** identify the electrical-modeling, protection, and data-model
precedents needed to discuss parallel line sections at different voltage levels
that share a mutual-impedance primitive.

## Targeted searches

The pass combined title/subject searches with backward citation chasing from
the direct multi-voltage papers. Query families included:

1. `mutual coupling parallel lines different voltage levels phase impedance`;
2. `multi-circuit multi-voltage overhead line mutual impedance per unit`;
3. `primitive admittance equivalent lattice mutually coupled branches`;
4. `partial mutual coupling line section protection out of service grounded`;
5. `CIM MutualCoupling line segment terminal`;
6. `PowSyBl line coupling extension`; and
7. `PowerWorld mutual impedance record coupled line fractions`.

DOI metadata was checked for journal and conference sources. The software and
information-model records were checked against official, version-pinned where
available, documentation rather than search-result snippets.

## Records added

Eight included, single-coded records were added:

- `EV-0030` — Wortman--Allen--Grigsby, a foundational unbalanced multiport
  building-block construction;
- `EV-0031` — Kersting, a joint model for physically parallel distribution
  circuits;
- `EV-0032` — Yan--Saha, the direct 11 kV/415 V phase-coordinate case;
- `EV-0033` — Dziendziel--Kocot--Kubek, geometry and per-unit treatment for
  multi-circuit multi-voltage HVAC lines;
- `EV-0034` — Tziouvaras--Altuve--Calero, protection consequences of partial
  overlap, orientation, switching, and grounded out-of-service circuits;
- `EV-0035` — IEC CIM `MutualCoupling` as a first-class relation;
- `EV-0036` — PowSyBl line couplings over identified line intervals; and
- `EV-0037` — PowerWorld's oriented, partial-section mutual-impedance record.

Grainger--Stevenson's textbook construction was added to the bibliography as
the classical source for converting an invertible reciprocal joint primitive
to an ordinary equivalent lattice. It is not coded as a separate evidence row
because this tranche uses the primary building-block paper for the general
equation-assembly result and the book supplies its own derivation and
executable certificate for the lattice identity.

## Synthesis decision

The literature supports three distinct statements that the chapter keeps
separate:

1. co-located circuits need not be graph-parallel or share nominal voltage;
2. their coupled sections belong to one joint phase-coordinate primitive; and
3. an invertible fixed-linear primitive can be stamped directly or represented
   by a generated ordinary-edge lattice at the equation level.

The source line assets and the coupling relation therefore remain canonical.
Generated cross-voltage edges are a lowering target with provenance, not new
conductors or a claim of galvanic connection.

## Limits

This was a targeted search and citation chase, not a fresh export from every
database named in the protocol. All new rows remain `single_coded`. The pass
does not establish geometry-to-impedance equivalence across all earth,
frequency, transposition, bundling, and shunt models. Nor does fixed-linear
terminal equivalence prove preservation of relay behavior, thermal limits,
switching decisions, or nonlinear feasible sets. Those scopes require separate
contracts and evidence.

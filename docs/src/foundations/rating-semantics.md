# [Rating and limit semantics](@id rating-semantics)

**Page status:** normative rating and limit vocabulary; utility-field mappings
remain future implementation work.

A rating is not a scalar decoration on an edge. It is a constraint attached to
an object, a quantity, an operating domain, and often an ambient or protection
assumption. A transformation can preserve the circuit equations while changing
which rating is enforceable.

## A typed limit

Represent a limit by a record

```math
\lambda=(a,\,q,\,\mathcal D,\,b,\,\chi,\,\omega),
```

where ``a`` is the constrained asset or terminal, ``q`` is the measured
quantity, ``\mathcal D`` is its domain, ``b`` is the bound, ``\chi`` is the
scenario/ambient validity condition, and ``\omega`` is the provenance or
protection owner. A feasible point ``x`` satisfies

```math
q_a(x,u;\theta)\in\mathcal D,
\qquad
q_a(x,u;\theta)\le b_a(\theta,\chi)
```

for every active limit record. The notation permits scalar, vector, complex,
thermal, apparent-power, and relay regions without pretending they are the
same constraint.

## Common distinctions

| Distinction | Examples | Why it matters for a reduction |
| --- | --- | --- |
| duration | continuous/normal, emergency, short-time | the admissible state and contingency set changes |
| environment | ambient-adjusted ampacity, seasonal, weather-dependent | the bound depends on ``\chi`` rather than only the asset |
| location | conductor, terminal equipment, transformer winding, busbar | a recovered branch current may not be the protected quantity |
| quantity | current magnitude, complex power, apparent power, temperature, CT/relay pickup | equal admittance does not imply equal feasible regions |
| ownership | line owner, protection zone, operator, investment project | a shared or aggregated limit can lose the decision owner |
| uncertainty | nameplate tolerance, forecast interval, scenario bound | nominal exactness is not robust preservation |

The running parallel cases use centered component-current discs as deliberately
simple limit regions. They are not nameplate ratings and should not be read as
continuous/emergency thermal limits. The certificate proves implication for
the declared discs and matrices only.

## Preservation obligations

When an object is projected, compiled, merged, or eliminated, the certificate
must classify each source limit as one of:

- **retained:** the same quantity and domain remain explicit;
- **mapped:** a recovery or coordinate map gives an exact target constraint;
- **conservative:** every target-feasible point satisfies the source limit,
  but valid source points may be excluded;
- **relaxed:** all source-feasible observations remain, but target points may
  violate a source limit;
- **scenario/uncertain:** implication is certified only over declared
  scenarios or parameter sets;
- **forgotten:** the target cannot answer the rating query.

In particular, a neutral-current limit after Kron elimination is normally
**mapped**, not forgotten: recover the eliminated neutral voltage or current
from the retained variables and impose the original magnitude or
multiconductor norm bound. A boundary ``Y`` matrix without that recovered
constraint answers terminal behaviour but not the neutral-rating decision.

For a parallel-line transformation, summing admittances preserves an aggregate
terminal relation but does not map two member limits to one scalar limit unless
the member feasible regions and their state/ownership semantics support that
map. The exact-pruning certificates in the guarded transformation cases retain the member factors and
remove only limits proved redundant under their declared nominal domains.

!!! warning "Power-system shorthand"
    “The line is rated at 200 A” is incomplete. Identify the member, terminal,
    conductor set, duration, ambient condition, measured quantity, and owner of
    the limit before comparing it with a transformed constraint.

## Vocabulary bridge to preservation contracts

The limit dispositions above describe what happens to an individual constraint;
the preservation-contract vocabulary describes the resulting feasible-set
relation. They are related, but not interchangeable:

| limit disposition | usual contract interpretation |
| --- | --- |
| retained | exact, with the same query still explicit |
| mapped | exact, provided the recovery map is part of the certificate |
| conservative | inner approximation |
| relaxed | outer approximation |
| scenario/uncertain | scenario-approximate |
| forgotten | no decision-level preservation claim |

This table is a translation aid, not a theorem: a single transformation can
retain some limits, map others, and forget the rest, so the contract must be
checked record by record.

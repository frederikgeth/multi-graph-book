# [From source data to a canonical network model](@id source-to-canonical-model)

**Page status:** semantic-projection and validation contract for entering a
network into the book's representation architecture.

The graph seen by a study is rarely copied directly from a source file. A
utility export, an OpenDSS deck, a CIM profile, or a solver dictionary carries
different mixtures of identifiers, terminals, implicit references, defaults,
device models, and study state. Before asking whether a graph transformation
preserves anything, we must know what network the source data actually means.

This chapter adapts the most useful BMOPFTools lesson to the book's broader
setting: ingestion is a **semantic projection**, not a promise of byte-level
round-trip identity. The output should be a canonical, typed network model
with explicit losses, inferences, and provenance.

## The projection contract

Let ``D`` be a source document and ``C`` a canonical network model. An adapter
is a partial map

```math
P:Dlongrightarrow (C,F,Pi),
```

where ``F`` is a finding ledger and ``\Pi`` is a provenance manifest. The map
is partial because an input may be malformed, incomplete, or outside the
supported factor library. A successful parse means only that ``P`` returned a
candidate model; it does not mean that every study question supported by ``D``
is preserved in ``C``.

The canonical model should make at least these objects explicit:

| Source concern | Canonical object | Why it matters for graphs |
|:--|:--|:--|
| stable equipment identity | asset/property record | keeps parallel and replacement assets distinct |
| endpoint and conductor names | ordered terminal maps | prevents phase/neutral permutations from hiding in matrices |
| connectivity and switching | state-resolved incidence | separates inventory topology from active topology |
| constitutive relation | line, shunt, transformer, load, or factor relation | prevents an edge from standing in for unknown physics |
| ratings and owners | typed constraint observations | keeps limits attached to the object they constrain |
| defaults and inferred meanings | finding with confidence/provenance | makes assumptions auditable |

The book's preferred identifiers retain the BMOPFTools-style ownership rule:
``\ell`` identifies an element, while ``\ell ij`` identifies an oriented
terminal attachment. A converter may reorder arrays or create virtual objects,
but it must publish the map that explains the change.

## Validation gates before graph construction

The following gates are deliberately ordered. A later graph cannot repair a
failure that should have been caught at an earlier semantic layer.

| Gate | Question | Typical failure |
|:--|:--|:--|
| schema | are fields and shapes structurally recognised? | malformed matrix or unknown component block |
| completeness | are required fields present for this factor subtype? | transformer winding lacks a terminal map |
| domain | are values physically and numerically plausible? | negative rating, impossible tap, invalid angle unit |
| integrity | do references and dimensions agree? | line points to a missing bus or mismatched conductor count |
| conformance | does the object satisfy study-specific rules? | WYE winding without a declared neutral or multiple active sources |
| readiness | is the declared decision problem well posed? | no voltage bounds, slack-only objective, or missing limit owner |

These checks should return stable finding codes and machine-readable details,
not only prose warnings. A graph quotient may be mathematically valid while
the input is semantically unfit for the intended decision problem.

## Inference is not identity

Practical formats often encode meaning positionally or through defaults. An
adapter may infer that terminal ``4`` is a neutral, that two named objects are
parallel members, or that a regulator is a transformer with a control loop.
Such inferences can be useful, but they are not source facts until recorded as
provenance-bearing findings. The canonical record should distinguish:

1. **declared** values copied from the source;
2. **derived** values computed from declared data;
3. **inferred** values introduced by an adapter rule; and
4. **unsupported** values that could not be represented.

This distinction is essential when a later transformation claims preservation.
An inferred terminal permutation may be harmless for a scalar connectivity
query but fatal for a conductor-current limit.

## What a safe adapter publishes

For every source-to-canonical map, record:

1. source format, profile, and version;
2. stable asset and terminal identifiers;
3. units, bases, phase, neutral, earth, and grounding conventions;
4. state, scenario, and control treatment;
5. factor, rating, and objective mappings;
6. generated objects and their source parents;
7. unsupported or lossy fields;
8. validation findings and their severity; and
9. round-trip or recovery checks for the declared observations.

The result is a transformation certificate at the data boundary. It is the
same preservation-contract language used later for Kron, aggregation, and
positive-sequence maps, but the source and target are data models rather than
electrical equations.

## Consequences for the graph views

The canonical model is not itself a single graph. It is the source from which
the book derives:

- an asset/dependency graph for ownership, maintenance, and failures;
- a terminal-connectivity graph for state and grounding questions;
- a directed/oriented multigraph for bus--branch equations;
- a port--factor graph for coupled and multi-terminal devices; and
- equation and sparsity graphs for a chosen formulation.

If the adapter collapses two assets, loses a neutral, or silently grounds a
terminal, every downstream view inherits that loss. Conversely, a solver may
create virtual buses or auxiliary factors that are useful computationally but
must map back to the canonical source objects before a decision or limit is
interpreted.

## Running-network application

The running fixture is intentionally small enough to audit. Its canonical
record declares four lines, a three-winding transformer, a switch, ordered
conductor sets, explicit neutral semantics, ratings, and state ownership.
The generated adapter crosswalk checks those obligations against the pinned
CIM/CGMES, PowerModelsDistribution, OpenDSS, and MATPOWER descriptions. That
crosswalk is not an import claim: it is a checklist of what an actual adapter
would have to preserve or mark unsupported.

The practical rule is therefore:

> Do not draw the graph first and infer the model later. Declare the canonical
> objects, validate them, and derive each graph as a named view with provenance.

This chapter supplies the missing front door for the representation maps. The
next chapters show how constitutive load and impedance choices can change the
feasible decision problem even when that front-door graph is unchanged.

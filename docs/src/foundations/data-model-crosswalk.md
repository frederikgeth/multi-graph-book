# [Data-model crosswalk](@id data-model-crosswalk)

The book's objects are semantic categories, not a claim that every software or
standard uses the same schema. This crosswalk records where common ecosystems
provide a direct correspondence, where an adapter is needed, and what meaning
must not be inferred from a successful import.

## Crosswalk

| Book object | CIM/CGMES | PowerModelsDistribution | OpenDSS | MATPOWER | Mapping status |
| --- | --- | --- | --- | --- | --- |
| asset/entity ``\mathfrak A`` | ``IdentifiedObject`` and typed equipment/asset classes | engineering dictionaries and source identifiers | named circuit objects and classes | row identity plus case metadata | partial; stable identity and lifecycle provenance need an adapter |
| terminal/port ``q`` | ``Terminal`` and phase attributes | engineering terminal maps and conductor sets | bus names with node/terminal suffixes | bus/branch endpoints, usually scalar bus indices | direct for topology; multiconductor semantics vary |
| connectivity node ``c`` | ``ConnectivityNode`` | engineering bus/connectivity data | bus connectivity | bus row in ``mpc.bus`` | direct only after phase/ground conventions are declared |
| topological node ``n_\sigma`` | ``TopologicalNode`` and state-derived topology | transformed mathematical bus/node set | active circuit connectivity | compiled bus set | state-resolved derived view |
| two-terminal factor | ``ConductingEquipment`` with terminals | line, switch, transformer, load, or generator object | line, transformer, reactor, load, generator | branch/gen/load rows | direct only within each tool's native factor library |
| multi-terminal factor | equipment plus multiple terminals | multiwinding transformer and coupled engineering objects | multiwinding/terminal object, often compiled for analysis | no native arbitrary-port object | requires a declared compiler and provenance |
| factor relation ``\mathcal R_\phi`` | electrical parameters plus profile-specific attributes | engineering-to-mathematical conversion and JuMP formulation | primitive stamping and solver model | standard ``\pi`` branch/gen/load equations | equations are not fully represented by topology data |
| rating/limit ``\lambda`` | equipment, operational limit, and profile-dependent attributes | thermal/current/voltage fields and correction routines | line/transformer/relay properties | branch/gen limits and extension fields | quantity, duration, ambient, and owner need explicit mapping |
| operating state | state variables, SSH/SV and equipment status profiles | multinetwork/state fields and conversion options | active/open objects and controls | ``status`` and in-service fields | scenario and provenance must be retained |

## Interpretation notes

CIM/CGMES is primarily an information and exchange model. Its distinction
between terminals, connectivity nodes, and topological nodes is especially
useful for the book's node--breaker compiler, but profile selection and state
processing remain part of the exchange contract [CIMTopologicalNode,
CGMESLibrary](@cite).

PowerModelsDistribution exposes an engineering data model and a conversion to
a mathematical model; the conversion may create several mathematical objects,
apply phase projection, Kron reduction, per-unit conversion, or multinetwork
expansion [PMDEngineering, PMDConversion](@cite). Those are precisely the kinds
of maps that this book requires to carry guards, source identities, and recovery
data.

OpenDSS is a practical circuit/equipment language with reduction operations.
Its reduction documentation is evidence of useful engineering procedures, not
a universal proof that limits, states, grounding, or provenance are preserved
[OpenDSSReduction](@cite).

MATPOWER's case format is intentionally compact: version-2 cases package
``baseMVA``, ``bus``, ``gen``, ``branch``, and optional ``gencost`` matrices, and
the conventional branch model combines lines, transformers, and phase shifters
in a common two-terminal representation [MATPOWERCaseFormat](@cite). The
modern data-model documentation makes the port/node connection idea more
explicit [MATPOWERDataModel](@cite), but arbitrary multiconductor factors,
asset lifecycle relations, and many-to-many provenance still require an
adapter.

## Adapter contract

An adapter should publish:

1. source format and version/profile;
2. identifier and terminal maps;
3. unit, base, phase, neutral, and grounding conventions;
4. state and scenario treatment;
5. factor and rating mappings;
6. generated objects and their provenance;
7. unsupported or lossy fields;
8. round-trip or recovery tests for the declared observations.

The crosswalk is therefore a starting vocabulary, not a certification that a
file imported successfully is semantically equivalent to the source model.


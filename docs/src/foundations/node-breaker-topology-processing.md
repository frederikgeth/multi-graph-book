# [Node--breaker, bus--breaker, and topology processing](@id node-breaker-topology)

**Page status:** scoped topology-processing definitions with a generated
node--breaker switch-state and radiality witness; larger running-network
topology lifts remain future work.

Topology processing is a state-conditioned compilation. It is not the same as
deleting switches from a graph or replacing every closed switch by a zero
impedance line without recording the state that justified the replacement.

## Connectivity and topological nodes

Let ``\mathcal T`` be the set of conducting-equipment terminals and let
``\mathcal C`` be connectivity nodes. A connectivity model records a partial
incidence map

```math
\kappa:\mathcal T\rightharpoonup\mathcal C
```

for zero-impedance terminal connections. Switches, breakers, disconnectors,
busbar sections, and jumpers are separate objects with a state
``\sigma_e``. For a fixed active state ``\sigma``, form the graph

```math
G_{\mathrm{closed}}(\sigma)
 = (\mathcal C,\{e:\sigma_e=\mathrm{closed}\}).
```

The **topological nodes** are the connected components of
``G_{\mathrm{closed}}(\sigma)``. Write

```math
\pi_\sigma:\mathcal C\longrightarrow\mathcal N_\sigma
```

for the component quotient. A bus--branch view is then compiled by attaching
each terminal to ``\pi_\sigma(\kappa(t))`` and retaining the conducting
equipment whose terminals are connected to distinct or equal topological
nodes.

This gives the state-resolved distinction:

| Object | Retained meaning |
| --- | --- |
| connectivity node | a zero-impedance connection point in the detailed model |
| switch/breaker | an identified asset with state, control, and protection semantics |
| topological node | a component of closed connectivity for one declared state |
| bus--branch bus | a compiled algorithmic node, often a topological node but not necessarily a physical bus |

An open switch remains an asset and a possible future action even though it is
not an edge of ``G_{\mathrm{closed}}(\sigma)``. A closed switch may disappear
from the compiled electrical equations for that state, but its provenance and
decision identity must remain recoverable.

## State-resolved compilation

Let ``M`` be a terminal or port--factor model with switch states. A topology
compiler is a partial map

```math
C_{\mathrm{top}}(M,\sigma)
 = (G_{\mathrm{bus}}(\sigma),\operatorname{prov}_\sigma,
    \operatorname{recover}_\sigma).
```

The compiler must declare:

1. the admissible state domain and whether unknown or failed states are
   allowed;
2. the zero-impedance relation used for contraction;
3. the component algorithm and treatment of isolated terminals;
4. the equipment classes that become bus--branch arcs;
5. the handling of loops, parallel members, multi-terminal factors, and
   grounding factors;
6. the map from each generated bus or arc to its source terminals and assets;
7. whether the compiled state is fixed, a scenario, or a decision variable.

For a fixed state, contracting closed ideal switches can preserve the declared
electrical connectivity relation. It does not preserve a switching decision,
protection boundary, maintenance identity, or an open-state contingency unless
those are carried by ``\operatorname{prov}_\sigma`` and the surrounding model.

## Node--breaker and bus--branch are not competing truths

The node--breaker view is the natural source for topology decisions because it
retains switching equipment and detailed connectivity. The bus--branch view is
often the natural target for a solved PF or OPF instance because it has fewer
nodes and a conventional incidence matrix. The transformation between them is
state- and purpose-relative:

| Question | Node--breaker view | State-resolved bus--branch view |
| --- | --- | --- |
| Which breaker is open? | direct | only through provenance/state metadata |
| Are two terminals connected now? | component query | same query after ``\pi_\sigma`` |
| Can a switch be operated? | direct decision object | lost if the quotient is frozen |
| What is the branch admittance? | attached factor or equipment | compiled arc relation |
| Are parallel assets distinct? | yes | yes only in a multigraph target |
| Is a multiwinding transformer native? | terminal/factor object | requires a declared compilation |

The simple graph of topological nodes is a further quotient. It may be useful
for islands and partitioning, but it forgets member identity and should not be
used as the source of switching or protection decisions.

### Generated state witness

The artifact
`experiments/generated/node-breaker-state-witness.json` uses four
connectivity nodes, three fixed line members, and two switch assets. It
enumerates four declared states: both switches open, a closed parallel switch,
a closed chord, and an unknown switch. For each resolved state it reports
member-radiality, simple adjacency-radiality, compiled-bus radiality, the
closed-switch contraction components, and the surviving line members. For the
unknown state it enumerates both admissible realizations rather than silently
choosing open or closed.

The witness exposes a useful separation:

| State | Member-radial | Adjacency-radial | Interpretation |
| --- | --- | --- | --- |
| both switches open | yes | yes | resolved tree |
| parallel switch closed | no | yes | member cycle hidden by simple projection |
| chord switch closed | no | no | visible adjacency cycle |
| switch unknown | unknown | unknown | report both admissible realizations |

These are state-conditioned predicates, not properties of the equipment
inventory alone. The compiled bus quotient can be radial even when the
identified-member graph is not, because closed ideal switches contract
connectivity components and remove self-loops from the bus view.

![Inventory and active-state radiality differ.](../assets/active-radiality.png)

The active-state panel makes the qualification explicit: report both the simple-projection predicate and the identified-member predicate, together with the state ``\sigma`` that selects open and closed members.

![One substation shown as four bus representations.](../assets/bus-meaning-overlays.png)

The same physical drawing is therefore not one graph with four labels: each overlay retains a different object set and answers different queries.

## Relation to CIM/CGMES and software topology views

CIM distinguishes equipment terminals and connectivity/topological nodes; the
topological-node layer is derived from the currently connected state rather
than being a replacement for equipment identity [CIMTopologicalNode,
CGMESLibrary](@cite). PowSyBl similarly describes topology views as a
state-dependent processing step [PowsyblTopology](@cite). These are useful
external precedents for ``\kappa`` and ``\pi_\sigma``; they do not by
themselves specify multiconductor factor equations, member-level ratings, or
decision-preserving reductions.

!!! warning "Decision-model consequence"
    A bus count that falls after switch contraction is not evidence that a
    switching problem has been preserved. The state and the contraction map
    are part of the model contract.

## Minimal running-case interpretation

In the running fixture, ``w_0`` is a switch between ``i_0`` and ``i_1``. The
fixed closed PF/OPF instance may compile it into a terminal connection, while
the discrete extension must retain ``w_0`` as an asset and state variable. The
parallel lines ``\ell_1`` and ``\ell_2`` remain separate identified factors
after topology processing; their common endpoint pair does not authorize
aggregation.

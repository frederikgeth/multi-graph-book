# Terminology

| Term | Meaning in this book |
| --- | --- |
| Asset | A physical or organizational entity with stable identity and lifecycle facts |
| Port | A typed interface at which variables interact with a component or subsystem |
| Junction | An interconnection object imposing equality/conservation structure |
| Factor | A constitutive, control, limit, measurement, or decision relation over ports |
| Hierarchy | Explicit containment with declared subsystem boundary ports |
| Projection | A map that forgets distinctions without solving governing equations |
| Compilation | Replacement of a high-level component by a realization in a target vocabulary |
| Normalization | A semantics-preserving rewrite into a selected canonical physical/model form |
| Behavioral reduction | Elimination of hidden variables preserving a declared external relation |
| Approximate reduction | Reduction with a stated observation domain, metric and error |
| Preservation contract | Precise statement of retained observations, constraints, assumptions and recovery |
| Recovery map | Map from retained/reduced variables to eliminated source quantities |
| Provenance | Traceable correspondence among source, generated and reduced objects |
| Morphism | A map preserving the declared structure within one representation framework |
| Isomorphism | A reversible morphism; a change of names or coordinates rather than a quotient or compilation |
| Query factorization | Evidence that a source query can be answered from a target because it factors through the declared transformation |
| Simple cycle | A closed cycle of at least three distinct vertices in a loopless simple graph |
| Line-identity cycle | A minimal-support nonzero vector in the incidence nullspace of an identified multigraph |
| Parallel fibre | The set of identified elements mapped to one unordered endpoint pair by the simple quotient |
| Bridge | An identified edge whose deletion increases the number of connected components in the declared graph |
| Radial tail | A maximal bridge path ending at a leaf in a specified graph and active state |
| Adjacency-radial | Forest property of the simple topology projection |
| Member-radial | Forest property of the identified line multigraph |
| Terminal power | Complex-power injection at one declared device terminal; generally one member of a two-end or multiport observation tuple |
| Energized | Connected through the declared active device states to an admissible source under the study's electrical semantics |
| Complex symmetric | Matrix satisfying ``\mathbf A^{\mathsf T}=\mathbf A``; not synonymous with Hermitian |
| Physical merge | Rewrite asserting that source assets are subdivisions or representations of one target asset |
| Composite equivalent | Behavioral object representing several source components without claiming homogeneous physical identity |
| Closure | Property that a model class remains in the same class under a transformation |
| Confluence | Property that different valid rewrite orders reach equivalent normal forms |

## Terms to use carefully

### Structure preserving

Always qualify the structure: Laplacian, sparsity, radiality, phase
connectivity, port-Hamiltonian form, equipment class, asset correspondence,
limits, or dynamic equations. The unqualified phrase is too ambiguous.

### Equivalent

Always state the interface, operating/model domain, observations, constraints,
and whether the claim is exact, conservative, relaxed, or approximate.

### Bus

Distinguish at least:

- physical busbar or busbar section;
- connectivity node;
- state-dependent topological node;
- mathematical nodal variable group;
- reporting or planning bus.

### Line

Distinguish:

- physical circuit or cable system;
- homogeneous construction segment;
- model section introduced by discretization;
- mathematical two-port branch;
- behavioral equivalent with no single physical counterpart.

### Flow

Distinguish a commodity-flow variable, an internal series current, a terminal
current, a terminal complex power, and an observed operating-point transfer.
A lossy AC branch generally has a pair of terminal powers rather than one
conserved edge-flow scalar.

### Directed

State whether direction means stored orientation, terminal-current sign,
positive power reference, observed operating transfer, causal dependency, or
one-way admissibility. These meanings do not imply one another.

### Connected and energized

Graph connectivity is a structural predicate. Energization additionally
depends on active state, admissible sources, terminal connectivity, and the
electrical semantics of the study.

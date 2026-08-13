# Literature map

The relevant work is substantial but fragmented across communities. No single
literature currently supplies the full combination of typed physical assets,
multiconductor terminal structure, exact/approximate behavioral maps,
decision-constraint preservation, provenance, and executable normalization
rules.

## Circuit and graph theory

Kron reduction gives the foundational boundary-variable elimination through a
Schur complement. Dörfler and Bullo analyze the resulting topology, algebra,
spectrum, effective resistance, and sensitivity for loopy Laplacians
[DorflerBullo2013](@cite). This is the right reference for exact linear
terminal reduction, but its retained graph is an equivalent network rather than
a physical asset model.

Caliskan and Tabuada extend Kron ideas to generalized electrical networks in
the time domain and identify homogeneity conditions under which compatible
network structure survives [CaliskanTabuada2014](@cite). This is one of the
closest theoretical precedents for construction-aware closure rules.

Circular planar resistor-network theory studies response matrices, local
electrical transformations and recoverability. Curtis and Morrow provide a
book-length treatment [CurtisMorrow2000](@cite). This literature teaches that
boundary equivalence, internal identifiability, minimality, and a unique normal
form are different questions.

Baez and Fong separate circuit syntax from external behavior through a
compositional black-box construction [BaezFong2018](@cite). Port-Hamiltonian
systems similarly emphasize energy, ports, interconnection and passivity
[vanderSchaftMaschke2013](@cite). These frameworks are strong foundations for
multiport composition but do not by themselves encode utility asset semantics
or OPF decision constraints.

## Power-system network reduction

The mainstream power-system literature emphasizes external-system equivalents,
Kron/Ward/REI methods, coherency, and dynamic model reduction. "Structure
preserving" has several meanings.

Ward's original construction treats suppressed loads and generation as
approximately constant current, retains tie terminals, and realizes the
external network as a boundary mesh with equivalent terminal injections
[Ward1949](@cite). The operating-state extended Ward construction addresses
boundary-bus designation, external shunts, and contingency use from a single
estimated state [Monticelli1979](@cite). Ward--PV instead retains external
generator buses after load-node elimination and may then aggregate coherent
generator groups [Machowski1988](@cite). These sources support a family
taxonomy, not one universal `Ward` operator.

Grudzien and coauthors use topology-guided reductions of lines, trees and
triangular subgraphs while preserving power-flow behavior for their model class
[Grudzien2018](@cite). Sistermanns and coauthors seek to avoid artificial
entities and maintain physical correspondence for important transmission-grid
features [Sistermanns2019](@cite). These works are directly relevant, although
they do not establish a general typed asset-preservation framework.

The line-limit-preserving equivalent work demonstrates that thermal transfer
constraints require special treatment beyond ordinary network equivalencing
[Jang2013](@cite). This should be regarded as a prototype of a broader theory
of decision-set preservation.

Molzahn studies a complementary operation for parallel scalar AC lines:
delete a flow-limit constraint only after a positive-semidefinite quadratic
containment test proves that another parallel member implies it at both line
ends [Molzahn2018](@cite). This is especially important for the book's
taxonomy. It is exact presolve on an unchanged physical model, not parallel
asset aggregation. The result gives a concrete decision-feasible-set
certificate and a useful transmission special case, while leaving open the
multiconductor, state-dependent, and asset-decision generalizations.
In the reported PEGASE cases, the method identified between 203 and 650
redundant parallel-line limits, with MIPS OPF runtime reductions of 2.0% to
5.7%; these are useful presolve results, not evidence for replacing the lines.

## Distribution feeder reduction

Pecenak and coauthors address multiphase unbalance, mutual coupling and spatial
variation while targeting accuracy at selected critical buses
[Pecenak2018](@cite). Opti-KRON work targets voltage reproduction, phase
connectivity [Mokhtari2027](@cite) and restored radiality
[MokhtariRadial2025](@cite). This literature is
more sensitive than classical transmission equivalents to phase availability
and feeder topology, but explicit neutral grounding, physical line codes,
parallel-asset decisions, protection and provenance remain underdeveloped.

OpenDSS implements practical reduction options including unloaded-intermediate
bus elimination, short-line merging, parallel-line merging and lateral
aggregation [OpenDSSReduction](@cite). These procedures are important test
cases for formalization: their operational usefulness is clear, while their
preservation domains and failure cases deserve explicit certificates.

## Topology processing and information models

CIM's connectivity/topological-node distinction and software such as PowSyBl
provide mature state-dependent topology processing [CIMTopologicalNode,
PowsyblTopology](@cite). This is perhaps the most widely deployed graph
projection in power-system operations. Its limitation is not correctness but
scope: connectivity quotienting is only one of the transformations needed.

PowerModelsDistribution provides a concrete engineering-to-mathematical
compiler and supports conductor terminals, grounding and multiwinding
transformers [PMDEngineering, PMDConversion](@cite). It offers an excellent
implementation case study for provenance-aware compilation.

## Graph transformation and model-driven engineering

Typed algebraic graph transformation supplies formal rule matching, negative
application conditions, rewrite composition, critical-pair analysis and
confluence [Ehrig2006](@cite). These ideas are common in software and systems
model transformations but have not been deeply integrated with power-system
network equivalents.

## Current assessment

| Topic | Attention | Main limitation relative to this agenda |
| --- | --- | --- |
| Switch topology processing | High | state quotient, not general physical normalization |
| Linear terminal/Kron equivalents | High | artificial edges; limits and assets usually omitted |
| Dynamic equivalents | High | preservation is input--output/dynamic, not asset semantic |
| Voltage/flow-oriented feeder reduction | Moderate | scenario/application dependent |
| Radiality and phase preservation | Emerging | limited device and neutral detail |
| Thermal-limit preservation | Specialized | not generalized to arbitrary decision constraints |
| Typed equipment-class closure | Low | few formal rewrite guards |
| Explicit neutral/grounding preservation | Low | often eliminated or treated as an implementation detail |
| Parallel-asset decision preservation | Low | exact scalar constraint pruning exists, but aggregation and multiconductor/state-dependent cases remain open |
| Provenance and reversible compilation | Low | implemented inconsistently, weakly theorized |
| Unified certified normalization | Very low | central research gap |

This table is a provisional assessment to be replaced by a systematic review
with a reproducible search protocol and coded evidence matrix.

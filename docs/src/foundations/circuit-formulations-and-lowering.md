# [Circuit formulations and the lowering boundary](@id circuit-formulations-and-lowering)

**Page status:** scoped formulation guide; the definitions and guards below are
book conventions supported by circuit and power-system precedents, while a
complete formulation-equivalence theory remains future work.

The same power network can be compiled into several equation systems. A nodal
admittance matrix is one particularly useful target, but it is not a universal
representation of general *power networks*. A numerical ``\mathbf Y`` may be
available while asset identity, switch states, branch currents, grounding,
multi-terminal behaviour, controls, limits, or decisions have already been
discarded. Conversely, a faithful source model may require a tableau, modified
nodal system, branch-current variables, or an unevaluated port--factor relation.

This chapter supplies the formulation boundary for [From source graphs to
views and graph surgery](@ref compiled-views-and-graph-surgery). The source
object and its view registry remain authoritative there; this chapter explains
what equation targets can and cannot be reached from those views.

## 1. Formulation families

Let ``\mathcal M`` be a declared power-network model with voltage, current,
power, control, state, and parameter variables. A formulation is a choice of
unknowns ``x``, equations ``F(x;u,\theta)=0``, inequalities ``g(x;u,\theta)\le
0``, and an observation map ``h``. The formulation is therefore more than a
matrix: the variable ownership, limits, state domain, and recovery map are
part of its contract.

| Formulation | Primary unknowns | Strong use | Typical loss or guard |
| --- | --- | --- | --- |
| nodal admittance | retained node voltages | fixed linear network stamping and PF linear subproblems | requires admittance-form branch relations; hides branch variables and asset identity |
| modified nodal analysis | node voltages plus selected branch currents | ideal voltage sources, current-controlled elements, switches, and mixed devices | larger saddle-point system; source provenance still has to be attached |
| sparse tableau | node, branch, port, and device variables | OPF limits, node--breaker models, multiport factors, and fixed sparsity | more variables and equations; elimination is a separate transformation |
| branch-current or branch-flow | voltages, currents, and often powers on identified members | explicit ratings, radial identities, and device-level constraints | equations depend on chosen branch model and orientation conventions |
| hybrid/port parameters | selected boundary efforts and flows | multiport composition and boundary equivalents | a representation is local to declared ports and may be singular at some frequencies or states |
| general port--factor relation | ordered typed ports and behavioural relations | nonlinear, controlled, dynamic, and multi-terminal equipment | not itself a single sparse matrix or ordinary graph |

The circuit literature distinguishes nodal analysis from modified and tableau
extensions precisely because some elements do not admit a convenient
admittance-only branch relation [HoRuehliBrennan1975, HachtelBraytonGustavson1971](@cite).
Power-system work makes the same boundary operational: sparse tableau
formulations retain multi-port element variables and node--breaker actions that
would otherwise require changing ``Y_{\mathrm{bus}}`` between states
[ParkHolzerDeMarco2019](@cite).

These formulations may be mathematically equivalent after elimination on a
restricted domain. They are not interchangeable source models: eliminating a
current variable can remove the direct place to attach a thermal limit, a
switch state, or a protection relation.

## 2. When an exact nodal admittance target exists

For a declared set ``\Phi_{\mathrm{lin}}`` of fixed linear factors, choose a
retained voltage vector ``\mathbf U``. If each factor has an admittance-form
terminal relation

```math
\mathbf i_\phi=\mathbf Y_\phi\mathbf A_\phi\mathbf U
```

and its current injection maps back through ``\mathbf A_\phi^{\mathsf T}``,
then assembly gives

```math
\mathbf Y^{\mathrm N}
 =\sum_{\phi\in\Phi_{\mathrm{lin}}}
   \mathbf A_\phi^{\mathsf T}\mathbf Y_\phi\mathbf A_\phi,
\qquad
\mathbf i^{\mathrm{inj}}=\mathbf Y^{\mathrm N}\mathbf U.
```

This is an assembly identity, not a claim that ``\mathbf Y^{\mathrm N}`` is a
canonical factorization or a complete power-network model. A useful sufficient
guard for exact nodal stamping is:

1. the retained variables are node-voltage coordinates sufficient for the
   declared observation and decision queries;
2. every included factor has a well-defined linear relation in those voltage
   coordinates, or has already been exactly eliminated with a declared Schur
   complement and recovery map;
3. voltage-source, current-controlled, dynamic, and algebraic-constraint
   variables that cannot be eliminated are retained elsewhere in the target;
4. the topology and device state used for assembly are fixed, or the target is
   rebuilt for each declared state;
5. grounding, reference, terminal maps, and coordinate order are declared; and
6. every limit, control, and decision that the study queries has a surviving
   variable or an explicit recovery/constraint map.

Failure of these guards does not make the network invalid. It means that a
bare ``\mathbf Y`` target is unavailable, incomplete, or semantically lossy for
the declared study. A reduced ``\mathbf Y`` can still be useful for a narrower
boundary-voltage query, provided that the omitted variables and limits are
recorded.

### A nodal matrix is not a complete power-network graph

The support of ``\mathbf Y^{\mathrm N}`` records nonzero coupling among the
retained voltage coordinates. It does not, by itself, record:

- which parallel assets contributed to one block;
- whether a coupling came from a line, transformer, grounding factor, or
  eliminated internal node;
- which switch or breaker state produced the assembled topology;
- branch currents and member-specific ratings;
- multi-terminal factor identity or internal winding variables; or
- the feasible-set and objective semantics of an OPF decision problem.

This is why [Two topology levels and the nodal projection](@ref
two-level-topology-and-nodal-projection) treats nodal support as a derived
computational view. A support graph can be useful and exact for one query while
being insufficient as the source of another.

## 3. Modified nodal and sparse tableau targets

Modified nodal analysis augments node voltages with currents through elements
whose constitutive relation is not naturally an admittance injection. A common
linear schematic form is

```math
\begin{bmatrix}
\mathbf Y & \mathbf B\\
\mathbf C & \mathbf D
\end{bmatrix}
\begin{bmatrix}\mathbf U\\\mathbf I_{\mathrm e}\end{bmatrix}
=
\begin{bmatrix}\mathbf J\\\mathbf e\end{bmatrix}.
```

The blocks encode KCL, selected element currents, voltage-source or control
relations, and any declared algebraic coupling. The matrix can be sparse even
when eliminating ``\mathbf I_{\mathrm e}`` would create dense fill-in.

A sparse tableau keeps this idea at the factor boundary. Let ``\mathbf z``
collect node, terminal, branch-current, power, and device variables. A tableau
target records

```math
\mathbf F_{\mathrm{KCL}}(\mathbf z)=0,
\qquad
\mathbf F_{\mathrm{KVL}}(\mathbf z)=0,
\qquad
\mathbf F_{\mathrm{device}}(\mathbf z;\theta)=0,
\qquad
\mathbf g(\mathbf z;\theta)\le 0.
```

This is especially useful when the study needs branch currents, multi-port
device variables, switch constraints, or member-level limits. The sparse
tableau node--breaker precedent keeps breaker actions in component constraints
instead of silently replacing each action with a new fixed ``Y_{\mathrm{bus}}``
[ParkHolzerDeMarco2019](@cite).

The tableau is not automatically “more physical” or “more canonical.” It is a
better target only for the declared questions. If the study asks only for a
fixed linear boundary voltage relation, eliminating tableau variables may be
appropriate; if it asks for switching, protection, or member ratings, the
uneliminated variables are part of the preservation contract.

## 4. Lowering from a source model

The formulation-aware compilation boundary is:

```math
\mathcal M
 \xrightarrow{C}
 \mathcal M_{\mathrm{port}}
 \xrightarrow{A}
 \mathcal E=(\mathbf F,\mathbf g,\operatorname{obs},\operatorname{prov}),
```

where ``\mathcal E`` is a declared equation/constraint operator. Optional
targets are then guarded lowerings:

```math
\mathcal E
 \xrightarrow{L_{\mathrm{MNA}}}
 \mathcal E_{\mathrm{MNA}},
\qquad
\mathcal E
 \xrightarrow{L_{\mathrm{Y}}}
 (\mathbf Y^{\mathrm N},\operatorname{recover})
 \quad\text{when the nodal guards hold.}
```

Direct factor stamping into ``\mathcal E`` is the default. ``L_Y`` is not an
automatic final pass after every factor compiler. It may fail because a factor
needs extra unknowns, because an elimination block is singular, because a
state-dependent switch changes the target structure, or because the resulting
matrix would omit a queried constraint. The compiler must return a diagnostic
and retain the source-to-target map rather than inventing a virtual admittance.

Every lowering record should state:

1. the source ports, factors, states, and coordinate order;
2. the target variables and equations;
3. the eliminated variables and the condition for elimination;
4. the preserved observations, constraints, and decisions;
5. the omitted semantics and unresolved guards; and
6. the recovery and provenance maps.

This is the formulation-specific instance of the general compiled-view
contract. It also explains why a compiler pipeline can legitimately stop at a
tableau or factor operator even when a smaller numerical matrix could be
constructed for a narrower query.

## 5. Scope collapses and literature alternatives

Several familiar power-flow models are valid collapses when their guards are
declared:

| Starting target | Collapse | What must be checked |
| --- | --- | --- |
| fixed linear port factors | ``\mathbf Y^{\mathrm N}`` | admittance-form relations, regular elimination, fixed grounding and state |
| MNA/tableau | nodal admittance | all retained extra variables are eliminable and unqueried |
| multiconductor model | scalar or positive-sequence ``Y`` | phase symmetry, balance, grounding, limits, and observations |
| node--breaker tableau | bus--branch ``Y_{\mathrm{bus}}`` | state fixed and switch/protection decisions outside the query |
| port--factor source | ordinary-edge graph | declared n-port realizability and retained provenance |

The alternatives are therefore not a contest for one universally best graph.
They are formulation choices indexed by the study's observations, constraints,
and decisions. The [representation taxonomy](@ref representation-taxonomy)
classifies their retained meanings; the [transformation semantics register](@ref
transformation-semantics-register) records the guards for moving among them.

!!! warning "Power-system shorthand"
    “The network has a Y-bus” usually means that one study formulation has
    assembled a nodal operator for one declared state and variable set. It does
    not mean that the full power-network source model is a simple graph, a
    two-terminal multigraph, or a lossless collection of admittance edges.

## 6. Evidence boundary

The circuit and power-system precedents establish that nodal, modified-nodal,
and sparse-tableau formulations are established alternatives. The book's
stronger claim—that a formulation-aware lowering contract can preserve the
declared power-network decisions and provenance—is a proposed architecture.
The generated artifact
`experiments/generated/circuit-formulation-witness.json` supplies three minimal
failure cases:

1. an ideal voltage source whose source current requires an MNA variable;
2. a floating two-node network whose nodal operator is singular without a
   reference or shunt; and
3. aligned parallel members whose aggregate admittance is exact for the
   terminal relation but cannot carry their distinct current limits.

The first case solves two right-hand sides in MNA form, showing identical source
voltage but different source currents. The other cases separate numerical
singularity from semantic loss. These are scoped formulation witnesses, not a
universal impossibility result for every circuit or power-network model.

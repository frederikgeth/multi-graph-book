# R2 engineering and scientific audit snapshot

Date: 2026-08-17

This snapshot records the formula-level audit completed before external
technical review. It is a scope and consistency audit, not an external
mathematical review and not a source-faithful validation of a utility model.

| Area | Checked obligations | Executable evidence | Remaining boundary |
|:--|:--|:--|:--|
| Positive sequence | Fortescue transform is invertible; decoupling requires circulant/sequence-invariant factors, compatible grounding, balanced data, symmetric decisions, and restricted observations; transposition alone is insufficient | `positive-sequence-collapse.jl`, balanced transmission witness, and non-circulant rejection | Controls, phase-specific limits, contingencies, and global decision equivalence remain open |
| Phase-to-neutral | The 3-by-4 map is a coordinate congruence, not neutral deletion or Kron reduction; zero-ground-current, shunt, grounding, and recovery guards are explicit | four-wire impedance ladder and grounding/Kron witnesses | Typed four-wire certificate and standards-aligned grounding validation remain open |
| Phase-to-phase | The 2-by-3 map quotients common mode; zero-sum current lifting and the active-tree guard are required; mesh, shunt, and multiple grounding create a residual | active-state radiality and four-wire/coordinate tests | General meshed and earth-coupled quotient theorem remains open |
| Kron | The internal block must be invertible; affine recovery assumes fixed internal injections; current coordinates use the power-dual action; transpose reciprocity is separated from adjoint coordinate covariance | typed Kron fixture, randomized covariance campaign, near-degenerate internal block, and running-network witnesses | Nonlinear/state-dependent and uncertainty-wide certification remain open |
| Ward and optimized equivalents | Ward-style targets are operating-point/scenario approximations; exact linear Kron, calibration-point agreement, scenario objective selection, and solver optimality are separate claims | Kron/Ward/Opti-KRON chapter fixtures and solver diagnostics | Source-faithful Opti-KRON implementation, global optimality, and external model validation remain open |
| Nominal-π and parallel limits | Series, shunt, terminal, and branch-current quantities are distinct; member identity and both-end constraints are retained for implication claims | scalar, multiconductor, four-wire, and nominal-π decision witnesses | Broader protection/contingency and asset-adapter claims remain scoped |

## Audit conclusions

1. The high-risk equations now state their invertibility, coordinate-dual,
   grounding, reciprocity, shunt-placement, and observation assumptions where
   they are used.
2. Numerical evidence now distinguishes algebraic residuals from solver and
   optimality claims. The typed Kron certificate records residual, tolerance,
   conditioning, backward error, and uncertainty status explicitly.
3. The repository distinguishes independent reimplementation of a synthetic
   fixture from source-faithful external-model validation. The former exists
   for selected witnesses; the latter remains an external-review item.
4. The claim ledger now carries a controlled `exactness_object` field for all
   95 claims. Claims that do not make an exactness assertion use
   `not_applicable`; claims about equations, boundary behaviour, feasible sets,
   connectivity views, representation definitions, and observed fixtures name
   their primary object explicitly. A claim can still preserve several
   dimensions; this field identifies the object to which its exactness label
   applies.

The complete executable suite passed after this audit, including the package
certificate matrix. No claim in this snapshot should be read as externally
reviewed.

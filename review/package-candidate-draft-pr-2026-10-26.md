# Prepared package draft PR

**State:** description only; no PR has been opened or package branch pushed by
this preparation. Repository: `frederikgeth/BMOPFTools.jl`.

**Proposed title:** Add coverage-aware independent solution audits and repair IBR monitor sharing

## Problem and resulting behavior

Solver status, aggregate power agreement and reported residual fields do not
establish independently evaluated device equations, nodal KCL or limit coverage.
Add direct SI `audit_linear_solution` and broader bounded `audit_solution` APIs
that preserve evaluated, reconstructed and unassessed obligations, explicit
tolerances and known failures under incomplete coverage.

The linear evaluator retains its narrow domain. The broader evaluator adds
supported source returns, constant-power load/coil incidence, fixed switches,
generator and transformer families, voltage/angle/sequence limits and bounded
AC IBR/control equations. It recognizes declared prices and rating metadata
without treating them as selected objectives or inferred limits. Unsupported
fields, topologies and missing observations retain explicit refusal boundaries.

For a combined four-leg IBR controller, monitoring the same quantity with
different effective averaging previously duplicated magnitude-definition keys.
Share the physical magnitude definitions while retaining controller-specific
per-phase/mean inputs and local normalization. Remove the matching audit refusal
after the full reference matrix builds and its supplied-point constraints pass.

## Scope and review entry points

- Audit implementation: `src/validation/linear_audit.jl`,
  `src/validation/connected_audit.jl` and their included family evaluators.
- Native monitor repair: `ext/BMOPFOpfExt/ibr.jl`.
- Examples and fixtures: `examples/*audit*.jl` and `test/data/linear_audit/`.
- Regression suite: family audit tests, especially
  `test/ibr_droop_composition_audit_tests.jl`.
- Runtime metadata and documentation: generated executable knowledge,
  `docs/src/tutorial_trust_but_verify.md` and related component conventions.

Keep the 31-commit history and review the complete difference from the accepted
base. This candidate does not expose the new audits through execution MCP,
replace the existing witness contract, or change the book's published package pin.

## Validation

Recorded candidate `6c6515153`: full package suite 54,774 passed / 37 broken;
focused combined-control tests 2,169 passed, including 1,512 semantic-input and
unique-definition assertions. All 72 topology/reference combinations build with
zero violated supplied-point native primal rows. Package Finding/export checks
pass. The source-bound book companion records 1,687 assertions and 50 source
bindings; its fresh portable run is reported separately in the handoff evidence.

The running case keeps three default-point generator P-bound failures and zero
unknown obligations; the tighter point passes bounded electrical checks. Both
points and settings are retained. The case has no IBR and is not evidence for
the control catalogue. Native/independent comparisons do not establish physical
adequacy or local/global optimality.

## Draft boundaries

Obtain scoped domain/implementation review, run package-owned hosted CI and
resolve findings before merge. Live/parameterized recipe authentication,
unsupported control/topology/filter/DC behavior, custom constraints and physical
adequacy remain outside the checked domain. No external-review or release
readiness claim follows from the local test totals. Integration repinning and
execution-MCP exposure require separate reviewed changes.

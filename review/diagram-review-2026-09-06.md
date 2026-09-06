# Scientific diagram revision, 6 September 2026

## Scope and review limits

The review inventoried the 33 figures used by the selective core before this
pass, screened their visible statements and drawings, and inspected the
renderers behind identified problems. Twelve existing figures were revised;
three were added. This was an internal scientific/editorial check, not an
independent rederivation of every inherited plot or external scientific review.
The full specialist figure library has not received an equivalent new audit.

Automated raster contrast and accessibility checks did not detect the scientific
errors below. Their pass status must not be described as mathematical validation.
The new quantitative regressions address specific earlier failures, not every
possible incorrect diagram.

## Corrections to existing figures

| Figure stem | Correction and reason |
| --- | --- |
| `orientation-power-transfer` | Replace ordering of complex power with terminal active-power sign. State the series-only current convention, separate reactive-power sign and account for losses. |
| `start-here-same-ybus` | Show the opening resistive calculation in amperes, with its conductances, ratings and 150 A/15 A witness. Remove the unsupported melting claim; the later MW dispatch example remains in the prose. |
| `parallel-feasible-set-card` | Plot both discs and the 15 V witness on one voltage scale. Remove the arbitrary ellipse: it represented an additional, unspecified constraint rather than this scalar calculation. |
| `recovery-map-loop` | Order target point, recovery and source checking correctly. Distinguish pointwise checking, universal target-to-source inclusion and the reverse inclusion required for observed-set equality. Correct the adjacent prose. |
| `source-canonical-pipeline` | Readiness concerns specified study inputs, not a guarantee of well-posedness. Name implementation conformance without declaring an unsupported connection physically invalid. |
| `kron-fill-in` | Remove the already-present boundary edge so the drawing actually demonstrates fill. State zero internal injection and invertibility of the eliminated block. |
| `start-here-radial-triangles` | Call the drawn cross-bus support cyclic, not triangular or chordal. It contains induced four-cycles and omits within-bus entries. Preserve the distinction from the separate full-stamp clique illustration. |
| `start-here-neutral-recovery` | Fix an unreadable subscript; remove an unqualified precision assertion; distinguish recovered current-limit enforcement from preservation of phase behavior alone. The numerical current/limit illustration is retained from the chapter. |
| `exactness-classes` | Show checked sample points rather than a certified sample region. Keep source boundaries visible through target outlines and state observation-level inclusion. |
| `formulation-lowering-lattice` | Replace the title's unsupported formal lattice characterization with formulation applicability conditions. |
| `parallel-redundancy-certificate` | Read bounds, ratings and served fractions from the certificate files. Use a single current scale; identify the depicted phase-a row; remove misleading map geometry and uncover bar labels. |
| `running-network-views` | Route the transformer attachment around unrelated line/factor boxes; remove a doubled transformer label. Source identities and attachment maps are unchanged; regenerate the figure hash in its source-map record. |

These changes delete no files. Replaced renderer bodies delegate to the shared
teaching renderer where appropriate, so the older rendering commands cannot
silently restore the superseded figures. Stable chapter anchors, claim IDs and
PSK identities remain unchanged.

## New worked diagrams

- **Equipment to matrix:** the actual `e1` stamp from `assemble_network.py`, its
  contribution to the assembled matrix, and the `(s,m,t)` to `(t,s,m)`
  permutation. Outlines identify the contribution without relying on colour.
- **Outage and reduction:** the equal-conductance star, its reduced triangle,
  the opened source and rebuilt equivalent. Exact labels distinguish the
  correct 1/2 S result from the tempting 1/3 S edge deletion.
- **Multiplier maps:** the analytical scaled multiplier curve and mapped
  physical sensitivity, plus the nonnegative line segment of duplicate-
  constraint multiplier allocations. The horizontal scaling axis is explicitly
  logarithmic; the two panels concern their declared distinct formulations.

The sentinel example remains a table. There are no new chapters or scientific
claims, and no new BMOPFTools capability is implied.

## Reproduction and regression coverage

`experiments/render_teaching_figures.py` produces seven SVG/PNG pairs using the
standard-library lesson calculations. Existing entry points remain available.
`experiments/render_parallel_certificate_geometry.py` reads the maintained
multiconductor and four-wire certificate data. Rendering needs `rsvg-convert`.
The case guide records the commands.

Four standard-library tests in `scripts/test_teaching_figures.py` check:

1. maintained teaching SVGs agree with their current renderers;
2. both parallel discs and the witness use the same scale;
3. the certificate bound/rating radius ratio agrees with the phase-a certificate
   and its retained-limit contributions;
4. served-fraction bar-height ratios agree with the certificate values.

The tests run in CI. Numerical rasterization and rounding are distinguished
from the exact lesson calculations. These tests supplement visual inspection;
they do not authenticate the physical input data or establish model adequacy.

Scientific knowledge, snapshot/live federation, deterministic LLM reproducibility,
claim mentions, artifact integrity, math hygiene, figure checks and the existing
assembly/practical lesson checks pass. The deterministic corpus has 913 records
and 81 answer-contract cases. Held-out hybrid recall at ten remains 46.6%, with
five zero-recall queries among 33. The ledger remains 112 claims: 106 self-checked,
six independently implemented and zero externally reviewed. No neural benchmark
or measured agent experiment was rerun; synthetic conformance and pilot fixtures
were regenerated under their existing evidence status.

The maintained family has 68 SVG/PNG pairs, in addition to the separately
checked raster-only views. HTML/PDF are rebuilt and changed figures inspected
at page scale; detailed author review remains the next step. The final PDF has
168 pages and the HTML library retains 78 pages. All 132 internal PDF links
and 39 PDF-to-library links resolve against the local build.

# Response to the expert review (2026-08-14)

## Disposition

I agree with the review's central diagnosis. The scientific core is now strong
enough that visible craft defects, missing approximation theory, and the shape
of the reader's route are the binding constraints. The figure suggestions are
also right: the next figures should carry arguments, not merely report that a
computation ran.

| Review theme | Disposition | Response and roadmap location |
|---|---|---|
| Dark PNG backgrounds | **Agree — repaired** | Generated preservation-contract and transformer SVGs now contain explicit white background rectangles and their PNG serialisations have been regenerated. The local figure audit remains the acceptance check. |
| Clipped/overprinted numerical witness | **Agree — repaired** | The canvas, lower-panel spacing, rotated labels, and legend placement were revised in `experiments/generate_numerical_structure_views.py`; the former overloaded witness is now represented by separate fill-in and Jacobian-dependency arguments. |
| Malformed chapter-status rows | **Agree — repaired** | The status parser now matches one physical metadata line and only consumes intentional wrapped continuation lines. It cannot cross a blank line into a heading, table, or body paragraph. The generated status and knowledge-base indexes were rebuilt. |
| Invisible `ARCH-PORT-001` evidence | **Agree — repaired** | The formal-framework chapter now names the claim, states exactly what the witness validates, and points to the generated evidence register. The repository-wide claim-to-prose audit is now enforced by `scripts/check_claim_mentions.py`. |
| Numerical certificate schema drift | **Agree — repaired** | The optional numerical block is aligned with schema v1.2, and generated certificates plus the artifact audit validate the resulting contract. |
| Positive-sequence collapse lacks numbers and a useful residual story | **Agree — repaired** | The numerical sequence witness, convention statement, and residual-to-decision discussion are now included in the collapse chapter and generated evidence. |
| Certified approximation is missing | **Agree — implemented with scope** | The Ward scenario fixture now composes parameter/model residual, state error, constraint margin, and decision margin, with certified/ambiguous/violated classification. Global nonlinear guarantees remain explicitly out of scope. |
| Ward taxonomy without construction | **Agree — repaired** | The extended-Ward support-injection construction is explicit, while the base-state target and Opti-KRON-style selector retain separate model contracts and provenance labels. |
| Earth/ground ladder needs a load-bearing fixture | **Agree — repaired** | The earth/ground model ladder is paired with explicit grounding witnesses and a phase-to-neutral versus neutral-Schur-complement comparison, scoped to the declared conductor model. |
| Crosswalk and route structure | **Agree — implemented** | The data crosswalk is organized around traps and model boundaries; `PAGES_PDF` is curated for argument value, `index.md` is a route paragraph, and Part I is split into representations versus physical/computational reference. |
| Figure portfolio | **Agree — implemented** | The argument batch and second explanatory batch are generated, audited, linked from their chapters, and checked for monochrome-safe SVG/PNG output. Existing result figures remain evidence rather than the sole explanatory layer. |

## Figure decisions

The supplied figure notes are adopted as a design brief with the following
priority order:

1. **Exactness classes as set containment.** This becomes the book's reusable
   visual definition of exact, inner, outer, and scenario-approximate.
2. **Recovery-map mechanism.** The same source/target picture will show the
   exact lifted case and the inflated feasible set produced when recovery is
   absent.
3. **Argument spine.** A full front-matter map is complemented by a thin
   chapter-header band, with one stage highlighted per chapter.
4. **Partial order under two query families.** The figure will make the
   incomparability of electrical and asset/dependency views visible.

The case-escalation grid, audience route map, sequence-subspace geometry,
bus-overlay figure, certificate-composition ladder, and guarded-rule gate are
the second batch. An orientation/power panel and a cycles/parallelism/radial
panel are supporting figures only if the existing five-bus argument figure and
the terminology chapters do not already carry those claims.

The duplicate scalar feasible-set cards have been consolidated and the
numerical-structure witness separated into its distinct structural claims. The
visual acceptance contract is: one claim per figure, a caption that states the
claim, explicit source/generator provenance, alt text, monochrome-safe
encodings, and both HTML/PDF render checks.

## Acceptance gates

- [x] repair the two dark-background PNGs;
- [x] repair the clipped numerical witness;
- [x] make chapter-status extraction line-safe and regenerate indexes;
- [x] surface `ARCH-PORT-001` in its defining chapter;
- [x] complete the schema v1.2 numerical-field decision;
- [x] implement and test the certified-approximation chain;
- [x] add the four first-batch argument diagrams and consolidate duplicates;
- [x] re-curate the PDF route and simplify the front-matter route map;
- [ ] obtain independent reviews for the highest-risk theorem claims.

The corresponding active queue is recorded in [`ROADMAP.md`](../../ROADMAP.md),
under M1, M2, and M4a. The completed items above are backed by the local
artifact, figure, claim, and build audits. The remaining independent review
gate, plus later-scope items such as global nonlinear bounds, package
publication, database double-coding, and solver-private factorization
diagnostics, remain tracked there.

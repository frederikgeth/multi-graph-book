# R3 search-and-coding release gate

**Date:** 2026-08-17  
**Protocol:** `review/protocol.md` v0.1.0  
**Scope:** literature-map strengthening and readiness for a defensible scoping-review release

## Gate decision

The literature-map tranche is complete, but the systematic-review gate remains
open. The repository must continue to describe the evidence base as a
**single-coded seed review**. It must not use systematic-review or PRISMA-style
language to imply exhaustive database coverage, complete screening, or
independent double-coding.

## Control status

| Control | Current evidence | Status | Release requirement |
|---|---|---|---|
| Database exports | Four dated targeted search records in `review/search-runs/`; no archived IEEE Xplore, Scopus, Web of Science, Compendex, Inspec, MathSciNet, or zbMATH exports | open | Preserve raw exports, platform/query/filter/result-count metadata, and export timestamps |
| Backward/forward citation chasing | Targeted citation chasing is recorded in `2026-08-15-information-model-citation-chase.md`; it is not a two-index backward/forward chase from the final eligible set | open | Record seed sources, backward and forward indexes, discovered records, and stopping rule |
| Duplicate resolution | `review/deduplication-register.csv` is joined to all 29 current matrix rows and validated by the snapshot checker | partial | Re-run DOI/title/author deduplication over the complete imported corpus and record unresolved probable duplicates |
| Screening | The matrix is a deliberately curated seed; it does not contain the screened-and-rejected universe needed for a PRISMA-style flow | open | Import all screened records and preserve inclusion, exclusion, uncertainty, and exclusion-reason fields |
| Independent human double-coding | `review/second-coding-2026-08-15.md` is an automated independent pass and disagreement log; it is not an independent human second code | open | Complete a blinded second pass, reconcile disagreements, and record coder identities and dates |
| Historical seed preservation | `review/snapshot-manifest.json` records the 29-row matrix, deduplication register, search runs, protocol inputs, hashes, and `independent_double_coding = false` | complete | Do not overwrite this snapshot when a later coded corpus is created |

## What is already safe to claim

- The seed matrix is reproducible as a 29-record, single-coded snapshot.
- The bibliography now has a stronger set of primary anchors for multiphase
  modelling, ground-return impedance, EMS topology processing, and provenance
  semantics.
- The rendered literature map distinguishes source authority from the book's
  synthesis and repository demonstrations.
- The current coverage and gap statements are provisional assessments of the
  coded seed matrix, not bibliometric prevalence results.

## Completion evidence required before closing this gate

1. Archive exports or a dated explanation for every database named in the
   protocol, including zero-result runs where applicable.
2. Archive backward and forward citation-chasing logs from the final eligible
   set, with the indexes used and the stopping rule.
3. Recompute the deduplication register against the imported corpus and retain
   the duplicate decisions as a versioned artifact.
4. Have an independent human coder complete the blank second-coding template
   without consulting the primary coding, then reconcile field-level conflicts.
5. Update the snapshot manifest with the new corpus, coding state, unresolved
   conflicts, and hashes; retain this 2026-08-17 seed snapshot unchanged.

Until those records exist, the appropriate release label is **expanded,
audited seed literature map**, not a completed systematic review.

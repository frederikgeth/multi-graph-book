# Federated scientific knowledge: end-to-end trace

**Page status:** maintained cross-repository implementation trace and scope boundary.

This page traces one scientific statement from book evidence to an executable BMOPFTools guardrail and back into the book's existing LLM context packet. The stable ownership rules are defined in the repository-root `ARCHITECTURE.md`; this page is the worked implementation trace.

## The linked objects

| Layer | Stable identity | Owner | Purpose |
|---|---|---|---|
| Scientific knowledge | `PSK-000001` | this book | States the scoped result and what it does not establish |
| Claims | `TR-PAR-001`, `TR-PAR-002`, `TR-PAR-003` | this book | Bind the statement to certificates and source passages |
| Misconception | `parallel-admittance-implies-decision-equivalence` | this book | Routes the dangerous shortcut to mandatory evidence |
| Executable contract | `parallel_member_limit_preservation` | BMOPFTools | Decides the supported scalar case or explicitly refuses it |
| API operation | `check_parallel_member_limit_preservation` | BMOPFTools | Exposes the contract as a structured result |
| Counterexample fixture | `parallel-rating-outer-relaxation-001` | BMOPFTools | Reproduces a minimized negative witness |
| Finding | `W.CONTRACT.PARALLEL_MEMBER_LIMIT_LOSS` | BMOPFTools | Reports loss of the member-constrained feasible region |

The same identifiers appear in two exports, but their contents do not have two owners. `generated/scientific_knowledge.jsonl` describes the scientific object. BMOPFTools' `generated/executable_knowledge.jsonl` describes code, Findings, and fixtures. `generated/federated-knowledge-pair-manifest.json` pins the matching export hashes and checks that both sides agree on their shared IDs.

## Scientific statement and evidence

`PSK-000001` states that summing fixed linear parallel admittances preserves the unconstrained aggregate terminal relation, while giving the aggregate the sum of member ratings can relax the member-constrained feasible set. Its declared scope is fixed-linear members with common endpoints and voltage coordinates, retained admittances, and explicit current limits.

The record deliberately does **not** establish that all parallel aggregation is invalid, that every aggregate rating is an outer relaxation, or that a scalar witness proves the multiconductor or state-dependent case. The claims and generated book artifacts remain the evidence authority; the package does not independently rewrite that conclusion.

## Executable decision

BMOPFTools receives an explicit mapping from source members to a target aggregate. In its current supported domain it requires scalar, finite, nonzero, series-only impedances, common terminal coordinates, and scalar ratings. It then performs two distinct checks:

1. It verifies that the target admittance equals the sum of the source-member admittances. Failure produces `E.CONTRACT.PARALLEL_TERMINAL_RELATION_MISMATCH`.
2. If terminal behavior is preserved, it compares the exact scalar voltage-drop region induced by every source member rating with the target aggregate-rating region. An inner restriction or outer relaxation produces `W.CONTRACT.PARALLEL_MEMBER_LIMIT_LOSS`.

Missing mapped data produces `W.CONTRACT.INDETERMINATE`. Multiconductor, shunted, singular, or otherwise out-of-domain cases produce `I.CONTRACT.NOT_APPLICABLE`. Those statuses are part of the scientific behavior: the implementation refuses to silently generalize beyond its declared domain.

For the minimized fixture, the two source lines have resistances 0.1 Ω and 1 Ω and ratings of 100 A each. Their summed admittance is 11 S, so the target resistance is 1/11 Ω. A naïve 200 A aggregate rating permits a voltage drop of about 18.18 V, while the source members permit only 10 V. At the committed 15 V witness, aggregate current is 165 A, but member currents are 150 A and 15 A. The target accepts the point while the first source member is overloaded. The exact scalar target rating is 110 A, not 200 A.

## Retrieval and answer contract

A query such as “Can a preprocessing pass merge parallel branches by summing admittance and capacity?” follows the existing misconception router. The context packet makes the three claims, three vocabulary concepts, and `knowledge:PSK-000001` mandatory. It retains the existing `qualified`, `under_retrieved`, and `unsupported` statuses and source-hash checks.

The packet now also exposes explicit sections:

- `scientific_basis` for the scoped PSK statement and evidence status;
- `known_misconceptions` for the tempting shortcut and required qualification;
- `counterexamples` for book artifacts and stable fixture identities;
- `executable_checks` for the BMOPFTools repository, contract IDs, Finding codes, fixtures, and implementation status;
- `implementation_examples` for concrete executable fixtures; and
- `unresolved_boundaries` for every claim the scientific object says it does not establish.

These are structured views over mandatory records, not a second retrieval index. The deterministic corpus, release identity, source hashes, retrieval evaluation, MCP route, HTTP route, and CLI route remain the book's established machinery.

## What generalizes

The federation pattern generalizes to other scientific guardrails:

- one stable PSK identity can link claims, misconceptions, artifacts, executable contracts, APIs, Findings, fixtures, and recipes;
- scientific and executable exports can evolve independently while a pair manifest detects incompatible releases;
- retrieval can make a PSK mandatory through the existing misconception graph;
- implementations can report `passed`, `failed`, `inapplicable`, or `indeterminate` without turning absence of evidence into a pass; and
- source hashes make context packets and cross-repository links auditable.

The numerical formula used by this first contract does **not** generalize automatically. The scalar voltage-drop reduction, lack of shunts, fixed linear admittances, common coordinates, and explicit current ratings are case-specific. Multiconductor coupling, nonlinear devices, operating-state dependence, protection quantities, switching choices, member provenance, and general feasible-set projection require separate PSK objects or broader contracts with their own evidence and fixtures.

## Reproduction and release pairing

From the book repository with BMOPFTools checked out beside it:

```bash
python3 scripts/generate_scientific_knowledge.py --check
python3 scripts/check_federated_knowledge.py --check --bmopf-root ../BMOPFTools.jl
python3 scripts/check_llm_reproducibility.py
```

From BMOPFTools:

```bash
python3 scripts/generate_executable_knowledge.py --check
julia --project=test --startup-file=no -e \
  'using Test, BMOPFTools; include("test/scientific_contract_tests.jl"); include("test/executable_knowledge_tests.jl")'
```

Changing either export requires regenerating and reviewing the pair manifest. A normal book-only check validates its pinned snapshot; the sibling-aware check proves that the local BMOPFTools checkout still matches that snapshot.

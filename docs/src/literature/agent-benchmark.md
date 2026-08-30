# [Scientifically constrained agent benchmark](@id agent-benchmark)

**Page status:** first transparent benchmark substrate; no agent runs or
condition effects are claimed.

The first benchmark slice asks a narrow question: can an agent reject a naïve
parallel-line aggregation when terminal behavior is preserved but member
current limits are not, and can it abstain when the same scalar result is
asserted outside its declared domain? The slice is anchored to `PSK-000001`,
the book's parallel-branch misconception route, and BMOPFTools'
`parallel_member_limit_preservation` contract and minimized fixture.

This is a benchmark *substrate*, not a benchmark result. It freezes tasks,
conditions, structured submissions, scoring, and source hashes. The committed
submissions are synthetic conformance fixtures that test the harness; no model
produced them, and their scores cannot support a claim that richer context
improves agent performance.

## Research question and first-slice boundary

The longer-term question is how much explicit positive and negative domain
knowledge can compensate for unreliable latent scientific knowledge in coding
agents. This first slice establishes only that the repository can pose and
score two relevant decisions reproducibly:

1. detect the invalid inference from summed admittance to summed-rating
   decision equivalence; and
2. abstain when a scalar, series-only contract is generalized to an unspecified
   multiconductor, shunted model.

The task is a structured scientific review, not a code-editing task. Eight
dimensions are exercised: schema validity, model-semantic correctness,
physical qualification, numerical witness validity, scientific-inference
correctness, reproducibility, invalid-assumption detection, and abstention.
`code_correctness` remains explicitly unscored until a later isolated patch
task has a package-owned executable oracle.

## Cumulative conditions

Each condition adds one capability to the previous condition. A controlled run
must otherwise hold the task text, order, runtime limits, model revision, and
scorer version fixed.

| ID | Added capability | Cumulative interpretation |
|---|---|---|
| `C0_MODEL_ONLY` | none | model prompt only |
| `C1_REPOSITORY_DOCS` | repository documentation | the same prompt plus repository prose |
| `C2_MACHINE_KNOWLEDGE` | scientific knowledge export | source-bound `PSK-*` records and the prior resources |
| `C3_EXECUTION_TOOLS` | read-only execution tools | deterministic access to the existing package surface |
| `C4_WORKFLOW_GUIDANCE` | agent workflow guidance | repository editing and scientific-guardrail instructions |
| `C5_EXECUTABLE_CONTRACTS` | executable contract and recipe | the reviewed package oracle and minimized fixture |
| `C6_NEGATIVE_KNOWLEDGE` | misconception and counterexample retrieval | explicit dangerous shortcut, qualifications, and negative evidence |

This condition order is a protocol choice, not an assumption that every added
capability must improve performance. Anchoring, distraction, or tool misuse may
make a richer condition worse; that is one reason actual runs must retain all
condition-level results.

## Cases and oracles

### Unsafe scalar aggregation

The proposal replaces two scalar series-only parallel members by one line with
summed admittance and summed current rating. The terminal relation is preserved,
but the target is an outer relaxation of the member-constrained feasible set.
A conforming response rejects approval, reports contract status `failed`,
classification `outer_relaxation`, Finding
`W.CONTRACT.PARALLEL_MEMBER_LIMIT_LOSS`, and the existing 15 V witness.

The numerical fields are not a new derivation in this benchmark. They are
checked against BMOPFTools' source-hash-bound fixture and contract evidence.

### Unsupported generalization

The second prompt asserts that the scalar result approves an otherwise
unspecified multiconductor, shunted aggregation. A conforming response abstains,
reports `inapplicable`, identifies `I.CONTRACT.NOT_APPLICABLE`, and states that
no preservation conclusion follows. It must not turn absence of executable
coverage into either acceptance or a claim of failure.

## Deterministic scoring and provenance

The canonical specification is
`benchmarks/agent/parallel-member-limits-v1.json`. JSON schemas define the task
and submission shapes. The checker validates the cumulative condition lattice,
stable identities, scoring coverage, scientific boundary, conformance fixtures,
book source hashes, the pinned federated pair, and—when a sibling path is
supplied—the referenced BMOPFTools files.

```sh
python3 scripts/check_agent_benchmark.py --check \
  --bmopf-root ../BMOPFTools.jl
```

One structured submission can be scored without changing the committed
conformance report:

```sh
python3 scripts/check_agent_benchmark.py --score \
  benchmarks/agent/submissions/conforming-c6.json
```

The generated manifest binds the exact book LLM corpus, federated pair,
BMOPFTools executable corpus, task specification, schemas, checker, and package
fixture/recipe sources. Missing provenance fails the reproducibility dimension;
it does not silently invalidate or rewrite the other dimension scores.

## Conformance evidence is not an agent comparison

The three committed submissions are deterministic scorer tests:

- one satisfies both task oracles and the pinned provenance;
- one approves the unsafe transformation and fails invalid-assumption
  detection;
- one handles the scalar case but overclaims at the unsupported boundary and
  fails abstention.

The generated report must continue to observe one passing fixture and two
failing fixtures. This establishes that the scorer distinguishes the intended
response classes. It does not establish model reliability, an advantage for
MCP, an effect of negative-knowledge retrieval, or generalization beyond the
two transparent cases.

## Next experimental step

A controlled pilot should pre-register model revisions, sampling settings,
resource exposure, task ordering, time/tool budgets, repetitions, and exclusion
rules. It should run at least the model-only, documentation, executable-contract,
and negative-knowledge conditions before expanding to all seven. Report every
dimension and abstention outcome by condition; do not collapse the study to one
top-line accuracy score.

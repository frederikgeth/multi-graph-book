# [Use this resource with ChatGPT](@id chatgpt-access)

**Page status:** reader-facing access and grounding guide. The repository's
developer/operator details remain in `llm/README.md`.

This resource can be used through ChatGPT at three levels. The first two are
convenient for readers; the third is the supported integration route for a
software application. In every case, treat the book's release identity and
evidence boundary as part of the answer, not as implementation detail.

## Quickest route: a ChatGPT Project

Create a Project, upload the released book PDF or the chapters relevant to the
question, and add the following project instructions:

> Use the attached resource as the primary authority. Answer in the reader's
> domain language, but preserve the resource's qualifications. State the source
> representation, derived representation or formulation, operating state, and
> exactness or preservation object. Distinguish physical assets and behavioural
> factors from graph and matrix views. Explain the tempting short answer and why
> it can fail. Cite the relevant chapter, claim, or source anchor. If the
> resource does not establish the answer, say **unsupported by this resource**
> and identify what evidence would be needed.

Projects keep related files, chats, and instructions together. They are useful
for a reader who wants to ask follow-up questions over several sessions. See
[Projects in ChatGPT](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt)
for the current product instructions and limits.

Begin with a question that declares the audience and task, for example:

> I am a power engineer. Using only this resource, explain whether a
> constant-admittance load belongs in the graph, in the nodal admittance
> matrix, or both. Separate source-model identity from formulation placement
> and cite the relevant sections.

Uploading a book to a conversation or Project gives ChatGPT a snapshot of the
files supplied for that workspace. It is not a live connection to this
repository, so check the release identity when the answer matters.

## Reusable route: a custom GPT

A custom GPT can package the same approach for a class, team, or public reader
experience. Configure it with:

- the curated release bundle as Knowledge;
- the answer contract above as Instructions;
- conversation starters for students, power engineers, software engineers,
  and mathematical modellers;
- a requirement to name the release identity and cite chapter or claim
  anchors; and
- an explicit `unsupported` response when no qualified evidence is found.

Custom GPTs use uploaded Knowledge files and configured Instructions inside
ChatGPT. They are not a live synchronization mechanism: update the Knowledge
files whenever a new book release changes the supported content. See
[GPTs in ChatGPT](https://help.openai.com/en/articles/8554407-gpts-in-chatgpt)
and [Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-a-gpt)
for current configuration and sharing details.

Creating or publishing a new GPT depends on the current account and workspace
permissions. If GPT creation is unavailable, use a Project with the same files
and instructions; an existing shared GPT can still be used when the reader has
access to it.

Do not describe a custom GPT as an independent authority. It is a reader
interface over a particular resource release. Its instructions should require
the same distinctions and abstention behaviour as the book.

## Developer route: the grounded access service

The repository contains a model-independent corpus and a deterministic local
access service. From the repository root:

```sh
python3 scripts/serve_llm_access.py --port 8787
```

The service provides:

- `GET /healthz` for availability;
- `GET /v1/manifest` for the corpus release identity and hashes;
- `GET|POST /v1/search` for ranked source records; and
- `GET|POST /v1/context` for an answer-oriented context packet.

The context packet is the preferred interface for an application. It carries
the supported answer basis, representation and scope, qualifications,
counterexamples, structured negative results, numerical pathologies, scope
boundaries, and open questions,
source anchors, evidence status, and an explicit
`unsupported` or `under_retrieved` result when the corpus cannot support a
qualified answer. The downstream model should render that packet into the
user's domain language; it should not replace the packet with uncited model
memory.

Compatible local clients can use the MCP adapter:

```sh
python3 scripts/mcp_llm_server.py
```

The local service and MCP adapter are developer interfaces. A normal ChatGPT
conversation cannot call a service running on a private computer unless a
separate, trusted integration makes it available. For a hosted application,
load the generated corpus into a retrieval service or API vector store and
retain the corpus manifest identifier and source metadata.

## Recommended answer contract

Every grounded answer should contain, as applicable:

1. a direct answer supported by the resource;
2. the named representation, formulation, state, and exactness object;
3. assumptions and load-bearing qualifications;
4. the tempting shortcut and its failure consequence;
5. a translation into the reader's domain language without changing meaning;
6. chapter, claim, or source anchors and their evidence status; and
7. an unresolved boundary or an explicit `unsupported` status.

The answer should not call a nodal matrix “the network” without naming the
source model and formulation. It should not call a graph self-loop a shunt,
or assume that a load or generator has one fixed graph membership across all
studies. These are precisely the shortcuts for which the retrieval layer keeps
misconception contracts.

## Keeping ChatGPT context synchronized

The canonical sources are the Markdown chapters, claims ledger, vocabulary
registry, evidence artifacts, and release manifest. The generated corpus is a
derived access artifact. Do not edit it by hand.

At each release:

1. regenerate the corpus from canonical sources;
2. run the LLM accessibility and retrieval checks;
3. publish the corpus manifest with its source commit and hashes;
4. rebuild any hosted retrieval index or custom GPT Knowledge files; and
5. test the audience prompts and high-risk misconception cases against the new
   release before presenting it as current.

A Project or custom GPT uploaded before step 4 is a stale snapshot. Its answers
must not be described as representing the latest book release.

## Choosing the route

| Need | Recommended route | Main limitation |
|---|---|---|
| One reader asking questions | ChatGPT Project with uploaded chapters | File snapshot; not automatically synchronized |
| Class or team reader experience | Custom GPT with a pinned release bundle | Knowledge must be rebuilt when the book changes |
| Software or service integration | `/v1/context`, MCP, or hosted retrieval/API | Requires deployment and integration work |
| Unstructured ordinary ChatGPT question | Use only for orientation | The answer is not necessarily book-grounded |

For scientific or engineering decisions, use a grounded route and inspect the
source anchors. The model's fluency is not evidence that the resource supports
the conclusion.

# [Use this resource with Claude](@id claude-access)

**Page status:** reader-facing access and grounding guide. The repository's
developer/operator details remain in `llm/README.md`.

This resource can be used through Claude at four levels. The first two are
convenient for readers; the third connects Claude to a live, versioned view of
this repository; the fourth is the supported integration route for a software
application. In every case, treat the book's release identity and evidence
boundary as part of the answer, not as implementation detail.

The companion page [Use this resource with ChatGPT](@ref chatgpt-access)
documents the same obligations for that assistant. The two pages differ in one
substantive way: Claude can connect directly to this repository's local access
service through the Model Context Protocol, so a grounded route is available to
a reader without building an application.

## Quickest route: a Claude Project

Create a Project, add the released book PDF or the chapters relevant to the
question as project knowledge, and set the following custom instructions:

> Use the attached resource as the primary authority. Answer in the reader's
> domain language, but preserve the resource's qualifications. State the source
> representation, derived representation or formulation, operating state, and
> exactness or preservation object. Distinguish physical assets and behavioural
> factors from graph and matrix views. Explain the tempting short answer and why
> it can fail. Cite the relevant chapter, claim, or source anchor. If the
> resource does not establish the answer, say **unsupported by this resource**
> and identify what evidence would be needed.

Projects keep related files, chats, and instructions together, so a reader can
ask follow-up questions over several sessions without restating the contract.
See [Projects in Claude](https://support.anthropic.com/en/articles/9517075-what-are-projects)
for the current product instructions and limits.

Begin with a question that declares the audience and task, for example:

> I am a power engineer. Using only this resource, explain whether a
> constant-admittance load belongs in the graph, in the nodal admittance
> matrix, or both. Separate source-model identity from formulation placement
> and cite the relevant sections.

Adding files to a Project gives Claude a snapshot of what was uploaded to that
workspace. It is not a live connection to this repository, so check the release
identity when the answer matters.

## Reusable route: a shared Project

A Project shared with a class or team packages the same approach for repeated
use. Configure it with:

- the curated release bundle as project knowledge;
- the answer contract above as custom instructions;
- starter questions for students, power engineers, software engineers, and
  mathematical modellers;
- a requirement to name the release identity and cite chapter or claim
  anchors; and
- an explicit `unsupported` response when no qualified evidence is found.

Project sharing depends on the current plan and workspace permissions. If
sharing is unavailable, each reader can build the same Project from the same
release bundle and instructions.

A shared Project is not a synchronization mechanism: update its knowledge files
whenever a new book release changes the supported content. Do not describe such
a Project as an independent authority. It is a reader interface over a
particular resource release, and its instructions should require the same
distinctions and abstention behaviour as the book.

## Connected route: the MCP server

This repository ships an adapter for the
[Model Context Protocol](https://modelcontextprotocol.io/), so Claude can query
the generated corpus directly instead of reading an uploaded snapshot. From the
repository root the adapter runs as a local stdio server:

```sh
python3 scripts/mcp_llm_server.py
```

It advertises the server name `multi-graph-book` and exposes two tools and one
resource:

- `book_search` returns ranked, stable, source-linked corpus records. It takes
  `query`, and optionally `limit` and a `method` of `lexical`, `char_tfidf`,
  `hybrid`, or `graph`.
- `book_context` returns an answer-oriented context packet. It takes the same
  arguments plus an optional `audience` of `student`, `software_engineer`, or
  `power_engineer`.
- `book://multi-graph-book/manifest` exposes the corpus release identity and
  record count as a resource.

To use it from Claude Code, register the server once:

```sh
claude mcp add multi-graph-book -- python3 /absolute/path/to/scripts/mcp_llm_server.py
```

To use it from the Claude desktop app, add the same command to the app's MCP
server configuration:

```json
{
  "mcpServers": {
    "multi-graph-book": {
      "command": "python3",
      "args": ["/absolute/path/to/scripts/mcp_llm_server.py"]
    }
  }
}
```

See the [Claude Code MCP documentation](https://docs.claude.com/en/docs/claude-code/mcp)
and the [desktop app guide](https://support.anthropic.com/en/articles/10167454-using-the-claude-desktop-app)
for current configuration details.

This route differs from an uploaded Project in a way that matters for
correctness. The adapter reads the generated corpus in the working tree, so the
answers follow whatever release is checked out, and `book_context` supplies the
qualification structure rather than leaving Claude to reconstruct it from prose.
The adapter is local and read-only over generated artifacts; it does not publish
the repository, and it cannot be reached by a Claude conversation on another
machine.

The corpus is a derived access artifact. If it has not been regenerated for the
current sources, this route reports a stale release identity rather than a
silently different answer, which is why the manifest resource is worth reading
before trusting a result.

## Developer route: the grounded access service

For a hosted application, the same service is available over HTTP:

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
counterexamples, structured negative results and numerical pathologies,
source anchors, evidence status, and an explicit `unsupported`
or `under_retrieved` result when the corpus cannot support a qualified answer.
The downstream model should render that packet into the user's domain language;
it should not replace the packet with uncited model memory.

An application built on the Claude API should expose `book_search` and
`book_context` as tools rather than pasting corpus text into a prompt, so that
the abstention status and source anchors survive into the answer. See the
[tool use documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
for the current request shape. Record the model identifier alongside the corpus
manifest identifier: an answer is reproducible only when both are known.

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

## Keeping Claude context synchronized

The canonical sources are the Markdown chapters, claims ledger, vocabulary
registry, evidence artifacts, and release manifest. The generated corpus is a
derived access artifact. Do not edit it by hand.

At each release:

1. regenerate the corpus from canonical sources;
2. run the LLM accessibility and retrieval checks;
3. publish the corpus manifest with its source commit and hashes;
4. rebuild any hosted retrieval index or Project knowledge files; and
5. test the audience prompts and high-risk misconception cases against the new
   release before presenting it as current.

The MCP and HTTP routes pick up step 1 automatically, because they read the
generated corpus rather than a copy of it. A Project uploaded before step 4 is
a stale snapshot, and its answers must not be described as representing the
latest book release.

## Choosing the route

| Need | Recommended route | Main limitation |
|---|---|---|
| One reader asking questions | Claude Project with uploaded chapters | File snapshot; not automatically synchronized |
| Class or team reader experience | Shared Project with a pinned release bundle | Knowledge must be rebuilt when the book changes |
| Reader who has the repository checked out | MCP server via Claude Code or the desktop app | Local process; requires a checkout and a regenerated corpus |
| Software or service integration | `/v1/context`, MCP, or hosted retrieval/API | Requires deployment and integration work |
| Unstructured ordinary Claude question | Use only for orientation | The answer is not necessarily book-grounded |

For scientific or engineering decisions, use a grounded route and inspect the
source anchors. The model's fluency is not evidence that the resource supports
the conclusion.

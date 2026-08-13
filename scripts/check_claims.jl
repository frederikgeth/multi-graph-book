using TOML

const ROOT = normpath(joinpath(@__DIR__, ".."))
const LEDGER = joinpath(ROOT, "claims", "claims.toml")
const BIBLIOGRAPHY = joinpath(ROOT, "docs", "src", "references.bib")
const REQUIRED = Set([
    "claim_id", "chapter", "claim_text", "status", "evidence_type",
    "citation_keys", "model_scope", "assumptions", "reviewer",
    "review_date", "unresolved_issue",
])
const STATUSES = Set([
    "definition", "established_result", "empirical_result",
    "engineering_practice", "interpretation", "proposal",
    "conjecture", "open_question",
])

ledger = TOML.parsefile(LEDGER)
claims = get(ledger, "claim", Any[])
isempty(claims) && error("claims ledger contains no claims")

bib = read(BIBLIOGRAPHY, String)
bibkeys = Set(match.captures[1] for match in eachmatch(r"@[A-Za-z]+\s*\{\s*([^,\s]+)", bib))
ids = Set{String}()

for claim in claims
    missing = setdiff(REQUIRED, Set(keys(claim)))
    isempty(missing) || error("$(get(claim, "claim_id", "<unknown>")) missing fields: $(sort!(collect(missing)))")
    id = claim["claim_id"]
    id in ids && error("duplicate claim_id: $id")
    push!(ids, id)
    claim["status"] in STATUSES || error("$id has unknown status $(claim["status"])")
    isfile(joinpath(ROOT, claim["chapter"])) || error("$id chapter does not exist: $(claim["chapter"])")
    for key in claim["citation_keys"]
        key in bibkeys || error("$id cites missing BibTeX key: $key")
    end
end

println("claims ledger: $(length(claims)) unique claims; all paths, statuses, and citation keys valid")

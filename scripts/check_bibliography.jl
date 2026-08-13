using TOML

const ROOT = normpath(joinpath(@__DIR__, ".."))
const BIBLIOGRAPHY = joinpath(ROOT, "docs", "src", "references.bib")
const AUDIT = joinpath(ROOT, "review", "bibliography-audit.toml")
const ALLOWED_STATUSES = Set(["verified", "corrected"])

bib = read(BIBLIOGRAPHY, String)
bibkeys = Set(match.captures[1] for match in eachmatch(r"@[A-Za-z]+\s*\{\s*([^,\s]+)", bib))
dois = [lowercase(strip(match.captures[1])) for match in eachmatch(r"(?im)^\s*doi\s*=\s*\{([^}]+)\}", bib)]
length(dois) == length(unique(dois)) || error("bibliography contains duplicate DOI fields")

audit = TOML.parsefile(AUDIT)
entries = get(audit, "entry", Any[])
auditkeys = Set{String}()
for entry in entries
    for field in ("key", "status", "verification_source", "verified_on", "note")
        haskey(entry, field) || error("bibliography audit entry is missing $field")
    end
    key = entry["key"]
    key in auditkeys && error("duplicate bibliography audit key: $key")
    push!(auditkeys, key)
    entry["status"] in ALLOWED_STATUSES || error("$key has invalid audit status $(entry["status"])")
    startswith(entry["verification_source"], "https://") ||
        error("$key verification source is not an HTTPS URL")
    occursin(r"^\d{4}-\d{2}-\d{2}$", entry["verified_on"]) ||
        error("$key has invalid verification date")
end

missing = setdiff(bibkeys, auditkeys)
extra = setdiff(auditkeys, bibkeys)
isempty(missing) || error("BibTeX keys without audit entries: $(sort!(collect(missing)))")
isempty(extra) || error("audit entries without BibTeX records: $(sort!(collect(extra)))")

println("bibliography audit: $(length(bibkeys)) records covered; $(length(dois)) unique DOI fields")

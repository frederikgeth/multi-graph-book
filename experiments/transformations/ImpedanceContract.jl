module ImpedanceContract

using TOML

export contract_schema, validate_impedance_contract

const VALID_STATUSES = Set(["declared", "derived", "inferred", "unsupported", "unresolved"])

function contract_schema(path=joinpath(@__DIR__, "..", "data", "impedance_contract_schema.toml"))
    TOML.parsefile(path)
end

function _required(value, key, findings, context)
    if !haskey(value, key)
        push!(findings, "IMP-MISSING-FIELD:$context.$key")
        return nothing
    end
    value[key]
end

"Return stable finding codes; an empty vector means the v0.1 contract is valid."
function validate_impedance_contract(contract; schema=contract_schema())
    findings = String[]
    schema_id = _required(contract, "schema_id", findings, "contract")
    version = _required(contract, "schema_version", findings, "contract")
    schema_id == schema["schema"]["id"] || push!(findings, "IMP-SCHEMA-ID")
    version == schema["schema"]["version"] || push!(findings, "IMP-SCHEMA-VERSION")
    elements = _required(contract, "elements", findings, "contract")
    elements isa AbstractVector || push!(findings, "IMP-ELEMENTS-TYPE")
    elements isa AbstractVector || return findings
    isempty(elements) && push!(findings, "IMP-NO-ELEMENTS")
    required = schema["schema"]["required_element_fields"]
    valid_statuses = Set(schema["schema"]["status_vocabulary"])
    for (index, element) in enumerate(elements)
        context = "elements[$index]"
        element isa AbstractDict || begin
            push!(findings, "IMP-ELEMENT-TYPE:$context")
            continue
        end
        for key in required
            _required(element, key, findings, context)
        end
        terminals = get(element, "terminals", nothing)
        terminals isa AbstractVector && length(terminals) >= 2 || push!(findings, "IMP-TERMINALS:$context")
        blocks = get(element, "blocks", nothing)
        if !(blocks isa AbstractDict)
            push!(findings, "IMP-BLOCKS-TYPE:$context")
        else
            for block in schema["blocks"]["required"]
                _required(blocks, block, findings, "$context.blocks")
            end
        end
        units = get(element, "units", nothing)
        units isa AbstractDict || push!(findings, "IMP-UNITS-TYPE:$context")
        limits = get(element, "limits", nothing)
        if !(limits isa AbstractDict)
            push!(findings, "IMP-LIMITS-TYPE:$context")
        else
            for key in schema["limits"]["required"]
                _required(limits, key, findings, "$context.limits")
            end
        end
        grounding = get(element, "grounding", nothing)
        if !(grounding isa AbstractDict)
            push!(findings, "IMP-GROUNDING-TYPE:$context")
        else
            for key in schema["grounding"]["required"]
                _required(grounding, key, findings, "$context.grounding")
            end
            get(grounding, "status", nothing) in valid_statuses || push!(findings, "IMP-GROUNDING-STATUS:$context")
        end
        provenance = get(element, "provenance", nothing)
        if !(provenance isa AbstractDict)
            push!(findings, "IMP-PROVENANCE-TYPE:$context")
        else
            for key in schema["provenance"]["required"]
                _required(provenance, key, findings, "$context.provenance")
            end
            status = get(provenance, "status", nothing)
            status in valid_statuses || push!(findings, "IMP-STATUS:$context")
        end
        get(element, "views", nothing) isa AbstractVector || push!(findings, "IMP-VIEWS-TYPE:$context")
        findings_value = get(element, "findings", nothing)
        if !(findings_value isa AbstractVector)
            push!(findings, "IMP-FINDINGS-TYPE:$context")
        else
            for finding in findings_value
                finding isa AbstractDict || push!(findings, "IMP-FINDING-TYPE:$context")
                finding isa AbstractDict || continue
                get(finding, "code", "") isa AbstractString || push!(findings, "IMP-FINDING-CODE:$context")
                get(finding, "severity", "") in ("info", "warning", "error") || push!(findings, "IMP-FINDING-SEVERITY:$context")
            end
        end
    end
    unique(findings)
end

end

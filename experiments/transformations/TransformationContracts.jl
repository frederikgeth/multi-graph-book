module TransformationContracts

export CERTIFICATE_CLASSIFICATIONS,
       compose_certificates,
       validate_certificate

const CERTIFICATE_CLASSIFICATIONS = Set([
    "exact_normalization",
    "exact_behavioral_reduction",
    "inner_restriction",
    "outer_relaxation",
    "scenario_approximate",
    "mixed",
])

const REQUIRED_FIELDS = Set([
    "schema_version",
    "certificate_id",
    "rule_id",
    "classification",
    "source",
    "target",
    "preconditions",
    "preserves",
    "forgets",
    "recovery_map",
    "constraint_map",
    "provenance",
    "evidence",
])

"Return structural errors in a package-independent certificate dictionary."
function validate_certificate(certificate::AbstractDict)
    errors = String[]
    missing = setdiff(REQUIRED_FIELDS, Set(String.(keys(certificate))))
    isempty(missing) || push!(errors, "missing fields: $(join(sort!(collect(missing)), ", "))")
    get(certificate, "schema_version", nothing) == "1.0.0" ||
        push!(errors, "unsupported schema_version")
    get(certificate, "classification", nothing) in CERTIFICATE_CLASSIFICATIONS ||
        push!(errors, "unknown classification")
    for side in ("source", "target")
        value = get(certificate, side, nothing)
        if !(value isa AbstractDict)
            push!(errors, "$side must be an object")
            continue
        end
        haskey(value, "model_category") || push!(errors, "$side is missing model_category")
        ids = get(value, "object_ids", nothing)
        ids isa AbstractVector && !isempty(ids) || push!(errors, "$side must contain object_ids")
    end
    for field in ("preconditions", "preserves", "forgets")
        get(certificate, field, nothing) isa AbstractVector || push!(errors, "$field must be an array")
    end
    for field in ("recovery_map", "constraint_map", "provenance", "evidence")
        get(certificate, field, nothing) isa AbstractDict || push!(errors, "$field must be an object")
    end
    errors
end

function prefixed_map(prefix, mapping)
    Dict("$prefix.$key" => value for (key, value) in mapping)
end

"""
Compose two exact certificates whose generated/source identities meet.

Recovery is recorded in reverse execution order. The function rejects a
composition whose first target is not consumed by the second rule or whose
classification is not exact.
"""
function compose_certificates(
    first::AbstractDict,
    second::AbstractDict;
    certificate_id,
)
    isempty(validate_certificate(first)) || throw(ArgumentError("invalid first certificate"))
    isempty(validate_certificate(second)) || throw(ArgumentError("invalid second certificate"))
    startswith(first["classification"], "exact_") ||
        throw(ArgumentError("first certificate is not exact"))
    startswith(second["classification"], "exact_") ||
        throw(ArgumentError("second certificate is not exact"))

    intermediate = Set(String.(first["target"]["object_ids"]))
    second_sources = Set(String.(second["source"]["object_ids"]))
    isempty(intersect(intermediate, second_sources)) &&
        throw(ArgumentError("first target is not a source of the second rule"))

    untouched_second_sources = setdiff(second_sources, intermediate)
    source_ids = sort!(collect(union(
        Set(String.(first["source"]["object_ids"])),
        untouched_second_sources,
    )))
    first_preserves_all = "all_declared_source_semantics" in first["preserves"]
    preserved = first_preserves_all ? String.(second["preserves"]) :
        collect(intersect(Set(String.(first["preserves"])), Set(String.(second["preserves"]))))

    result = Dict{String,Any}(
        "schema_version" => "1.0.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "sequential_composition",
        "classification" => second["classification"],
        "source" => Dict(
            "model_category" => "composed_source_models",
            "object_ids" => source_ids,
            "detail" => Dict(
                "component_model_categories" => [
                    first["source"]["model_category"],
                    second["source"]["model_category"],
                ],
            ),
        ),
        "target" => deepcopy(second["target"]),
        "preconditions" => unique(vcat(String.(first["preconditions"]), String.(second["preconditions"]))),
        "preserves" => unique(preserved),
        "forgets" => unique(vcat(String.(first["forgets"]), String.(second["forgets"]))),
        "recovery_map" => merge(
            prefixed_map("reverse_step_1", second["recovery_map"]),
            prefixed_map("reverse_step_2", first["recovery_map"]),
        ),
        "constraint_map" => merge(
            prefixed_map("forward_step_1", first["constraint_map"]),
            prefixed_map("forward_step_2", second["constraint_map"]),
        ),
        "provenance" => Dict(
            "component_certificates" => [first["certificate_id"], second["certificate_id"]],
            "intermediate_object_ids" => sort!(collect(intermediate)),
            "execution_order" => [first["rule_id"], second["rule_id"]],
        ),
        "evidence" => Dict(
            "composition_check" => "the first target is consumed by the second rule",
            "recovery_order" => "apply the second recovery map, then the first recovery map",
        ),
    )
    errors = validate_certificate(result)
    isempty(errors) || error("internal composition error: $(join(errors, "; "))")
    result
end

end

module TransformationContracts

export CERTIFICATE_CLASSIFICATIONS,
       attach_typed_interfaces,
       compose_certificates,
       validate_certificate

const CERTIFICATE_CLASSIFICATIONS = Set([
    "exact_normalization",
    "exact_compilation",
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
    "interfaces",
    "preconditions",
    "preserves",
    "forgets",
    "recovery_map",
    "constraint_map",
    "provenance",
    "evidence",
])

const TYPED_STATE_SPACE_REF = "experiments/generated/state-space-unit-witness.json"
const NUMERICAL_OPTIMALITY_STATUSES = Set([
    "not_applicable", "not_assessed", "local", "branch_scoped", "global_certified",
])

function unit_families(label)
    text = lowercase(String(label))
    families = String[]
    (occursin("voltage", text) || occursin(r"(^|[^a-z])v([^a-z]|$)", text)) && push!(families, "voltage")
    (occursin("current", text) || occursin(r"(^|[^a-z])a([^a-z]|$)", text)) && push!(families, "current")
    any(token -> occursin(token, text), ("power", "mva", "mw", "kw")) && push!(families, "power")
    (occursin("ohm", text) || occursin("impedance", text)) && push!(families, "impedance")
    (occursin("siemens", text) || occursin("admittance", text) || occursin(r"(^|[^a-z])s([^a-z]|$)", text)) &&
        push!(families, "admittance")
    (occursin("dimensionless", text) || occursin("per-unit", text) || occursin(r"(^|[^a-z])pu([^a-z]|$)", text)) &&
        push!(families, "dimensionless")
    sort!(unique(families))
end

"Attach the canonical typed state-space/unit crosswalk to a certificate dictionary."
function attach_typed_interfaces(certificate::AbstractDict; state_space_ref=TYPED_STATE_SPACE_REF)
    interfaces = certificate["interfaces"]
    source_units = String.(interfaces["units"]["source"])
    target_units = String.(interfaces["units"]["target"])
    labels = sort!(unique(vcat(source_units, target_units)))
    unit_map = Dict(label => unit_families(label) for label in labels)
    unresolved = [label for label in labels if isempty(unit_map[label])]
    typed = Dict{String,Any}(
        "state_space_ref" => String(state_space_ref),
        "source_variable_labels" => unique(String.(interfaces["state_variables"]["source"])),
        "target_variable_labels" => unique(String.(interfaces["state_variables"]["target"])),
        "source_unit_families" => sort!(unique(vcat(unit_families.(source_units)...))),
        "target_unit_families" => sort!(unique(vcat(unit_families.(target_units)...))),
        "source_boundary_labels" => unique(String.(interfaces["boundary_quantities"]["source"])),
        "target_boundary_labels" => unique(String.(interfaces["boundary_quantities"]["target"])),
        "state_domain_ids" => String[],
        "unit_family_map" => unit_map,
        "unresolved_unit_labels" => unresolved,
        "attachment_rule" => "certificate-local interface labels are crosswalked to the checked typed state-space/unit vocabulary; unresolved labels remain explicit rather than being guessed",
    )
    result = deepcopy(certificate)
    result["typed_interfaces"] = typed
    result
end

"Return structural errors in a package-independent certificate dictionary."
function validate_certificate(certificate::AbstractDict)
    errors = String[]
    missing = setdiff(REQUIRED_FIELDS, Set(String.(keys(certificate))))
    isempty(missing) || push!(errors, "missing fields: $(join(sort!(collect(missing)), ", "))")
    get(certificate, "schema_version", nothing) == "1.1.0" ||
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
    if haskey(certificate, "numerical_evidence")
        numerical = certificate["numerical_evidence"]
        if !(numerical isa AbstractDict)
            push!(errors, "numerical_evidence must be an object")
        else
            for name in (
                "solver_status", "optimality_status", "residual", "tolerance",
                "conditioning", "backward_error", "uncertainty_status",
            )
                haskey(numerical, name) || push!(errors, "numerical_evidence.$name is missing")
            end
            get(numerical, "solver_status", nothing) isa AbstractString ||
                push!(errors, "numerical_evidence.solver_status must be a string")
            get(numerical, "optimality_status", nothing) in NUMERICAL_OPTIMALITY_STATUSES ||
                push!(errors, "numerical_evidence.optimality_status is unknown")
            for name in ("residual", "tolerance", "backward_error")
                value = get(numerical, name, nothing)
                value isa Real && value >= 0 ||
                    push!(errors, "numerical_evidence.$name must be nonnegative")
            end
            tolerance = get(numerical, "tolerance", nothing)
            tolerance isa Real && tolerance > 0 ||
                push!(errors, "numerical_evidence.tolerance must be positive")
            conditioning = get(numerical, "conditioning", nothing)
            (conditioning === nothing || conditioning isa Real && conditioning >= 0) ||
                push!(errors, "numerical_evidence.conditioning must be nonnegative or null")
            get(numerical, "uncertainty_status", nothing) isa AbstractString ||
                push!(errors, "numerical_evidence.uncertainty_status must be a string")
        end
    end
    interfaces = get(certificate, "interfaces", nothing)
    if !(interfaces isa AbstractDict)
        push!(errors, "interfaces must be an object")
    else
        for name in ("state_variables", "constraints", "decisions", "objectives", "units", "boundary_quantities")
            mapping = get(interfaces, name, nothing)
            if !(mapping isa AbstractDict)
                push!(errors, "interfaces.$name must be an object")
                continue
            end
            get(mapping, "source", nothing) isa AbstractVector ||
                push!(errors, "interfaces.$name.source must be an array")
            get(mapping, "target", nothing) isa AbstractVector ||
                push!(errors, "interfaces.$name.target must be an array")
            get(mapping, "relation", nothing) isa AbstractString ||
                push!(errors, "interfaces.$name.relation must be a string")
        end
    end
    if haskey(certificate, "typed_interfaces")
        typed = certificate["typed_interfaces"]
        if !(typed isa AbstractDict)
            push!(errors, "typed_interfaces must be an object")
        else
            for name in (
                "state_space_ref", "source_variable_labels", "target_variable_labels",
                "source_unit_families", "target_unit_families", "source_boundary_labels",
                "target_boundary_labels", "state_domain_ids", "unit_family_map",
                "unresolved_unit_labels", "attachment_rule",
            )
                haskey(typed, name) || push!(errors, "typed_interfaces.$name is missing")
            end
            for name in (
                "source_variable_labels", "target_variable_labels", "source_unit_families",
                "target_unit_families", "source_boundary_labels", "target_boundary_labels",
                "state_domain_ids", "unresolved_unit_labels",
            )
                value = get(typed, name, nothing)
                value isa AbstractVector || push!(errors, "typed_interfaces.$name must be an array")
            end
            get(typed, "state_space_ref", nothing) isa AbstractString ||
                push!(errors, "typed_interfaces.state_space_ref must be a string")
            get(typed, "unit_family_map", nothing) isa AbstractDict ||
                push!(errors, "typed_interfaces.unit_family_map must be an object")
            get(typed, "attachment_rule", nothing) isa AbstractString ||
                push!(errors, "typed_interfaces.attachment_rule must be a string")
        end
    end
    errors
end

function prefixed_map(prefix, mapping)
    Dict("$prefix.$key" => value for (key, value) in mapping)
end

function composed_interfaces(first, second)
    Dict(name => Dict(
        "source" => String.(first["interfaces"][name]["source"]),
        "target" => String.(second["interfaces"][name]["target"]),
        "relation" => "first: $(first["interfaces"][name]["relation"]); second: $(second["interfaces"][name]["relation"])",
    ) for name in ("state_variables", "constraints", "decisions", "objectives", "units", "boundary_quantities"))
end

function composed_typed_interfaces(first, second)
    first_typed = first["typed_interfaces"]
    second_typed = second["typed_interfaces"]
    first_typed["state_space_ref"] == second_typed["state_space_ref"] ||
        throw(ArgumentError("typed interface attachments use different state spaces"))
    Dict(
        "state_space_ref" => first_typed["state_space_ref"],
        "source_variable_labels" => String.(first_typed["source_variable_labels"]),
        "target_variable_labels" => String.(second_typed["target_variable_labels"]),
        "source_unit_families" => String.(first_typed["source_unit_families"]),
        "target_unit_families" => String.(second_typed["target_unit_families"]),
        "source_boundary_labels" => String.(first_typed["source_boundary_labels"]),
        "target_boundary_labels" => String.(second_typed["target_boundary_labels"]),
        "state_domain_ids" => unique(vcat(
            String.(first_typed["state_domain_ids"]), String.(second_typed["state_domain_ids"]),
        )),
        "unit_family_map" => merge(first_typed["unit_family_map"], second_typed["unit_family_map"]),
        "unresolved_unit_labels" => unique(vcat(
            String.(first_typed["unresolved_unit_labels"]),
            String.(second_typed["unresolved_unit_labels"]),
        )),
        "attachment_rule" => "sequential composition carries the typed source attachment from step one and target attachment from step two",
    )
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
        "schema_version" => "1.1.0",
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
        "interfaces" => composed_interfaces(first, second),
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
    if haskey(first, "typed_interfaces") && haskey(second, "typed_interfaces")
        result["typed_interfaces"] = composed_typed_interfaces(first, second)
    end
    errors = validate_certificate(result)
    isempty(errors) || error("internal composition error: $(join(errors, "; "))")
    result
end

end

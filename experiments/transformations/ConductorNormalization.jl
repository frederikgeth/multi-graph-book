module ConductorNormalization

using ..SeriesElimination: SeriesElement

export NormalizationRejection,
       NormalizationResult,
       normalize_conductor_coordinates

struct NormalizationResult
    target::SeriesElement
    certificate::Dict{String,Any}
end

struct NormalizationRejection
    rule_id::String
    source_id::String
    requested_order::Vector{String}
    failed_guards::Vector{String}
end

function permutation_matrix(source_labels, target_labels)
    Set(source_labels) == Set(target_labels) || return nothing
    P = zeros(Float64, length(source_labels), length(source_labels))
    for (row, label) in enumerate(target_labels)
        column = findfirst(==(label), source_labels)
        column === nothing && return nothing
        P[row, column] = 1.0
    end
    P
end

function complex_matrix_rows(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

"""
Rewrite a series element into a requested from-terminal coordinate order.

If `x_new = P*x_old`, then `Z_new = P*Z_old*P'`. The same row permutation is
applied to the paired to-terminal map and to componentwise current limits.
"""
function normalize_conductor_coordinates(
    source::SeriesElement,
    requested_order;
    certificate_id="TR-COORD-001",
)
    order = String.(requested_order)
    failed_guards = String[]
    length(order) == length(source.terminals_from) ||
        push!(failed_guards, "requested_coordinate_arity_mismatch")
    length(unique(order)) == length(order) ||
        push!(failed_guards, "requested_coordinate_labels_not_unique")
    Set(order) == Set(source.terminals_from) ||
        push!(failed_guards, "requested_coordinate_set_differs_from_source")
    isempty(failed_guards) || return NormalizationRejection(
        "conductor_coordinate_normalization",
        source.id,
        order,
        unique(failed_guards),
    )

    P = permutation_matrix(source.terminals_from, order)
    P === nothing && error("internal error: normalization guards passed without a permutation")
    target_to = [source.terminals_to[findfirst(==(label), source.terminals_from)] for label in order]
    impedance = P * source.impedance * transpose(P)
    current_limit = source.current_limit === nothing ? nothing : P * source.current_limit
    target_id = "normalized__$(source.id)__$(join(order, "_"))"
    target = SeriesElement(
        target_id,
        source.bus_from,
        source.bus_to,
        order,
        target_to,
        impedance;
        current_limit=current_limit,
        construction_code=source.construction_code,
    )

    certificate = Dict{String,Any}(
        "schema_version" => "1.0.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "conductor_coordinate_normalization",
        "classification" => "exact_normalization",
        "source" => Dict(
            "model_category" => "ordered_multiconductor_series_element",
            "object_ids" => [source.id],
        ),
        "target" => Dict(
            "model_category" => "ordered_multiconductor_series_element",
            "object_ids" => [target.id],
            "detail" => Dict(
                "terminal_map_from" => target.terminals_from,
                "terminal_map_to" => target.terminals_to,
                "impedance_ohm" => complex_matrix_rows(target.impedance),
                "current_limit_A" => target.current_limit,
            ),
        ),
        "preconditions" => [
            "requested and source conductor labels are unique",
            "requested and source conductor sets are equal",
            "each from-terminal label remains paired with its original to-terminal label",
        ],
        "preserves" => [
            "all_declared_source_semantics",
            "external_terminal_voltage_current_relation",
            "conductor_identity",
            "componentwise_current_limits",
            "source_to_target_provenance",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "source_coordinates" => "x_source = P' * x_target",
            "source_impedance" => "Z_source = P' * Z_target * P",
        ),
        "constraint_map" => Dict(
            "target_coordinates" => "x_target = P * x_source",
            "target_impedance" => "Z_target = P * Z_source * P'",
            "target_componentwise_limit" => "i_max_target = P * i_max_source",
        ),
        "provenance" => Dict(
            "generated_object" => target.id,
            "source_element" => source.id,
        ),
        "evidence" => Dict(
            "permutation_matrix" => [collect(row) for row in eachrow(P)],
            "source_order" => source.terminals_from,
            "target_order" => target.terminals_from,
        ),
    )
    NormalizationResult(target, certificate)
end

end

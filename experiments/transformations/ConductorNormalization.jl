module ConductorNormalization

using ..SeriesElimination: SeriesElement
using ..CoordinateActions: CoordinateActionRejection,
                           coordinate_action,
                           pushforward_bilinear,
                           pushforward_vector

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
    isempty(source.mutual_couplings) || return NormalizationRejection(
        "conductor_coordinate_normalization",
        source.id,
        order,
        ["element_pair_mutual_coupling_requires_joint_normalization"],
    )
    action = coordinate_action(source.terminals_from, order)
    action isa CoordinateActionRejection && return NormalizationRejection(
        "conductor_coordinate_normalization",
        source.id,
        order,
        action.failed_guards,
    )

    P = action.permutation
    target_to = [source.terminals_to[findfirst(==(label), source.terminals_from)] for label in order]
    impedance = pushforward_bilinear(action, source.impedance)
    current_limit = source.current_limit === nothing ? nothing :
        pushforward_vector(action, source.current_limit)
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
        "schema_version" => "1.1.0",
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
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["ordered conductor state x_source"],
                "target" => ["ordered conductor state x_target"],
                "relation" => "x_target = P * x_source",
            ),
            "constraints" => Dict(
                "source" => ["source-coordinate componentwise current limits"],
                "target" => ["target-coordinate componentwise current limits"],
                "relation" => "constraint coordinates are permuted by P",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "any conductor-indexed decisions must follow the same permutation; none occur in this example",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "the rule declares no objective term",
            ),
            "units" => Dict(
                "source" => ["V", "A", "ohm"], "target" => ["V", "A", "ohm"],
                "relation" => "permutation changes order but not units",
            ),
            "boundary_quantities" => Dict(
                "source" => ["source-order terminal voltage and current vectors"],
                "target" => ["target-order terminal voltage and current vectors"],
                "relation" => "boundary vectors map bijectively by P and P'",
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

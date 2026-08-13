module SeriesElimination

export JunctionContext,
       SeriesElement,
       TransformationCertificate,
       TransformationRejection,
       TransformationResult,
       certificate_dict,
       eliminate_degree_two

"A two-terminal series element with explicitly ordered conductor coordinates."
struct SeriesElement
    id::String
    bus_from::String
    bus_to::String
    terminals_from::Vector{String}
    terminals_to::Vector{String}
    impedance::Matrix{ComplexF64}
    current_limit::Union{Nothing,Vector{Float64}}
    construction_code::Union{Nothing,String}

    function SeriesElement(
        id,
        bus_from,
        bus_to,
        terminals_from,
        terminals_to,
        impedance;
        current_limit=nothing,
        construction_code=nothing,
    )
        n = length(terminals_from)
        length(terminals_to) == n || throw(ArgumentError("terminal maps must have equal length"))
        size(impedance) == (n, n) || throw(ArgumentError("impedance must be $n by $n"))
        length(unique(terminals_from)) == n || throw(ArgumentError("from-terminal labels must be unique"))
        length(unique(terminals_to)) == n || throw(ArgumentError("to-terminal labels must be unique"))
        current_limit === nothing || length(current_limit) == n ||
            throw(ArgumentError("current limit must have one entry per conductor"))
        new(
            String(id),
            String(bus_from),
            String(bus_to),
            String.(terminals_from),
            String.(terminals_to),
            ComplexF64.(impedance),
            current_limit === nothing ? nothing : Float64.(current_limit),
            construction_code === nothing ? nothing : String(construction_code),
        )
    end
end

"Facts at the candidate junction that can block a degree-two elimination."
Base.@kwdef struct JunctionContext
    id::String
    injections::Vector{String} = String[]
    shunts::Vector{String} = String[]
    measurements::Vector{String} = String[]
    controls::Vector{String} = String[]
    protection_boundaries::Vector{String} = String[]
    external_couplings::Vector{String} = String[]
end

struct TransformationCertificate
    certificate_id::String
    classification::String
    source_ids::Vector{String}
    target_id::String
    preserves::Vector{String}
    forgets::Vector{String}
    conductor_permutation::Matrix{Float64}
    recovery_map::Dict{String,String}
    constraint_map::Dict{String,String}
    physical_classification::String
    provenance::Dict{String,Any}
end

struct TransformationResult
    target::SeriesElement
    certificate::TransformationCertificate
end

struct TransformationRejection
    rule_id::String
    source_ids::Vector{String}
    junction_id::String
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

function permutation_matrix(source_labels, target_labels)
    Set(source_labels) == Set(target_labels) || return nothing
    n = length(source_labels)
    P = zeros(Float64, n, n)
    for (row, label) in enumerate(target_labels)
        col = findfirst(==(label), source_labels)
        col === nothing && return nothing
        P[row, col] = 1.0
    end
    P
end

function junction_failures(first, second, junction)
    failures = String[]
    first.bus_to == junction.id || push!(failures, "first_element_does_not_end_at_junction")
    second.bus_from == junction.id || push!(failures, "second_element_does_not_start_at_junction")
    first.id != second.id || push!(failures, "source_element_identity_not_distinct")
    length(first.terminals_to) == length(second.terminals_from) ||
        push!(failures, "junction_terminal_arity_mismatch")
    Set(first.terminals_to) == Set(second.terminals_from) ||
        push!(failures, "junction_conductor_sets_do_not_match")
    isempty(junction.injections) || push!(failures, "junction_has_injection")
    isempty(junction.shunts) || push!(failures, "junction_has_shunt_or_grounding")
    isempty(junction.measurements) || push!(failures, "junction_has_measurement")
    isempty(junction.controls) || push!(failures, "junction_has_control")
    isempty(junction.protection_boundaries) || push!(failures, "junction_is_protection_boundary")
    isempty(junction.external_couplings) || push!(failures, "element_has_external_mutual_coupling")
    failures
end

function aligned_limit(first_limit, second_limit, P)
    first_limit === nothing && second_limit === nothing && return nothing
    n = size(P, 1)
    first_aligned = first_limit === nothing ? fill(Inf, n) : first_limit
    second_aligned = second_limit === nothing ? fill(Inf, n) : transpose(P) * second_limit
    min.(first_aligned, second_aligned)
end

"""
Eliminate a zero-injection degree-two junction.

The result is an exact terminal-behaviour composite, not automatically one
longer physical line. The returned certificate retains the source identities,
member constraints, conductor permutation, and recovery equations.
"""
function eliminate_degree_two(
    first::SeriesElement,
    second::SeriesElement,
    junction::JunctionContext;
    certificate_id="TR-SER-001",
)
    failures = junction_failures(first, second, junction)
    if !isempty(failures)
        return TransformationRejection(
            "degree_two_series_elimination",
            [first.id, second.id],
            junction.id,
            failures,
            Dict(
                "injections" => junction.injections,
                "shunts" => junction.shunts,
                "measurements" => junction.measurements,
                "controls" => junction.controls,
                "protection_boundaries" => junction.protection_boundaries,
                "external_couplings" => junction.external_couplings,
            ),
        )
    end

    # P maps currents and voltages from the first element's junction order to
    # the second element's junction order: x₂ = P*x₁.
    P = permutation_matrix(first.terminals_to, second.terminals_from)
    P === nothing && error("internal error: conductor guard passed without a permutation")
    impedance = first.impedance + transpose(P) * second.impedance * P
    target_to = [second.terminals_to[findfirst(==(label), second.terminals_from)]
                 for label in first.terminals_to]
    limit = aligned_limit(first.current_limit, second.current_limit, P)
    target_id = "generated_series__$(first.id)__$(second.id)"
    target = SeriesElement(
        target_id,
        first.bus_from,
        second.bus_to,
        first.terminals_from,
        target_to,
        impedance;
        current_limit=limit,
        construction_code=nothing,
    )

    same_code = first.construction_code !== nothing &&
                first.construction_code == second.construction_code
    physical_classification = same_code ?
        "homogeneous_line_candidate_additional_guards_required" :
        "exact_behavioral_composite_not_a_homogeneous_physical_line"

    certificate = TransformationCertificate(
        String(certificate_id),
        "exact_behavioral_reduction",
        [first.id, second.id, junction.id],
        target_id,
        [
            "external_terminal_voltage_current_relation",
            "ordered_conductor_identity",
            "source_current_limits_via_intersection",
            "source_to_target_provenance",
        ],
        ["independent_visibility_of_the_internal_junction"],
        P,
        Dict(
            "source_current_$(first.id)" => "i_$(first.id) = i_equivalent",
            "source_current_$(second.id)" => "i_$(second.id) = P * i_equivalent",
            "junction_voltage" => "u_$(junction.id) = u_$(first.bus_from) - Z_$(first.id) * i_equivalent",
        ),
        Dict(
            "current_feasible_set" => "C_equivalent = C_$(first.id) intersect P' * C_$(second.id)",
            "componentwise_current_limit" => "i_max_equivalent = min(i_max_$(first.id), P' * i_max_$(second.id))",
        ),
        physical_classification,
        Dict(
            "generated_object" => target_id,
            "source_elements" => [first.id, second.id],
            "eliminated_junction" => junction.id,
        ),
    )
    TransformationResult(target, certificate)
end

function complex_matrix_rows(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

function certificate_dict(result::TransformationResult)
    target = result.target
    certificate = result.certificate
    Dict{String,Any}(
        "schema_version" => "1.0.0",
        "certificate_id" => certificate.certificate_id,
        "rule_id" => "degree_two_series_elimination",
        "classification" => certificate.classification,
        "source" => Dict(
            "model_category" => "ordered_multiconductor_series_chain",
            "object_ids" => certificate.source_ids,
        ),
        "target" => Dict(
            "model_category" => "ordered_multiconductor_series_element",
            "object_ids" => [target.id],
            "detail" => Dict(
                "bus_from" => target.bus_from,
                "bus_to" => target.bus_to,
                "terminal_map_from" => target.terminals_from,
                "terminal_map_to" => target.terminals_to,
                "impedance_ohm" => complex_matrix_rows(target.impedance),
                "current_limit_A" => target.current_limit,
                "physical_classification" => certificate.physical_classification,
            ),
        ),
        "preconditions" => [
            "the first element ends at the eliminated junction",
            "the second element starts at the eliminated junction",
            "junction conductor sets agree up to permutation",
            "the junction has no injection, shunt, grounding, measurement, control, or protection boundary",
            "neither source element has an external mutual coupling",
        ],
        "preserves" => certificate.preserves,
        "forgets" => certificate.forgets,
        "recovery_map" => certificate.recovery_map,
        "constraint_map" => certificate.constraint_map,
        "provenance" => certificate.provenance,
        "evidence" => Dict(
            "conductor_permutation" => [collect(row) for row in eachrow(certificate.conductor_permutation)],
            "impedance_derivation" => "Z_equivalent = Z_first + P' * Z_second * P",
            "physical_classification" => certificate.physical_classification,
        ),
    )
end

end

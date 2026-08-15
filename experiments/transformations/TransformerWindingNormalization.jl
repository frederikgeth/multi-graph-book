module TransformerWindingNormalization

using ..CoordinateActions: CoordinateActionRejection,
                           coordinate_action,
                           pushforward_operator

export WindingFactor,
       WindingNormalizationRejection,
       WindingNormalizationResult,
       delta_incidence,
       normalize_winding_terminals,
       wye_incidence

"A winding port whose coil voltages satisfy `v_coil = A_terminal*v_terminal`."
struct WindingFactor
    id::String
    transformer_id::String
    winding_position::Int
    bus::String
    terminals::Vector{String}
    connection::String
    coil_labels::Vector{String}
    terminal_to_coil::Matrix{Float64}
    coil_current_limit::Vector{Float64}
    terminal_current_limit::Union{Nothing,Vector{Float64}}
    attributes::Dict{String,Any}

    function WindingFactor(
        id,
        transformer_id,
        winding_position,
        bus,
        terminals,
        connection,
        terminal_to_coil,
        coil_current_limit;
        coil_labels=["coil_$row" for row in axes(terminal_to_coil, 1)],
        terminal_current_limit=nothing,
        attributes=Dict{String,Any}(),
    )
        n_terminal = length(terminals)
        size(terminal_to_coil, 2) == n_terminal ||
            throw(ArgumentError("connection matrix must have one column per terminal"))
        size(terminal_to_coil, 1) == length(coil_current_limit) ||
            throw(ArgumentError("coil limits must match connection-matrix rows"))
        size(terminal_to_coil, 1) == length(coil_labels) ||
            throw(ArgumentError("coil labels must match connection-matrix rows"))
        length(unique(String.(coil_labels))) == length(coil_labels) ||
            throw(ArgumentError("coil labels must be unique"))
        terminal_limit = terminal_current_limit === nothing ? nothing : Float64.(terminal_current_limit)
        terminal_limit === nothing || length(terminal_limit) == n_terminal ||
            throw(ArgumentError("terminal current limits must match terminal coordinates"))
        new(
            String(id),
            String(transformer_id),
            Int(winding_position),
            String(bus),
            String.(terminals),
            String(connection),
            String.(coil_labels),
            Float64.(terminal_to_coil),
            Float64.(coil_current_limit),
            terminal_limit,
            Dict{String,Any}(String(key) => value for (key, value) in attributes),
        )
    end
end

struct WindingNormalizationResult
    target::WindingFactor
    certificate::Dict{String,Any}
end

struct WindingNormalizationRejection
    rule_id::String
    source_id::String
    requested_order::Vector{String}
    failed_guards::Vector{String}
end

"Phase-to-neutral coil incidence for an ordered wye terminal list."
function wye_incidence(terminals; neutral="n")
    labels = String.(terminals)
    neutral_position = findfirst(==(String(neutral)), labels)
    neutral_position === nothing && throw(ArgumentError("wye winding requires an explicit neutral"))
    phases = [position for position in eachindex(labels) if position != neutral_position]
    A = zeros(Float64, length(phases), length(labels))
    for (row, phase_position) in enumerate(phases)
        A[row, phase_position] = 1.0
        A[row, neutral_position] = -1.0
    end
    A
end

"Cyclic delta coil incidence, retaining coil-row identity under terminal changes."
function delta_incidence(terminals; roll=-1)
    labels = String.(terminals)
    length(labels) >= 2 || throw(ArgumentError("delta winding requires at least two terminals"))
    roll in (-1, 1) || throw(ArgumentError("delta roll must be -1 or 1"))
    A = zeros(Float64, length(labels), length(labels))
    for row in eachindex(labels)
        other = mod1(row + roll, length(labels))
        A[row, row] = 1.0
        A[row, other] = -1.0
    end
    A
end

function matrix_rows(matrix)
    [collect(row) for row in eachrow(matrix)]
end

"""Normalize a winding's terminal coordinates without changing its coil coordinates."""
function normalize_winding_terminals(
    source::WindingFactor,
    requested_order;
    certificate_id="TR-XFMR-001",
)
    order = String.(requested_order)
    action = coordinate_action(source.terminals, order)
    action isa CoordinateActionRejection && return WindingNormalizationRejection(
        "transformer_winding_terminal_normalization",
        source.id,
        order,
        action.failed_guards,
    )

    transformed_connection = pushforward_operator(action, source.terminal_to_coil)
    target_id = "normalized__$(replace(source.id, '/' => '_'))__$(join(order, "_"))"
    target = WindingFactor(
        target_id,
        source.transformer_id,
        source.winding_position,
        source.bus,
        order,
        source.connection,
        transformed_connection,
        source.coil_current_limit;
        coil_labels=source.coil_labels,
        terminal_current_limit=source.terminal_current_limit === nothing ?
            nothing : action.permutation * source.terminal_current_limit,
        attributes=source.attributes,
    )

    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "transformer_winding_terminal_normalization",
        "classification" => "exact_normalization",
        "source" => Dict(
            "model_category" => "typed_multiwinding_transformer_winding_factor",
            "object_ids" => [source.id],
            "detail" => Dict(
                "transformer_id" => source.transformer_id,
                "winding_position" => source.winding_position,
                "connection" => source.connection,
                "coil_labels" => source.coil_labels,
                "coil_current_limit_A" => source.coil_current_limit,
                "terminal_current_limit_A" => source.terminal_current_limit,
            ),
        ),
        "target" => Dict(
            "model_category" => "typed_multiwinding_transformer_winding_factor",
            "object_ids" => [target.id],
            "detail" => Dict(
                "terminal_order" => target.terminals,
                "terminal_to_coil_incidence" => matrix_rows(target.terminal_to_coil),
                "coil_labels" => target.coil_labels,
                "coil_current_limit_A" => target.coil_current_limit,
                "terminal_current_limit_A" => target.terminal_current_limit,
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["source-order winding terminal voltages", "stable coil voltages"],
                "target" => ["target-order winding terminal voltages", "stable coil voltages"],
                "relation" => "terminal voltages map by P while coil coordinates remain fixed",
            ),
            "constraints" => Dict(
                "source" => source.terminal_current_limit === nothing ?
                    ["coil current limits"] : ["coil current limits", "terminal current limits"],
                "target" => target.terminal_current_limit === nothing ?
                    ["coil current limits"] : ["coil current limits", "terminal current limits"],
                "relation" => "coil-indexed limits are unchanged; terminal-current limits, when declared, follow the dual permutation",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "no tap, switching, or investment decision is changed",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "no winding-local objective term is declared",
            ),
            "units" => Dict(
                "source" => ["V", "A"], "target" => ["V", "A"],
                "relation" => "terminal permutation leaves voltage and current units unchanged",
            ),
            "boundary_quantities" => Dict(
                "source" => ["winding terminal voltages", "coil voltages"],
                "target" => ["winding terminal voltages", "coil voltages"],
                "relation" => "A_target * U_target = A_source * U_source",
            ),
        ),
        "preconditions" => [
            "source and target terminal labels are unique",
            "source and target terminal sets are equal",
            "the complete terminal-to-coil relation is transformed",
            "coil coordinates and coil limits retain their identities",
        ],
        "preserves" => [
            "winding_terminal_to_coil_voltage_relation",
            "winding_connection_semantics",
            "coil_current_limits",
            "terminal_current_dual_map",
            "transformer_and_winding_identity",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "source_terminal_voltage" => "u_source = P' * u_target",
            "source_connection" => "A_source = A_target * P",
            "source_terminal_current" => "i_source = P' * i_target",
            "source_terminal_current_limit" => "i_max_source = P' * i_max_target when terminal limits are declared",
        ),
        "constraint_map" => Dict(
            "target_terminal_voltage" => "u_target = P * u_source",
            "target_connection" => "A_target = A_source * P'",
            "coil_limits" => "coil coordinates are unchanged, so their limits are unchanged",
            "terminal_current" => "i_target = P * i_source",
            "terminal_current_limits" => "i_max_target = P * i_max_source when terminal limits are declared",
        ),
        "provenance" => Dict(
            "source_transformer" => source.transformer_id,
            "source_winding" => source.winding_position,
            "generated_object" => target.id,
        ),
        "evidence" => Dict{String,Any}(
            "permutation_matrix" => matrix_rows(action.permutation),
            "source_terminal_order" => source.terminals,
            "target_terminal_order" => target.terminals,
            "source_terminal_to_coil_incidence" => matrix_rows(source.terminal_to_coil),
            "target_terminal_to_coil_incidence" => matrix_rows(target.terminal_to_coil),
        ),
    )
    WindingNormalizationResult(target, certificate)
end

end

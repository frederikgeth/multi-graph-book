module TransformerFactorCompletion

using LinearAlgebra

using ..CoordinateActions: CoordinateActionRejection, coordinate_action
using ..MultiwindingTerminalAssembly: MultiwindingTerminalAssemblyResult

export ExcitationShunt,
       InternalGrounding,
       TransformerCompletionData,
       TransformerCompletionRejection,
       TransformerCompletionResult,
       WindingTransfer,
       assemble_complete_transformer,
       completion_data_from_dict,
       completion_data_to_dict

"A declared voltage transfer from connected-coil to leakage coordinates."
struct WindingTransfer
    id::String
    transformer_id::String
    winding_id::String
    winding_position::Int
    terminal_labels::Vector{String}
    coil_labels::Vector{String}
    control_mode::String
    coefficient::Vector{ComplexF64}
    decision_id::Union{Nothing,String}
    attributes::Dict{String,Any}
end

function WindingTransfer(
    id,
    transformer_id,
    winding_id,
    winding_position,
    coil_labels,
    control_mode,
    coefficient;
    terminal_labels=String[],
    decision_id=nothing,
    attributes=Dict{String,Any}(),
)
    WindingTransfer(
        String(id),
        String(transformer_id),
        String(winding_id),
        Int(winding_position),
        String.(terminal_labels),
        String.(coil_labels),
        String(control_mode),
        ComplexF64.(coefficient),
        decision_id === nothing ? nothing : String(decision_id),
        Dict{String,Any}(String(key) => value for (key, value) in attributes),
    )
end

"A linear no-load/core-loss shunt placed across one winding's labelled coils."
struct ExcitationShunt
    id::String
    transformer_id::String
    winding_position::Int
    coil_labels::Vector{String}
    admittance::Matrix{ComplexF64}
    attributes::Dict{String,Any}
end

function ExcitationShunt(
    id,
    transformer_id,
    winding_position,
    coil_labels,
    admittance;
    attributes=Dict{String,Any}(),
)
    ExcitationShunt(
        String(id),
        String(transformer_id),
        Int(winding_position),
        String.(coil_labels),
        ComplexF64.(admittance),
        Dict{String,Any}(String(key) => value for (key, value) in attributes),
    )
end

"A transformer-internal terminal-to-earth admittance, distinct from bus grounding."
struct InternalGrounding
    id::String
    transformer_id::String
    winding_position::Int
    terminal::String
    admittance::ComplexF64
    scope::String
    attributes::Dict{String,Any}
end

function InternalGrounding(
    id,
    transformer_id,
    winding_position,
    terminal,
    admittance;
    scope="transformer_internal",
    attributes=Dict{String,Any}(),
)
    InternalGrounding(
        String(id),
        String(transformer_id),
        Int(winding_position),
        String(terminal),
        ComplexF64(admittance),
        String(scope),
        Dict{String,Any}(String(key) => value for (key, value) in attributes),
    )
end

"Compact, typed completion data layered on a certified terminal leakage factor."
struct TransformerCompletionData
    id::String
    transformer_id::String
    status::String
    voltage_transfer_convention::String
    winding_transfers::Vector{WindingTransfer}
    excitation_shunt::Union{Nothing,ExcitationShunt}
    internal_groundings::Vector{InternalGrounding}
    metadata::Dict{String,Any}
end

function TransformerCompletionData(
    id,
    transformer_id,
    status,
    voltage_transfer_convention,
    winding_transfers;
    excitation_shunt=nothing,
    internal_groundings=InternalGrounding[],
    metadata=Dict{String,Any}(),
)
    TransformerCompletionData(
        String(id),
        String(transformer_id),
        String(status),
        String(voltage_transfer_convention),
        WindingTransfer[transfer for transfer in winding_transfers],
        excitation_shunt,
        InternalGrounding[grounding for grounding in internal_groundings],
        Dict{String,Any}(String(key) => value for (key, value) in metadata),
    )
end

struct TransformerCompletionResult
    contract_id::String
    transformer_id::String
    qualified_terminal_labels::Vector{String}
    transfer_permutations::Vector{Matrix{Float64}}
    voltage_transfer::Matrix{ComplexF64}
    leakage_voltage_map::Matrix{ComplexF64}
    leakage_current_map::Matrix{ComplexF64}
    winding_leakage_current_map::Matrix{ComplexF64}
    excitation_voltage_map::Matrix{ComplexF64}
    excitation_current_map::Matrix{ComplexF64}
    ground_current_map::Matrix{ComplexF64}
    terminal_admittance::Matrix{ComplexF64}
    leakage_current_limit::Vector{Float64}
    certificate::Dict{String,Any}
end

struct TransformerCompletionRejection
    rule_id::String
    source_ids::Vector{String}
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

function block_diagonal(blocks::AbstractVector{<:AbstractMatrix})
    isempty(blocks) && return zeros(ComplexF64, 0, 0)
    rows = sum(size(block, 1) for block in blocks)
    columns = sum(size(block, 2) for block in blocks)
    result = zeros(promote_type(map(eltype, blocks)...), rows, columns)
    row_start = 1
    column_start = 1
    for block in blocks
        row_range = row_start:row_start + size(block, 1) - 1
        column_range = column_start:column_start + size(block, 2) - 1
        result[row_range, column_range] .= block
        row_start += size(block, 1)
        column_start += size(block, 2)
    end
    result
end

complex_value(value) = Dict("real" => real(value), "imag" => imag(value))
complex_rows(matrix) = [[complex_value(value) for value in row] for row in eachrow(matrix)]
matrix_rows(matrix) = [collect(row) for row in eachrow(matrix)]

function complex_from_dict(value)
    value isa Number && return ComplexF64(value)
    value isa AbstractDict || throw(ArgumentError("complex value must be a number or object"))
    ComplexF64(Float64(value["real"]), Float64(value["imag"]))
end

function complex_matrix_from_dict(rows)
    isempty(rows) && return zeros(ComplexF64, 0, 0)
    width = length(first(rows))
    all(length(row) == width for row in rows) ||
        throw(ArgumentError("complex matrix rows have inconsistent lengths"))
    reduce(vcat, [permutedims(complex_from_dict.(row)) for row in rows])
end

"Parse the versioned JSON-facing contract without depending on a JSON package."
function completion_data_from_dict(raw::AbstractDict)
    get(raw, "schema_version", nothing) == "0.1.0" ||
        throw(ArgumentError("unsupported transformer completion schema_version"))
    transfers = WindingTransfer[]
    for item in raw["winding_transfers"]
        push!(transfers, WindingTransfer(
            item["id"], raw["transformer_id"], item["winding_id"],
            item["winding_position"], item["coil_order"], item["control_mode"],
            complex_from_dict.(item["coefficient"]);
            terminal_labels=item["terminal_order"],
            decision_id=get(item, "decision_id", nothing),
            attributes=get(item, "attributes", Dict{String,Any}()),
        ))
    end
    shunt = if get(raw, "excitation_shunt", nothing) === nothing
        nothing
    else
        item = raw["excitation_shunt"]
        ExcitationShunt(
            item["id"], raw["transformer_id"], item["winding_position"],
            item["coil_order"], complex_matrix_from_dict(item["admittance_S"]);
            attributes=get(item, "attributes", Dict{String,Any}()),
        )
    end
    groundings = InternalGrounding[
        InternalGrounding(
            item["id"], raw["transformer_id"], item["winding_position"],
            item["terminal"], complex_from_dict(item["admittance_S"]);
            scope=item["scope"],
            attributes=get(item, "attributes", Dict{String,Any}()),
        ) for item in get(raw, "internal_groundings", Any[])
    ]
    TransformerCompletionData(
        raw["contract_id"], raw["transformer_id"], raw["status"],
        raw["voltage_transfer_convention"], transfers;
        excitation_shunt=shunt,
        internal_groundings=groundings,
        metadata=get(raw, "metadata", Dict{String,Any}()),
    )
end

"Return a JSON-compatible representation with stable semantic field names."
function completion_data_to_dict(data::TransformerCompletionData)
    transfers = [Dict{String,Any}(
        "id" => transfer.id,
        "winding_id" => transfer.winding_id,
        "winding_position" => transfer.winding_position,
        "terminal_order" => transfer.terminal_labels,
        "coil_order" => transfer.coil_labels,
        "control_mode" => transfer.control_mode,
        "coefficient" => complex_value.(transfer.coefficient),
        "attributes" => transfer.attributes,
    ) for transfer in data.winding_transfers]
    for (item, transfer) in zip(transfers, data.winding_transfers)
        transfer.decision_id === nothing || (item["decision_id"] = transfer.decision_id)
    end
    shunt = data.excitation_shunt === nothing ? nothing : Dict{String,Any}(
        "id" => data.excitation_shunt.id,
        "winding_position" => data.excitation_shunt.winding_position,
        "coil_order" => data.excitation_shunt.coil_labels,
        "admittance_S" => complex_rows(data.excitation_shunt.admittance),
        "attributes" => data.excitation_shunt.attributes,
    )
    groundings = [Dict{String,Any}(
        "id" => grounding.id,
        "winding_position" => grounding.winding_position,
        "terminal" => grounding.terminal,
        "admittance_S" => complex_value(grounding.admittance),
        "scope" => grounding.scope,
        "attributes" => grounding.attributes,
    ) for grounding in data.internal_groundings]
    Dict{String,Any}(
        "schema_version" => "0.1.0",
        "contract_id" => data.id,
        "transformer_id" => data.transformer_id,
        "status" => data.status,
        "voltage_transfer_convention" => data.voltage_transfer_convention,
        "winding_transfers" => transfers,
        "excitation_shunt" => shunt,
        "internal_groundings" => groundings,
        "metadata" => data.metadata,
    )
end

function rejection(leakage, data, failed_guards; evidence=Dict{String,Any}())
    TransformerCompletionRejection(
        "fixed_linear_transformer_factor_completion",
        unique(vcat(
            String.(leakage.certificate["target"]["object_ids"]),
            [data.id],
        )),
        unique(String.(failed_guards)),
        Dict{String,Any}(evidence),
    )
end

function passive(matrix; tolerance)
    isempty(matrix) && return true
    hermitian_part = Hermitian((matrix + matrix') / 2)
    scale = max(1.0, opnorm(matrix, 2))
    minimum(eigvals(hermitian_part)) >= -tolerance * scale
end

"""
Compile a fixed linear transformer factor around a certified leakage assembly.

For aligned connected-coil voltages `v = A*u`, the declared transfer is
`v_leak = T*v`. Power preservation fixes the winding-side leakage current as
`i_winding = T'*i_leak`; therefore the series block is `(T*A)'*Ycoil*(T*A)`.
Excitation and transformer-internal grounding currents remain separate maps.
Adjustable transfers are deliberately rejected by this static compiler.
"""
function assemble_complete_transformer(
    leakage::MultiwindingTerminalAssemblyResult,
    data::TransformerCompletionData;
    certificate_id="TR-XFMR-004",
    tolerance=1.0e-10,
)
    transfers = sort!(copy(data.winding_transfers); by=transfer -> transfer.winding_position)
    n_winding = length(leakage.winding_ids)
    n_coil = length(leakage.common_coil_labels)
    failed = String[]
    data.transformer_id == leakage.transformer_id ||
        push!(failed, "completion_and_leakage_transformer_ids_differ")
    data.voltage_transfer_convention ==
        "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc" ||
        push!(failed, "unsupported_voltage_transfer_convention")
    length(transfers) == n_winding ||
        push!(failed, "winding_transfer_count_does_not_match_leakage_factor")
    isempty(failed) || return rejection(leakage, data, failed)

    positions = [transfer.winding_position for transfer in transfers]
    positions == collect(1:n_winding) ||
        push!(failed, "winding_transfer_positions_must_cover_1_to_n")
    [transfer.winding_id for transfer in transfers] == leakage.winding_ids ||
        push!(failed, "winding_transfer_ids_do_not_match_leakage_factor")
    all(transfer.transformer_id == data.transformer_id for transfer in transfers) ||
        push!(failed, "winding_transfers_have_different_transformer_ids")
    expected_terminal_orders = [
        [split(leakage.qualified_terminal_labels[index], "/terminal/"; limit=2)[2]
         for index in leakage.winding_terminal_ranges[position]]
        for position in 1:n_winding
    ]
    all(transfer.terminal_labels == expected_terminal_orders[index]
        for (index, transfer) in enumerate(transfers)) ||
        push!(failed, "winding_transfer_terminal_orders_do_not_match_leakage_factor")
    all(length(unique(transfer.coil_labels)) == length(transfer.coil_labels) == n_coil
        for transfer in transfers) ||
        push!(failed, "winding_transfer_coil_labels_are_not_unique")
    all(Set(transfer.coil_labels) == Set(leakage.common_coil_labels) for transfer in transfers) ||
        push!(failed, "winding_transfer_coil_coordinate_sets_differ")
    all(length(transfer.coefficient) == n_coil for transfer in transfers) ||
        push!(failed, "winding_transfer_coefficient_arities_differ")
    all(all(isfinite, transfer.coefficient) for transfer in transfers) ||
        push!(failed, "winding_transfer_coefficients_must_be_finite")
    all(all(abs.(transfer.coefficient) .> tolerance) for transfer in transfers) ||
        push!(failed, "winding_transfer_coefficients_must_be_nonzero")
    all(transfer.control_mode in ("fixed", "continuous", "discrete") for transfer in transfers) ||
        push!(failed, "unsupported_winding_transfer_control_mode")
    adjustable = [transfer for transfer in transfers if transfer.control_mode != "fixed"]
    all(transfer.decision_id !== nothing for transfer in adjustable) ||
        push!(failed, "adjustable_winding_transfer_requires_decision_identity")
    isempty(adjustable) ||
        push!(failed, "adjustable_winding_transfer_requires_factorized_decision_model")

    shunt = data.excitation_shunt
    if shunt !== nothing
        shunt.transformer_id == data.transformer_id ||
            push!(failed, "excitation_shunt_has_different_transformer_id")
        1 <= shunt.winding_position <= n_winding ||
            push!(failed, "excitation_shunt_winding_position_is_out_of_range")
        length(unique(shunt.coil_labels)) == length(shunt.coil_labels) == n_coil ||
            push!(failed, "excitation_shunt_coil_labels_are_not_unique")
        Set(shunt.coil_labels) == Set(leakage.common_coil_labels) ||
            push!(failed, "excitation_shunt_coil_coordinate_set_differs")
        size(shunt.admittance) == (n_coil, n_coil) ||
            push!(failed, "excitation_shunt_admittance_has_wrong_dimension")
        all(isfinite, shunt.admittance) ||
            push!(failed, "excitation_shunt_admittance_must_be_finite")
        isapprox(shunt.admittance, transpose(shunt.admittance); atol=tolerance, rtol=tolerance) ||
            push!(failed, "excitation_shunt_admittance_must_be_reciprocal")
        passive(shunt.admittance; tolerance=tolerance) ||
            push!(failed, "excitation_shunt_admittance_must_be_passive")
    end

    terminal_targets = Tuple{Int,String}[]
    for grounding in data.internal_groundings
        grounding.transformer_id == data.transformer_id ||
            push!(failed, "internal_grounding_has_different_transformer_id")
        1 <= grounding.winding_position <= n_winding ||
            push!(failed, "internal_grounding_winding_position_is_out_of_range")
        grounding.scope == "transformer_internal" ||
            push!(failed, "external_bus_grounding_cannot_be_absorbed")
        isfinite(grounding.admittance) ||
            push!(failed, "internal_grounding_admittance_must_be_finite")
        real(grounding.admittance) >= -tolerance ||
            push!(failed, "internal_grounding_admittance_must_be_passive")
        if 1 <= grounding.winding_position <= n_winding
            winding_range = leakage.winding_terminal_ranges[grounding.winding_position]
            suffix = "/terminal/$(grounding.terminal)"
            any(endswith(leakage.qualified_terminal_labels[index], suffix) for index in winding_range) ||
                push!(failed, "internal_grounding_terminal_does_not_exist")
        end
        push!(terminal_targets, (grounding.winding_position, grounding.terminal))
    end
    length(unique(terminal_targets)) == length(terminal_targets) ||
        push!(failed, "internal_grounding_targets_are_duplicated")

    isempty(failed) || return rejection(leakage, data, failed; evidence=Dict(
        "winding_transfer_modes" => Dict(transfer.winding_id => transfer.control_mode for transfer in transfers),
        "adjustable_decision_ids" => [transfer.decision_id for transfer in adjustable],
    ))

    actions = [coordinate_action(transfer.coil_labels, leakage.common_coil_labels) for transfer in transfers]
    any(action -> action isa CoordinateActionRejection, actions) &&
        return rejection(leakage, data, ["winding_transfer_coordinate_alignment_failed"])
    permutations = [action.permutation for action in actions]
    aligned_transfer_blocks = [
        permutations[index] * Diagonal(transfer.coefficient) * permutations[index]'
        for (index, transfer) in enumerate(transfers)
    ]
    transfer_matrix = block_diagonal(aligned_transfer_blocks)
    connection = ComplexF64.(leakage.terminal_to_coil)
    leakage_voltage_map = transfer_matrix * connection
    leakage_current_map = leakage.coil_admittance * leakage_voltage_map
    winding_leakage_current_map = transfer_matrix' * leakage_current_map
    terminal_admittance = leakage_voltage_map' * leakage.coil_admittance * leakage_voltage_map

    n_terminal = length(leakage.qualified_terminal_labels)
    excitation_voltage_map = zeros(ComplexF64, n_coil, n_terminal)
    excitation_current_map = zeros(ComplexF64, n_coil, n_terminal)
    if shunt !== nothing
        action = coordinate_action(shunt.coil_labels, leakage.common_coil_labels)
        permutation = action.permutation
        aligned_admittance = permutation * shunt.admittance * permutation'
        coil_range = leakage.winding_coil_ranges[shunt.winding_position]
        terminal_range = leakage.winding_terminal_ranges[shunt.winding_position]
        excitation_voltage_map[:, terminal_range] .= connection[coil_range, terminal_range]
        excitation_current_map .= aligned_admittance * excitation_voltage_map
        terminal_admittance .+= excitation_voltage_map' * excitation_current_map
    end

    ground_current_map = zeros(ComplexF64, n_terminal, n_terminal)
    for grounding in data.internal_groundings
        winding_range = leakage.winding_terminal_ranges[grounding.winding_position]
        suffix = "/terminal/$(grounding.terminal)"
        position = only(index for index in winding_range if
            endswith(leakage.qualified_terminal_labels[index], suffix))
        ground_current_map[position, position] += grounding.admittance
    end
    terminal_admittance .+= ground_current_map

    generated_ids = [
        "generated_complete_terminal_factor__$(data.transformer_id)",
        "generated_winding_current_recovery__$(data.transformer_id)",
        "generated_excitation_current_recovery__$(data.transformer_id)",
        "generated_internal_ground_current_recovery__$(data.transformer_id)",
    ]
    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "fixed_linear_transformer_factor_completion",
        "classification" => "exact_compilation",
        "source" => Dict(
            "model_category" => "terminal_leakage_factor_and_typed_transformer_completion_contract",
            "object_ids" => unique(vcat(
                String.(leakage.certificate["target"]["object_ids"]),
                [data.id],
            )),
            "detail" => Dict(
                "transformer_id" => data.transformer_id,
                "completion_status" => data.status,
                "source_leakage_certificate" => leakage.certificate["certificate_id"],
                "voltage_transfer_convention" => data.voltage_transfer_convention,
            ),
        ),
        "target" => Dict(
            "model_category" => "fixed_linear_complete_transformer_terminal_factor_with_recovery_maps",
            "object_ids" => generated_ids,
            "detail" => Dict(
                "terminal_dimension" => n_terminal,
                "leakage_coil_dimension" => size(leakage_voltage_map, 1),
                "excitation_coil_dimension" => shunt === nothing ? 0 : n_coil,
                "internal_grounding_count" => length(data.internal_groundings),
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["terminal voltages", "leakage coil voltages and currents", "excitation and internal-ground currents"],
                "target" => ["stacked terminal voltages and currents", "recoverable component currents"],
                "relation" => "v_leak=T*A*u; i_leak=Ycoil*v_leak; i_winding=T^H*i_leak; excitation and internal-ground currents are retained separately",
            ),
            "constraints" => Dict(
                "source" => ["leakage-path coil-current limits", "declared fixed transfer settings"],
                "target" => ["limits on the recovered winding leakage-current map", "unchanged fixed settings"],
                "relation" => "source leakage-path currents recover as T^H*Ycoil*T*A*u; excitation and grounding maps remain available for separately declared total-current or loss limits",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "all voltage transfers are fixed; adjustable controls are rejected rather than frozen",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "no transformer-local objective term is introduced",
            ),
            "units" => Dict(
                "source" => ["V", "A", "S"], "target" => ["V", "A", "S"],
                "relation" => "dimensionless voltage transfers, SI admittances, and power-dual current maps preserve units",
            ),
            "boundary_quantities" => Dict(
                "source" => ["all winding terminal voltages and currents"],
                "target" => ["all winding terminal voltages and currents"],
                "relation" => "the complete terminal current is the sum of leakage, excitation, and transformer-internal grounding contributions",
            ),
        ),
        "preconditions" => [
            "the source terminal leakage factor is exact in labelled coil coordinates",
            "every winding has one nonzero finite fixed voltage-transfer coefficient per labelled coil",
            "the voltage-transfer convention maps connected-coil voltage to leakage voltage explicitly",
            "the excitation shunt, when present, is finite, reciprocal, passive, and explicitly placed on one winding",
            "grounding factors are passive transformer-internal terminal-to-earth branches",
            "external bus grounding is not absorbed into the transformer factor",
        ],
        "preserves" => [
            "all_declared_source_semantics",
            "fixed_linear_terminal_current_voltage_relation",
            "complex_power_balance_across_voltage_transfer",
            "winding_terminal_and_coil_identity",
            "leakage_excitation_and_internal_ground_current_recovery",
            "leakage_path_coil_current_limits",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "leakage_coil_voltage" => "v_leak = T*A*u",
            "leakage_coil_current" => "i_leak = Ycoil*T*A*u",
            "winding_leakage_current" => "i_winding = T^H*i_leak",
            "excitation_current" => "i_excitation = Y0*S*u",
            "internal_ground_current" => "i_ground = Yground*u",
            "terminal_current" => "i_terminal = (T*A)^H*i_leak + S^H*i_excitation + i_ground",
        ),
        "constraint_map" => Dict(
            "voltage_transfer" => "v_leak_xkc = coefficient_xkc*v_connected_coil_xkc",
            "leakage_current_limits" => "abs((T^H*Ycoil*T*A*u)[x,k,c]) <= limit[x,k,c]",
            "adjustable_controls" => "continuous or discrete transfers remain parameterized factors with their decision identities and are not accepted by this static compiler",
            "grounding_scope" => "only transformer-internal branches may be stamped into the transformer terminal factor",
        ),
        "provenance" => Dict(
            "source_transformer" => data.transformer_id,
            "source_completion_contract" => data.id,
            "source_terminal_leakage_certificate" => leakage.certificate["certificate_id"],
            "winding_transfers" => [transfer.id for transfer in transfers],
            "excitation_shunt" => shunt === nothing ? nothing : shunt.id,
            "internal_groundings" => [grounding.id for grounding in data.internal_groundings],
            "generated_objects" => generated_ids,
            "qualified_terminal_order" => leakage.qualified_terminal_labels,
        ),
        "evidence" => Dict(
            "winding_transfer_modes" => Dict(transfer.winding_id => transfer.control_mode for transfer in transfers),
            "aligned_voltage_transfer_matrix" => complex_rows(transfer_matrix),
            "terminal_admittance_matrix_S" => complex_rows(terminal_admittance),
            "leakage_current_limits_A" => leakage.coil_current_limit,
        ),
    )

    TransformerCompletionResult(
        data.id,
        data.transformer_id,
        leakage.qualified_terminal_labels,
        permutations,
        transfer_matrix,
        leakage_voltage_map,
        leakage_current_map,
        winding_leakage_current_map,
        excitation_voltage_map,
        excitation_current_map,
        ground_current_map,
        terminal_admittance,
        leakage.coil_current_limit,
        certificate,
    )
end

end

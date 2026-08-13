module MultiwindingTerminalAssembly

using LinearAlgebra

using ..CoordinateActions: CoordinateActionRejection, coordinate_action
using ..MultiwindingLeakageCompilation: MultiwindingLeakageResult
using ..TransformerWindingNormalization: WindingFactor

export MultiwindingTerminalAssemblyResult,
       MultiwindingTerminalAssemblyRejection,
       assemble_terminal_leakage

struct MultiwindingTerminalAssemblyResult
    transformer_id::String
    winding_ids::Vector{String}
    common_coil_labels::Vector{String}
    qualified_terminal_labels::Vector{String}
    coil_permutations::Vector{Matrix{Float64}}
    terminal_to_coil::Matrix{Float64}
    coil_admittance::Matrix{ComplexF64}
    terminal_admittance::Matrix{ComplexF64}
    coil_current_map::Matrix{ComplexF64}
    coil_current_limit::Vector{Float64}
    winding_terminal_ranges::Vector{UnitRange{Int}}
    winding_coil_ranges::Vector{UnitRange{Int}}
    certificate::Dict{String,Any}
end

struct MultiwindingTerminalAssemblyRejection
    rule_id::String
    source_ids::Vector{String}
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

function block_diagonal(blocks::AbstractVector{<:AbstractMatrix})
    isempty(blocks) && return zeros(Float64, 0, 0)
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

function consecutive_ranges(lengths)
    ranges = UnitRange{Int}[]
    start = 1
    for length in lengths
        push!(ranges, start:start + length - 1)
        start += length
    end
    ranges
end

complex_value(value) = Dict("real" => real(value), "imag" => imag(value))
complex_rows(matrix) = [[complex_value(value) for value in row] for row in eachrow(matrix)]
matrix_rows(matrix) = [collect(row) for row in eachrow(matrix)]

function rejection(windings, failed_guards; evidence=Dict{String,Any}())
    MultiwindingTerminalAssemblyRejection(
        "multiwinding_terminal_leakage_factor_assembly",
        [winding.id for winding in windings],
        unique(String.(failed_guards)),
        Dict{String,Any}(evidence),
    )
end

"""
Assemble winding connection factors and a leakage factor at external terminals.

All winding coil rows are first aligned to winding 1's stable coil labels. If
`A` is the resulting block connection matrix, then
`Y_terminal = A' * kron(Y_winding, I_coil) * A`. The lifted coil-current map
is retained so per-winding limits remain exact constraints.
"""
function assemble_terminal_leakage(
    leakage::MultiwindingLeakageResult,
    winding_factors::AbstractVector{<:WindingFactor};
    certificate_id="TR-XFMR-003",
    tolerance=1.0e-10,
)
    factors = sort!(collect(winding_factors); by=factor -> factor.winding_position)
    n = size(leakage.winding_admittance, 1)
    failed = String[]
    size(leakage.winding_admittance, 2) == n ||
        push!(failed, "winding_admittance_is_not_square")
    length(factors) == n || push!(failed, "winding_factor_count_does_not_match_leakage_factor")
    length(leakage.current_limit) == n ||
        push!(failed, "leakage_current_limit_count_does_not_match_windings")
    isempty(factors) && push!(failed, "at_least_one_winding_factor_is_required")
    isempty(failed) || return rejection(factors, failed)

    positions = [factor.winding_position for factor in factors]
    positions == collect(1:n) || push!(failed, "winding_positions_must_cover_1_to_n")
    transformer_ids = unique(factor.transformer_id for factor in factors)
    length(transformer_ids) == 1 || push!(failed, "winding_factors_have_different_transformer_ids")
    all(length(unique(factor.terminals)) == length(factor.terminals) for factor in factors) ||
        push!(failed, "winding_terminal_labels_are_not_unique")
    all(all(isfinite, factor.terminal_to_coil) for factor in factors) ||
        push!(failed, "connection_matrices_must_be_finite")
    all(isfinite, leakage.winding_admittance) ||
        push!(failed, "winding_admittance_must_be_finite")

    common_coils = factors[1].coil_labels
    all(Set(factor.coil_labels) == Set(common_coils) for factor in factors) ||
        push!(failed, "winding_coil_coordinate_sets_differ")
    all(length(factor.coil_labels) == length(common_coils) for factor in factors) ||
        push!(failed, "winding_coil_arities_differ")
    if length(leakage.current_limit) == n
        all(
            all(isapprox(limit, leakage.current_limit[factor.winding_position]; atol=tolerance, rtol=tolerance)
                for limit in factor.coil_current_limit)
            for factor in factors
        ) || push!(failed, "winding_and_leakage_current_limits_disagree")
    end
    isempty(failed) || return rejection(factors, failed; evidence=Dict(
        "winding_positions" => positions,
        "coil_coordinate_orders" => Dict(factor.id => factor.coil_labels for factor in factors),
    ))

    actions = [coordinate_action(factor.coil_labels, common_coils) for factor in factors]
    any(action -> action isa CoordinateActionRejection, actions) &&
        return rejection(factors, ["coil_coordinate_alignment_failed"])
    permutations = [action.permutation for action in actions]
    aligned_connections = [
        permutations[index] * factor.terminal_to_coil
        for (index, factor) in enumerate(factors)
    ]
    aligned_limits = [
        permutations[index] * factor.coil_current_limit
        for (index, factor) in enumerate(factors)
    ]

    connection = block_diagonal(aligned_connections)
    n_coil = length(common_coils)
    coil_admittance = kron(leakage.winding_admittance, Matrix{Float64}(I, n_coil, n_coil))
    terminal_admittance = connection' * coil_admittance * connection
    coil_current_map = coil_admittance * connection
    terminal_ranges = consecutive_ranges(length(factor.terminals) for factor in factors)
    coil_ranges = consecutive_ranges(fill(n_coil, n))
    qualified_terminals = [
        "$(factor.id)/terminal/$terminal"
        for factor in factors for terminal in factor.terminals
    ]
    winding_ids = [factor.id for factor in factors]
    transformer_id = only(transformer_ids)
    generated_ids = [
        "generated_terminal_leakage__$(transformer_id)",
        "generated_coil_current_recovery__$(transformer_id)",
    ]

    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "multiwinding_terminal_leakage_factor_assembly",
        "classification" => "exact_compilation",
        "source" => Dict(
            "model_category" => "multiwinding_leakage_and_typed_winding_connection_factors",
            "object_ids" => unique(vcat(
                String.(leakage.certificate["target"]["object_ids"]),
                winding_ids,
            )),
            "detail" => Dict(
                "transformer_id" => transformer_id,
                "winding_ids" => winding_ids,
                "connection_types" => [factor.connection for factor in factors],
                "source_leakage_certificate" => leakage.certificate["certificate_id"],
            ),
        ),
        "target" => Dict(
            "model_category" => "terminal_level_multiwinding_leakage_factor_with_lifted_coil_limits",
            "object_ids" => generated_ids,
            "detail" => Dict(
                "terminal_dimension" => length(qualified_terminals),
                "coil_dimension" => size(connection, 1),
                "common_coil_order" => common_coils,
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["winding terminal voltages", "winding coil voltages and currents"],
                "target" => ["stacked terminal voltages and currents", "recoverable aligned coil currents"],
                "relation" => "v_coil=A*v_terminal, i_coil=(Yw kron I)*v_coil, and i_terminal=A'*i_coil",
            ),
            "constraints" => Dict(
                "source" => ["per-coil current limits by winding identity"],
                "target" => ["lifted per-coil limits on the retained coil-current map"],
                "relation" => "each source coil current is recovered by its inverse row permutation before enforcing its unchanged limit",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "fixed connection and leakage factors introduce no tap, topology, or investment decision",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "no transformer-local objective term is declared",
            ),
            "units" => Dict(
                "source" => ["winding-own V", "winding-own A", "S"],
                "target" => ["winding-terminal V", "winding-terminal A", "S"],
                "relation" => "dimensionless connection incidence maps coil and terminal quantities without changing units",
            ),
            "boundary_quantities" => Dict(
                "source" => ["all winding terminal voltages and currents"],
                "target" => ["all winding terminal voltages and currents"],
                "relation" => "Yterminal=A'*(Yw kron I)*A preserves the terminal leakage relation",
            ),
        ),
        "preconditions" => [
            "winding positions cover the leakage-factor winding order exactly",
            "all winding factors belong to the same transformer",
            "all windings declare the same unique coil-coordinate set",
            "connection matrices and winding admittance are finite",
            "winding-factor coil limits agree with leakage-factor winding limits",
            "connection factors are fixed parameters",
            "the leakage factor is exact on winding-own coil coordinates",
            "the winding leakage admittance applies identically and independently to each common coil coordinate",
        ],
        "preserves" => [
            "all_declared_source_semantics",
            "external_terminal_leakage_relation",
            "wye_and_delta_connection_incidence",
            "winding_and_coil_identity",
            "per_coil_current_limits",
            "terminal_and_coil_coordinate_provenance",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "aligned_coil_voltage" => "v_coil = A*v_terminal",
            "aligned_coil_current" => "i_coil = (Yw kron I)*A*v_terminal",
            "source_coil_current" => "i_coil_source[k] = P_k'*i_coil_aligned[k]",
            "terminal_current" => "i_terminal = A'*i_coil = Yterminal*v_terminal",
        ),
        "constraint_map" => Dict(
            "coil_coordinate_alignment" => "A_k_aligned = P_k*A_k and limit_k_aligned = P_k*limit_k",
            "coil_admittance" => "Ycoil = Yw kron I_coil",
            "terminal_admittance" => "Yterminal = A'*Ycoil*A",
            "coil_current_limits" => "abs((Ycoil*A*v_terminal)[k,c]) <= limit[k,c]",
        ),
        "provenance" => Dict(
            "source_transformer" => transformer_id,
            "source_windings" => winding_ids,
            "source_leakage_certificate" => leakage.certificate["certificate_id"],
            "generated_objects" => generated_ids,
            "qualified_terminal_order" => qualified_terminals,
        ),
        "evidence" => Dict(
            "common_coil_order" => common_coils,
            "coil_permutations" => Dict(
                factor.id => matrix_rows(permutations[index])
                for (index, factor) in enumerate(factors)
            ),
            "terminal_to_coil_matrix" => matrix_rows(connection),
            "coil_current_limits_A" => vcat(aligned_limits...),
            "terminal_admittance_matrix_S" => complex_rows(terminal_admittance),
        ),
    )

    MultiwindingTerminalAssemblyResult(
        transformer_id,
        winding_ids,
        common_coils,
        qualified_terminals,
        permutations,
        connection,
        coil_admittance,
        terminal_admittance,
        coil_current_map,
        vcat(aligned_limits...),
        terminal_ranges,
        coil_ranges,
        certificate,
    )
end

end

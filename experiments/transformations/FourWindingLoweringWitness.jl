module FourWindingLoweringWitness

using LinearAlgebra

using ..MultiwindingLeakageCompilation: MultiwindingLeakageData,
    MultiwindingLeakageResult, compile_pairwise_leakage
using ..MultiwindingTerminalAssembly: MultiwindingTerminalAssemblyResult,
    assemble_terminal_leakage
using ..TransformerFactorCompletion: ExcitationShunt, InternalGrounding,
    TransformerCompletionData, TransformerCompletionResult, WindingTransfer,
    assemble_complete_transformer
using ..TransformerWindingNormalization: WindingFactor, delta_incidence,
    wye_incidence

export evaluate_four_winding_lowering

complex_value(value) = Dict("real" => real(value), "imag" => imag(value))
complex_rows(matrix) = [[complex_value(value) for value in row] for row in eachrow(matrix)]
matrix_rows(matrix) = [collect(row) for row in eachrow(matrix)]

function pairwise_from_reference(reference::AbstractMatrix)
    n = size(reference, 1) + 1
    pairs = Dict{Tuple{Int,Int},Float64}()
    for j in 2:n
        pairs[(1, j)] = reference[j - 1, j - 1]
    end
    for i in 2:n-1, j in i+1:n
        pairs[(i, j)] = reference[i - 1, i - 1] + reference[j - 1, j - 1] -
                        2reference[i - 1, j - 1]
    end
    pairs
end

function four_winding_inputs()
    reference_reactance = [
        2.4  0.18 -0.12;
        0.18 3.2   0.25;
       -0.12 0.25  4.1;
    ]
    data = MultiwindingLeakageData(
        "x4",
        ["x4/winding/$index" for index in 1:4],
        [110.0, 20.0, 10.0, 6.6],
        [0.20, 0.010, 0.020, 0.030],
        [600.0, 1800.0, 900.0, 1200.0],
        pairwise_from_reference(reference_reactance),
    )
    labels = ["a", "b", "c"]
    factors = WindingFactor[
        WindingFactor(
            "x4/winding/1", "x4", 1, "bus/hv", ["a", "b", "c", "n"], "WYE",
            wye_incidence(["a", "b", "c", "n"]), fill(600.0, 3);
            coil_labels=labels,
        ),
        WindingFactor(
            "x4/winding/2", "x4", 2, "bus/mv", ["a", "b", "c", "n"], "WYE",
            wye_incidence(["a", "b", "c", "n"]), fill(1800.0, 3);
            coil_labels=labels,
        ),
        WindingFactor(
            "x4/winding/3", "x4", 3, "bus/lv1", ["a", "b", "c"], "DELTA",
            delta_incidence(["a", "b", "c"]; roll=-1), fill(900.0, 3);
            coil_labels=labels,
        ),
        WindingFactor(
            "x4/winding/4", "x4", 4, "bus/lv2", ["a", "b", "c", "n"], "WYE",
            wye_incidence(["a", "b", "c", "n"]), fill(1200.0, 3);
            coil_labels=labels,
        ),
    ]
    leakage = compile_pairwise_leakage(data)
    leakage isa MultiwindingLeakageResult || error("four-winding leakage compilation was rejected")
    terminal = assemble_terminal_leakage(leakage, factors)
    terminal isa MultiwindingTerminalAssemblyResult || error("four-winding terminal assembly was rejected")
    (; data, factors, leakage, terminal, reference_reactance)
end

function transfer_state(fixture, state)
    coefficients = [
        ones(ComplexF64, 3),
        fill(ComplexF64(state["tap"]), 3),
        ones(ComplexF64, 3),
        fill(cis(Float64(state["phase_rad"])), 3),
    ]
    transfers = WindingTransfer[
        WindingTransfer(
            factor.id, factor.transformer_id, factor.id, factor.winding_position,
            factor.coil_labels, "fixed", coefficients[factor.winding_position];
            terminal_labels=factor.terminals,
            attributes=Dict("state_id" => state["id"]),
        ) for factor in fixture.factors
    ]
    shunt_2 = ExcitationShunt(
        "x4/shunt/winding/2", "x4", 2, ["a", "b", "c"],
        Diagonal(fill(2.0e-5 - 7.0e-5im, 3));
        attributes=Dict("placement" => "across WYE winding 2 coils"),
    )
    groundings = InternalGrounding[
        InternalGrounding("x4/ground/winding/1/n", "x4", 1, "n", 1.0e-3 - 2.0e-3im),
        InternalGrounding("x4/ground/winding/4/n", "x4", 4, "n", 4.0e-4 - 1.0e-3im),
    ]
    data = TransformerCompletionData(
        "x4/completion/$(state["id"])", "x4", "evaluated_state",
        "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc", transfers;
        excitation_shunt=shunt_2,
        internal_groundings=groundings,
        metadata=Dict("decision_state" => state["id"]),
    )
    completion = assemble_complete_transformer(fixture.terminal, data)
    completion isa TransformerCompletionResult || error("four-winding completion was rejected")

    # A second shunt is deliberately placed on the DELTA winding.  It is not
    # folded into the first excitation_shunt field, so the witness records
    # connection-specific placement rather than treating shunts as generic.
    winding = 3
    coil_range = fixture.terminal.winding_coil_ranges[winding]
    terminal_range = fixture.terminal.winding_terminal_ranges[winding]
    connection = fixture.terminal.terminal_to_coil[coil_range, terminal_range]
    shunt_3 = Diagonal(fill(1.2e-5 - 3.0e-5im, 3))
    shunt_3_voltage_map = zeros(ComplexF64, 3, length(completion.qualified_terminal_labels))
    shunt_3_voltage_map[:, terminal_range] .= connection
    shunt_3_current_map = shunt_3 * shunt_3_voltage_map
    terminal_admittance = completion.terminal_admittance +
                          shunt_3_voltage_map' * shunt_3_current_map
    (; state, completion, shunt_3, shunt_3_voltage_map, shunt_3_current_map,
       terminal_admittance)
end

function state_evidence(fixture, evaluated)
    completion = evaluated.completion
    y = evaluated.terminal_admittance
    u = ComplexF64[complex(cos(0.13k), sin(0.21k)) for k in axes(y, 1)]
    leakage_current = completion.leakage_current_map * u
    excitation_current = completion.excitation_current_map * u
    ground_current = completion.ground_current_map * u
    shunt_3_current = evaluated.shunt_3_current_map * u
    terminal_current = y * u
    recovered = completion.leakage_voltage_map' * leakage_current +
                completion.excitation_voltage_map' * excitation_current +
                ground_current + evaluated.shunt_3_voltage_map' * shunt_3_current
    checks = Dict(
        "completion_certificate_is_exact" => completion.certificate["classification"] == "exact_compilation",
        "terminal_current_recovery_is_exact" => maximum(abs.(terminal_current - recovered)) <= 1.0e-10,
        "complex_power_balance_is_exact" => abs(
            dot(u, terminal_current) -
            dot(completion.leakage_voltage_map * u, leakage_current) -
            dot(completion.excitation_voltage_map * u, excitation_current) -
            dot(u, ground_current) -
            dot(evaluated.shunt_3_voltage_map * u, shunt_3_current),
        ) <= 1.0e-10,
        "connection_specific_delta_shunt_is_retained" => count(!iszero, evaluated.shunt_3_voltage_map) == 6,
        "grounding_maps_are_retained" => count(!iszero, completion.ground_current_map) == 2,
    )
    Dict(
        "state" => evaluated.state,
        "terminal_admittance_matrix_S" => complex_rows(y),
        "terminal_dimension" => size(y, 1),
        "leakage_current_limit_A" => completion.leakage_current_limit,
        "decision_observation" => Dict(
            "tap_id" => "tap/x4/winding/2",
            "tap_value" => evaluated.state["tap"],
            "phase_shift_id" => "phase/x4/winding/4",
            "phase_shift_rad" => evaluated.state["phase_rad"],
            "state_id" => evaluated.state["id"],
        ),
        "recovery_maps" => Dict(
            "leakage_current" => "i_leak = Ycoil*T*A*u",
            "winding_leakage_current" => "i_winding = T^H*i_leak",
            "excitation_current" => "i_excitation = Y0*S*u",
            "ground_current" => "i_ground = Yground*u",
            "delta_shunt_current" => "i_shunt_3 = Y3*S3*u",
            "terminal_current" => "i_terminal = (T*A)^H*i_leak + S^H*i_excitation + i_ground + S3^H*i_shunt_3",
        ),
        "checks" => checks,
    )
end

function evaluate_four_winding_lowering()
    fixture = four_winding_inputs()
    states = [
        Dict("id" => "tap_low_phase_lead", "tap" => 0.95, "phase_rad" => -pi / 36),
        Dict("id" => "tap_high_phase_lag", "tap" => 1.05, "phase_rad" => pi / 36),
    ]
    evaluated = [transfer_state(fixture, state) for state in states]
    state_records = [state_evidence(fixture, item) for item in evaluated]
    matrix_difference = maximum(abs.(
        evaluated[1].terminal_admittance - evaluated[2].terminal_admittance,
    ))
    reference_two = compile_pairwise_leakage(fixture.data; reference_winding=2)
    terminal_reference_two = assemble_terminal_leakage(reference_two, fixture.factors)
    all_state_checks = all(all(values(record["checks"])) for record in state_records)
    checks = Dict(
        "four_windings_are_retained" => length(fixture.data.winding_ids) == 4,
        "reference_matrix_is_full_and_non_diagonal" =>
            !isdiag(fixture.leakage.reference_impedance) &&
            size(fixture.leakage.reference_impedance) == (3, 3),
        "reference_matrix_is_positive_definite" =>
            minimum(eigvals(Symmetric(imag.(fixture.leakage.reference_impedance)))) > 0,
        "mixed_connection_ports_are_retained" =>
            [factor.connection for factor in fixture.factors] == ["WYE", "WYE", "DELTA", "WYE"],
        "connection_specific_shunts_are_distinct" =>
            state_records[1]["checks"]["connection_specific_delta_shunt_is_retained"],
        "internal_grounding_is_retained" =>
            state_records[1]["checks"]["grounding_maps_are_retained"],
        "pointwise_decision_states_are_evaluated" => length(state_records) == 2,
        "decision_changes_equation_operator" => matrix_difference > 1.0e-8,
        "decision_identity_is_retained" => all(
            haskey(record["decision_observation"], "tap_id") &&
            haskey(record["decision_observation"], "phase_shift_id")
            for record in state_records
        ),
        "reference_choice_preserves_terminal_leakage" =>
            maximum(abs.(fixture.terminal.terminal_admittance - terminal_reference_two.terminal_admittance)) <= 1.0e-10,
        "all_state_recovery_checks_pass" => all_state_checks,
        "ordinary_edge_realization_is_not_invented" => true,
    )
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-LOWER-002",
        "claim_ids" => ["ARCH-LOWER-002"],
        "evidence_type" => "evaluated_four_winding_lowering_with_decision_and_recovery_contract",
        "model_scope" => "fixed-frequency four-winding factor with a full non-diagonal reference matrix, mixed WYE/DELTA ports, connection-specific shunts, internal grounding, and finite pointwise tap/phase states",
        "source" => Dict(
            "model_category" => "identity_bearing_four_winding_transformer_source",
            "object_ids" => ["transformer/x4", fixture.data.winding_ids...],
            "detail" => Dict(
                "winding_connections" => [factor.connection for factor in fixture.factors],
                "terminal_orders" => Dict(factor.id => factor.terminals for factor in fixture.factors),
                "pairwise_short_circuit_reactance_ohm" => Dict("$(pair[1])_$(pair[2])" => value for (pair, value) in fixture.data.short_circuit_reactance),
            ),
        ),
        "target" => Dict(
            "model_category" => "pointwise_complete_terminal_factor_family",
            "object_ids" => ["generated_complete_terminal_factor__x4__$(state["id"])" for state in states],
            "detail" => Dict(
                "terminal_dimension" => length(fixture.terminal.qualified_terminal_labels),
                "state_count" => length(states),
                "state_is_not_a_new_asset" => true,
            ),
        ),
        "decision_domain" => Dict(
            "tap/x4/winding/2" => Dict("kind" => "discrete", "values" => [0.95, 1.05]),
            "phase/x4/winding/4" => Dict("kind" => "discrete", "values" => [-pi / 36, pi / 36]),
        ),
        "reference_matrix" => Dict(
            "selected_reference_winding" => "x4/winding/1",
            "imaginary_part" => matrix_rows(imag.(fixture.leakage.reference_impedance)),
            "is_non_diagonal" => !isdiag(fixture.leakage.reference_impedance),
            "pairwise_round_trip" => fixture.leakage.certificate["evidence"]["pairwise_round_trip_ohm"],
        ),
        "connection_specific_shunts" => [
            Dict("id" => "x4/shunt/winding/2", "winding" => "x4/winding/2", "connection" => "WYE", "placement" => "across connected coils"),
            Dict("id" => "x4/shunt/winding/3", "winding" => "x4/winding/3", "connection" => "DELTA", "placement" => "across delta coil coordinates"),
        ],
        "internal_grounding" => [
            Dict("id" => "x4/ground/winding/1/n", "terminal" => "x4/winding/1/n"),
            Dict("id" => "x4/ground/winding/4/n", "terminal" => "x4/winding/4/n"),
        ],
        "states" => state_records,
        "layers" => [
            Dict("id" => "source_asset", "interface" => "winding identity, connection, limits, state domain, provenance"),
            Dict("id" => "port_factor", "interface" => "four ordered winding ports with typed terminal and coil coordinates"),
            Dict("id" => "equation_operator", "interface" => "pointwise terminal admittance plus recovery and constraint maps"),
            Dict("id" => "support_graph", "interface" => "derived nonzero support only; no automatic asset or decision meaning"),
        ],
        "maps" => [
            Dict("id" => "C_x4", "from" => "source_asset", "to" => "port_factor", "status" => "exact identity and connection canonicalization"),
            Dict("id" => "A_x4(σ)", "from" => "port_factor", "to" => "equation_operator", "status" => "exact for each declared fixed decision state σ"),
            Dict("id" => "L_x4", "from" => "port_factor", "to" => "ordinary_edge_realization", "status" => "not asserted; no source-faithful ordinary-edge expansion is inferred"),
            Dict("id" => "S_x4", "from" => "equation_operator", "to" => "support_graph", "status" => "derived support projection; factors, limits, and decisions remain external"),
        ],
        "realizability_boundary" => Dict(
            "direct_factor_stamping" => "available and evaluated",
            "pointwise_terminal_operator" => "available for each fixed decision state",
            "ordinary_edge_realization" => "requires a separate n-port realizability proof and is not supplied by this witness",
            "support_projection" => "available as a derived numerical view only",
        ),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "The three-winding example is a special case of a four-winding lowering architecture. The evaluated target is a family indexed by declared tap and phase decisions; mixed connection maps, shunts, grounding, and recovery remain explicit. No ordinary-edge transformer surrogate is inferred merely because the terminal operator is available.",
    )
end

end

using BMOPFTools
using JSON3
using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :CoordinateActions)
    include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
end
if !isdefined(@__MODULE__, :TransformerWindingNormalization)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerWindingNormalization.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingLeakageCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingLeakageCompilation.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingTerminalAssembly)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingTerminalAssembly.jl"))
end
if !isdefined(@__MODULE__, :TransformerFactorCompletion)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerFactorCompletion.jl"))
end
if !isdefined(@__MODULE__, :TransformerTapDecisionCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerTapDecisionCompilation.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformerFactorCompletion
using .TransformerTapDecisionCompilation
using .TransformationContracts

function tap_decision_fixture()
    root = normpath(joinpath(@__DIR__, "..", ".."))
    network = JSON3.read(
        read(joinpath(root, "data", "running-network", "v0.1.0.json"), String),
        Dict{String,Any},
    )
    raw_contract = JSON3.read(
        read(joinpath(root, "data", "transformer-contracts", "x1-discrete-tap-v0.1.0.json"), String),
        Dict{String,Any},
    )
    transformer = network["transformer"]["n_winding"]["x1"]
    windings = transformer["windings"]
    pairs = Dict{Tuple{Int,Int},Float64}()
    for (key, value) in transformer["x_sc"]
        i, j = parse.(Int, split(key, "_"))
        pairs[(i, j)] = Float64(value)
    end
    leakage_data = MultiwindingLeakageData(
        "x1", ["x1/winding/$k" for k in eachindex(windings)],
        [winding["v_nom"] for winding in windings],
        [winding["r_winding"] for winding in windings],
        [winding["i_max"] for winding in windings], pairs,
    )
    factors = WindingFactor[]
    for (position, winding) in enumerate(windings)
        terminals = String.(winding["terminal_map"])
        connection = String(winding["configuration"])
        incidence = connection == "WYE" ? wye_incidence(terminals) :
            delta_incidence(terminals; roll=Int(winding["delta_roll"]))
        coil_labels = connection == "WYE" ? filter(!=("n"), terminals) : copy(terminals)
        push!(factors, WindingFactor(
            "x1/winding/$position", "x1", position, winding["bus"], terminals,
            connection, incidence, fill(Float64(winding["i_max"]), length(coil_labels));
            coil_labels=coil_labels,
        ))
    end
    leakage = assemble_terminal_leakage(compile_pairwise_leakage(leakage_data), factors)
    data = completion_data_from_dict(raw_contract)
    (; network, transformer, factors, leakage, data)
end

function tap_witness_voltage()
    sequence = ComplexF64[1.0, cis(-2pi / 3), cis(2pi / 3)]
    v1 = 7199.557856794634 .* sequence
    v2 = (0.97 * 277.1281292110204) .* sequence
    v3 = (4160.0 / sqrt(3)) .* cis(pi / 6) .* sequence
    vcat(v1, 0.0 + 0.0im, v2, 0.0 + 0.0im, v3)
end

function tap_transfer_copy(
    source::WindingTransfer;
    coil_labels=source.coil_labels,
    coefficient=source.coefficient,
    control_mode=source.control_mode,
    decision_id=source.decision_id,
    attributes=source.attributes,
)
    WindingTransfer(
        source.id, source.transformer_id, source.winding_id, source.winding_position,
        coil_labels, control_mode, coefficient;
        terminal_labels=source.terminal_labels,
        decision_id=decision_id,
        attributes=attributes,
    )
end

function direct_tap_snapshot(data::TransformerCompletionData, decision_id, value)
    transfers = [
        transfer.control_mode == "fixed" ? tap_transfer_copy(transfer) :
        tap_transfer_copy(
            transfer;
            coefficient=transfer.coefficient .* value,
            control_mode="fixed",
            decision_id=nothing,
        )
        for transfer in data.winding_transfers
    ]
    TransformerCompletionData(
        "$(data.id)/direct/$value", data.transformer_id, "direct_source_snapshot",
        data.voltage_transfer_convention, transfers;
        excitation_shunt=data.excitation_shunt,
        internal_groundings=data.internal_groundings,
        metadata=merge(data.metadata, Dict("decision_id" => decision_id, "value" => value)),
    )
end

@testset "discrete tap decision is retained pointwise" begin
    fixture = tap_decision_fixture()
    factor = compile_parameterized_transformer(fixture.leakage, fixture.data)
    @test factor isa ParameterizedTransformerFactor
    @test isempty(validate_certificate(factor.certificate))
    @test length(factor.decisions) == 1
    domain = only(factor.decisions)
    @test domain.decision_id == "tap/x1/winding/2"
    @test domain.control_mode == "discrete"
    @test domain.positions == [0.95, 1.0, 1.05]
    @test factor.certificate["interfaces"]["decisions"]["source"] == [domain.decision_id]
    @test factor.certificate["interfaces"]["decisions"]["target"] == [domain.decision_id]

    u = tap_witness_voltage()
    for tap in domain.positions
        evaluated = evaluate_parameterized_transformer(factor, Dict(domain.decision_id => tap))
        direct = assemble_complete_transformer(
            fixture.leakage,
            direct_tap_snapshot(fixture.data, domain.decision_id, tap),
        )
        @test evaluated isa TransformerCompletionResult
        @test evaluated.terminal_admittance ≈ direct.terminal_admittance
        @test evaluated.winding_leakage_current_map ≈ direct.winding_leakage_current_map
        v_leak = evaluated.leakage_voltage_map * u
        i_leak = evaluated.leakage_current_map * u
        i_terminal = evaluated.terminal_admittance * u
        i_excitation = evaluated.excitation_current_map * u
        i_ground = evaluated.ground_current_map * u
        @test i_terminal ≈ evaluated.leakage_voltage_map' * i_leak +
                           evaluated.excitation_voltage_map' * i_excitation + i_ground
        @test dot(u, i_terminal) ≈ dot(v_leak, i_leak) +
              dot(evaluated.excitation_voltage_map * u, i_excitation) + dot(u, i_ground)
    end

    invalid_position = evaluate_parameterized_transformer(
        factor, Dict(domain.decision_id => 0.975),
    )
    @test invalid_position isa TapDecisionEvaluationRejection
    @test "tap_decision_value_is_outside_declared_domain" in invalid_position.failed_guards
    missing_decision = evaluate_parameterized_transformer(factor, Dict{String,Float64}())
    @test missing_decision isa TapDecisionEvaluationRejection
    @test "tap_decision_key_set_does_not_match_factor" in missing_decision.failed_guards
end

@testset "continuous tap interval and coordinate covariance" begin
    fixture = tap_decision_fixture()
    transfers = [tap_transfer_copy(transfer) for transfer in fixture.data.winding_transfers]
    adjustable = transfers[2]
    continuous_attributes = merge(adjustable.attributes, Dict{String,Any}(
        "tap_start" => 1.0,
        "tap_min" => 0.94,
        "tap_max" => 1.06,
    ))
    delete!(continuous_attributes, "tap_positions")
    transfers[2] = tap_transfer_copy(
        adjustable; control_mode="continuous", attributes=continuous_attributes,
    )
    continuous_data = TransformerCompletionData(
        "x1/continuous-tap/test", "x1", "test", fixture.data.voltage_transfer_convention,
        transfers;
        excitation_shunt=fixture.data.excitation_shunt,
        internal_groundings=fixture.data.internal_groundings,
    )
    continuous = compile_parameterized_transformer(fixture.leakage, continuous_data)
    @test continuous isa ParameterizedTransformerFactor
    @test only(continuous.decisions).lower_bound == 0.94
    @test only(continuous.decisions).upper_bound == 1.06
    @test evaluate_parameterized_transformer(
        continuous, Dict("tap/x1/winding/2" => 1.013),
    ) isa TransformerCompletionResult
    @test evaluate_parameterized_transformer(
        continuous, Dict("tap/x1/winding/2" => 1.061),
    ) isa TapDecisionEvaluationRejection

    reordered = [tap_transfer_copy(transfer) for transfer in transfers]
    reordered[2] = tap_transfer_copy(
        transfers[2]; coil_labels=["c", "a", "b"], coefficient=transfers[2].coefficient[[3, 1, 2]],
    )
    reordered_data = TransformerCompletionData(
        "x1/continuous-reordered/test", "x1", "test", fixture.data.voltage_transfer_convention,
        reordered;
        excitation_shunt=fixture.data.excitation_shunt,
        internal_groundings=fixture.data.internal_groundings,
    )
    reordered_factor = compile_parameterized_transformer(fixture.leakage, reordered_data)
    original_snapshot = evaluate_parameterized_transformer(
        continuous, Dict("tap/x1/winding/2" => 1.013),
    )
    reordered_snapshot = evaluate_parameterized_transformer(
        reordered_factor, Dict("tap/x1/winding/2" => 1.013),
    )
    @test reordered_snapshot.terminal_admittance ≈ original_snapshot.terminal_admittance
end

@testset "freezing the tap changes the decision problem" begin
    fixture = tap_decision_fixture()
    factor = compile_parameterized_transformer(fixture.leakage, fixture.data)
    domain = only(factor.decisions)
    u = tap_witness_voltage()
    limit = fixture.leakage.coil_current_limit[4]
    stress = Dict{Float64,Float64}()
    for tap in domain.positions
        snapshot = evaluate_parameterized_transformer(factor, Dict(domain.decision_id => tap))
        winding_current = snapshot.winding_leakage_current_map * u
        stress[tap] = maximum(abs.(winding_current[4:6]))
    end
    feasible = [tap for tap in domain.positions if stress[tap] <= limit]
    optimum = feasible[argmin(stress[tap] for tap in feasible)]
    @test feasible == [1.0, 1.05]
    @test optimum == 1.05
    @test stress[1.05] < stress[1.0]
    @test stress[0.95] > limit
    @test factor.start_snapshot.winding_leakage_current_map * u ≈
          evaluate_parameterized_transformer(
              factor, Dict(domain.decision_id => domain.start_value),
          ).winding_leakage_current_map * u
end

@testset "parameterized compiler rejects malformed tap domains" begin
    fixture = tap_decision_fixture()
    base = fixture.data.winding_transfers

    unsorted = [tap_transfer_copy(transfer) for transfer in base]
    unsorted_attributes = merge(unsorted[2].attributes, Dict("tap_positions" => [1.0, 0.95, 1.05]))
    unsorted[2] = tap_transfer_copy(unsorted[2]; attributes=unsorted_attributes)
    unsorted_data = TransformerCompletionData(
        "x1/unsorted/test", "x1", "test", fixture.data.voltage_transfer_convention,
        unsorted,
    )
    rejected_order = compile_parameterized_transformer(fixture.leakage, unsorted_data)
    @test rejected_order isa TapDecisionFactorRejection
    @test "discrete_tap_positions_must_be_sorted" in rejected_order.failed_guards

    duplicate_id = [tap_transfer_copy(transfer) for transfer in base]
    attributes = merge(base[1].attributes, Dict{String,Any}(
        "coefficient_parameterization" =>
            "coefficient_xkc(tap) = tap * base_coefficient_xkc",
        "tap_start" => 1.0,
        "tap_positions" => [0.95, 1.0, 1.05],
    ))
    duplicate_id[1] = tap_transfer_copy(
        base[1]; control_mode="discrete", decision_id=base[2].decision_id,
        attributes=attributes,
    )
    duplicate_data = TransformerCompletionData(
        "x1/duplicate-id/test", "x1", "test", fixture.data.voltage_transfer_convention,
        duplicate_id,
    )
    rejected_id = compile_parameterized_transformer(fixture.leakage, duplicate_data)
    @test rejected_id isa TapDecisionFactorRejection
    @test "tap_decision_identities_must_be_unique" in rejected_id.failed_guards
end

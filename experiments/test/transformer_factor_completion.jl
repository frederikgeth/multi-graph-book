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
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformerFactorCompletion
using .TransformationContracts

function completion_fixture()
    root = normpath(joinpath(@__DIR__, "..", ".."))
    network = JSON3.read(
        read(joinpath(root, "data", "running-network", "v0.1.0.json"), String),
        Dict{String,Any},
    )
    raw_contract = JSON3.read(
        read(joinpath(root, "data", "transformer-contracts", "x1-fixed-linear-v0.1.0.json"), String),
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
        "x1",
        ["x1/winding/$k" for k in eachindex(windings)],
        [winding["v_nom"] for winding in windings],
        [winding["r_winding"] for winding in windings],
        [winding["i_max"] for winding in windings],
        pairs,
    )
    factors = WindingFactor[]
    for (position, winding) in enumerate(windings)
        terminals = String.(winding["terminal_map"])
        connection = String(winding["configuration"])
        incidence = connection == "WYE" ?
            wye_incidence(terminals) :
            delta_incidence(terminals; roll=Int(winding["delta_roll"]))
        coil_labels = connection == "WYE" ? filter(!=("n"), terminals) : copy(terminals)
        push!(factors, WindingFactor(
            "x1/winding/$position", "x1", position, winding["bus"], terminals,
            connection, incidence, fill(Float64(winding["i_max"]), length(coil_labels));
            coil_labels=coil_labels,
        ))
    end
    leakage = compile_pairwise_leakage(leakage_data)
    terminal = assemble_terminal_leakage(leakage, factors)
    (; network, transformer, factors, terminal, raw_contract)
end

function fixed_transfer_copy(
    source::WindingTransfer;
    coil_labels=source.coil_labels,
    coefficient=source.coefficient,
    control_mode=source.control_mode,
    decision_id=source.decision_id,
)
    WindingTransfer(
        source.id, source.transformer_id, source.winding_id, source.winding_position,
        coil_labels, control_mode, coefficient;
        terminal_labels=source.terminal_labels,
        decision_id=decision_id,
        attributes=source.attributes,
    )
end

@testset "serialized fixed-linear transformer completion" begin
    fixture = completion_fixture()
    data = completion_data_from_dict(fixture.raw_contract)
    round_trip = completion_data_from_dict(completion_data_to_dict(data))
    @test round_trip.id == data.id
    @test round_trip.transformer_id == data.transformer_id
    @test [transfer.coefficient for transfer in round_trip.winding_transfers] ==
          [transfer.coefficient for transfer in data.winding_transfers]
    @test [transfer.terminal_labels for transfer in round_trip.winding_transfers] ==
          [transfer.terminal_labels for transfer in data.winding_transfers]
    @test round_trip.excitation_shunt.admittance == data.excitation_shunt.admittance
    @test only(round_trip.internal_groundings).admittance ==
          only(data.internal_groundings).admittance

    result = assemble_complete_transformer(fixture.terminal, data)
    @test result isa TransformerCompletionResult
    @test isempty(validate_certificate(result.certificate))
    @test size(result.voltage_transfer) == (9, 9)
    @test size(result.leakage_voltage_map) == (9, 11)
    @test size(result.winding_leakage_current_map) == (9, 11)
    @test size(result.excitation_current_map) == (3, 11)
    @test size(result.ground_current_map) == (11, 11)
    @test size(result.terminal_admittance) == (11, 11)

    grounded_position = findfirst(
        ==("x1/winding/1/terminal/n"), result.qualified_terminal_labels,
    )
    @test grounded_position !== nothing
    @test result.ground_current_map[grounded_position, grounded_position] == 0.001 - 0.002im
    @test count(!iszero, result.ground_current_map) == 1

    terminal_voltage = ComplexF64[
        complex(cos(0.31k), sin(0.19k)) for k in axes(result.terminal_admittance, 1)
    ]
    leakage_voltage = result.leakage_voltage_map * terminal_voltage
    leakage_current = result.leakage_current_map * terminal_voltage
    winding_current = result.winding_leakage_current_map * terminal_voltage
    excitation_voltage = result.excitation_voltage_map * terminal_voltage
    excitation_current = result.excitation_current_map * terminal_voltage
    ground_current = result.ground_current_map * terminal_voltage
    terminal_current = result.terminal_admittance * terminal_voltage
    recovered_terminal_current = result.leakage_voltage_map' * leakage_current +
                                 result.excitation_voltage_map' * excitation_current +
                                 ground_current
    @test winding_current ≈ result.voltage_transfer' * leakage_current
    @test terminal_current ≈ recovered_terminal_current
    @test dot(terminal_voltage, terminal_current) ≈
          dot(leakage_voltage, leakage_current) +
          dot(excitation_voltage, excitation_current) +
          dot(terminal_voltage, ground_current)

    # With identity voltage transfers, removing the two completion shunts
    # recovers the already-certified terminal leakage block exactly.
    completed_shunts = result.excitation_voltage_map' * result.excitation_current_map +
                       result.ground_current_map
    @test result.terminal_admittance - completed_shunts ≈ fixture.terminal.terminal_admittance
end

@testset "BMOPFTools n-winding primitive cross-check" begin
    fixture = completion_fixture()
    data = completion_data_from_dict(fixture.raw_contract)
    result = assemble_complete_transformer(fixture.terminal, data)

    transformer = deepcopy(fixture.transformer)
    y0 = data.excitation_shunt.admittance[1, 1]
    transformer["g_no_load"] = real(y0)
    transformer["b_no_load"] = imag(y0)
    nodes, independent = BMOPFTools.nwinding_yprim(transformer)
    expected_labels = ["$(bus)/terminal/$(terminal)" for (bus, terminal) in nodes]
    actual_labels = [replace(label, r"^x1/winding/\d+/terminal/" =>
        "$(fixture.factors[parse(Int, split(label, '/')[3])].bus)/terminal/")
        for label in result.qualified_terminal_labels]
    @test actual_labels == expected_labels
    @test result.terminal_admittance - result.ground_current_map ≈ independent atol=1.0e-12
end

@testset "fixed tap and phase operators are power dual" begin
    fixture = completion_fixture()
    base = completion_data_from_dict(fixture.raw_contract)
    phase = cis(deg2rad(7.5))
    coefficients = (
        ComplexF64[1.0, 1.0, 1.0],
        ComplexF64[1.01, 1.02, 1.03],
        fill(ComplexF64(phase), 3),
    )
    transfers = [fixed_transfer_copy(transfer; coefficient=coefficients[index])
                 for (index, transfer) in enumerate(base.winding_transfers)]
    data = TransformerCompletionData(
        "x1/fixed-tap-phase/test", "x1", "test", base.voltage_transfer_convention,
        transfers,
    )
    result = assemble_complete_transformer(fixture.terminal, data)
    @test result isa TransformerCompletionResult
    @test !isapprox(result.terminal_admittance, transpose(result.terminal_admittance); atol=1.0e-9)

    u = ComplexF64[complex(sin(0.13k), cos(0.17k)) for k in 1:11]
    v_leak = result.leakage_voltage_map * u
    i_leak = result.leakage_current_map * u
    i_terminal = result.terminal_admittance * u
    @test i_terminal ≈ result.leakage_voltage_map' * i_leak
    @test dot(u, i_terminal) ≈ dot(v_leak, i_leak)

    # Reordering one transfer's labelled coefficients is a coordinate action,
    # not a change in the physical transfer.
    reordered = [fixed_transfer_copy(transfer) for transfer in transfers]
    reordered[2] = fixed_transfer_copy(
        transfers[2];
        coil_labels=["c", "a", "b"],
        coefficient=coefficients[2][[3, 1, 2]],
    )
    reordered_data = TransformerCompletionData(
        "x1/reordered-transfer/test", "x1", "test", base.voltage_transfer_convention,
        reordered,
    )
    reordered_result = assemble_complete_transformer(fixture.terminal, reordered_data)
    @test reordered_result.terminal_admittance ≈ result.terminal_admittance
    @test reordered_result.winding_leakage_current_map ≈ result.winding_leakage_current_map
end

@testset "static completion rejects decision and scope loss" begin
    fixture = completion_fixture()
    base = completion_data_from_dict(fixture.raw_contract)

    adjustable = [fixed_transfer_copy(transfer) for transfer in base.winding_transfers]
    adjustable[2] = fixed_transfer_copy(
        adjustable[2]; control_mode="continuous", decision_id="tap/x1/winding/2",
    )
    adjustable_data = TransformerCompletionData(
        "x1/adjustable/test", "x1", "test", base.voltage_transfer_convention,
        adjustable;
        excitation_shunt=base.excitation_shunt,
        internal_groundings=base.internal_groundings,
    )
    rejected_decision = assemble_complete_transformer(fixture.terminal, adjustable_data)
    @test rejected_decision isa TransformerCompletionRejection
    @test "adjustable_winding_transfer_requires_factorized_decision_model" in
          rejected_decision.failed_guards

    external_ground = InternalGrounding(
        "bus/i1/ground", "x1", 1, "n", 0.001 - 0.002im; scope="external_bus",
    )
    external_data = TransformerCompletionData(
        "x1/external-ground/test", "x1", "test", base.voltage_transfer_convention,
        base.winding_transfers;
        excitation_shunt=base.excitation_shunt,
        internal_groundings=[external_ground],
    )
    rejected_ground = assemble_complete_transformer(fixture.terminal, external_data)
    @test rejected_ground isa TransformerCompletionRejection
    @test "external_bus_grounding_cannot_be_absorbed" in rejected_ground.failed_guards

    active_shunt = ExcitationShunt(
        "x1/active-shunt", "x1", 2, ["a", "b", "c"],
        Diagonal(fill(-1.0e-5 - 4.0e-5im, 3)),
    )
    active_data = TransformerCompletionData(
        "x1/active-shunt/test", "x1", "test", base.voltage_transfer_convention,
        base.winding_transfers; excitation_shunt=active_shunt,
    )
    rejected_shunt = assemble_complete_transformer(fixture.terminal, active_data)
    @test rejected_shunt isa TransformerCompletionRejection
    @test "excitation_shunt_admittance_must_be_passive" in rejected_shunt.failed_guards

    missing_terminal = InternalGrounding("x1/bad-ground", "x1", 3, "n", 0.01 + 0.0im)
    missing_data = TransformerCompletionData(
        "x1/missing-terminal/test", "x1", "test", base.voltage_transfer_convention,
        base.winding_transfers; internal_groundings=[missing_terminal],
    )
    rejected_terminal = assemble_complete_transformer(fixture.terminal, missing_data)
    @test rejected_terminal isa TransformerCompletionRejection
    @test "internal_grounding_terminal_does_not_exist" in rejected_terminal.failed_guards
end

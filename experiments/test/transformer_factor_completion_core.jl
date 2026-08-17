using LinearAlgebra
using Test

include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "..", "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "..", "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "..", "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "..", "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "..", "transformations", "TransformerTapDecisionCompilation.jl"))
include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformerFactorCompletion
using .TransformerTapDecisionCompilation
using .TransformationContracts

leakage_data = MultiwindingLeakageData(
    "x1",
    ["x1/winding/1", "x1/winding/2", "x1/winding/3"],
    [7199.557856794634, 277.1281292110204, 4160.0],
    [0.38875225, 0.000576, 0.12979200000000002],
    [180.0, 2200.0, 280.0],
    Dict((1, 2) => 4.665027, (1, 3) => 5.4425315, (2, 3) => 3.8875225),
)
labels = ["a", "b", "c"]
windings = [
    WindingFactor(
        "x1/winding/1", "x1", 1, "i1", ["a", "b", "c", "n"], "WYE",
        wye_incidence(["a", "b", "c", "n"]), fill(180.0, 3); coil_labels=labels,
    ),
    WindingFactor(
        "x1/winding/2", "x1", 2, "i5", ["a", "b", "c", "n"], "WYE",
        wye_incidence(["a", "b", "c", "n"]), fill(2200.0, 3); coil_labels=labels,
    ),
    WindingFactor(
        "x1/winding/3", "x1", 3, "i6", ["a", "b", "c"], "DELTA",
        delta_incidence(["a", "b", "c"]; roll=-1), fill(280.0, 3); coil_labels=labels,
    ),
]
terminal_leakage = assemble_terminal_leakage(compile_pairwise_leakage(leakage_data), windings)
transfers = [
    WindingTransfer(
        "x1/transfer/$k", "x1", "x1/winding/$k", k, labels, "fixed",
        k == 3 ? fill(cis(deg2rad(7.5)), 3) : fill(1.0 + 0.0im, 3);
        terminal_labels=k == 3 ? ["a", "b", "c"] : ["a", "b", "c", "n"],
    ) for k in 1:3
]
completion = TransformerCompletionData(
    "x1/core-test", "x1", "test",
    "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc",
    transfers;
    excitation_shunt=ExcitationShunt(
        "x1/excitation", "x1", 2, labels,
        Diagonal(fill(1.0e-5 - 4.0e-5im, 3)),
    ),
    internal_groundings=[InternalGrounding(
        "x1/internal-ground/1/n", "x1", 1, "n", 0.001 - 0.002im,
    )],
)

@testset "package-independent transformer completion core" begin
    result = assemble_complete_transformer(terminal_leakage, completion)
    @test result isa TransformerCompletionResult
    @test isempty(validate_certificate(result.certificate))
    @test size(result.terminal_admittance) == (11, 11)
    u = ComplexF64[complex(cos(0.23k), sin(0.11k)) for k in 1:11]
    v_leak = result.leakage_voltage_map * u
    i_leak = result.leakage_current_map * u
    v_excitation = result.excitation_voltage_map * u
    i_excitation = result.excitation_current_map * u
    i_ground = result.ground_current_map * u
    i_terminal = result.terminal_admittance * u
    @test i_terminal ≈ result.leakage_voltage_map' * i_leak +
                       result.excitation_voltage_map' * i_excitation + i_ground
    @test dot(u, i_terminal) ≈ dot(v_leak, i_leak) +
          dot(v_excitation, i_excitation) + dot(u, i_ground)

    adjustable = copy(transfers)
    adjustable[2] = WindingTransfer(
        "x1/transfer/2", "x1", "x1/winding/2", 2, labels, "continuous",
        fill(1.0 + 0.0im, 3);
        terminal_labels=["a", "b", "c", "n"],
        decision_id="tap/x1/winding/2",
    )
    rejected = assemble_complete_transformer(
        terminal_leakage,
        TransformerCompletionData(
            "x1/adjustable", "x1", "test", completion.voltage_transfer_convention,
            adjustable,
        ),
    )
    @test rejected isa TransformerCompletionRejection
    @test "adjustable_winding_transfer_requires_factorized_decision_model" in
          rejected.failed_guards
end

@testset "package-independent transformer tap decision core" begin
    adjustable = copy(transfers)
    adjustable[2] = WindingTransfer(
        "x1/transfer/2", "x1", "x1/winding/2", 2, labels, "discrete",
        fill(1.0 + 0.0im, 3);
        terminal_labels=["a", "b", "c", "n"],
        decision_id="tap/x1/winding/2",
        attributes=Dict{String,Any}(
            "coefficient_parameterization" =>
                "coefficient_xkc(tap) = tap * base_coefficient_xkc",
            "tap_start" => 1.0,
            "tap_positions" => [0.95, 1.0, 1.05],
        ),
    )
    parameterized_data = TransformerCompletionData(
        "x1/tap-core-test", "x1", "test",
        "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc",
        adjustable;
        excitation_shunt=completion.excitation_shunt,
        internal_groundings=completion.internal_groundings,
    )
    factor = compile_parameterized_transformer(terminal_leakage, parameterized_data)
    @test factor isa ParameterizedTransformerFactor
    @test isempty(validate_certificate(factor.certificate))
    @test factor.certificate["interfaces"]["decisions"]["source"] ==
          ["tap/x1/winding/2"]
    @test evaluate_parameterized_transformer(
        factor, Dict("tap/x1/winding/2" => 1.05),
    ) isa TransformerCompletionResult
    rejected = evaluate_parameterized_transformer(
        factor, Dict("tap/x1/winding/2" => 0.975),
    )
    @test rejected isa TapDecisionEvaluationRejection
end

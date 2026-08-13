using Test

if !isdefined(@__MODULE__, :CoordinateActions)
    include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
end
if !isdefined(@__MODULE__, :TransformerWindingNormalization)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerWindingNormalization.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .CoordinateActions
using .TransformerWindingNormalization
using .TransformationContracts

@testset "transformer-winding terminal normalization" begin
    delta = WindingFactor(
        "x1/winding/3", "x1", 3, "i6", ["a", "b", "c"], "DELTA",
        delta_incidence(["a", "b", "c"]; roll=-1), fill(280.0, 3),
    )
    normalized_delta = normalize_winding_terminals(delta, ["c", "a", "b"])
    @test normalized_delta isa WindingNormalizationResult
    @test normalized_delta.target.terminals == ["c", "a", "b"]
    @test normalized_delta.target.coil_current_limit == fill(280.0, 3)
    @test isempty(validate_certificate(normalized_delta.certificate))

    action = coordinate_action(delta.terminals, normalized_delta.target.terminals)
    terminal_voltage = ComplexF64[1.0+0.1im, -0.4-0.8im, -0.6+0.7im]
    target_voltage = pushforward_vector(action, terminal_voltage)
    @test delta.terminal_to_coil * terminal_voltage ≈
        normalized_delta.target.terminal_to_coil * target_voltage
    @test normalized_delta.target.terminal_to_coil * action.permutation ≈
        delta.terminal_to_coil

    wye = WindingFactor(
        "x1/winding/1", "x1", 1, "i1", ["a", "b", "c", "n"], "WYE",
        wye_incidence(["a", "b", "c", "n"]), fill(180.0, 3),
    )
    normalized_wye = normalize_winding_terminals(wye, ["c", "a", "b", "n"])
    @test normalized_wye isa WindingNormalizationResult
    wye_action = coordinate_action(wye.terminals, normalized_wye.target.terminals)
    wye_voltage = ComplexF64[1.0, cis(-2pi/3), cis(2pi/3), 0.02]
    @test wye.terminal_to_coil * wye_voltage ≈
        normalized_wye.target.terminal_to_coil * pushforward_vector(wye_action, wye_voltage)

    rejected = normalize_winding_terminals(delta, ["a", "b", "n"])
    @test rejected isa WindingNormalizationRejection
    @test "coordinate_sets_differ" in rejected.failed_guards
end

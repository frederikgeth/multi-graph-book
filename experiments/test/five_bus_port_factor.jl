using Test

if !isdefined(@__MODULE__, :PortFactorArchitecture)
    include(joinpath(@__DIR__, "..", "transformations", "PortFactorArchitecture.jl"))
end
using .PortFactorArchitecture

@testset "five-bus port-factor lift" begin
    bundle = five_bus_port_factor_bundle()
    validation = validate_port_factor_bundle(bundle)
    @test validation["valid"]
    @test validation["n_ports"] == 14
    @test validation["n_junctions"] == 5
    @test validation["n_factors"] == 7
    @test validation["n_lambda_relations"] == 7
    @test bundle["source_fixture"] == "experiments/generated/five-bus-cycle-space-analysis.json"
    @test bundle["model"]["factors"][1]["factor_type"] == "scalar_series_line"
    @test bundle["model"]["factors"][1]["ports"] == ["line/q/port/from", "line/q/port/to"]
    @test bundle["model"]["ports"][1]["junction"] == "j"
    @test bundle["model"]["ports"][2]["junction"] == "i"
end

using Test

if !isdefined(@__MODULE__, :PortFactorArchitecture)
    include(joinpath(@__DIR__, "..", "transformations", "PortFactorArchitecture.jl"))
end
using .PortFactorArchitecture

@testset "minimal running-network port-factor architecture" begin
    bundle = running_port_factor_bundle()
    @test bundle["claim_id"] == "ARCH-PORT-001"
    validation = validate_port_factor_bundle(bundle)
    @test validation["valid"]
    @test validation["n_ports"] == 8
    @test validation["n_junctions"] == 4
    @test validation["n_factors"] == 4
    @test validation["n_lambda_relations"] == 7
    @test validation["multi_asset_or_factor_link"]

    transformer = only(factor for factor in bundle["model"]["factors"] if factor["id"] == "transformer/x1")
    @test length(transformer["ports"]) == 3
    @test transformer["factor_type"] == "multiwinding_transformer"
    @test count(relation -> relation["asset"] == "transformer/x1", bundle["lambda"]) == 4
    @test all(relation -> relation["relation_type"] in ("realizes", "owns_port"), bundle["lambda"])

    malformed = deepcopy(bundle)
    malformed["model"]["ports"][1]["junction"] = "missing-junction"
    rejected = validate_port_factor_bundle(malformed)
    @test !rejected["valid"]
    @test any(occursin("unknown junction", error) for error in rejected["errors"])
end

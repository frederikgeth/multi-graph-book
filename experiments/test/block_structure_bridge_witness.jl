using Test

if !isdefined(@__MODULE__, :BlockStructureBridgeWitness)
    include(joinpath(@__DIR__, "..", "transformations", "BlockStructureBridgeWitness.jl"))
end
using .BlockStructureBridgeWitness

@testset "block structure bridge" begin
    result = evaluate_block_structure_bridge()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-BLOCK-001"
    @test result["checks"]["block_support_is_two_by_two_simple_support"]
    @test result["checks"]["scalar_support_exposes_dense_conductor_coupling"]
    @test result["checks"]["realification_doubles_coordinates_only"]
    @test result["checks"]["support_does_not_encode_factor_identity"]
end

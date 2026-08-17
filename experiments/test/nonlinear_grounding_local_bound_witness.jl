using Test

if !isdefined(@__MODULE__, :NonlinearGroundingLocalBoundWitness)
    include(joinpath(@__DIR__, "..", "transformations", "NonlinearGroundingLocalBoundWitness.jl"))
end
using .NonlinearGroundingLocalBoundWitness

@testset "local nonlinear grounding bound" begin
    result = nonlinear_grounding_local_bound_witness()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "TR-KRON-NEUTRAL-008"
    @test result["checks"]["frozen_map_has_nonzero_shifted_residual"]
    @test result["checks"]["recomputed_jacobian_is_more_accurate_locally"]
    @test result["checks"]["local_error_decreases_with_step"]
end

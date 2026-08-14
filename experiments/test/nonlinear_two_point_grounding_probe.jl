using Test

include(joinpath(@__DIR__, "..", "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

@testset "nonlinear two-point grounding probe" begin
    result = ExplicitEarthKronWitness.evaluate_nonlinear_two_point_grounding_probe()
    @test result.witness_id == "TR-KRON-NEUTRAL-006"
    @test result.claim_id == "TR-KRON-NEUTRAL-006"
    @test all(values(result.checks))
    @test result.checks["frozen_chain_map_is_not_exact"]
    @test result.checks["recomputed_chain_map_is_exact"]
    @test result.shifted["residual"] ≤ 1.0e-11
end

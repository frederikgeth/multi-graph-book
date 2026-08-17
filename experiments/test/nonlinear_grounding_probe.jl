using Test

include(joinpath(@__DIR__, "..", "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

@testset "nonlinear grounding probe" begin
    result = ExplicitEarthKronWitness.evaluate_nonlinear_grounding_probe()
    @test result.witness_id == "TR-KRON-NEUTRAL-005"
    @test result.claim_id == "TR-KRON-NEUTRAL-005"
    @test all(values(result.checks))
    @test result.checks["frozen_map_is_not_exact_at_shifted_state"]
    @test result.checks["recomputed_map_is_exact_at_shifted_state"]
    @test result.shifted["residual"] ≤ 1.0e-11
end

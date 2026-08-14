using Test

include(joinpath(@__DIR__, "..", "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

@testset "nonlinear two-point grounding continuation" begin
    result = ExplicitEarthKronWitness.evaluate_nonlinear_two_point_continuation()
    @test result.witness_id == "TR-KRON-NEUTRAL-007"
    @test result.claim_id == "TR-KRON-NEUTRAL-007"
    @test all(values(result.checks))
    @test length(result.rows) == 5
    @test result.checks["frozen_nominal_map_fails_off_base"]
    @test result.checks["recomputed_path_has_multiple_states"]
end

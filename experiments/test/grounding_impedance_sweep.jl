using Test

include(joinpath(@__DIR__, "..", "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

@testset "grounding impedance sweep witness" begin
    result = evaluate_grounding_impedance_sweep()
    @test result.witness_id == "TR-KRON-NEUTRAL-004"
    @test result.claim_id == "TR-KRON-NEUTRAL-004"
    @test all(values(result.checks))
    @test length(result.rows) == 4
    @test result.checks["all_grounding_kcl_residuals_are_small"]
    @test result.checks["feasibility_classification_changes"]
end

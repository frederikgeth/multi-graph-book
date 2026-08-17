using Test

include(joinpath(@__DIR__, "..", "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

@testset "explicit earth Kron witness" begin
    result = evaluate_explicit_earth_kron()
    @test result.witness_id == "TR-KRON-NEUTRAL-002"
    @test result.claim_id == "TR-KRON-NEUTRAL-002"
    @test all(values(result.checks))
    @test result.dimensions["conductor_count"] == 5
    @test result.terminal_order == ["a", "b", "c", "n", "e"]
    @test result.residuals["neutral_kcl"] ≤ 1.0e-11
    @test result.residuals["earth_kcl"] ≤ 1.0e-11
    @test result.checks["neutral_limit_is_evaluated"]
    @test result.multiple_grounding_witness["all_checks_pass"]
    @test result.multiple_grounding_witness["internal_points"] == ["m1", "m2"]
    @test result.multiple_grounding_witness["checks"]["first_bond_kcl_is_exact"]
    @test result.multiple_grounding_witness["checks"]["second_bond_kcl_is_exact"]
end

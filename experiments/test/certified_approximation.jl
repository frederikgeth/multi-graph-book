using Test

include(joinpath(@__DIR__, "..", "transformations", "CertifiedApproximation.jl"))
using .CertifiedApproximation

@testset "certified approximation chain" begin
    result = evaluate_certified_approximation()
    @test result.witness_id == "TR-KRON-003"
    @test result.checks["bound_dominates_direct_constraint_error"]
    @test result.checks["base_is_exactly_calibrated"]
    @test result.checks["has_certified_feasible_case"]
    @test result.checks["has_ambiguous_case"]
    @test result.checks["has_certified_violated_case"]
    @test result.classifications["high_load"] == "ambiguous"
    @test result.classifications["low_voltage"] == "certified_feasible"
    @test result.classifications["internal_outage_proxy"] == "certified_violated"
end

using LinearAlgebra
using Test

include(joinpath(@__DIR__, "..", "transformations", "KronWardScenario.jl"))
using .KronWardScenario

@testset "Kron, Ward, and scenario-selected reduction" begin
    result = evaluate_comparison()
    @test result.base_scenario == "base"
    @test all(row["current_error_norm"] ≤ 1e-12 for row in result.ward_rows if row["base_exact"])
    @test any(row["current_error_norm"] > 1e-4 for row in result.ward_rows if !row["base_exact"])
    @test all(row["current_error_norm"] ≤ 1e-12 for row in result.extended_rows)
    @test any(row["support_injection_norm"] > 1e-6 for row in result.extended_rows if !row["base_exact"])
    @test haskey(result.scenario_objective, "full_kron")
    @test result.selected_candidate != "full_kron"
    @test !result.selected_is_exact
    @test all(haskey(row, "predicted_limit_satisfied") for rows in values(result.candidate_rows) for row in rows)
    @test all(haskey(row, "boundary_voltage_norm") for row in result.exact_rows)
    @test all(haskey(row, "internal_current_recovery_error_norm") for row in result.exact_rows)
    @test all(row["internal_current_recovery_error_norm"] ≤ 1e-12 for row in result.exact_rows)
    @test all(haskey(row, "constraint_margin") for rows in values(result.candidate_rows) for row in rows)
    @test all(haskey(row, "recovered_internal_current_norm") for rows in values(result.candidate_rows) for row in rows)
    @test count(row["selected"] for row in result.decision_observations) == 1
end

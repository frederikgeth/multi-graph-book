using Test

if !isdefined(@__MODULE__, :MulticonductorParallelACDecision)
    include(joinpath(@__DIR__, "..", "transformations", "MulticonductorParallelACDecision.jl"))
end
using .MulticonductorParallelACDecision

@testset "multiconductor AC parallel decision comparison" begin
    source = solve_multiconductor_ac_formulation(:source)
    naive = solve_multiconductor_ac_formulation(:naive_aggregate)
    exact = solve_multiconductor_ac_formulation(:exact_lifted)
    for result in (source, naive, exact)
        @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
        @test result["current_balance_residual_pu"] <= 1.0e-7
        @test 0.70 - 1.0e-7 <= result["load_voltage_magnitude_pu"] <= 1.05 + 1.0e-7
    end
    @test exact["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test naive["objective_served_fraction"] > source["objective_served_fraction"] + 0.25
    @test maximum(member["magnitude_pu"] for line in source["member_currents"] for member in line) <= 0.600001
    @test maximum(member["magnitude_pu"] for line in exact["member_currents"] for member in line) <= 0.600001
    @test maximum(member["magnitude_pu"] for line in naive["member_currents"] for member in line) > 0.9

    closed_form = closed_form_current_limited_optima()
    @test source["objective_served_fraction"] ≈
        closed_form["source"]["objective_served_fraction"] atol=1.0e-7
    @test naive["objective_served_fraction"] ≈
        closed_form["naive_aggregate"]["objective_served_fraction"] atol=1.0e-7
    @test source["load_voltage_magnitude_pu"] ≈
        closed_form["source"]["load_voltage_magnitude_pu"] atol=1.0e-7
    @test closed_form["source"]["served_fraction_derivative_at_limit"] > 0
    @test closed_form["naive_aggregate"]["served_fraction_derivative_at_limit"] > 0

    certificate = multiconductor_ac_certificate()
    @test certificate["classification"] == "outer_relaxation"
    @test certificate["evidence"]["naive_served_fraction_gap"] > 0.25
    @test abs(certificate["evidence"]["exact_lifted_served_fraction_gap"]) <= 1.0e-7
    @test abs(certificate["evidence"]["source_solver_minus_closed_form"]) <= 1.0e-7
    @test abs(certificate["evidence"]["naive_solver_minus_closed_form"]) <= 1.0e-7
end

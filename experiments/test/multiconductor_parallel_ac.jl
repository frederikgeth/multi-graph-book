using Test

if !isdefined(@__MODULE__, :MulticonductorParallelACDecision)
    include(joinpath(@__DIR__, "..", "transformations", "MulticonductorParallelACDecision.jl"))
end
using .MulticonductorParallelACDecision

@testset "multiconductor AC parallel decision comparison" begin
    source = solve_multiconductor_ac_formulation(:source)
    naive = solve_multiconductor_ac_formulation(:naive_aggregate)
    exact = solve_multiconductor_ac_formulation(:exact_lifted)
    pruned = solve_multiconductor_ac_formulation(:exact_pruned)
    for result in (source, naive, exact, pruned)
        @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
        @test result["current_balance_residual_pu"] <= 1.0e-7
        @test 0.70 - 1.0e-7 <= result["load_voltage_magnitude_pu"] <= 1.05 + 1.0e-7
    end
    @test exact["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test pruned["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test naive["objective_served_fraction"] > source["objective_served_fraction"] + 0.25
    @test maximum(member["magnitude_pu"] for line in source["member_currents"] for member in line) <= 0.600001
    @test maximum(member["magnitude_pu"] for line in exact["member_currents"] for member in line) <= 0.600001
    @test maximum(member["magnitude_pu"] for line in pruned["member_currents"] for member in line) <= 0.600001
    @test maximum(member["magnitude_pu"] for member in pruned["member_currents"][2]) <= 0.060001
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

    redundancy = proportional_parallel_redundancy()
    @test redundancy["retained_member"] == 1
    @test redundancy["redundant_member"] == 2
    @test redundancy["current_map_ratio"]["real"] ≈ 0.1 atol=1.0e-12
    @test redundancy["current_map_ratio"]["imag"] ≈ 0.0 atol=1.0e-12
    @test redundancy["maximum_proportionality_residual"] <= 1.0e-12

    quadratic_redundancy = multiconductor_parallel_redundancy()
    @test quadratic_redundancy["certified"]
    @test quadratic_redundancy["required_terminal_ends"] == ["ij", "ji"]
    @test length(quadratic_redundancy["checks"]) == 4
    @test all(check["certified"] for check in quadratic_redundancy["checks"])

    certificate = multiconductor_ac_certificate()
    @test certificate["classification"] == "outer_relaxation"
    @test certificate["evidence"]["naive_served_fraction_gap"] > 0.25
    @test abs(certificate["evidence"]["exact_lifted_served_fraction_gap"]) <= 1.0e-7
    @test abs(certificate["evidence"]["exact_pruned_served_fraction_gap"]) <= 1.0e-7
    @test abs(certificate["evidence"]["source_solver_minus_closed_form"]) <= 1.0e-7
    @test abs(certificate["evidence"]["naive_solver_minus_closed_form"]) <= 1.0e-7
    @test certificate["evidence"]["certified_redundancy"]["certified"]
end

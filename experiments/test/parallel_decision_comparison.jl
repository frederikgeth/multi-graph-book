using Test

if !isdefined(@__MODULE__, :ParallelDecisionComparison)
    include(joinpath(@__DIR__, "..", "transformations", "ParallelDecisionComparison.jl"))
end
using .ParallelDecisionComparison

@testset "parallel decision comparison" begin
    source = solve_parallel_formulation(:source)
    naive = solve_parallel_formulation(:naive_aggregate)
    exact = solve_parallel_formulation(:exact_lifted)
    @test source["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test naive["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test exact["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test source["objective_MW"] ≈ 110.0 atol=1e-5
    @test source["angle_difference_rad"] ≈ 0.1 atol=1e-6
    @test naive["objective_MW"] ≈ 200.0 atol=1e-5
    @test naive["angle_difference_rad"] ≈ 2 / 11 atol=1e-6
    @test exact["objective_MW"] ≈ source["objective_MW"] atol=1e-5
    @test exact["angle_difference_rad"] ≈ source["angle_difference_rad"] atol=1e-6

    certificate = parallel_decision_certificate()
    @test certificate["classification"] == "outer_relaxation"
    @test certificate["evidence"]["naive_objective_gap_MW"] ≈ 90.0 atol=1e-5
    @test certificate["evidence"]["exact_lifted_objective_gap_MW"] ≈ 0.0 atol=1e-5
end

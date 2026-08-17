using Test

include(joinpath(@__DIR__, "..", "transformations", "NonlinearWardWitness.jl"))
using .NonlinearWardWitness

@testset "scoped nonlinear Ward witness" begin
    result = evaluate_nonlinear_witness()
    @test result.checks["base_residual_is_small"]
    @test result.checks["small_shift_is_locally_bounded"]
    @test result.checks["large_shift_exposes_nonlinear_residual"]
    @test result.checks["all_newton_solves_converged"]
    @test result.checks["has_local_feasible_case"]
    @test result.checks["has_local_ambiguous_case"]
    @test result.rows[1]["classification"] != "local_bound_ambiguous"
end

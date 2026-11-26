using LinearAlgebra
using Test

include(joinpath(@__DIR__, "..", "transformations", "RobustOptiKronWitness.jl"))
using .RobustOptiKronWitness

@testset "Robust versus scenario-certified Opti-KRON assignments" begin
    r = evaluate_witness()
    f = r.fixture
    # the linear model is LinDistFlow: K = shared path resistance
    @test r.K[4, 5] ≈ f.resistance[2] + f.resistance[3]
    @test r.K[1, :] == zeros(5)
    @test r.n_assignments > 1
    @test r.scenario_samples == ["heavy_uniform", "light_uniform"]
    # scenarios admit strictly fewer supernodes than the hull of the same data
    @test r.k_scen < r.k_hull ≤ r.k_box
    # hence every scenario-optimal assignment violates the bound at a training loading
    @test all(row["worst_scenario_error_over_bound"] ≤ 1 + 1e-9 for row in r.scenario_rows)
    @test all(row["worst_training_error_over_bound"] > 1 for row in r.scenario_rows)
    @test all(!isempty(row["violating_samples"]) for row in r.scenario_rows)
    # robust assignments hold at every training loading (and over the box set)
    @test all(row["worst_training_error_over_bound"] ≤ 1 + 1e-9 for row in r.robust_rows)
    @test all(row["worst_set_error_over_bound"] ≤ 1 + 1e-9 for row in r.robust_rows)
    # zero-injection Kron step is exact once injections are relocated
    @test r.kron_err ≤ 1e-12
end

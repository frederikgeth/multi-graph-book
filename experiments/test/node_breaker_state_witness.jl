using Test

include(joinpath(@__DIR__, "..", "transformations", "NodeBreakerStateWitness.jl"))
using .NodeBreakerStateWitness

@testset "node-breaker state and radiality witness" begin
    result = evaluate_node_breaker_states()
    @test all(values(result.checks))
    @test length(result.rows) == 4
    @test result.rows[end]["realization_count"] == 2
end

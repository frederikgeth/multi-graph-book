using Test

include(joinpath(@__DIR__, "..", "transformations", "GuardedParallelReductionWitness.jl"))
using .GuardedParallelReductionWitness

@testset "guarded singular and state-conditioned reduction witness" begin
    result = evaluate_guarded_witness()
    @test all(values(result.checks))
    @test result.singular_map["realified_rank"] < result.singular_map["realified_dimension"][1]
    @test result.jointly_retained["retained_member_count"] == 3
    @test result.jointly_retained["candidate_limit"] >= result.jointly_retained["exact_worst_case_magnitude"]
    @test result.state_conditioned["classification"] == "decision-conditioned map required"
end

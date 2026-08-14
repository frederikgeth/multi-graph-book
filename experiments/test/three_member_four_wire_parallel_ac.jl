using Test

include(joinpath(@__DIR__, "..", "transformations", "ThreeMemberFourWireParallelACDecision.jl"))
using .ThreeMemberFourWireParallelACDecision

@testset "three-member four-wire parallel AC joint pruning" begin
    data = three_member_data()
    certificate = three_member_joint_certificate(; data)
    @test certificate["certified"]
    @test certificate["retained_members"] == ["l1", "l2"]
    @test certificate["candidate_member"] == "l3"
    @test maximum(certificate["exact_worst_case_component_magnitudes"]) < 0.15

    source = solve_three_member_formulation(:source; data)
    pruned = solve_three_member_formulation(:exact_pruned; data)
    @test source["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test pruned["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test source["neutral_kcl_residual_pu"] ≤ 1.0e-7
    @test pruned["neutral_kcl_residual_pu"] ≤ 1.0e-7
    @test pruned["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test maximum(pruned["member_current_loading"][3]) < 1.0

    result = three_member_certificate()
    @test abs(result["objective_gap"]) ≤ 1.0e-7
    independent = result["independent_source_boundary"]
    @test independent["power_flow_residual"] ≤ 1.0e-9
    @test independent["bracket_width"] ≤ 1.0e-8
    @test abs(result["independent_source_objective_gap"]) ≤ 3.0e-8
end

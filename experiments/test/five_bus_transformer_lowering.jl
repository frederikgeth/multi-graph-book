using Test

if !isdefined(@__MODULE__, :FiveBusTransformerLowering)
    include(joinpath(@__DIR__, "..", "transformations", "FiveBusTransformerLowering.jl"))
end
using .FiveBusTransformerLowering

@testset "five-bus transformer lowering" begin
    result = five_bus_transformer_lowering_witness()
    @test result["all_checks_pass"]
    @test result["base_line_graph"]["member_cycle_rank"] == 3
    @test result["transformer_extension"]["local_views"]["port_factor_incidence"]["member_cycle_rank"] == 0
    @test result["transformer_extension"]["local_views"]["star_realization"]["member_cycle_rank"] == 0
    @test result["transformer_extension"]["local_views"]["terminal_clique"]["member_cycle_rank"] == 1
    @test result["embedded_views"]["compiled_star"]["member_cycle_rank"] == 5
    @test result["embedded_views"]["terminal_clique"]["member_cycle_rank"] == 6
    @test result["negative_star_arm_guard"]["minimum_star_reactance_ohm"] == -0.5
    @test result["negative_star_arm_guard"]["minimum_reference_reactance_eigenvalue_ohm"] == 0.5
    @test length(result["layers"]) == 5
    @test length(result["loss_ledger"]) == 4
end

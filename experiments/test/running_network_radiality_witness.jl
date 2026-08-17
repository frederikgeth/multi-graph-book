using Test

include(joinpath(@__DIR__, "..", "transformations", "RunningNetworkRadialityWitness.jl"))
using .RunningNetworkRadialityWitness

@testset "running network state radiality witness" begin
    result = evaluate_running_network_radiality()
    @test all(values(result.checks))
    @test length(result.rows) == 4
    @test result.rows[1]["analysis"]["terminal_object_count"] > 0
    @test result.checks["switch_state_changes_inventory"]
    @test result.checks["line_outage_changes_inventory"]
    @test result.checks["switch_open_excludes_switch_member"]
    @test result.checks["line_outage_excludes_l2_member"]
    @test result.checks["transformer_windings_remain_explicit"]
end

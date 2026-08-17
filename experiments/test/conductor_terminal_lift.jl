using Test

include(joinpath(@__DIR__, "..", "transformations", "ConductorTerminalLift.jl"))
using .ConductorTerminalLift

@testset "conductor-terminal incidence lift" begin
    result = evaluate_conductor_terminal_lift()
    @test all(values(result.checks))
    @test result.checks["transformer_is_multi_terminal"]
    @test result.switch_contracted["unknown"] === nothing
    @test result.checks["conductor_terminal_vertices_preserved"]
    @test result.checks["terminal_member_parallel_cycle_retained"]
    @test result.checks["state_conditioned_terminal_analysis_present"]
    @test result.checks["unknown_switch_terminal_state_is_unresolved"]
end

using Test

if !isdefined(@__MODULE__, :ConductorTerminalLift)
    include(joinpath(@__DIR__, "..", "transformations", "ConductorTerminalLift.jl"))
end
using .ConductorTerminalLift

@testset "five-bus scalar conductor-terminal lift" begin
    result = evaluate_five_bus_terminal_lift()
    @test all(values(result.checks))
    @test result.checks["scalar_line_factors_are_two_port"]
    @test length(result.junctions) == 5
    @test length(result.ports) == 14
    @test length(result.factors) == 7
    @test result.simple_projection["cycle_rank"] == 2
    @test result.source_fixture == "experiments/generated/five-bus-cycle-space-analysis.json"
end

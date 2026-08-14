using Test

if !isdefined(@__MODULE__, :ConductorTerminalLift)
    include(joinpath(@__DIR__, "..", "transformations", "ConductorTerminalLift.jl"))
end
using .ConductorTerminalLift

@testset "multiwinding contract conductor-terminal lift" begin
    result = evaluate_multiwinding_terminal_lift()
    @test all(values(result.checks))
    @test result.witness_id == "ARCH-CONDUCTOR-MULTI-001"
    @test length(result.ports) == 3
    @test result.ports[1]["terminal_order"] == ["a", "b", "c", "n"]
    @test result.ports[3]["terminal_order"] == ["a", "b", "c"]
    @test result.observations["internal_groundings"] == 1
end

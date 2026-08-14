using JSON3
using Test

if !isdefined(@__MODULE__, :RunningNetworkCycleSpace)
    include(joinpath(@__DIR__, "..", "transformations", "RunningNetworkCycleSpace.jl"))
end
using .RunningNetworkCycleSpace

@testset "running-network line-identity cycle space" begin
    path = joinpath(@__DIR__, "..", "..", "data", "running-network", "v0.1.0.json")
    result = running_network_cycle_analysis(JSON3.read(read(path, String)))
    @test result["witness_id"] == "GRAPH-CYCLE-RUNNING-001"
    @test result["line_order"] == ["l1", "l2", "l3", "l4"]
    @test result["cycle_rank"] == 1
    @test result["simple_cycle_rank"] == 0
    @test result["chord_ids"] == ["l2"]
    @test result["parallel_members"] == ["l1", "l2"]
    @test result["bridges"] == ["l3", "l4"]
    @test result["cycle_residual"] == 0
    @test result["excluded_assets"] == ["switch/w0", "transformer/n_winding"]
end

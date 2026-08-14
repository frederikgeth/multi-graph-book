using Test

if !isdefined(@__MODULE__, :ActiveRadiality)
    include(joinpath(@__DIR__, "..", "transformations", "ActiveRadiality.jl"))
end
using .ActiveRadiality

@testset "five-bus inventory and active radiality" begin
    result = five_bus_active_radiality_witness()
    @test result["all_checks_pass"]
    @test length(result["states"]) == 2
    inventory, tree = result["states"]
    @test inventory["member_cycle_rank"] == 3
    @test inventory["adjacency_cycle_rank"] == 2
    @test !inventory["member_radial"]
    @test tree["member_radial"]
    @test tree["adjacency_radial"]
    @test result["source_fixture"] == "experiments/generated/five-bus-cycle-space-analysis.json"
end

using Test

if !isdefined(@__MODULE__, :ActiveRadiality)
    include(joinpath(@__DIR__, "..", "transformations", "ActiveRadiality.jl"))
end
using .ActiveRadiality

@testset "active-state radiality" begin
    result = active_radiality_witness()
    @test result["inventory_adjacency_radial"]
    @test !result["inventory_member_radial"]
    @test result["active_adjacency_radial"]
    @test result["active_member_radial"]
    @test result["hidden_inventory_parallel_cycle"]
    @test result["active_state_is_tree"]
end

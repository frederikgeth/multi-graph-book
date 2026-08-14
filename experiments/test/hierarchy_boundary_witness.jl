using Test

include(joinpath(@__DIR__, "..", "transformations", "HierarchyBoundaryWitness.jl"))
using .HierarchyBoundaryWitness

@testset "hierarchy and boundary refinement witness" begin
    result = evaluate_hierarchy_boundary()
    @test all(values(result.checks))
    @test isempty(result.errors)
    @test result.state_cases["unknown"]["boundary_map_defined"] === false
    @test result.checks["hierarchy_is_acyclic_by_parent_chain"]
    @test result.checks["gluing_ports_are_declared"]
    @test result.checks["state_domain_is_explicit"]
end

using Test

if !isdefined(@__MODULE__, :TopologyProjectionWitness)
    include(joinpath(@__DIR__, "..", "transformations", "TopologyProjectionWitness.jl"))
end
using .TopologyProjectionWitness

@testset "two-level topology and nodal projection" begin
    result = topology_projection_witness()
    @test result["all_checks_pass"]
    @test Set(result["claim_ids"]) == Set([
        "ARCH-NODAL-001",
        "ARCH-SUPPORT-001",
        "ARCH-CHORDAL-001",
    ])

    parallel = result["parallel_split"]
    @test parallel["checks"]["splits_are_distinct"]
    @test parallel["checks"]["assembled_operators_are_bit_identical"]
    @test parallel["checks"]["consistency_test_is_attribution_blind"]
    @test parallel["base_normalized_frobenius_error"] == 0
    @test parallel["alternate_normalized_frobenius_error"] == 0

    chordal = result["radial_clique_support"]
    @test chordal["bus_graph"]["cycle_rank"] == 0
    @test chordal["structural_support_cycle_rank"] > 0
    @test chordal["perfect_elimination"]["fill_count"] == 0
    @test chordal["bad_elimination"]["fill_count"] > 0
end

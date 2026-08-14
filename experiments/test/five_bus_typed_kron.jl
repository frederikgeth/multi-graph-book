using Test

if !isdefined(@__MODULE__, :FiveBusTypedKronWitness)
    include(joinpath(@__DIR__, "..", "transformations", "FiveBusTypedKronWitness.jl"))
end
using .FiveBusTypedKronWitness

@testset "five-bus scalar typed Kron reduction" begin
    result = five_bus_typed_kron_witness()
    @test result["all_checks_pass"]
    @test result["eliminated_vertex"] == "m"
    @test result["eliminated_incident_members"] == ["x"]
    @test result["checks"]["reduced_matches_direct_leaf_deletion"]
    @test result["checks"]["boundary_current_recovery"]
    @test result["checks"]["full_nodal_residual_is_zero"]
    @test result["checks"]["non_pendant_internal_block_is_invertible"]
    @test result["checks"]["non_pendant_boundary_current_recovery"]
    @test result["checks"]["non_pendant_fill_jm_is_present"]
    @test result["checks"]["non_pendant_fill_km_is_present"]
    @test result["checks"]["recovered_line_x_current_is_exact"]
    @test result["checks"]["tight_line_x_limit_is_not_satisfied"]
    @test result["non_pendant_fill_edges"] == ["j-m", "k-m"]
    @test result["source_fixture"] == "experiments/generated/five-bus-cycle-space-analysis.json"
end

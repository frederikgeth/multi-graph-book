using Test

if !isdefined(@__MODULE__, :NodalRecoveryGuardsWitness)
    include(joinpath(@__DIR__, "..", "transformations", "NodalRecoveryGuardsWitness.jl"))
end
using .NodalRecoveryGuardsWitness

@testset "guarded nodal source recovery" begin
    result = nodal_recovery_guards_witness()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-RECOVERY-GUARDS-001"

    cases = result["cases"]
    @test cases["catalog_bounds"]["status"] == "bounded-non-identifiable"
    @test cases["catalog_bounds"]["checks"]["bounds_do_not_make_recovery_unique"]
    @test cases["member_current_measurement"]["status"] == "identifiable"
    @test cases["member_current_measurement"]["checks"]["member_measurement_lifts_parallel_ambiguity"]
    @test cases["grounding_declaration"]["status"] == "identifiable-with-declaration"
    @test cases["grounding_declaration"]["checks"]["declared_grounding_recovers_local_shunt"]
    @test cases["transformer_state_declaration"]["status"] == "identifiable-with-state"
    @test cases["transformer_state_declaration"]["checks"]["declared_tap_recovers_base_primitive"]
end

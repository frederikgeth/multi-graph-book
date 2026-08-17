using Test

if !isdefined(@__MODULE__, :MulticonductorRecoveryWitness)
    include(joinpath(@__DIR__, "..", "transformations", "MulticonductorRecoveryWitness.jl"))
end
using .MulticonductorRecoveryWitness

@testset "multiconductor source recovery" begin
    result = multiconductor_recovery_witness()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-RECOVERY-MULTI-001"

    cases = result["cases"]
    @test cases["full_rank_voltage_sweep"]["status"] == "identifiable"
    @test cases["full_rank_voltage_sweep"]["checks"]["factor_one_is_recovered"]
    @test cases["single_snapshot"]["status"] == "non-identifiable"
    @test cases["single_snapshot"]["checks"]["nonzero_reciprocal_ambiguity_annihilates_snapshot"]
    @test cases["phase_selective"]["status"] == "non-identifiable"
    @test cases["phase_selective"]["checks"]["unobserved_phase_currents_change"]
end

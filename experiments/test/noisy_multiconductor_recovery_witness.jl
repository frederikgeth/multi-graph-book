using Test

if !isdefined(@__MODULE__, :NoisyMulticonductorRecoveryWitness)
    include(joinpath(@__DIR__, "..", "transformations", "NoisyMulticonductorRecoveryWitness.jl"))
end
using .NoisyMulticonductorRecoveryWitness

@testset "noisy multiconductor source recovery" begin
    result = noisy_multiconductor_recovery_witness()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-RECOVERY-NOISE-001"
    @test result["well_conditioned"]["status"] == "bounded-uncertain"
    @test result["ill_conditioned"]["status"] == "bounded-uncertain"
    @test result["checks"]["ill_conditioning_amplifies_uncertainty"]
    @test result["well_conditioned"]["checks"]["estimate_respects_deterministic_error_bound"]
    @test result["ill_conditioned"]["checks"]["estimate_respects_deterministic_error_bound"]
end

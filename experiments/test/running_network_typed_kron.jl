using Test

include(joinpath(@__DIR__, "..", "transformations", "RunningNetworkTypedKronWitness.jl"))
using .RunningNetworkTypedKronWitness

@testset "running-network typed Kron witness" begin
    result = evaluate_running_network_typed_kron()
    @test result.witness_id == "TR-KRON-RUNNING-001"
    @test result.claim_id == "TR-KRON-001"
    @test all(values(result.checks))
    @test result.dimensions["retained_coordinates"] == 8
    @test result.dimensions["internal_coordinates"] == 4
    @test result.residuals["primitive"] ≤ 1.0e-11
    @test result.residuals["midpoint"] ≤ 1.0e-11
    @test result.checks["neutral_current_recovery_is_exact"]
    @test result.checks["neutral_limit_is_not_silently_dropped"]
    @test result.neutral_limit_witness["reduced_limit_constraint_evaluated"]
    @test result.checks["shunt_internal_block_is_invertible"]
    @test result.checks["neutral_shunt_recovery_kcl_is_exact"]
    @test result.checks["neutral_shunt_limit_is_evaluated"]
end

using Test

if !isdefined(@__MODULE__, :BalancedTransmissionWitness)
    include(joinpath(@__DIR__, "..", "transformations", "BalancedTransmissionWitness.jl"))
end
using .BalancedTransmissionWitness

@testset "balanced transmission collapse witness" begin
    witness = balanced_transmission_witness()
    @test witness["claim_id"] == "COLLAPSE-001"
    @test witness["all_checks_pass"]
    @test witness["checks"]["nominal_pi_shunts_included"]
    @test witness["residuals"]["phase_voltage_inf_norm"] <= 1.0e-10
    @test witness["residuals"]["positive_subspace_inf_norm"] <= 1.0e-10
    @test all(row["current_residual"] <= 1.0e-10 for row in witness["branches"])
end

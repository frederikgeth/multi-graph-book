using Test

include(joinpath(@__DIR__, "..", "transformations", "TransformerControlFamilyWitness.jl"))
using .TransformerControlFamilyWitness

@testset "transformer control family witness" begin
    result = evaluate_control_family()
    @test all(values(result.checks))
    @test length(result.rows) == 6
    @test result.rows[end]["classification"] == "tap-conditioned loss map required"
    @test result.checks["solver_backed_control_probes_solve"]
    @test result.checks["network_control_probes_solve"]
    @test all(row["solver_backed"] for row in result.rows)
    @test result.automatic_probe["solver_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test all(probe.status in ("LOCALLY_SOLVED", "OPTIMAL") for probe in values(result.network_probes))
end

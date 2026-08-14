using Test

if !isdefined(@__MODULE__, :NodalSourceRecoveryWitness)
    include(joinpath(@__DIR__, "..", "transformations", "NodalSourceRecoveryWitness.jl"))
end
using .NodalSourceRecoveryWitness

@testset "scoped nodal source recovery" begin
    result = nodal_source_recovery_witness()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-RECOVERY-001"

    classes = result["classes"]
    @test classes["support_separated"]["status"] == "identifiable"
    @test classes["support_separated"]["checks"]["off_diagonal_recovers_unique_factor"]
    @test classes["parallel_multiplicity"]["status"] == "non-identifiable"
    @test classes["parallel_multiplicity"]["checks"]["candidate_operators_are_identical"]
    @test classes["eliminated_coordinate"]["status"] == "non-identifiable"
    @test classes["eliminated_coordinate"]["checks"]["boundary_operator_matches_direct_factor"]
    @test classes["over_parameterized"]["status"] == "set-identifiable"
    @test classes["over_parameterized"]["checks"]["terminal_primitives_are_identical"]
end

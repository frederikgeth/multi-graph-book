using Test

if !isdefined(@__MODULE__, :MultiwindingTypedKronWitness)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingTypedKronWitness.jl"))
end
using .MultiwindingTypedKronWitness

@testset "multiwinding typed Kron witness" begin
    result = evaluate_multiwinding_typed_kron()
    @test all(values(result.checks))
    @test result.witness_id == "TR-KRON-MULTI-001"
    @test result.retained_terminal_order[end] == "x1/winding/2/n"
    @test result.eliminated_terminal_order == ["x1/winding/3/a", "x1/winding/3/b", "x1/winding/3/c"]
    @test result.residuals["internal_block_rank"] < result.residuals["internal_block_dimension"]
    @test result.reduced_admittance === nothing
    @test result.constraint_observation_ledger["eliminated_delta_coil_limit_count"] == 3
end

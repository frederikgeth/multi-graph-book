using Test

if !isdefined(@__MODULE__, :PositiveSequenceCollapse)
    include(joinpath(@__DIR__, "..", "transformations", "PositiveSequenceCollapse.jl"))
end
using .PositiveSequenceCollapse

@testset "positive-sequence collapse witness" begin
    witness = positive_sequence_witness()
    @test witness["claim_id"] == "COLLAPSE-002"
    @test witness["circulant"]["sequence_diagonal_residual"] <= 1.0e-12
    @test witness["circulant"]["positive_subspace_residual"] <= 1.0e-12
    @test witness["non_circulant_rejection"]["sequence_diagonal_residual"] > 1.0e-3
    @test witness["non_circulant_rejection"]["positive_subspace_residual"] > 1.0e-3
end

using Test

if !isdefined(@__MODULE__, :NarrowCircuitTransformations)
    include(joinpath(@__DIR__, "..", "transformations", "NarrowCircuitTransformations.jl"))
end
using .NarrowCircuitTransformations

@testset "narrow circuit transformations" begin
    star_delta = star_delta_witness()
    @test star_delta["floating_scalar_guards_hold"]
    @test star_delta["terminal_equivalence_holds"]
    @test star_delta["inverse_recovers_source"]

    grounded = grounded_star_guard_witness()
    @test !grounded["guards"]["floating_internal_node"]
    @test grounded["compiler_rejected"]
    @test grounded["grounding_asset_retained"]

    shunt = asymmetric_shunt_witness()
    @test shunt["endpoint_shunts_unequal"]
    @test shunt["off_diagonal_reciprocity_residual"] <= 1.0e-12
    @test shunt["adapter_must_report_loss"]
    @test !shunt["endpoint_asymmetry_is_nonreciprocity"]

    @test narrow_circuit_witnesses()["all_witnesses_pass"]
end

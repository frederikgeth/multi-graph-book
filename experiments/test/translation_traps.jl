using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :TranslationTraps)
    include(joinpath(@__DIR__, "..", "transformations", "TranslationTraps.jl"))
end
using .TranslationTraps

@testset "translation-trap witnesses" begin
    energization = energization_witness()
    @test energization["connected_in_asset_graph"]
    @test !energization["energized_in_active_graph"]
    @test energization["open_member"] == "line_bus_a_bus_b"

    symmetry = symmetry_witness()
    @test symmetry["complex_symmetric"]
    @test !symmetry["hermitian"]
    @test symmetry["hermitian_part_positive_semidefinite"]
    @test symmetry["hermitian_part_min_eigenvalue"] >= -1.0e-12

    ratings = terminal_rating_witness()
    @test ratings["terminal_magnitudes_differ"]
    @test ratings["from_terminal_exceeds_rating"] != ratings["to_terminal_exceeds_rating"]
    @test ratings["series_current_pu"] != ratings["from_terminal_current_pu"]
    @test ratings["series_current_pu"] != ratings["to_terminal_current_pu"]

    all_witnesses = translation_trap_witnesses()
    @test all_witnesses["all_witnesses_pass"]
end

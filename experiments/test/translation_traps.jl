using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :TranslationTraps)
    include(joinpath(@__DIR__, "..", "transformations", "TranslationTraps.jl"))
end
using .TranslationTraps

if !isdefined(@__MODULE__, :AntiPatternWitnesses)
    include(joinpath(@__DIR__, "..", "transformations", "AntiPatternWitnesses.jl"))
end
using .AntiPatternWitnesses

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

    anti_patterns = anti_pattern_witnesses()
    @test anti_patterns["all_witnesses_pass"]
    @test anti_patterns["heterogeneous_series_merge"]["accepted_behavioural_reduction"]
    @test !anti_patterns["heterogeneous_series_merge"]["homogeneous_line_class_preserved"]
    @test anti_patterns["external_grounding_absorption"]["compiler_rejected"]
    @test !anti_patterns["line_transformer_flattening"]["multi_terminal_incidence_preserved"]
    @test anti_patterns["bim_bfm_index_loss"]["aggregate_balance_holds"]
    @test !anti_patterns["bim_bfm_index_loss"]["member_consistency_holds"]
end

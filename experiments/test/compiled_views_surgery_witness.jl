using Test

include(joinpath(@__DIR__, "..", "transformations", "CompiledViewsSurgeryWitness.jl"))
using .CompiledViewsSurgeryWitness

@testset "compiled views and graph surgery witness" begin
    result = evaluate_compiled_views_surgery()
    @test result.all_checks_pass
    @test length(result.view_registry) == 6
    @test length(result.view_maps) == 4
    @test result.view_maps[end]["reverse_status"] == "partial_with_fibre"
    @test result.cases["nport_lowering"]["source_factor"]["factor_type"] == "multiwinding_transformer"
    @test result.cases["parallel_ideal_switches"]["diagnostic"] == "under_determined_duplicate_ideal_switches"
    @test result.cases["phase_only_switching"]["checks"]["neutral_connectivity_is_unchanged"]
    @test result.cases["zone_surgery"]["checks"]["unknown_state_returns_family"]
    @test result.cases["nterminal_surgery"]["checks"]["port_specific_state_is_retained"]
    @test result.cases["model_quality_diagnostics"]["checks"]["singular_map_is_reported"]
end

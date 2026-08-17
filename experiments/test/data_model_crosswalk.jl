using Test

include(joinpath(@__DIR__, "..", "transformations", "DataModelCrosswalk.jl"))
using .DataModelCrosswalk

@testset "version-pinned data-model crosswalk" begin
    result = evaluate_data_model_crosswalk()
    @test result.witness_id == "DATA-XWALK-001"
    @test result.claim_id == "DATA-XWALK-001"
    @test all(values(result.checks))
    @test length(result.profiles) == 4
    @test result.profiles[end]["ecosystem"] == "MATPOWER"
    @test result.profiles[end]["native_multi_terminal"] === false
    @test length(result.canonical.ratings) == 8
    @test length(result.canonical.terminals) == 8
end

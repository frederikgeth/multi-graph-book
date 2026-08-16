using Test

if !isdefined(@__MODULE__, :LayerLensApiWitness)
    include(joinpath(@__DIR__, "..", "transformations", "LayerLensApiWitness.jl"))
end
using .LayerLensApiWitness

@testset "layer-lens API crosswalk" begin
    result = evaluate_layer_lens_api()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-LENS-001"
    @test result["checks"]["source_data_api_has_assets_and_terminals"]
    @test result["checks"]["matrix_is_rectangular"]
    @test result["checks"]["direct_factor_to_equation_route_is_declared"]
    @test result["checks"]["ordinary_edge_route_is_optional"]
    @test result["checks"]["optimization_api_retains_decision_semantics"]
    @test result["checks"]["sparse_api_exposes_support_without_provenance"]
    @test result["checks"]["graph_learning_tensor_contract_is_explicit"]
    @test result["checks"]["support_graph_does_not_infer_asset_identity"]
    @test result["checks"]["decision_is_not_assigned_to_support_graph"]
    @test length(result["api_contracts"]) == 4
    @test result["api_contracts"][2]["status"] == "smoke_tested_without_solver"
    @test result["api_contracts"][4]["status"] == "package_independent_contract"
end

using Test
using GraphModelsForPowerNetworks

@testset "GraphModelsForPowerNetworks package" begin
    manifest = api_manifest()
    @test manifest["package"] == "GraphModelsForPowerNetworks"
    @test manifest["version"] == "0.1.0"
    exported = setdiff(Set(string.(names(GraphModelsForPowerNetworks; all=false))), Set(["GraphModelsForPowerNetworks"]))
    @test Set(manifest["stable_exports"]) == exported

    edge = IdentifiedEdge("l", "i", "j", 1.0)
    @test cycle_rank(["i", "j"], [edge]) == 0
    @test incidence_matrix(["i", "j"], [edge]) == [-1.0; 1.0;;]

    volts = UnitSpec(:V, :voltage)
    kilovolts = UnitSpec(:kV, :voltage; scale=1_000.0)
    @test convert_value(2.0, kilovolts, volts) == 2_000.0
    @test_throws ArgumentError convert_value(1.0, volts, UnitSpec(:A, :current))
    @test validate_state_space(running_state_space())["valid"] === true

    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => "TR-PKG-001",
        "rule_id" => "package_test",
        "classification" => "exact_normalization",
        "source" => Dict("model_category" => "source", "object_ids" => ["x"]),
        "target" => Dict("model_category" => "target", "object_ids" => ["x"]),
        "interfaces" => Dict(
            "state_variables" => Dict("source" => ["x"], "target" => ["x"], "relation" => "identity"),
            "constraints" => Dict("source" => ["c"], "target" => ["c"], "relation" => "identity"),
            "decisions" => Dict("source" => ["d"], "target" => ["d"], "relation" => "identity"),
            "objectives" => Dict("source" => ["o"], "target" => ["o"], "relation" => "identity"),
            "units" => Dict("source" => ["voltage"], "target" => ["voltage"], "relation" => "identity"),
            "boundary_quantities" => Dict("source" => ["v"], "target" => ["v"], "relation" => "identity"),
        ),
        "preconditions" => Any[],
        "preserves" => ["x"],
        "forgets" => Any[],
        "recovery_map" => Dict("available" => true, "description" => "identity"),
        "constraint_map" => Dict("mode" => "identity"),
        "provenance" => Dict("sources" => ["package test"]),
        "evidence" => Dict("tests" => ["package/GraphModelsForPowerNetworks/test/runtests.jl"]),
    )
    attached = attach_typed_interfaces(certificate)
    @test isempty(validate_certificate(attached))
    @test attached["typed_interfaces"]["state_space_ref"] == "experiments/generated/state-space-unit-witness.json"
end

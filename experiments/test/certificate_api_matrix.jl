using JSON3
using Test
import GraphModelsForPowerNetworks

const CERTIFICATE_ARTIFACTS = [
    "parallel-branch-certificate.json",
    "degree-two-series-certificate.json",
    "coordinate-normalization-certificate.json",
    "coordinate-series-composition-certificate.json",
    "parallel-opf-comparison.json",
    "transformer-winding-normalization-certificate.json",
    "multiwinding-leakage-compilation-certificate.json",
    "multiwinding-terminal-assembly-certificate.json",
    "transformer-factor-completion-certificate.json",
    "transformer-tap-decision-certificate.json",
    "transformer-tap-ac-decision-certificate.json",
    "transformer-tap-ac-independent-certificate.json",
    "multiconductor-parallel-ac-certificate.json",
    "four-wire-parallel-ac-certificate.json",
    "pi-four-wire-parallel-ac-certificate.json",
    "typed-kron-certificate.json",
]

@testset "typed certificate package matrix" begin
    root = normpath(joinpath(@__DIR__, "..", "generated"))
    for artifact in CERTIFICATE_ARTIFACTS
        certificate = JSON3.read(read(joinpath(root, artifact), String), Dict{String,Any})
        @test isempty(GraphModelsForPowerNetworks.validate_certificate(certificate))
        typed = certificate["typed_interfaces"]
        @test typed["state_space_ref"] == "experiments/generated/state-space-unit-witness.json"
        @test typed["unit_family_map"] isa AbstractDict
        @test typed["attachment_rule"] isa AbstractString
        raw = deepcopy(certificate)
        delete!(raw, "typed_interfaces")
        rebuilt = GraphModelsForPowerNetworks.attach_typed_interfaces(raw)
        rebuilt_typed = rebuilt["typed_interfaces"]
        @test rebuilt_typed["state_space_ref"] == typed["state_space_ref"]
        @test Set(rebuilt_typed["source_unit_families"]) == Set(typed["source_unit_families"])
        @test Set(rebuilt_typed["target_unit_families"]) == Set(typed["target_unit_families"])
    end
    matrix = JSON3.read(read(joinpath(root, "semantic-evaluator-matrix.json"), String), Dict{String,Any})
    @test matrix["witness_id"] == "PKG-SEMANTIC-001"
    @test matrix["valid"] === true
    @test length(matrix["rows"]) == length(CERTIFICATE_ARTIFACTS)
    @test all(row["valid"] === true for row in matrix["rows"])
    @test all(value === true for value in values(matrix["checks"]))
end

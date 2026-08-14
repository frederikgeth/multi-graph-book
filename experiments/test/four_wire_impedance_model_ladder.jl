using Test

if !isdefined(@__MODULE__, :FourWireImpedanceModelLadder)
    include(joinpath(@__DIR__, "..", "transformations", "FourWireImpedanceModelLadder.jl"))
end
using .FourWireImpedanceModelLadder

@testset "four-wire impedance model ladder" begin
    witness = four_wire_impedance_ladder()
    @test witness["witness_id"] == "IMPEDANCE-LADDER-001"
    @test witness["claim_id"] == "IMPEDANCE-LADDER-001"
    @test witness["all_checks_pass"]
    checks = witness["checks"]
    @test checks["source_matrix_is_complex_symmetric"]
    @test checks["source_matrix_is_not_hermitian"]
    @test checks["neutral_block_is_invertible"]
    @test checks["kron_phase_relation_is_defined"]
    @test checks["phase_neutral_current_is_recoverable"]
    @test checks["phase_neutral_drop_is_recovered"]
    @test checks["fortescue_transform_is_invertible"]
    @test checks["sequence_mixing_is_visible"]
    @test checks["positive_sequence_guard_is_required"]
    @test checks["shunt_deletion_changes_declared_factor"]
    @test checks["every_path_rule_has_risk_tags"]
    @test length(witness["transformation_path"]) == 7
    @test witness["transformation_path"][2]["rule"] == "K_n"
    @test witness["transformation_path"][2]["exactness"] == "guarded-exact"
    @test witness["transformation_path"][4]["exactness"] == "approximate"
    @test witness["transformation_path"][7]["exactness"] == "restricted-approximation"
    @test witness["checks"]["main_path_composes"]
    @test witness["checks"]["phase_to_neutral_branch_composes"]
    @test witness["path_compositions"]["main"]["preservation_status"] == "not-preserved"
    @test !isempty(witness["path_compositions"]["main"]["unresolved_guards"])
    @test isempty(witness["path_compositions"]["phase_to_neutral"]["findings"])
    broken = compose_path([
        Dict("rule" => "a", "source" => "x", "target" => "y", "exactness" => "exact-coordinate", "guards" => String[], "risk_tags" => String[], "forgets" => String[]),
        Dict("rule" => "b", "source" => "z", "target" => "q", "exactness" => "exact-coordinate", "guards" => String[], "risk_tags" => String[], "forgets" => String[]),
    ])
    @test !broken["composable"]
    @test "IMP-PATH-MISMATCH:1" in broken["findings"]
    @test witness["sample_observation"]["neutral_current_magnitude"] > 0.0
end

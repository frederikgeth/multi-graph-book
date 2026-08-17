using JSON3
using Test

include(joinpath(@__DIR__, "..", "transformations", "ImpedanceContract.jl"))
using .ImpedanceContract

const australian_artifact = joinpath(@__DIR__, "..", "generated", "australian-carson-reproduction.json")

@testset "Australian Carson reproduction artifact" begin
    @test isfile(australian_artifact)
    artifact = JSON3.read(read(australian_artifact, String))

    @test artifact["artifact_id"] == "AUSTRALIAN-CARSON-001"
    @test artifact["open_dss_settings"]["matrix_inputs_reused"] == false
    @test artifact["open_dss_settings"]["vminpu"] == 0
    @test artifact["open_dss_settings"]["vmaxpu"] == 2
    audit = artifact["source_inputs"]["audit"]
    @test audit["schema"]["version"] == "0.1.0"
    @test audit["case"]["overhead"]["reference_frequency_status"] == "inferred_from_probe"
    @test audit["case"]["underground"]["mapping_status"] == "unresolved"
    contract = artifact["impedance_contract"]
    @test contract["schema_id"] == "power-network-impedance"
    @test contract["schema_version"] == "0.1.0"
    @test isempty(validate_impedance_contract(contract))
    @test all(length(element["terminals"]) == 4 for element in contract["elements"])
    @test all(element["limits"]["ampacity_a"] == 400 for element in contract["elements"])
    @test all(element["grounding"]["model"] == "external_grounding_reactor" for element in contract["elements"])
    @test all(element["provenance"]["field_status"]["reference_alignment"] !== nothing for element in contract["elements"])

    overhead = artifact["cases"]["overhead"]
    @test overhead["reference_case"]["matrix_used_as_input"] == false
    overhead_probe = overhead["reference_case"]["frequency_probe"]
    @test overhead_probe[2]["frequency_hz"] == 60
    @test overhead_probe[2]["permutation"] == [4, 1, 2, 3]
    @test overhead_probe[2]["permuted_max_series_error_ohm_per_km"] < 1.0e-3
    @test overhead["cases"]["source_veryunbalanced"]["solve"]["converged"]
    @test all(v > 1.0 for v in overhead["cases"]["source_veryunbalanced"]["voltage_magnitudes_v"])
    @test overhead["cases"]["source_veryunbalanced"]["independent_reference"]["converged"]
    @test overhead["cases"]["source_veryunbalanced"]["independent_reference"]["crosscheck_status"] == "agreement"
    @test overhead["cases"]["source_veryunbalanced"]["independent_reference"]["complex_line_loss_error_va"] < 1.0

    underground = artifact["cases"]["underground"]
    @test underground["reference_case"]["matrix_used_as_input"] == false
    @test underground["reference_case"]["series_reference_ohm_per_km"] !== nothing
    underground_probe = underground["reference_case"]["frequency_probe"]
    @test underground_probe[2]["permuted_max_series_error_ohm_per_km"] > underground_probe[1]["permuted_max_series_error_ohm_per_km"]
    @test occursin("mapping not present", lowercase(String(artifact["underground_mapping_note"])))
    @test all(underground["cases"][name]["solve"]["converged"] for name in ("balanced", "unbalanced", "veryunbalanced"))
    @test all(underground["cases"][name]["independent_reference"]["converged"] for name in ("balanced", "unbalanced", "veryunbalanced"))
    @test all(underground["cases"][name]["independent_reference"]["crosscheck_status"] == "agreement" for name in ("balanced", "unbalanced", "veryunbalanced"))
    @test underground["cases"]["balanced"]["independent_reference"]["max_voltage_magnitude_error_v"] < 0.1
    @test underground["cases"]["balanced"]["independent_reference"]["complex_line_loss_error_va"] < 1.0
    @test underground["cases"]["unbalanced"]["independent_reference"]["complex_loss_error_va"] > 100.0
    @test underground["cases"]["balanced_low_grounding"]["independent_reference"]["crosscheck_status"] == "agreement"
    @test underground["cases"]["balanced_high_grounding"]["independent_reference"]["crosscheck_status"] == "agreement"
    @test underground["cases"]["balanced_low_grounding"]["independent_reference"]["grounding_impedance_ohm"]["re"] == 0.01
    @test underground["cases"]["balanced_low_grounding"]["independent_reference"]["grounding_impedance_ohm"]["im"] == 0.001
    @test underground["cases"]["balanced_low_grounding"]["voltage_magnitudes_v"][4] < underground["cases"]["balanced_high_grounding"]["voltage_magnitudes_v"][4]
end

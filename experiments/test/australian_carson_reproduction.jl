using JSON3
using Test

const australian_artifact = joinpath(@__DIR__, "..", "generated", "australian-carson-reproduction.json")

@testset "Australian Carson reproduction artifact" begin
    @test isfile(australian_artifact)
    artifact = JSON3.read(read(australian_artifact, String))

    @test artifact["artifact_id"] == "AUSTRALIAN-CARSON-001"
    @test artifact["open_dss_settings"]["matrix_inputs_reused"] == false
    @test artifact["open_dss_settings"]["vminpu"] == 0
    @test artifact["open_dss_settings"]["vmaxpu"] == 2

    overhead = artifact["cases"]["overhead"]
    @test overhead["reference_case"]["matrix_used_as_input"] == false
    overhead_probe = overhead["reference_case"]["frequency_probe"]
    @test overhead_probe[2]["frequency_hz"] == 60
    @test overhead_probe[2]["permutation"] == [4, 1, 2, 3]
    @test overhead_probe[2]["permuted_max_series_error_ohm_per_km"] < 1.0e-3
    @test overhead["cases"]["source_veryunbalanced"]["solve"]["converged"]
    @test all(v > 1.0 for v in overhead["cases"]["source_veryunbalanced"]["voltage_magnitudes_v"])

    underground = artifact["cases"]["underground"]
    @test underground["reference_case"]["matrix_used_as_input"] == false
    @test underground["reference_case"]["series_reference_ohm_per_km"] !== nothing
    underground_probe = underground["reference_case"]["frequency_probe"]
    @test underground_probe[2]["permuted_max_series_error_ohm_per_km"] > underground_probe[1]["permuted_max_series_error_ohm_per_km"]
    @test occursin("mapping not present", lowercase(String(artifact["underground_mapping_note"])))
    @test all(underground["cases"][name]["solve"]["converged"] for name in ("balanced", "unbalanced", "veryunbalanced"))
end

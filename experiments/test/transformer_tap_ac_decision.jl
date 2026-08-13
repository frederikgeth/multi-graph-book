using Test

if !isdefined(@__MODULE__, :CoordinateActions)
    include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
end
if !isdefined(@__MODULE__, :TransformerWindingNormalization)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerWindingNormalization.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingLeakageCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingLeakageCompilation.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingTerminalAssembly)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingTerminalAssembly.jl"))
end
if !isdefined(@__MODULE__, :TransformerFactorCompletion)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerFactorCompletion.jl"))
end
if !isdefined(@__MODULE__, :TransformerTapDecisionCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerTapDecisionCompilation.jl"))
end
if !isdefined(@__MODULE__, :TransformerTapACDecision)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerTapACDecision.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .TransformerTapACDecision
using .TransformationContracts

@testset "solver-backed transformer tap AC network decision" begin
    case = load_transformer_tap_ac_case()
    @test length(case.factor.start_snapshot.qualified_terminal_labels) == 11
    @test only(case.factor.decisions).positions == [0.95, 1.0, 1.05]

    comparison = solve_transformer_tap_ac_decision(case)
    source = comparison["source_subproblems"]
    target = comparison["parameterized_target_subproblems"]
    @test length(source) == length(target) == 3
    for (source_result, target_result) in zip(source, target)
        for result in (source_result, target_result)
            @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
            @test result["secondary_neutral_kcl_residual_A"] <= 1.0e-7
            @test result["tertiary_kcl_residual_A"] <= 1.0e-7
            @test result["phase_power_balance_residual_MVA"] <= 1.0e-8
            @test result["delta_common_mode_voltage_pu"] <= 1.0e-8
            @test result["maximum_leakage_current_loading"] <= 1.0 + 1.0e-7
            @test all(0.90 - 1.0e-7 .<=
                      result["secondary_phase_to_neutral_voltage_pu"] .<= 1.05 + 1.0e-7)
            @test result["model_size"] == Dict("variables" => 15, "constraints" => 30)
        end
        @test source_result["tap_value"] == target_result["tap_value"]
        @test source_result["objective_served_fraction"] ≈
              target_result["objective_served_fraction"] atol=1.0e-9
        @test source_result["secondary_phase_to_neutral_voltage_pu"] ≈
              target_result["secondary_phase_to_neutral_voltage_pu"] atol=1.0e-9
        @test source_result["leakage_current_magnitude_A"] ≈
              target_result["leakage_current_magnitude_A"] atol=1.0e-6
        @test [record["real"] for record in source_result["terminal_voltage"]] ≈
              [record["real"] for record in target_result["terminal_voltage"]] atol=1.0e-8
        @test [record["imag"] for record in source_result["terminal_voltage"]] ≈
              [record["imag"] for record in target_result["terminal_voltage"]] atol=1.0e-8
    end
    @test all(
        difference["maximum_terminal_admittance_difference_S"] == 0.0 &&
        difference["maximum_leakage_current_map_difference_S"] == 0.0
        for difference in comparison["pointwise_factor_differences"]
    )

    optimum = comparison["parameterized_target_optimum"]
    frozen = comparison["frozen_start_solution"]
    @test optimum["tap_value"] == comparison["source_optimum"]["tap_value"] == 0.95
    @test optimum["objective_served_fraction"] ≈ 1.2305865271 atol=1.0e-7
    @test frozen["tap_value"] == 1.0
    @test frozen["objective_served_fraction"] ≈ 1.1704738810 atol=1.0e-7
    @test comparison["frozen_start_objective_gap"] > 0.060
    @test abs(comparison["source_target_objective_gap"]) <= 1.0e-9
    @test optimum["maximum_leakage_current_loading"] ≈ 1.0 atol=1.0e-7

    certificate = transformer_tap_ac_certificate()
    @test certificate["certificate_id"] == "TR-XFMR-006"
    @test certificate["classification"] == "exact_compilation"
    @test isempty(certificate["forgets"])
    @test isempty(validate_certificate(certificate))
    @test certificate["evidence"]["parameterized_target_optimum"]["tap_value"] == 0.95
    @test certificate["evidence"]["frozen_start_objective_gap"] > 0.060
end

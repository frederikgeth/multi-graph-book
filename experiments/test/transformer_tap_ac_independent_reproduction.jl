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
if !isdefined(@__MODULE__, :TransformerTapACIndependentReproduction)
    include(joinpath(
        @__DIR__, "..", "transformations", "TransformerTapACIndependentReproduction.jl",
    ))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .TransformerTapACDecision
using .TransformerTapACIndependentReproduction
using .TransformationContracts

@testset "independent transformer tap AC reproduction" begin
    case = load_transformer_tap_ac_case()
    reproduction = reproduce_transformer_tap_decision(case)
    @test reproduction isa Dict
    @test reproduction["positions"] == [0.95, 1.0, 1.05]
    @test reproduction["optimum"]["tap_value"] == 0.95

    expected = Dict(0.95 => 1.2305865271, 1.0 => 1.1704738810, 1.05 => 1.1159503679)
    for result in reproduction["tap_results"]
        @test result["served_fraction"] ≈ expected[result["tap_value"]] atol=1.0e-7
        @test result["maximum_scaled_equality_residual"] <= 1.0e-9
        @test result["maximum_constraint_violation"] <= 1.1e-10
        @test result["maximum_leakage_current_loading"] ≈ 1.0 atol=1.0e-8
        @test result["secondary_neutral_kcl_residual_A"] <= 1.0e-7
        @test result["tertiary_kcl_residual_A"] <= 1.0e-7
        @test result["delta_common_mode_voltage_pu"] <= 1.0e-9
        @test result["upper_infeasible_served_fraction"] - result["served_fraction"] <=
              1.1e-10
        @test result["scanned_points"] > 1
        @test result["bisection_iterations"] > 1
        @test result["total_newton_iterations"] > 0
        @test result["total_residual_evaluations"] > result["total_newton_iterations"]
    end

    alternate_scan = reproduce_transformer_tap_decision(case; scan_step=0.08)
    @test alternate_scan isa Dict
    @test alternate_scan["optimum"]["tap_value"] == 0.95
    @test [result["served_fraction"] for result in alternate_scan["tap_results"]] ≈
          [result["served_fraction"] for result in reproduction["tap_results"]] atol=2.0e-10

    unbracketed = solve_independent_tap_boundary(case, 0.95; scan_maximum=1.0)
    @test unbracketed isa IndependentReproductionRejection
    @test unbracketed.failed_guard ==
          "continuation_scan_did_not_bracket_upper_feasibility_boundary"

    impossible_voltage_case = TransformerTapACCase(
        case.factor,
        case.source_completion,
        case.terminal_voltage_base_V,
        case.slack_voltage_V,
        case.load_direction_MVA_per_phase,
        (1.10, 1.11),
    )
    no_feasible_point = solve_independent_tap_boundary(impossible_voltage_case, 0.95)
    @test no_feasible_point isa IndependentReproductionRejection
    @test no_feasible_point.failed_guard == "continuation_scan_found_no_feasible_point"

    certificate = independent_transformer_tap_certificate(case)
    @test certificate["certificate_id"] == "TR-XFMR-007"
    @test certificate["classification"] == "mixed"
    @test isempty(certificate["forgets"])
    @test isempty(validate_certificate(certificate))
    comparison = certificate["evidence"]["ipopt_comparison"]
    @test comparison["independent_optimal_tap"] == comparison["ipopt_optimal_tap"] == 0.95
    @test comparison["maximum_absolute_served_fraction_difference"] <= 1.0e-9
    @test comparison["maximum_secondary_voltage_difference_pu"] <= 1.0e-9
    @test comparison["maximum_leakage_current_difference_A"] <= 1.0e-5

    three_scenario = reproduce_transformer_tap_three_scenario_decision(case)
    @test three_scenario.branch_count == 27
    @test three_scenario.branch_completeness
    @test length(three_scenario.scenario_results) == 3
    @test all(length(result["tap_results"]) == 3 for result in three_scenario.scenario_results)
    @test three_scenario.selected_branch["scenario_taps"] == [0.95, 0.95, 0.95]

    three_certificate = independent_transformer_tap_three_scenario_certificate(case)
    @test three_certificate["certificate_id"] == "TR-XFMR-009-REPRO"
    @test three_certificate["classification"] == "mixed"
    @test isempty(three_certificate["forgets"])
    @test isempty(validate_certificate(three_certificate))
    @test three_certificate["evidence"]["ipopt_branch_count"] == 27
    @test three_certificate["evidence"]["selected_path_matches"]
    @test three_certificate["evidence"]["maximum_absolute_net_objective_difference"] <= 1.0e-8
    @test three_certificate["evidence"]["operation_limited_selected_path_matches"]
    @test three_certificate["evidence"]["operation_limited_ipopt_branch_count"] == 15
    @test three_certificate["evidence"]["operation_limited_maximum_absolute_net_objective_difference"] <= 1.0e-8
end

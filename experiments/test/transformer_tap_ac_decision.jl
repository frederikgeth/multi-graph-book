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

    switching = solve_transformer_tap_ac_switching_decision(case)
    @test switching.branch_count == 9
    @test switching.branch_completeness
    @test length(switching.branches) == switching.branch_count
    @test switching.selected_branch["net_objective"] ≈
          maximum(branch["net_objective"] for branch in switching.branches)
    @test switching.selected_branch["scenario_1_tap"] in switching.positions
    @test switching.selected_branch["scenario_2_tap"] in switching.positions
    @test switching.cost_sweep_branch_complete
    @test length(switching.cost_sweep) == 5
    @test all(row["branch_count"] == 9 for row in switching.cost_sweep)
    @test all(pair == (0.95, 0.95) for pair in switching.cost_sweep_selected_pairs)
    @test switching.positive_breakpoint_count > 0
    @test length(switching.positive_breakpoints) == switching.positive_breakpoint_count
    @test issorted([row["switching_cost"] for row in switching.positive_breakpoints])

    unbalanced = solve_transformer_tap_ac_unbalanced_switching_decision(case)
    @test unbalanced.branch_count == 9
    @test unbalanced.branch_completeness
    @test unbalanced.cost_sweep_branch_complete
    @test length(unbalanced.scenario_phase_scale) == 3
    @test length(unbalanced.scenario_1_phase_directions) == 3
    @test length(unbalanced.scenario_2_phase_directions) == 3
    @test any(
        abs(unbalanced.scenario_1_phase_directions[i] -
            unbalanced.scenario_2_phase_directions[i]) > 1.0e-12
        for i in 1:3
    )
    @test unbalanced.selected_branch["scenario_1_tap"] in unbalanced.positions
    @test unbalanced.selected_branch["scenario_2_tap"] in unbalanced.positions

    certificate = transformer_tap_ac_certificate()
    @test certificate["certificate_id"] == "TR-XFMR-006"
    @test certificate["classification"] == "exact_compilation"
    @test isempty(certificate["forgets"])
    @test isempty(validate_certificate(certificate))
    @test certificate["evidence"]["parameterized_target_optimum"]["tap_value"] == 0.95
    @test certificate["evidence"]["frozen_start_objective_gap"] > 0.060
    @test certificate["evidence"]["switching_decision"].branch_completeness
    @test certificate["evidence"]["switching_decision"].cost_sweep_branch_complete
    @test certificate["evidence"]["switching_decision"].positive_breakpoint_count > 0
    @test certificate["evidence"]["unbalanced_switching_decision"].branch_completeness
    @test certificate["evidence"]["unbalanced_switching_decision"].cost_sweep_branch_complete

    three_scenario = solve_transformer_tap_ac_three_scenario_decision(case)
    @test three_scenario.branch_count == 27
    @test three_scenario.branch_completeness
    @test three_scenario.cost_sweep_branch_complete
    @test length(three_scenario.scenario_phase_scales) == 3
    @test length(three_scenario.selected_branch["scenario_taps"]) == 3
    @test three_scenario.selected_branch["net_objective"] ≈
          maximum(branch["net_objective"] for branch in three_scenario.branches)
    @test certificate["evidence"]["three_scenario_decision"].branch_completeness
    @test certificate["evidence"]["three_scenario_decision"].branch_count == 27
    limited = certificate["evidence"]["operation_limited_three_scenario_decision"]
    @test limited.max_tap_operations == 1
    @test limited.branch_count == 27
    @test limited.admissible_branch_count == 15
    @test limited.branch_completeness
    @test limited.cost_sweep_branch_complete
    @test limited.selected_branch["tap_operations"] <= 1
end

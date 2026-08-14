module TransformerTapACIndependentReproduction

using LinearAlgebra

using ..TransformerFactorCompletion: TransformerCompletionResult
using ..TransformerTapACDecision: TransformerTapACCase,
                                         solve_transformer_tap_ac_decision,
                                         solve_transformer_tap_ac_three_scenario_decision
using ..TransformerTapDecisionCompilation: evaluate_parameterized_transformer

export IndependentReproductionRejection,
       independent_transformer_tap_certificate,
       independent_transformer_tap_three_scenario_certificate,
       reproduce_transformer_tap_decision,
       reproduce_transformer_tap_three_scenario_decision,
       solve_independent_tap_boundary,
       solve_independent_transformer_power_flow

const TAP_DECISION_ID = "tap/x1/winding/2"

struct IndependentReproductionRejection
    tap_value::Float64
    failed_guard::String
    evidence::Dict{String,Any}
end

function evaluated_snapshot(case::TransformerTapACCase, tap)
    snapshot = evaluate_parameterized_transformer(
        case.factor, Dict(TAP_DECISION_ID => Float64(tap)),
    )
    snapshot isa TransformerCompletionResult ||
        throw(ArgumentError("tap does not evaluate to a fixed transformer snapshot"))
    snapshot
end

function no_load_state(snapshot, case)
    admittance = snapshot.terminal_admittance
    unknown_block = admittance[5:11, 5:11]
    rhs = -admittance[5:11, 1:4] * case.slack_voltage_V
    gauge = zeros(ComplexF64, 1, 7)
    gauge[1, 5:7] .= 1
    augmented = [unknown_block transpose(conj(gauge)); gauge zeros(ComplexF64, 1, 1)]
    voltage = (augmented \ vcat(rhs, 0.0 + 0.0im))[1:7]
    normalized = voltage ./ case.terminal_voltage_base_V[5:11]
    vcat(real.(normalized), imag.(normalized))
end

function physical_voltage(case, state)
    length(state) == 14 || throw(ArgumentError("independent state must have 14 entries"))
    normalized = state[1:7] .+ im .* state[8:14]
    ComplexF64[case.slack_voltage_V;
               case.terminal_voltage_base_V[5:11] .* normalized]
end

"Fourteen scaled real residuals for the tap-conditioned network power flow."
function power_flow_residual(state, snapshot, case, served_fraction)
    voltage = physical_voltage(case, state)
    current = snapshot.terminal_admittance * voltage
    residual = Float64[]
    for phase in 5:7
        phase_voltage = voltage[phase] - voltage[8]
        load_power = -phase_voltage * conj(current[phase]) / 1.0e6
        mismatch = load_power - served_fraction * case.load_direction_MVA_per_phase[phase - 4]
        push!(residual, real(mismatch), imag(mismatch))
    end
    neutral_mismatch = sum(current[5:8]) / maximum(snapshot.leakage_current_limit[4:6])
    push!(residual, real(neutral_mismatch), imag(neutral_mismatch))
    tertiary_scale = maximum(snapshot.leakage_current_limit[7:9])
    for terminal in 9:10
        mismatch = current[terminal] / tertiary_scale
        push!(residual, real(mismatch), imag(mismatch))
    end
    delta_common_mode = sum(
        voltage[9:11] ./ case.terminal_voltage_base_V[9:11]
    )
    push!(residual, real(delta_common_mode), imag(delta_common_mode))
    residual
end

function finite_difference_jacobian(residual_function, state; step=1.0e-6)
    n = length(state)
    jacobian = Matrix{Float64}(undef, n, n)
    for column in 1:n
        increment = step * max(1.0, abs(state[column]))
        upper = copy(state)
        lower = copy(state)
        upper[column] += increment
        lower[column] -= increment
        jacobian[:, column] .=
            (residual_function(upper) .- residual_function(lower)) ./ (2increment)
    end
    jacobian
end

"Solve a fixed-load power flow with a damped finite-difference Newton method."
function solve_independent_transformer_power_flow(
    snapshot::TransformerCompletionResult,
    case::TransformerTapACCase,
    served_fraction::Real;
    start_state=no_load_state(snapshot, case),
    residual_tolerance=1.0e-10,
    maximum_iterations=30,
)
    state = Float64.(start_state)
    residual_function = candidate ->
        power_flow_residual(candidate, snapshot, case, Float64(served_fraction))
    residual_evaluations = 0
    for iteration in 0:maximum_iterations
        residual = residual_function(state)
        residual_evaluations += 1
        residual_norm = norm(residual, Inf)
        if residual_norm <= residual_tolerance
            return Dict{String,Any}(
                "converged" => true,
                "served_fraction" => Float64(served_fraction),
                "state" => state,
                "iterations" => iteration,
                "residual_evaluations" => residual_evaluations,
                "maximum_scaled_equality_residual" => residual_norm,
            )
        end
        iteration == maximum_iterations && break
        jacobian = finite_difference_jacobian(residual_function, state)
        residual_evaluations += 2length(state)
        step = try
            -(jacobian \ residual)
        catch
            return Dict{String,Any}(
                "converged" => false,
                "served_fraction" => Float64(served_fraction),
                "state" => state,
                "iterations" => iteration,
                "residual_evaluations" => residual_evaluations,
                "maximum_scaled_equality_residual" => residual_norm,
                "failure" => "finite_difference_jacobian_is_singular",
            )
        end
        accepted = false
        damping = 1.0
        while damping >= 2.0^-16
            candidate = state .+ damping .* step
            candidate_residual = residual_function(candidate)
            residual_evaluations += 1
            if norm(candidate_residual, Inf) < residual_norm
                state = candidate
                accepted = true
                break
            end
            damping /= 2
        end
        accepted || return Dict{String,Any}(
            "converged" => false,
            "served_fraction" => Float64(served_fraction),
            "state" => state,
            "iterations" => iteration,
            "residual_evaluations" => residual_evaluations,
            "maximum_scaled_equality_residual" => residual_norm,
            "failure" => "damped_newton_line_search_failed",
        )
    end
    final_residual = norm(residual_function(state), Inf)
    Dict{String,Any}(
        "converged" => false,
        "served_fraction" => Float64(served_fraction),
        "state" => state,
        "iterations" => maximum_iterations,
        "residual_evaluations" => residual_evaluations + 1,
        "maximum_scaled_equality_residual" => final_residual,
        "failure" => "maximum_newton_iterations_reached",
    )
end

function state_metrics(snapshot, case, power_flow)
    voltage = physical_voltage(case, power_flow["state"])
    terminal_current = snapshot.terminal_admittance * voltage
    leakage_current = snapshot.winding_leakage_current_map * voltage
    secondary_voltage_pu = abs.(voltage[5:7] .- voltage[8]) ./
                           case.terminal_voltage_base_V[5:7]
    lower, upper = case.secondary_voltage_bounds_pu
    current_loading = abs.(leakage_current) ./ snapshot.leakage_current_limit
    violations = vcat(
        current_loading .- 1,
        lower .- secondary_voltage_pu,
        secondary_voltage_pu .- upper,
    )
    Dict{String,Any}(
        "served_fraction" => power_flow["served_fraction"],
        "converged" => power_flow["converged"],
        "state" => power_flow["state"],
        "newton_iterations" => power_flow["iterations"],
        "residual_evaluations" => power_flow["residual_evaluations"],
        "maximum_scaled_equality_residual" =>
            power_flow["maximum_scaled_equality_residual"],
        "secondary_phase_to_neutral_voltage_pu" => secondary_voltage_pu,
        "leakage_current_magnitude_A" => abs.(leakage_current),
        "leakage_current_limit_A" => snapshot.leakage_current_limit,
        "maximum_leakage_current_loading" => maximum(current_loading),
        "maximum_constraint_violation" => max(0.0, maximum(violations)),
        "terminal_voltage_real_V" => real.(voltage),
        "terminal_voltage_imag_V" => imag.(voltage),
        "secondary_neutral_kcl_residual_A" => abs(sum(terminal_current[5:8])),
        "tertiary_kcl_residual_A" => maximum(abs.(terminal_current[9:11])),
        "delta_common_mode_voltage_pu" => abs(sum(
            voltage[9:11] ./ case.terminal_voltage_base_V[9:11]
        )),
    )
end

function rejection(tap, guard; evidence=Dict{String,Any}())
    IndependentReproductionRejection(
        Float64(tap), String(guard), Dict{String,Any}(evidence),
    )
end

"""
Trace one tap's high-voltage branch and locate its upper feasible boundary.

The scan must encounter a feasible point and then a converged infeasible point.
The latter guard prevents a truncated scan from being mislabeled as an optimum.
"""
function solve_independent_tap_boundary(
    case::TransformerTapACCase,
    tap::Real;
    scan_step=0.05,
    scan_maximum=1.60,
    boundary_tolerance=1.0e-10,
    feasibility_tolerance=1.0e-10,
)
    scan_step > 0 || throw(ArgumentError("scan_step must be positive"))
    scan_maximum > 0 || throw(ArgumentError("scan_maximum must be positive"))
    snapshot = evaluated_snapshot(case, tap)
    state = no_load_state(snapshot, case)
    last_feasible = nothing
    first_upper_infeasible = nothing
    scanned_points = 0
    total_newton_iterations = 0
    total_residual_evaluations = 0
    for served_fraction in 0.0:scan_step:scan_maximum
        power_flow = solve_independent_transformer_power_flow(
            snapshot, case, served_fraction; start_state=state,
        )
        scanned_points += 1
        total_newton_iterations += power_flow["iterations"]
        total_residual_evaluations += power_flow["residual_evaluations"]
        power_flow["converged"] || return rejection(
            tap, "continuation_power_flow_did_not_converge";
            evidence=Dict(
                "served_fraction" => served_fraction,
                "failure" => get(power_flow, "failure", "unknown"),
            ),
        )
        state = power_flow["state"]
        metrics = state_metrics(snapshot, case, power_flow)
        feasible = metrics["maximum_constraint_violation"] <= feasibility_tolerance
        if feasible
            last_feasible = metrics
        elseif last_feasible !== nothing
            first_upper_infeasible = metrics
            break
        end
    end
    last_feasible === nothing && return rejection(
        tap, "continuation_scan_found_no_feasible_point";
        evidence=Dict("scan_step" => scan_step, "scan_maximum" => scan_maximum),
    )
    first_upper_infeasible === nothing && return rejection(
        tap, "continuation_scan_did_not_bracket_upper_feasibility_boundary";
        evidence=Dict(
            "last_feasible_served_fraction" => last_feasible["served_fraction"],
            "scan_step" => scan_step,
            "scan_maximum" => scan_maximum,
        ),
    )

    lower = last_feasible
    upper = first_upper_infeasible
    bisection_iterations = 0
    while upper["served_fraction"] - lower["served_fraction"] > boundary_tolerance
        bisection_iterations += 1
        midpoint = (lower["served_fraction"] + upper["served_fraction"]) / 2
        interpolation = (midpoint - lower["served_fraction"]) /
                        (upper["served_fraction"] - lower["served_fraction"])
        start_state = lower["state"] .+ interpolation .* (upper["state"] .- lower["state"])
        power_flow = solve_independent_transformer_power_flow(
            snapshot, case, midpoint; start_state=start_state,
        )
        total_newton_iterations += power_flow["iterations"]
        total_residual_evaluations += power_flow["residual_evaluations"]
        power_flow["converged"] || return rejection(
            tap, "boundary_power_flow_did_not_converge";
            evidence=Dict("served_fraction" => midpoint),
        )
        metrics = state_metrics(snapshot, case, power_flow)
        if metrics["maximum_constraint_violation"] <= feasibility_tolerance
            lower = metrics
        else
            upper = metrics
        end
    end
    delete!(lower, "state")
    lower["tap_value"] = Float64(tap)
    lower["algorithm"] = "damped finite-difference Newton continuation and bisection"
    lower["scan_step"] = Float64(scan_step)
    lower["scan_maximum"] = Float64(scan_maximum)
    lower["scanned_points"] = scanned_points
    lower["bisection_iterations"] = bisection_iterations
    lower["total_newton_iterations"] = total_newton_iterations
    lower["total_residual_evaluations"] = total_residual_evaluations
    lower["upper_infeasible_served_fraction"] = upper["served_fraction"]
    lower
end

function reproduce_transformer_tap_decision(
    case::TransformerTapACCase;
    scan_step=0.05,
    scan_maximum=1.60,
)
    domain = only(case.factor.decisions)
    results = [solve_independent_tap_boundary(
        case, tap; scan_step=scan_step, scan_maximum=scan_maximum,
    ) for tap in domain.positions]
    any(result -> result isa IndependentReproductionRejection, results) &&
        return only(result for result in results
                    if result isa IndependentReproductionRejection)
    optimum = results[argmax(result["served_fraction"] for result in results)]
    Dict{String,Any}(
        "decision_id" => domain.decision_id,
        "positions" => domain.positions,
        "tap_results" => results,
        "optimum" => optimum,
    )
end

function comparison_with_ipopt(case, independent, ipopt)
    ipopt_by_tap = Dict(
        result["tap_value"] => result
        for result in ipopt["parameterized_target_subproblems"]
    )
    comparisons = [begin
        reference = ipopt_by_tap[result["tap_value"]]
        Dict{String,Any}(
            "tap_value" => result["tap_value"],
            "served_fraction_difference" =>
                result["served_fraction"] - reference["objective_served_fraction"],
            "maximum_secondary_voltage_difference_pu" => maximum(abs.(
                result["secondary_phase_to_neutral_voltage_pu"] .-
                reference["secondary_phase_to_neutral_voltage_pu"]
            )),
            "maximum_leakage_current_difference_A" => maximum(abs.(
                result["leakage_current_magnitude_A"] .-
                reference["leakage_current_magnitude_A"]
            )),
        )
    end for result in independent["tap_results"]]
    Dict{String,Any}(
        "pointwise_comparisons" => comparisons,
        "independent_optimal_tap" => independent["optimum"]["tap_value"],
        "ipopt_optimal_tap" => ipopt["parameterized_target_optimum"]["tap_value"],
        "maximum_absolute_served_fraction_difference" => maximum(
            abs(comparison["served_fraction_difference"]) for comparison in comparisons
        ),
        "maximum_secondary_voltage_difference_pu" => maximum(
            comparison["maximum_secondary_voltage_difference_pu"] for comparison in comparisons
        ),
        "maximum_leakage_current_difference_A" => maximum(
            comparison["maximum_leakage_current_difference_A"] for comparison in comparisons
        ),
    )
end

function independent_transformer_tap_certificate(
    case::TransformerTapACCase;
    certificate_id="TR-XFMR-007",
)
    independent = reproduce_transformer_tap_decision(case)
    independent isa IndependentReproductionRejection &&
        error("independent reproduction failed guard $(independent.failed_guard)")
    ipopt = solve_transformer_tap_ac_decision(case)
    comparison = comparison_with_ipopt(case, independent, ipopt)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "independent_transformer_tap_ac_numerical_reproduction",
        "classification" => "mixed",
        "source" => Dict(
            "model_category" => "jump_ipopt_transformer_tap_ac_network_decision",
            "object_ids" => ["TR-XFMR-006", TAP_DECISION_ID],
            "detail" => Dict(
                "solver" => "Ipopt through JuMP",
                "tap_positions" => independent["positions"],
            ),
        ),
        "target" => Dict(
            "model_category" => "independent_rectangular_residual_continuation_and_boundary_search",
            "object_ids" => [
                "generated_independent_power_flow_residual__x1",
                "generated_independent_tap_boundary_search__x1",
            ],
            "detail" => Dict(
                "equality_dimension" => 14,
                "jacobian" => "central finite differences",
                "nonlinear_solver" => "damped Newton",
                "decision_search" => "finite tap enumeration with continuation and bisection",
                "external_optimizer_packages" => String[],
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["JuMP rectangular voltage variables and served fraction"],
                "target" => ["14 normalized rectangular voltage coordinates and served fraction"],
                "relation" => "the normalized target coordinates map bijectively to the same seven unknown complex terminal voltages",
            ),
            "constraints" => Dict(
                "source" => ["JuMP phase-power, neutral-KCL, tertiary-KCL, gauge, voltage, and leakage-current constraints"],
                "target" => ["14 equality residuals plus independently evaluated voltage and leakage-current inequalities"],
                "relation" => "complex equations are split into scaled real and imaginary residuals without changing their zero set; inequalities are evaluated on recovered physical states",
            ),
            "decisions" => Dict(
                "source" => [TAP_DECISION_ID, "served-load fraction alpha"],
                "target" => [TAP_DECISION_ID, "served-load fraction alpha"],
                "relation" => "the finite tap domain is enumerated identically and alpha is traced on each high-voltage power-flow branch",
            ),
            "objectives" => Dict(
                "source" => ["maximize served-load fraction alpha"],
                "target" => ["locate the upper feasible alpha boundary on each traced branch and select the largest"],
                "relation" => "the target reproduces the source objective when the first upper boundary is the relevant branch optimum",
            ),
            "units" => Dict(
                "source" => ["V", "A", "MVA", "per-unit voltage"],
                "target" => ["the same physical units with scaled residuals"],
                "relation" => "residual scaling is invertible and does not change equality feasibility",
            ),
            "boundary_quantities" => Dict(
                "source" => ["11 terminal voltage and current phasors", "nine leakage currents"],
                "target" => ["the same quantities recovered from normalized rectangular coordinates"],
                "relation" => "both numerical paths evaluate the same parameterized transformer matrices",
            ),
        ),
        "preconditions" => [
            "TR-XFMR-006 supplies the same pointwise transformer and network equations",
            "the no-load linear solution lies on the high-voltage branch to be traced",
            "damped Newton converges at every continuation and boundary-search point",
            "the scan encounters a feasible point followed by a converged upper infeasible point",
            "the first upper feasibility boundary is the relevant maximum-served-load point on the traced branch",
        ],
        "preserves" => [
            "network_equality_zero_set_under_rectangular_scaling",
            "physical_voltage_and_current_recovery",
            "finite_tap_domain",
            "recorded_tap_conditioned_boundary_solutions",
            "recorded_optimal_tap_and_served_load",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "terminal_voltage" => "U[1:4]=Uslack and U[5:11]=Vbase.*(xre+j*xim)",
            "terminal_current" => "Iterminal=Ycomplete(tap)*U",
            "leakage_current" => "Ileakage=Mleakage(tap)*U",
        ),
        "constraint_map" => Dict(
            "complex_equalities" => "split phase power, neutral KCL, tertiary KCL, and gauge equations into 14 scaled real residuals",
            "inequalities" => "evaluate voltage bounds and nine leakage-current limits after physical-state recovery",
            "upper_boundary" => "require an explicit feasible/infeasible bracket before bisection",
        ),
        "provenance" => Dict(
            "reference_certificate" => "TR-XFMR-006",
            "implementation" => "experiments/transformations/TransformerTapACIndependentReproduction.jl",
            "independent_numerical_engine" => "LinearAlgebra-only damped Newton, continuation, and bisection",
            "shared_input" => case.factor.contract_id,
        ),
        "evidence" => Dict(
            "independent_reproduction" => independent,
            "ipopt_comparison" => comparison,
        ),
    )
end

function _phase_scaled_case(case::TransformerTapACCase, scale)
    TransformerTapACCase(
        case.factor,
        case.source_completion,
        case.terminal_voltage_base_V,
        case.slack_voltage_V,
        case.load_direction_MVA_per_phase .* ComplexF64.(scale),
        case.secondary_voltage_bounds_pu,
    )
end

"Independently reproduce every tap boundary in the three declared scenarios."
function reproduce_transformer_tap_three_scenario_decision(
    case::TransformerTapACCase;
    scenario_phase_scales=[[1.00, 1.00, 1.00], [1.02, 0.98, 1.01], [0.99, 1.03, 0.98]],
    switching_cost=0.02,
    max_tap_operations=nothing,
)
    scenario_cases = [_phase_scaled_case(case, scale) for scale in scenario_phase_scales]
    scenario_results = [reproduce_transformer_tap_decision(scenario) for scenario in scenario_cases]
    any(result -> result isa IndependentReproductionRejection, scenario_results) &&
        return only(result for result in scenario_results if result isa IndependentReproductionRejection)
    positions = only(case.factor.decisions).positions
    branches = Dict{String,Any}[]
    for i in eachindex(positions), j in eachindex(positions), k in eachindex(positions)
        taps = (positions[i], positions[j], positions[k])
        served = (
            scenario_results[1]["tap_results"][i]["served_fraction"],
            scenario_results[2]["tap_results"][j]["served_fraction"],
            scenario_results[3]["tap_results"][k]["served_fraction"],
        )
        movement = abs(taps[2] - taps[1]) + abs(taps[3] - taps[2])
        operations = Int(taps[2] != taps[1]) + Int(taps[3] != taps[2])
        push!(branches, Dict(
            "scenario_taps" => collect(taps),
            "scenario_served_fractions" => collect(served),
            "tap_movement" => movement,
            "tap_operations" => operations,
            "admissible" => max_tap_operations === nothing || operations <= max_tap_operations,
            "net_objective" => sum(served) - switching_cost * movement,
        ))
    end
    admissible = [branch for branch in branches if branch["admissible"]]
    isempty(admissible) && throw(ArgumentError("operation-count limit leaves no admissible tap path"))
    best = admissible[argmax(branch["net_objective"] for branch in admissible)]
    (; scenario_phase_scales = [Float64.(scale) for scale in scenario_phase_scales],
       positions,
       switching_cost,
       max_tap_operations,
       scenario_results,
       branches,
       admissible_branch_count = length(admissible),
       selected_branch = best,
       branch_count = length(branches),
       branch_completeness = length(branches) == length(positions)^3)
end

"Certificate comparing the independent three-scenario path with the Ipopt ledger."
function independent_transformer_tap_three_scenario_certificate(
    case::TransformerTapACCase;
    certificate_id="TR-XFMR-009-REPRO",
)
    independent = reproduce_transformer_tap_three_scenario_decision(case)
    independent isa IndependentReproductionRejection &&
        error("independent three-scenario reproduction failed guard $(independent.failed_guard)")
    ipopt = solve_transformer_tap_ac_three_scenario_decision(case)
    operation_limited_independent = reproduce_transformer_tap_three_scenario_decision(
        case; max_tap_operations=1,
    )
    operation_limited_ipopt = solve_transformer_tap_ac_three_scenario_decision(
        case; max_tap_operations=1,
    )
    ipopt_by_taps = Dict(
        Tuple(branch["scenario_taps"]) => branch
        for branch in ipopt.branches
    )
    comparisons = [begin
        reference = ipopt_by_taps[Tuple(branch["scenario_taps"])]
        Dict(
            "scenario_taps" => branch["scenario_taps"],
            "net_objective_difference" => branch["net_objective"] - reference["net_objective"],
            "tap_movement_difference" => branch["tap_movement"] - reference["tap_movement"],
        )
    end for branch in independent.branches]
    max_difference = maximum(abs(row["net_objective_difference"]) for row in comparisons)
    limited_ipopt_by_taps = Dict(
        Tuple(branch["scenario_taps"]) => branch
        for branch in operation_limited_ipopt.branches
        if branch["admissible"]
    )
    limited_differences = [
        independent_branch["net_objective"] - limited_ipopt_by_taps[Tuple(independent_branch["scenario_taps"])]["net_objective"]
        for independent_branch in operation_limited_independent.branches
        if independent_branch["admissible"]
    ]
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "independent_three_scenario_transformer_tap_path_reproduction",
        "classification" => "mixed",
        "source" => Dict(
            "model_category" => "jump_ipopt_three_scenario_unbalanced_transformer_tap_path",
            "object_ids" => ["TR-XFMR-009", TAP_DECISION_ID],
            "detail" => Dict("solver" => "Ipopt through JuMP", "branch_count" => ipopt.branch_count),
        ),
        "target" => Dict(
            "model_category" => "independent_rectangular_residual_three_scenario_boundary_search",
            "object_ids" => ["generated_independent_three_scenario_boundaries__x1"],
            "detail" => Dict(
                "nonlinear_solver" => "damped finite-difference Newton",
                "decision_search" => "independent tap enumeration in each scenario and 27-path enumeration",
                "external_optimizer_packages" => String[],
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict("source" => ["scenario-specific rectangular voltage states"], "target" => ["independently recovered rectangular voltage states"], "relation" => "same seven unknown complex terminal voltages are recovered per scenario and tap"),
            "constraints" => Dict("source" => ["phase-power, KCL, voltage, and leakage-current constraints"], "target" => ["finite-difference residual equations and independently evaluated inequalities"], "relation" => "complex equalities are split into scaled real residuals and constraints are checked after physical recovery"),
            "decisions" => Dict("source" => [TAP_DECISION_ID, "three scenario tap path"], "target" => [TAP_DECISION_ID, "three scenario tap path"], "relation" => "the same finite tap triples are enumerated"),
            "objectives" => Dict("source" => ["sum of served fractions minus movement cost"], "target" => ["same branch objective reconstructed from independent boundaries"], "relation" => "branch objectives use identical declared movement costs"),
            "units" => Dict("source" => ["V", "A", "MVA"], "target" => ["V", "A", "MVA"], "relation" => "physical quantities are recovered in the same units"),
            "boundary_quantities" => Dict("source" => ["nine scenario/tap boundary served fractions"], "target" => ["nine independently reproduced boundary served fractions"], "relation" => "each scenario/tap boundary is compared before path selection"),
        ),
        "preconditions" => [
            "TR-XFMR-009 supplies the same finite scenario scales and tap domain",
            "the independent high-voltage branch is traced with a feasible/infeasible bracket",
            "the first upper feasibility boundary is the relevant branch maximum",
        ],
        "preserves" => ["nine scenario/tap boundary values", "27-branch path domain", "phase-selective scenario identity", "selected path objective"],
        "forgets" => String[],
        "recovery_map" => Dict("boundary_state" => "recover physical terminal voltages and currents from normalized rectangular coordinates"),
        "constraint_map" => Dict("path_enumeration" => "enumerate every ordered tap triple and apply consecutive movement cost"),
        "provenance" => Dict("reference_certificate" => "TR-XFMR-009", "implementation" => "experiments/transformations/TransformerTapACIndependentReproduction.jl", "independent_numerical_engine" => "LinearAlgebra-only damped Newton, continuation, and bisection"),
        "evidence" => Dict(
            "independent_reproduction" => independent,
            "operation_limited_independent_reproduction" => operation_limited_independent,
            "ipopt_branch_count" => ipopt.branch_count,
            "operation_limited_ipopt_branch_count" => operation_limited_ipopt.admissible_branch_count,
            "maximum_absolute_net_objective_difference" => max_difference,
            "selected_path_matches" => independent.selected_branch["scenario_taps"] == ipopt.selected_branch["scenario_taps"],
            "operation_limited_selected_path_matches" => operation_limited_independent.selected_branch["scenario_taps"] == operation_limited_ipopt.selected_branch["scenario_taps"],
            "operation_limited_maximum_absolute_net_objective_difference" => maximum(abs.(limited_differences)),
            "comparisons" => comparisons,
        ),
    )
end

end

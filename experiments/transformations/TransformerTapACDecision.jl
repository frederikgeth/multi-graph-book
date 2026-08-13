module TransformerTapACDecision

using Ipopt
using JSON3
using JuMP
using LinearAlgebra

using ..MultiwindingLeakageCompilation: MultiwindingLeakageData,
                                            compile_pairwise_leakage
using ..MultiwindingTerminalAssembly: assemble_terminal_leakage
using ..TransformerFactorCompletion: TransformerCompletionData,
                                             TransformerCompletionResult,
                                             WindingTransfer,
                                             assemble_complete_transformer,
                                             completion_data_from_dict
using ..TransformerTapDecisionCompilation: ParameterizedTransformerFactor,
                                                compile_parameterized_transformer,
                                                evaluate_parameterized_transformer
using ..TransformerWindingNormalization: WindingFactor,
                                              delta_incidence,
                                              wye_incidence

export TransformerTapACCase,
       load_transformer_tap_ac_case,
       solve_transformer_tap_ac_decision,
       solve_transformer_tap_ac_snapshot,
       transformer_tap_ac_certificate

const TAP_DECISION_ID = "tap/x1/winding/2"

struct TransformerTapACCase
    factor::ParameterizedTransformerFactor
    source_completion::TransformerCompletionData
    terminal_voltage_base_V::Vector{Float64}
    slack_voltage_V::Vector{ComplexF64}
    load_direction_MVA_per_phase::ComplexF64
    secondary_voltage_bounds_pu::Tuple{Float64,Float64}
end

function transfer_copy(
    source::WindingTransfer;
    coefficient=source.coefficient,
    control_mode=source.control_mode,
    decision_id=source.decision_id,
)
    WindingTransfer(
        source.id,
        source.transformer_id,
        source.winding_id,
        source.winding_position,
        source.coil_labels,
        control_mode,
        coefficient;
        terminal_labels=source.terminal_labels,
        decision_id=decision_id,
        attributes=source.attributes,
    )
end

function direct_snapshot(case::TransformerTapACCase, tap)
    transfers = [
        transfer.control_mode == "fixed" ? transfer_copy(transfer) :
        transfer_copy(
            transfer;
            coefficient=transfer.coefficient .* tap,
            control_mode="fixed",
            decision_id=nothing,
        )
        for transfer in case.source_completion.winding_transfers
    ]
    data = TransformerCompletionData(
        "$(case.source_completion.id)/network-source/$tap",
        case.source_completion.transformer_id,
        "direct_source_network_snapshot",
        case.source_completion.voltage_transfer_convention,
        transfers;
        excitation_shunt=case.source_completion.excitation_shunt,
        internal_groundings=case.source_completion.internal_groundings,
        metadata=merge(case.source_completion.metadata, Dict{String,Any}(
            "decision_id" => TAP_DECISION_ID,
            "tap_value" => tap,
        )),
    )
    assemble_complete_transformer(case.factor.source_leakage, data)
end

function source_factor_from_files(root)
    network = JSON3.read(
        read(joinpath(root, "data", "running-network", "v0.1.0.json"), String),
        Dict{String,Any},
    )
    raw_contract = JSON3.read(
        read(
            joinpath(root, "data", "transformer-contracts", "x1-discrete-tap-v0.1.0.json"),
            String,
        ),
        Dict{String,Any},
    )
    transformer = network["transformer"]["n_winding"]["x1"]
    windings = transformer["windings"]
    pairs = Dict{Tuple{Int,Int},Float64}()
    for (key, value) in transformer["x_sc"]
        i, j = parse.(Int, split(key, "_"))
        pairs[(i, j)] = Float64(value)
    end
    leakage_data = MultiwindingLeakageData(
        "x1",
        ["x1/winding/$k" for k in eachindex(windings)],
        [winding["v_nom"] for winding in windings],
        [winding["r_winding"] for winding in windings],
        [winding["i_max"] for winding in windings],
        pairs,
    )
    factors = WindingFactor[]
    for (position, winding) in enumerate(windings)
        terminals = String.(winding["terminal_map"])
        connection = String(winding["configuration"])
        incidence = connection == "WYE" ? wye_incidence(terminals) :
            delta_incidence(terminals; roll=Int(winding["delta_roll"]))
        coil_labels = connection == "WYE" ? filter(!=("n"), terminals) : copy(terminals)
        push!(factors, WindingFactor(
            "x1/winding/$position",
            "x1",
            position,
            winding["bus"],
            terminals,
            connection,
            incidence,
            fill(Float64(winding["i_max"]), length(coil_labels));
            coil_labels=coil_labels,
        ))
    end
    leakage = assemble_terminal_leakage(compile_pairwise_leakage(leakage_data), factors)
    completion = completion_data_from_dict(raw_contract)
    factor = compile_parameterized_transformer(leakage, completion)
    factor, completion, Float64.([winding["v_nom"] for winding in windings])
end

"Load the running transformer's full 11-terminal discrete-tap AC decision case."
function load_transformer_tap_ac_case(root=normpath(joinpath(@__DIR__, "..", "..")))
    factor, completion, nominal_voltage = source_factor_from_files(root)
    sequence = ComplexF64[1.0, cis(-2pi / 3), cis(2pi / 3)]
    winding_1_phase_base = nominal_voltage[1]
    winding_2_phase_base = nominal_voltage[2]
    winding_3_terminal_base = nominal_voltage[3] / sqrt(3)
    terminal_bases = vcat(
        fill(winding_1_phase_base, 4),
        fill(winding_2_phase_base, 4),
        fill(winding_3_terminal_base, 3),
    )
    slack = vcat(winding_1_phase_base .* sequence, 0.0 + 0.0im)
    TransformerTapACCase(
        factor,
        completion,
        terminal_bases,
        slack,
        0.50 + 0.10im,
        (0.90, 1.05),
    )
end

function no_load_start(snapshot, case)
    slack = case.slack_voltage_V
    admittance = snapshot.terminal_admittance
    unknown_block = admittance[5:11, 5:11]
    rhs = -admittance[5:11, 1:4] * slack
    gauge = zeros(ComplexF64, 1, 7)
    gauge[1, 5:7] .= case.terminal_voltage_base_V[9]
    augmented = [unknown_block transpose(conj(gauge)); gauge zeros(ComplexF64, 1, 1)]
    augmented \ vcat(rhs, 0.0 + 0.0im) |> result -> result[1:7]
end

function snapshot_for(case, tap, formulation)
    if formulation == :source
        direct_snapshot(case, tap)
    elseif formulation == :parameterized
        evaluate_parameterized_transformer(case.factor, Dict(TAP_DECISION_ID => tap))
    else
        throw(ArgumentError("unknown formulation $formulation"))
    end
end

function complex_records(labels, values; scale=ones(length(values)))
    [Dict(
        "terminal" => labels[index],
        "real" => real(values[index]),
        "imag" => imag(values[index]),
        "magnitude" => abs(values[index]),
        "magnitude_pu" => abs(values[index]) / scale[index],
    ) for index in eachindex(values)]
end

"""
Solve one tap-conditioned continuous AC maximum-served-load subproblem.

Winding 1 is fixed at balanced nominal voltage. Winding 2 retains four
conductor voltages, three phase constant-power equations, and neutral KCL.
The open delta tertiary retains all three terminal voltages; two independent
zero-current equations plus a zero-common-mode gauge determine its state.
"""
function solve_transformer_tap_ac_snapshot(
    case::TransformerTapACCase,
    tap::Real;
    formulation=:parameterized,
)
    snapshot = snapshot_for(case, Float64(tap), formulation)
    snapshot isa TransformerCompletionResult ||
        throw(ArgumentError("tap does not evaluate to a fixed transformer snapshot"))
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    set_optimizer_attribute(model, "tol", 1.0e-9)
    set_optimizer_attribute(model, "constr_viol_tol", 1.0e-9)
    set_optimizer_attribute(model, "max_iter", 2000)

    @variable(model, voltage_real_pu[1:7])
    @variable(model, voltage_imag_pu[1:7])
    @variable(model, served_fraction >= 0)
    start_voltage = no_load_start(snapshot, case)
    for index in 1:7
        base = case.terminal_voltage_base_V[index + 4]
        set_start_value(voltage_real_pu[index], real(start_voltage[index]) / base)
        set_start_value(voltage_imag_pu[index], imag(start_voltage[index]) / base)
    end
    set_start_value(served_fraction, 0.8)

    voltage_real = Any[real(value) for value in case.slack_voltage_V]
    voltage_imag = Any[imag(value) for value in case.slack_voltage_V]
    for index in 1:7
        base = case.terminal_voltage_base_V[index + 4]
        push!(voltage_real, @expression(model, base * voltage_real_pu[index]))
        push!(voltage_imag, @expression(model, base * voltage_imag_pu[index]))
    end
    admittance = snapshot.terminal_admittance
    @expression(model, current_real[k=1:11], sum(
        real(admittance[k, d]) * voltage_real[d] -
        imag(admittance[k, d]) * voltage_imag[d]
        for d in 1:11
    ))
    @expression(model, current_imag[k=1:11], sum(
        imag(admittance[k, d]) * voltage_real[d] +
        real(admittance[k, d]) * voltage_imag[d]
        for d in 1:11
    ))

    p_direction = real(case.load_direction_MVA_per_phase)
    q_direction = imag(case.load_direction_MVA_per_phase)
    for phase in 5:7
        v_real = voltage_real[phase] - voltage_real[8]
        v_imag = voltage_imag[phase] - voltage_imag[8]
        @constraint(model,
            -(v_real * current_real[phase] + v_imag * current_imag[phase]) / 1.0e6 ==
            served_fraction * p_direction
        )
        @constraint(model,
            -(v_imag * current_real[phase] - v_real * current_imag[phase]) / 1.0e6 ==
            served_fraction * q_direction
        )
        lower, upper = case.secondary_voltage_bounds_pu
        base = case.terminal_voltage_base_V[phase]
        @constraint(model, v_real^2 + v_imag^2 >= (lower * base)^2)
        @constraint(model, v_real^2 + v_imag^2 <= (upper * base)^2)
    end
    @constraint(model, sum(current_real[index] for index in 5:8) == 0)
    @constraint(model, sum(current_imag[index] for index in 5:8) == 0)

    # Delta terminal currents sum identically. Enforce two independent KCL rows
    # and fix only the physically irrelevant common-mode voltage coordinate.
    @constraint(model, [index=9:10], current_real[index] == 0)
    @constraint(model, [index=9:10], current_imag[index] == 0)
    @constraint(model, sum(voltage_real_pu[index] for index in 5:7) == 0)
    @constraint(model, sum(voltage_imag_pu[index] for index in 5:7) == 0)

    leakage_map = snapshot.winding_leakage_current_map
    @expression(model, leakage_real[k=1:9], sum(
        real(leakage_map[k, d]) * voltage_real[d] -
        imag(leakage_map[k, d]) * voltage_imag[d]
        for d in 1:11
    ))
    @expression(model, leakage_imag[k=1:9], sum(
        imag(leakage_map[k, d]) * voltage_real[d] +
        real(leakage_map[k, d]) * voltage_imag[d]
        for d in 1:11
    ))
    for index in 1:9
        limit = snapshot.leakage_current_limit[index]
        @constraint(model,
            (leakage_real[index] / limit)^2 + (leakage_imag[index] / limit)^2 <= 1
        )
    end

    @objective(model, Max, served_fraction)
    optimize!(model)

    voltage = ComplexF64[case.slack_voltage_V; [
        case.terminal_voltage_base_V[index + 4] *
        (value(voltage_real_pu[index]) + im * value(voltage_imag_pu[index]))
        for index in 1:7
    ]]
    terminal_current = snapshot.terminal_admittance * voltage
    leakage_current = snapshot.winding_leakage_current_map * voltage
    secondary_voltage = voltage[5:7] .- voltage[8]
    load_power = -secondary_voltage .* conj.(terminal_current[5:7]) ./ 1.0e6
    tertiary_kcl_residual = maximum(abs.(terminal_current[9:11]))
    secondary_kcl_residual = abs(sum(terminal_current[5:8]))
    power_balance_residual = maximum(abs.(
        load_power .- value(served_fraction) .* case.load_direction_MVA_per_phase
    ))
    Dict{String,Any}(
        "formulation" => String(formulation),
        "tap_value" => Float64(tap),
        "termination_status" => string(termination_status(model)),
        "objective_served_fraction" => objective_value(model),
        "served_load_MVA" => Dict(
            "active" => 3 * real(case.load_direction_MVA_per_phase) * value(served_fraction),
            "reactive" => 3 * imag(case.load_direction_MVA_per_phase) * value(served_fraction),
        ),
        "secondary_phase_to_neutral_voltage_pu" =>
            abs.(secondary_voltage) ./ case.terminal_voltage_base_V[5:7],
        "terminal_voltage" => complex_records(
            snapshot.qualified_terminal_labels,
            voltage;
            scale=case.terminal_voltage_base_V,
        ),
        "leakage_current_magnitude_A" => abs.(leakage_current),
        "leakage_current_limit_A" => snapshot.leakage_current_limit,
        "maximum_leakage_current_loading" => maximum(
            abs.(leakage_current) ./ snapshot.leakage_current_limit
        ),
        "secondary_neutral_kcl_residual_A" => secondary_kcl_residual,
        "tertiary_kcl_residual_A" => tertiary_kcl_residual,
        "phase_power_balance_residual_MVA" => power_balance_residual,
        "delta_common_mode_voltage_pu" => abs(sum(
            voltage[9:11] ./ case.terminal_voltage_base_V[9:11]
        )),
        "model_size" => Dict(
            "variables" => num_variables(model),
            "constraints" => sum(num_constraints(model, function_type, set_type)
                for (function_type, set_type) in list_of_constraint_types(model)),
        ),
    )
end

function solve_transformer_tap_ac_decision(case::TransformerTapACCase)
    domain = only(case.factor.decisions)
    domain.control_mode == "discrete" ||
        throw(ArgumentError("the recorded network case requires a finite discrete tap domain"))
    source = [solve_transformer_tap_ac_snapshot(case, tap; formulation=:source)
              for tap in domain.positions]
    target = [solve_transformer_tap_ac_snapshot(case, tap; formulation=:parameterized)
              for tap in domain.positions]
    source_best = source[argmax(result["objective_served_fraction"] for result in source)]
    target_best = target[argmax(result["objective_served_fraction"] for result in target)]
    frozen = only(result for result in target if result["tap_value"] == domain.start_value)
    factor_differences = [begin
        source_snapshot = direct_snapshot(case, tap)
        target_snapshot = evaluate_parameterized_transformer(
            case.factor, Dict(domain.decision_id => tap),
        )
        Dict{String,Any}(
            "tap_value" => tap,
            "maximum_terminal_admittance_difference_S" => maximum(abs.(
                source_snapshot.terminal_admittance .- target_snapshot.terminal_admittance
            )),
            "maximum_leakage_current_map_difference_S" => maximum(abs.(
                source_snapshot.winding_leakage_current_map .-
                target_snapshot.winding_leakage_current_map
            )),
        )
    end for tap in domain.positions]
    Dict{String,Any}(
        "decision_id" => domain.decision_id,
        "positions" => domain.positions,
        "source_subproblems" => source,
        "parameterized_target_subproblems" => target,
        "source_optimum" => source_best,
        "parameterized_target_optimum" => target_best,
        "frozen_start_solution" => frozen,
        "pointwise_factor_differences" => factor_differences,
        "source_target_objective_gap" =>
            target_best["objective_served_fraction"] - source_best["objective_served_fraction"],
        "frozen_start_objective_gap" =>
            target_best["objective_served_fraction"] - frozen["objective_served_fraction"],
    )
end

function transformer_tap_ac_certificate(; certificate_id="TR-XFMR-006")
    case = load_transformer_tap_ac_case()
    comparison = solve_transformer_tap_ac_decision(case)
    domain = only(case.factor.decisions)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "parameterized_transformer_tap_network_decision_embedding",
        "classification" => "exact_compilation",
        "source" => Dict(
            "model_category" => "direct_multiwinding_transformer_discrete_tap_ac_network_opf",
            "object_ids" => [
                case.factor.transformer_id,
                domain.decision_id,
                "network/slack/winding/1",
                "network/load/winding/2",
                "network/open-delta/winding/3",
            ],
            "detail" => Dict(
                "terminal_count" => 11,
                "tap_positions" => domain.positions,
                "load_direction_MVA_per_phase" => Dict(
                    "real" => real(case.load_direction_MVA_per_phase),
                    "imag" => imag(case.load_direction_MVA_per_phase),
                ),
                "secondary_voltage_bounds_pu" => collect(case.secondary_voltage_bounds_pu),
            ),
        ),
        "target" => Dict(
            "model_category" => "parameterized_transformer_factor_embedded_in_discrete_tap_ac_network_opf",
            "object_ids" => [
                "generated_parameterized_transformer_factor__x1",
                "generated_network_tap_subproblems__x1",
            ],
            "detail" => Dict(
                "source_parameterized_factor_certificate" =>
                    case.factor.certificate["certificate_id"],
                "continuous_subproblem_count" => length(domain.positions),
                "selection_method" => "exact enumeration of the finite declared tap domain",
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["11 complex transformer terminal voltages", "terminal and leakage currents"],
                "target" => ["the same 11 complex voltages", "currents recovered from the evaluated parameterized factor"],
                "relation" => "for each tap, source and target stamp the same complex terminal and lifted leakage-current maps into the network equations",
            ),
            "constraints" => Dict(
                "source" => ["phase power balance", "neutral KCL", "open-tertiary KCL", "voltage bounds", "nine leakage-current limits"],
                "target" => ["the identical network and recovered transformer constraints"],
                "relation" => "all nonlinear network constraints are unchanged after pointwise factor evaluation",
            ),
            "decisions" => Dict(
                "source" => [domain.decision_id, "served-load fraction alpha"],
                "target" => [domain.decision_id, "served-load fraction alpha"],
                "relation" => "tap identity and finite domain are unchanged; each tap-conditioned continuous optimum is compared before exact selection",
            ),
            "objectives" => Dict(
                "source" => ["maximize served-load fraction alpha"],
                "target" => ["maximize served-load fraction alpha"],
                "relation" => "the objective is evaluated on the same recovered network state",
            ),
            "units" => Dict(
                "source" => ["dimensionless tap", "V", "A", "MVA", "per-unit voltage"],
                "target" => ["dimensionless tap", "V", "A", "MVA", "per-unit voltage"],
                "relation" => "physical transformer matrices use V, A, and S while normalized voltage variables improve numerical scaling only",
            ),
            "boundary_quantities" => Dict(
                "source" => ["all winding terminal voltage and current phasors"],
                "target" => ["the same winding terminal phasors"],
                "relation" => "the parameterized factor is pointwise identical at every retained tap position",
            ),
        ),
        "preconditions" => [
            "TR-XFMR-005 applies to the retained finite scalar tap domain",
            "the source and target use identical slack, load, voltage, KCL, current-limit, and objective equations",
            "the open delta tertiary has zero terminal injections and an explicit common-mode voltage gauge",
            "each finite tap-conditioned continuous subproblem is solved to the recorded local optimum",
        ],
        "preserves" => [
            "tap_decision_identity_and_domain",
            "network_voltage_and_power_balance_feasible_set_at_each_tap",
            "all_transformer_leakage_current_limits",
            "served_load_objective",
            "source_optimal_tap_and_continuous_state",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "tap" => "tap_source = tap_target",
            "terminal_voltage" => "U_source = U_target in the same qualified terminal order",
            "terminal_current" => "I_terminal = Y_complete(tap)*U",
            "leakage_current" => "I_leakage = M_leakage(tap)*U",
        ),
        "constraint_map" => Dict(
            "network_embedding" => "evaluate Y_complete(tap) and M_leakage(tap), then stamp unchanged phase-power, KCL, voltage, and current-limit constraints",
            "discrete_selection" => "solve every declared tap-conditioned continuous subproblem and select the maximum served-load objective",
            "frozen_start" => "tap=tap_start is a feasible-set restriction, not an exact replacement for the retained decision",
        ),
        "provenance" => Dict(
            "solver" => "Ipopt through JuMP",
            "implementation" => "experiments/transformations/TransformerTapACDecision.jl",
            "source_contract" => case.factor.contract_id,
            "source_factor_certificate" => case.factor.certificate["certificate_id"],
            "coordinate_system" => "rectangular complex conductor voltages with physical transformer matrices and normalized voltage variables",
        ),
        "evidence" => comparison,
    )
end

end

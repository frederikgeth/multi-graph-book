module TransformerTapDecisionCompilation

using LinearAlgebra

using ..MultiwindingTerminalAssembly: MultiwindingTerminalAssemblyResult
using ..TransformerFactorCompletion: TransformerCompletionData,
                                             TransformerCompletionRejection,
                                             TransformerCompletionResult,
                                             WindingTransfer,
                                             assemble_complete_transformer

export ParameterizedTransformerFactor,
       TapDecisionDomain,
       TapDecisionEvaluationRejection,
       TapDecisionFactorRejection,
       compile_parameterized_transformer,
       evaluate_parameterized_transformer

const TAP_PARAMETERIZATION =
    "coefficient_xkc(tap) = tap * base_coefficient_xkc"

struct TapDecisionDomain
    decision_id::String
    winding_id::String
    winding_position::Int
    control_mode::String
    start_value::Float64
    lower_bound::Float64
    upper_bound::Float64
    positions::Vector{Float64}
end

struct ParameterizedTransformerFactor
    contract_id::String
    transformer_id::String
    source_leakage::MultiwindingTerminalAssemblyResult
    source_completion::TransformerCompletionData
    decisions::Vector{TapDecisionDomain}
    start_snapshot::TransformerCompletionResult
    certificate::Dict{String,Any}
end

struct TapDecisionFactorRejection
    rule_id::String
    source_ids::Vector{String}
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

struct TapDecisionEvaluationRejection
    rule_id::String
    contract_id::String
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

function fixed_transfer(source::WindingTransfer, coefficient)
    WindingTransfer(
        source.id,
        source.transformer_id,
        source.winding_id,
        source.winding_position,
        source.coil_labels,
        "fixed",
        coefficient;
        terminal_labels=source.terminal_labels,
        attributes=source.attributes,
    )
end

function fixed_completion(data::TransformerCompletionData, decision_values)
    transfers = WindingTransfer[]
    for transfer in data.winding_transfers
        coefficient = transfer.control_mode == "fixed" ?
            transfer.coefficient :
            transfer.coefficient .* decision_values[something(transfer.decision_id)]
        push!(transfers, fixed_transfer(transfer, coefficient))
    end
    TransformerCompletionData(
        "$(data.id)/snapshot",
        data.transformer_id,
        "fixed_snapshot_of_parameterized_contract",
        data.voltage_transfer_convention,
        transfers;
        excitation_shunt=data.excitation_shunt,
        internal_groundings=data.internal_groundings,
        metadata=merge(data.metadata, Dict{String,Any}(
            "parameterized_contract" => data.id,
            "decision_values" => Dict(String(key) => value for (key, value) in decision_values),
        )),
    )
end

function factor_rejection(leakage, data, failed; evidence=Dict{String,Any}())
    TapDecisionFactorRejection(
        "parameterized_transformer_tap_factor_compilation",
        unique(vcat(
            String.(leakage.certificate["target"]["object_ids"]),
            [data.id],
        )),
        unique(String.(failed)),
        Dict{String,Any}(evidence),
    )
end

function domain_from_transfer(transfer::WindingTransfer)
    attributes = transfer.attributes
    mode = transfer.control_mode
    start = Float64(attributes["tap_start"])
    if mode == "continuous"
        lower = Float64(attributes["tap_min"])
        upper = Float64(attributes["tap_max"])
        positions = Float64[]
    else
        positions = Float64.(attributes["tap_positions"])
        lower = minimum(positions)
        upper = maximum(positions)
    end
    TapDecisionDomain(
        something(transfer.decision_id),
        transfer.winding_id,
        transfer.winding_position,
        mode,
        start,
        lower,
        upper,
        positions,
    )
end

function domain_dict(domain::TapDecisionDomain)
    result = Dict{String,Any}(
        "decision_id" => domain.decision_id,
        "winding_id" => domain.winding_id,
        "winding_position" => domain.winding_position,
        "control_mode" => domain.control_mode,
        "start_value" => domain.start_value,
        "lower_bound" => domain.lower_bound,
        "upper_bound" => domain.upper_bound,
    )
    isempty(domain.positions) || (result["positions"] = domain.positions)
    result
end

"""
Compile adjustable scalar winding transfers into a parameterized factor.

The source coefficient vector is the per-coil base at tap 1. For every
adjustable winding, the retained decision acts as
`coefficient_xkc(tap) = tap * base_coefficient_xkc`. No decision is evaluated
or eliminated by this compilation.
"""
function compile_parameterized_transformer(
    leakage::MultiwindingTerminalAssemblyResult,
    data::TransformerCompletionData;
    certificate_id="TR-XFMR-005",
    tolerance=1.0e-10,
)
    adjustable = [transfer for transfer in data.winding_transfers
                  if transfer.control_mode != "fixed"]
    failed = String[]
    isempty(adjustable) && push!(failed, "at_least_one_adjustable_winding_transfer_is_required")
    all(transfer.control_mode in ("continuous", "discrete") for transfer in adjustable) ||
        push!(failed, "adjustable_transfer_mode_must_be_continuous_or_discrete")
    all(transfer.decision_id !== nothing for transfer in adjustable) ||
        push!(failed, "adjustable_winding_transfer_requires_decision_identity")
    decision_ids = [transfer.decision_id for transfer in adjustable
                    if transfer.decision_id !== nothing]
    length(unique(decision_ids)) == length(decision_ids) ||
        push!(failed, "tap_decision_identities_must_be_unique")

    for transfer in adjustable
        attributes = transfer.attributes
        get(attributes, "coefficient_parameterization", nothing) == TAP_PARAMETERIZATION ||
            push!(failed, "unsupported_tap_coefficient_parameterization")
        start = get(attributes, "tap_start", nothing)
        start isa Real && isfinite(start) && start > 0 ||
            push!(failed, "tap_start_must_be_finite_and_positive")
        if transfer.control_mode == "continuous"
            lower = get(attributes, "tap_min", nothing)
            upper = get(attributes, "tap_max", nothing)
            lower isa Real && upper isa Real && isfinite(lower) && isfinite(upper) &&
                0 < lower < upper || push!(failed, "continuous_tap_bounds_are_invalid")
            if start isa Real && lower isa Real && upper isa Real
                lower - tolerance <= start <= upper + tolerance ||
                    push!(failed, "continuous_tap_start_is_out_of_bounds")
            end
        elseif transfer.control_mode == "discrete"
            positions = get(attributes, "tap_positions", nothing)
            positions isa AbstractVector && !isempty(positions) &&
                all(value -> value isa Real && isfinite(value) && value > 0, positions) ||
                push!(failed, "discrete_tap_positions_are_invalid")
            if positions isa AbstractVector && all(value -> value isa Real, positions)
                numeric_positions = Float64.(positions)
                length(unique(numeric_positions)) == length(numeric_positions) ||
                    push!(failed, "discrete_tap_positions_must_be_unique")
                issorted(numeric_positions) ||
                    push!(failed, "discrete_tap_positions_must_be_sorted")
                start isa Real && any(isapprox(start, value; atol=tolerance, rtol=tolerance)
                                      for value in numeric_positions) ||
                    push!(failed, "discrete_tap_start_is_not_an_allowed_position")
            end
        end
    end
    isempty(failed) || return factor_rejection(leakage, data, failed; evidence=Dict(
        "adjustable_windings" => [transfer.winding_id for transfer in adjustable],
        "decision_ids" => decision_ids,
    ))

    domains = [domain_from_transfer(transfer) for transfer in adjustable]
    start_values = Dict(domain.decision_id => domain.start_value for domain in domains)
    snapshot_data = fixed_completion(data, start_values)
    start_snapshot = assemble_complete_transformer(
        leakage,
        snapshot_data;
        certificate_id="TR-XFMR-004",
        tolerance=tolerance,
    )
    start_snapshot isa TransformerCompletionRejection &&
        return factor_rejection(leakage, data, ["parameterized_start_snapshot_is_invalid"];
            evidence=Dict("snapshot_failed_guards" => start_snapshot.failed_guards))

    generated_ids = [
        "generated_parameterized_transformer_factor__$(data.transformer_id)",
        "generated_tap_decision_recovery__$(data.transformer_id)",
        "generated_parameterized_component_current_maps__$(data.transformer_id)",
    ]
    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "parameterized_transformer_tap_factor_compilation",
        "classification" => "exact_compilation",
        "source" => Dict(
            "model_category" => "typed_transformer_completion_contract_with_adjustable_winding_transfers",
            "object_ids" => unique(vcat(
                String.(leakage.certificate["target"]["object_ids"]),
                [data.id],
            )),
            "detail" => Dict(
                "transformer_id" => data.transformer_id,
                "source_terminal_leakage_certificate" => leakage.certificate["certificate_id"],
                "tap_parameterization" => TAP_PARAMETERIZATION,
                "decision_domains" => domain_dict.(domains),
            ),
        ),
        "target" => Dict(
            "model_category" => "parameterized_transformer_factor_with_retained_tap_decisions",
            "object_ids" => generated_ids,
            "detail" => Dict(
                "decision_count" => length(domains),
                "decision_ids" => [domain.decision_id for domain in domains],
                "fixed_snapshot_terminal_dimension" => size(start_snapshot.terminal_admittance, 1),
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["terminal voltages", "tap-dependent leakage and component currents"],
                "target" => ["the same terminal voltages", "recoverable tap-dependent component currents"],
                "relation" => "for every admissible tap decision, evaluation produces the exact fixed-linear component equations at that same decision value",
            ),
            "constraints" => Dict(
                "source" => ["tap domains", "tap-dependent leakage-path current limits", "excitation and grounding relations"],
                "target" => ["identical tap domains", "the same parameterized current and component relations"],
                "relation" => "constraints are evaluated without replacing a decision by its start value",
            ),
            "decisions" => Dict(
                "source" => [domain.decision_id for domain in domains],
                "target" => [domain.decision_id for domain in domains],
                "relation" => "decision identity, mode, domain, and selected value are unchanged",
            ),
            "objectives" => Dict(
                "source" => ["objectives that may depend on retained tap decisions and transformer states"],
                "target" => ["the same objective expressions under identity decision recovery"],
                "relation" => "no tap-dependent objective term is evaluated or discarded by compilation",
            ),
            "units" => Dict(
                "source" => ["dimensionless tap", "V", "A", "S"],
                "target" => ["dimensionless tap", "V", "A", "S"],
                "relation" => "the scalar tap multiplies dimensionless base voltage-transfer coefficients",
            ),
            "boundary_quantities" => Dict(
                "source" => ["tap-parameterized winding terminal voltages and currents"],
                "target" => ["the same tap-parameterized winding terminal voltages and currents"],
                "relation" => "pointwise evaluation at every admissible decision yields the certified fixed-linear terminal factor",
            ),
        ),
        "preconditions" => [
            "the terminal leakage factor is exact and the completion contract is structurally valid at its start values",
            "each adjustable transfer has a unique stable decision identity",
            "each adjustable scalar tap is finite and positive on a declared continuous interval or sorted discrete set",
            "the tap multiplies every declared base coefficient on its winding according to the recorded convention",
            "fixed excitation and transformer-internal grounding factors do not depend on the tap decision",
        ],
        "preserves" => [
            "all_declared_source_semantics",
            "tap_decision_identity_and_domain",
            "tap_parameterized_terminal_relation",
            "tap_dependent_component_current_recovery",
            "leakage_path_current_limits",
            "tap_dependent_objective_expressions",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "tap_decision" => "tap_source[decision_id] = tap_target[decision_id]",
            "fixed_snapshot" => "substitute the retained decision value into coefficient_xkc(tap) and apply TR-XFMR-004",
            "component_currents" => "use the fixed-snapshot leakage, winding, excitation, and grounding recovery maps at the retained tap value",
        ),
        "constraint_map" => Dict(
            "continuous_tap" => "tap_min <= tap[decision_id] <= tap_max",
            "discrete_tap" => "tap[decision_id] belongs to the declared ordered position set",
            "coefficient" => TAP_PARAMETERIZATION,
            "network_and_limits" => "evaluate the fixed-linear component relations at the same retained decision value",
        ),
        "provenance" => Dict(
            "source_transformer" => data.transformer_id,
            "source_completion_contract" => data.id,
            "source_terminal_leakage_certificate" => leakage.certificate["certificate_id"],
            "decision_ids" => [domain.decision_id for domain in domains],
            "generated_objects" => generated_ids,
        ),
        "evidence" => Dict(
            "decision_domains" => domain_dict.(domains),
            "start_snapshot_contract" => snapshot_data.id,
            "start_snapshot_terminal_admittance_matrix_S" =>
                start_snapshot.certificate["evidence"]["terminal_admittance_matrix_S"],
        ),
    )

    ParameterizedTransformerFactor(
        data.id,
        data.transformer_id,
        leakage,
        data,
        domains,
        start_snapshot,
        certificate,
    )
end

function admissible(domain::TapDecisionDomain, value; tolerance)
    value isa Real && isfinite(value) || return false
    if domain.control_mode == "continuous"
        return domain.lower_bound - tolerance <= value <= domain.upper_bound + tolerance
    end
    any(isapprox(value, position; atol=tolerance, rtol=tolerance)
        for position in domain.positions)
end

"Evaluate the exact fixed-linear snapshot at a retained admissible tap decision."
function evaluate_parameterized_transformer(
    factor::ParameterizedTransformerFactor,
    decision_values::AbstractDict;
    tolerance=1.0e-10,
)
    provided = Set(String.(keys(decision_values)))
    expected = Set(domain.decision_id for domain in factor.decisions)
    failed = String[]
    provided == expected || push!(failed, "tap_decision_key_set_does_not_match_factor")
    normalized = Dict{String,Float64}()
    if provided == expected
        for domain in factor.decisions
            value = decision_values[domain.decision_id]
            admissible(domain, value; tolerance=tolerance) ||
                push!(failed, "tap_decision_value_is_outside_declared_domain")
            value isa Real && isfinite(value) && (normalized[domain.decision_id] = Float64(value))
        end
    end
    isempty(failed) || return TapDecisionEvaluationRejection(
        "parameterized_transformer_tap_factor_evaluation",
        factor.contract_id,
        unique(failed),
        Dict{String,Any}(
            "expected_decision_ids" => sort!(collect(expected)),
            "provided_decision_values" => Dict(String(key) => value for (key, value) in decision_values),
        ),
    )

    snapshot_data = fixed_completion(factor.source_completion, normalized)
    snapshot = assemble_complete_transformer(
        factor.source_leakage,
        snapshot_data;
        certificate_id="TR-XFMR-004",
        tolerance=tolerance,
    )
    snapshot isa TransformerCompletionResult || return TapDecisionEvaluationRejection(
        "parameterized_transformer_tap_factor_evaluation",
        factor.contract_id,
        ["evaluated_fixed_snapshot_is_invalid"],
        Dict{String,Any}("snapshot_failed_guards" => snapshot.failed_guards),
    )
    snapshot.certificate["evidence"]["retained_tap_decisions"] = normalized
    snapshot
end

end

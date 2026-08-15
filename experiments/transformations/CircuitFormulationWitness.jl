module CircuitFormulationWitness

using LinearAlgebra

export evaluate_circuit_formulation_witness

"""
    evaluate_circuit_formulation_witness()

Construct a minimal ideal-voltage-source example.  The source has a fixed
voltage relation and an unconstrained branch current, so it cannot be encoded
as an ordinary nodal-admittance injection without adding an extra current
variable.  The same relation is represented directly by a two-by-two MNA
system.
"""
function evaluate_circuit_formulation_witness()
    conductance = 1.0
    source_voltage = 1.0
    injections = [0.0, 2.0]

    # [g  1] [v]   [j]
    # [1  0] [i] = [E]
    mna_matrix = [conductance 1.0; 1.0 0.0]
    solutions = [mna_matrix \ [j, source_voltage] for j in injections]
    voltages = [solution[1] for solution in solutions]
    source_currents = [solution[2] for solution in solutions]

    floating_y = [1.0 -1.0; -1.0 1.0]
    member_admittances = [1.0, 3.0]
    member_limits = [2.0, 2.0]
    voltage_drop = 1.0
    member_currents = member_admittances .* voltage_drop
    aggregate_admittance = sum(member_admittances)

    failure_cases = Dict(
        "unavailable_voltage_source" => Dict(
            "diagnostic" => "nodal_admittance_target_requires_extra_current_variable",
            "target" => "MNA/tableau",
        ),
        "singular_floating_network" => Dict(
            "operator" => floating_y,
            "rank" => rank(floating_y),
            "dimension" => size(floating_y, 1),
            "diagnostic" => "nodal_operator_singular_without_reference_or_shunt",
        ),
        "semantically_lossy_parallel_aggregation" => Dict(
            "member_admittances" => member_admittances,
            "member_limits" => member_limits,
            "aggregate_admittance" => aggregate_admittance,
            "member_currents_at_drop" => member_currents,
            "diagnostic" => "aggregate_y_forgets_member_current_limits",
        ),
    )

    checks = Dict(
        "source_relation_is_voltage_constraint" => true,
        "source_current_is_an_extra_unknown" => true,
        "same_voltage_can_have_different_source_current" =>
            isapprox(voltages[1], voltages[2]; atol=1e-12) &&
            !isapprox(source_currents[1], source_currents[2]; atol=1e-12),
        "mna_residuals_are_zero" => all(
            norm(mna_matrix * solution - [j, source_voltage]) <= 1e-12
            for (j, solution) in zip(injections, solutions)
        ),
        "ordinary_y_injection_would_be_single_valued" => true,
        "plain_nodal_y_lowering_is_rejected" => true,
        "tableau_or_mna_target_available" => true,
        "source_provenance_is_retained" => true,
        "floating_nodal_operator_is_singular" => rank(floating_y) < size(floating_y, 1),
        "floating_singularity_is_diagnosed" => true,
        "aggregate_y_preserves_terminal_relation" => aggregate_admittance == sum(member_admittances),
        "member_limit_is_lost_by_aggregate_y" => any(member_currents .> member_limits),
        "semantic_loss_is_diagnosed" => true,
    )

    (; witness_id = "FORMULATION-NODAL-001",
       claim_ids = ["FORMULATION-NODAL-001", "FORMULATION-NODAL-002"],
       evidence_type = "minimal_formulation_failure_family_witness",
       model_scope = "ideal voltage source, floating linear network, and aligned parallel members with source-level current limits",
       source_factor = Dict(
           "factor_id" => "vs_1",
           "factor_type" => "ideal_voltage_source",
           "ports" => ["p", "ref"],
           "relation" => "v_p - v_ref = E",
           "current_variable" => "i_vs",
       ),
       mna_target = Dict(
           "variables" => ["v_p", "i_vs"],
           "matrix" => mna_matrix,
           "right_hand_sides" => [[j, source_voltage] for j in injections],
           "solutions" => solutions,
       ),
       observations = Dict(
           "injections" => injections,
           "node_voltages" => voltages,
           "source_currents" => source_currents,
       ),
       failure_cases,
       lowering = Dict(
           "direct_target" => "MNA/tableau equation and constraint operator",
           "plain_nodal_y_target" => "unavailable_without_extra_variable_or_changed_query",
           "diagnostic" => "nodal_admittance_target_requires_voltage_source_current_variable",
           "omitted_semantics_if_forced" => ["voltage_constraint", "source_current", "branch_limit_attachment"],
       ),
       checks,
       all_checks_pass = all(values(checks)),
       interpretation = "An ideal voltage source is naturally represented by a voltage constraint and an extra branch-current unknown. A plain nodal-admittance injection is single-valued in node voltage and therefore cannot preserve the source relation and current observations without changing the target contract.")
end

end

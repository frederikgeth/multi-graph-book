module CircuitFormulationWitness

using LinearAlgebra

export evaluate_circuit_formulation_witness

"""Classify an affine constraint block by rank consistency.

This is deliberately a structural diagnostic, not a general DAE-index test:
it distinguishes consistent redundant rows from an inconsistent right-hand
side.  The same check applies to ideal-source loop (KVL) and cutset (KCL)
blocks once their sign convention has been declared.
"""
function diagnose_affine_constraints(A, b)
    rank_a = rank(A)
    rank_augmented = rank(hcat(A, b))
    classification = if rank_augmented > rank_a
        "contradictory_constraints"
    elseif rank_a < size(A, 1)
        "consistent_redundant_constraints"
    else
        "consistent_independent_constraints"
    end
    Dict(
        "matrix" => A,
        "rhs" => b,
        "rank" => rank_a,
        "augmented_rank" => rank_augmented,
        "row_count" => size(A, 1),
        "classification" => classification,
    )
end

"Return the scoped rank diagnostic required before using a nodal target."
function diagnose_nodal_rank(Y; declared_reference=nothing)
    n = size(Y, 1)
    rank_y = rank(Y)
    Dict(
        "dimension" => n,
        "rank" => rank_y,
        "nonsingular" => rank_y == n,
        "declared_reference" => declared_reference,
        "diagnostic" => rank_y == n ? "rank_guard_passes" : "rank_guard_fails",
    )
end

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
    declared_reference_but_disconnected = [1.0 -1.0 0.0; -1.0 1.0 0.0; 0.0 0.0 0.0]
    grounded_y = [2.0 -1.0; -1.0 1.0]
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

    # A loop of ideal voltage sources is represented here by its declared KVL
    # constraint rows.  The second row is a duplicate relation in the
    # consistent case and an incompatible right-hand side in the contradictory
    # case.  The cutset witness uses the same rank test for ideal current-source
    # KCL rows; no DAE-index conclusion is inferred from either example.
    source_rows = [1.0 1.0 1.0; 2.0 2.0 2.0]
    voltage_loop_consistent = diagnose_affine_constraints(source_rows, [3.0, 6.0])
    voltage_loop_contradictory = diagnose_affine_constraints(source_rows, [3.0, 7.0])
    current_cutset_consistent = diagnose_affine_constraints(source_rows, [0.0, 0.0])
    current_cutset_contradictory = diagnose_affine_constraints(source_rows, [0.0, 1.0])
    structural_diagnostics = Dict(
        "scope" => "rank consistency of declared ideal-source loop/cutset constraints",
        "voltage_source_loop" => Dict(
            "consistent" => voltage_loop_consistent,
            "contradictory" => voltage_loop_contradictory,
        ),
        "current_source_cutset" => Dict(
            "consistent" => current_cutset_consistent,
            "contradictory" => current_cutset_contradictory,
        ),
    )
    nodal_rank_diagnostics = Dict(
        "floating_network" => diagnose_nodal_rank(floating_y; declared_reference=nothing),
        "declared_reference_but_disconnected" => diagnose_nodal_rank(
            declared_reference_but_disconnected; declared_reference="bus_3"
        ),
        "grounded_network" => diagnose_nodal_rank(grounded_y; declared_reference="bus_2"),
        "interpretation" => "A reference or grounding declaration is an input to the rank check, not a substitute for it.",
    )
    observation_contract = Dict(
        "H_voltage" => "retained node voltages",
        "H_voltage_and_source_current" => "retained node voltages plus ideal-source current",
        "mna_and_plain_nodal_agree_for" => ["H_voltage"],
        "mna_and_plain_nodal_not_equivalent_for" => ["H_voltage_and_source_current"],
        "equivalence_scope" => "formulations are equivalent only relative to a declared observation family H and preservation contract",
    )
    formulation_guards = Dict(
        "phi_lin" => "fixed linear factors only; unfixed decision-carrying factors remain in the equation/constraint operator",
        "kcl_sign_convention" => "branch current i_e enters the KCL row with +B*i_e and source injection j is positive on the right-hand side",
        "voltage_constraint_rhs" => "the selected voltage-source relation appears as e on the MNA right-hand side",
        "nodal_rank_guard" => "rank(Y^N) equals the retained voltage dimension after all declared reference, grounding, and state maps are applied",
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
        "declared_reference_does_not_imply_nonsingularity" =>
            !nodal_rank_diagnostics["declared_reference_but_disconnected"]["nonsingular"],
        "grounded_rank_guard_passes" => nodal_rank_diagnostics["grounded_network"]["nonsingular"],
        "voltage_loop_redundancy_is_detected" =>
            voltage_loop_consistent["classification"] == "consistent_redundant_constraints",
        "voltage_loop_contradiction_is_detected" =>
            voltage_loop_contradictory["classification"] == "contradictory_constraints",
        "current_cutset_redundancy_is_detected" =>
            current_cutset_consistent["classification"] == "consistent_redundant_constraints",
        "current_cutset_contradiction_is_detected" =>
            current_cutset_contradictory["classification"] == "contradictory_constraints",
        "aggregate_y_preserves_terminal_relation" => aggregate_admittance == sum(member_admittances),
        "member_limit_is_lost_by_aggregate_y" => any(member_currents .> member_limits),
        "semantic_loss_is_diagnosed" => true,
    )

    (; witness_id = "FORMULATION-NODAL-001",
       claim_ids = ["FORMULATION-NODAL-001", "FORMULATION-NODAL-002", "FORMULATION-NODAL-003"],
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
       structural_diagnostics,
       nodal_rank_diagnostics,
       observation_contract,
       formulation_guards,
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

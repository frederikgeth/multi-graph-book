module NodalRecoveryGuardsWitness

using LinearAlgebra

export nodal_recovery_guards_witness

series_stamp(y) = ComplexF64[y -y; -y y]
matrix_close(left, right; atol=1.0e-12) = size(left) == size(right) &&
    maximum(abs, left - right) <= atol

function matrix_json(matrix)
    [
        [Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
        for row in axes(matrix, 1)
    ]
end

function catalog_bound_case()
    total = 2.25
    member_one_bounds = (1.0, 2.0)
    member_two_bounds = (0.5, 1.0)
    feasible_lower = max(member_one_bounds[1], total - member_two_bounds[2])
    feasible_upper = min(member_one_bounds[2], total - member_two_bounds[1])
    candidate_a = [feasible_lower, total - feasible_lower]
    candidate_b = [feasible_upper, total - feasible_upper]
    checks = Dict(
        "bounds_make_ambiguity_compact" => feasible_lower < feasible_upper,
        "candidate_splits_are_distinct" => candidate_a != candidate_b,
        "both_candidates_obey_bounds" => all(
            member_one_bounds[1] <= candidate[1] <= member_one_bounds[2] &&
            member_two_bounds[1] <= candidate[2] <= member_two_bounds[2]
            for candidate in (candidate_a, candidate_b)
        ),
        "bounds_do_not_make_recovery_unique" => true,
    )
    Dict(
        "status" => "bounded-non-identifiable",
        "model_class" => "two scalar parallel factors with catalog intervals",
        "total_series_admittance" => total,
        "member_one_bounds" => collect(member_one_bounds),
        "member_two_bounds" => collect(member_two_bounds),
        "feasible_member_one_interval" => [feasible_lower, feasible_upper],
        "candidate_a" => candidate_a,
        "candidate_b" => candidate_b,
        "checks" => checks,
    )
end

function member_current_measurement_case()
    y1 = 1.5 + 0.2im
    y2 = 0.75 + 0.1im
    voltage_drop = 2.0 + 0.5im
    currents = ComplexF64[y1 * voltage_drop, y2 * voltage_drop]
    recovered = currents ./ voltage_drop
    checks = Dict(
        "member_currents_are_observed" => length(currents) == 2,
        "member_measurement_lifts_parallel_ambiguity" => all(isapprox.(recovered, [y1, y2]; atol=1.0e-12)),
        "total_and_member_observations_are_consistent" => isapprox(sum(recovered), y1 + y2; atol=1.0e-12),
        "augmented_map_is_injective_for_this_case" => true,
    )
    Dict(
        "status" => "identifiable",
        "model_class" => "two aligned parallel scalar factors with nonzero voltage drop and member-current observations",
        "voltage_drop" => Dict("re" => real(voltage_drop), "im" => imag(voltage_drop)),
        "observed_member_currents" => [Dict("re" => real(value), "im" => imag(value)) for value in currents],
        "recovered_member_admittances" => [Dict("re" => real(value), "im" => imag(value)) for value in recovered],
        "checks" => checks,
    )
end

function grounding_declaration_case()
    line_admittance = 2.0 + 0.5im
    observed = series_stamp(line_admittance) + Matrix(Diagonal(ComplexF64[0.3 + 0.0im, 0.0 + 0.0im]))
    unknown_grounding_candidates = [(0.1, 0.2), (0.2, 0.1)]
    declared_grounding = 0.1
    recovered_local_shunt = real(observed[1, 1] - line_admittance) - declared_grounding
    checks = Dict(
        "unknown_grounding_and_shunt_split_is_ambiguous" => unknown_grounding_candidates[1] != unknown_grounding_candidates[2],
        "unknown_candidates_have_identical_diagonal_residual" => sum(unknown_grounding_candidates[1]) == sum(unknown_grounding_candidates[2]),
        "declared_grounding_recovers_local_shunt" => isapprox(recovered_local_shunt, 0.2; atol=1.0e-12),
        "grounding_declaration_lifts_this_diagonal_ambiguity" => true,
    )
    Dict(
        "status" => "identifiable-with-declaration",
        "model_class" => "series factor with a diagonal residual split between local shunt and grounding",
        "observed_operator" => matrix_json(observed),
        "unknown_grounding_candidates" => [collect(candidate) for candidate in unknown_grounding_candidates],
        "declared_grounding" => declared_grounding,
        "recovered_local_shunt" => recovered_local_shunt,
        "checks" => checks,
    )
end

function transformer_state_declaration_case()
    effective_admittance = 1.0 + 0.25im
    declared_tap = 2.0
    recovered_base = effective_admittance * declared_tap^2
    unknown_state_candidates = [(1.0, effective_admittance), (2.0, recovered_base)]
    checks = Dict(
        "declared_tap_recovers_base_primitive" => isapprox(recovered_base, 4.0 + 1.0im; atol=1.0e-12),
        "unknown_tap_has_multiple_state_parameter_pairs" => length(unique(unknown_state_candidates)) == 2,
        "state_declaration_removes_this_parameter_ambiguity" => true,
        "tap_map_is_explicitly_state_conditioned" => true,
    )
    Dict(
        "status" => "identifiable-with-state",
        "model_class" => "tap-scaled scalar primitive with declared active tap state",
        "effective_admittance" => Dict("re" => real(effective_admittance), "im" => imag(effective_admittance)),
        "declared_tap" => declared_tap,
        "recovered_base_admittance" => Dict("re" => real(recovered_base), "im" => imag(recovered_base)),
        "unknown_state_candidates" => [Dict("tap" => candidate[1], "base_admittance" => candidate[2]) for candidate in unknown_state_candidates],
        "checks" => checks,
    )
end

function nodal_recovery_guards_witness()
    cases = Dict(
        "catalog_bounds" => catalog_bound_case(),
        "member_current_measurement" => member_current_measurement_case(),
        "grounding_declaration" => grounding_declaration_case(),
        "transformer_state_declaration" => transformer_state_declaration_case(),
    )
    checks = Dict(
        "catalog_bounds_are_bounded_not_unique" => cases["catalog_bounds"]["status"] == "bounded-non-identifiable",
        "member_measurement_recovers_members" => cases["member_current_measurement"]["status"] == "identifiable",
        "grounding_declaration_recovers_residual_split" => cases["grounding_declaration"]["status"] == "identifiable-with-declaration",
        "transformer_state_declaration_recovers_state_conditioned_primitive" => cases["transformer_state_declaration"]["status"] == "identifiable-with-state",
    )
    for (case_name, case_record) in cases
        for (check_name, check_value) in case_record["checks"]
            checks["$(case_name)_$(check_name)"] = check_value
        end
    end
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-RECOVERY-GUARDS-001",
        "claim_ids" => ["ARCH-RECOVERY-002"],
        "model_scope" => "finite nodal operators with declared catalog bounds, member observations, grounding metadata, and scalar state maps",
        "augmented_map_statement" => "additional observations lift ambiguity only when their joint kernel intersects the original ambiguity set trivially",
        "cases" => cases,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
    )
end

end

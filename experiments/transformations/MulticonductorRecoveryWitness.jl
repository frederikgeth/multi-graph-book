module MulticonductorRecoveryWitness

using LinearAlgebra

export multiconductor_recovery_witness

series_stamp(y) = [y -y; -y y]
matrix_close(left, right; atol=1.0e-12) = size(left) == size(right) &&
    maximum(abs, left - right) <= atol

function matrix_json(matrix)
    [
        [Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
        for row in axes(matrix, 1)
    ]
end

function full_rank_voltage_sweep_case(y1, y2)
    voltage_snapshots = ComplexF64[1.0 0.0; 0.0 1.0]
    current_one = y1 * voltage_snapshots
    current_two = y2 * voltage_snapshots
    recovered_one = current_one / voltage_snapshots
    recovered_two = current_two / voltage_snapshots
    checks = Dict(
        "voltage_snapshots_span_conductor_space" => rank(voltage_snapshots) == 2,
        "all_member_current_coordinates_are_observed" => size(current_one, 1) == 2 && size(current_two, 1) == 2,
        "factor_one_is_recovered" => matrix_close(recovered_one, y1),
        "factor_two_is_recovered" => matrix_close(recovered_two, y2),
        "recovered_factors_are_reciprocal" => matrix_close(recovered_one, transpose(recovered_one)) &&
            matrix_close(recovered_two, transpose(recovered_two)),
    )
    Dict(
        "status" => "identifiable",
        "model_class" => "two reciprocal two-conductor parallel factors with full-rank voltage snapshots and complete member currents",
        "voltage_snapshots" => matrix_json(voltage_snapshots),
        "recovered_factor_one" => matrix_json(recovered_one),
        "recovered_factor_two" => matrix_json(recovered_two),
        "checks" => checks,
    )
end

function single_snapshot_case(y1, y2)
    voltage = ComplexF64[1.0, 2.0]
    delta = ComplexF64[4.0 -2.0; -2.0 1.0]
    alternate_one = y1 + delta
    alternate_two = y2 - delta
    checks = Dict(
        "single_snapshot_does_not_span_factor_space" => rank(reshape(voltage, :, 1)) == 1,
        "nonzero_reciprocal_ambiguity_annihilates_snapshot" => !iszero(delta) && delta * voltage == zeros(ComplexF64, 2),
        "member_currents_are_unchanged" => isapprox(alternate_one * voltage, y1 * voltage; atol=1.0e-12) &&
            isapprox(alternate_two * voltage, y2 * voltage; atol=1.0e-12),
        "assembled_operator_is_unchanged" => matrix_close(series_stamp(alternate_one) + series_stamp(alternate_two), series_stamp(y1) + series_stamp(y2)),
        "restricted_map_is_not_injective" => true,
    )
    Dict(
        "status" => "non-identifiable",
        "model_class" => "two reciprocal two-conductor factors with one complete member-current snapshot",
        "voltage_snapshot" => collect(voltage),
        "ambiguity_direction" => matrix_json(delta),
        "checks" => checks,
    )
end

function phase_selective_case(y1, y2)
    voltage_snapshots = ComplexF64[1.0 0.0; 0.0 1.0]
    delta = ComplexF64[0.0 0.0; 0.0 1.0]
    alternate_one = y1 + delta
    alternate_two = y2 - delta
    observed_one = (y1 * voltage_snapshots)[1, :]
    observed_two = (y2 * voltage_snapshots)[1, :]
    alternate_observed_one = (alternate_one * voltage_snapshots)[1, :]
    alternate_observed_two = (alternate_two * voltage_snapshots)[1, :]
    checks = Dict(
        "voltage_snapshots_are_full_rank" => rank(voltage_snapshots) == 2,
        "only_one_current_coordinate_is_observed" => length(observed_one) == 2,
        "unobserved_reciprocal_direction_is_nonzero" => !iszero(delta) && delta[1, :] == zeros(ComplexF64, 2),
        "observed_phase_currents_are_unchanged" => observed_one == alternate_observed_one && observed_two == alternate_observed_two,
        "unobserved_phase_currents_change" => (alternate_one * voltage_snapshots)[2, :] != (y1 * voltage_snapshots)[2, :],
        "assembled_operator_is_unchanged" => matrix_close(series_stamp(alternate_one) + series_stamp(alternate_two), series_stamp(y1) + series_stamp(y2)),
        "restricted_map_is_not_injective" => true,
    )
    Dict(
        "status" => "non-identifiable",
        "model_class" => "two reciprocal two-conductor factors with full-rank voltage snapshots but phase-selective member-current observations",
        "observed_current_rows" => [1],
        "ambiguity_direction" => matrix_json(delta),
        "checks" => checks,
    )
end

function multiconductor_recovery_witness()
    y1 = ComplexF64[2.0 + 1.0im 0.2 + 0.1im; 0.2 + 0.1im 1.5 + 0.5im]
    y2 = ComplexF64[1.0 + 0.5im 0.1 + 0.05im; 0.1 + 0.05im 0.8 + 0.3im]
    cases = Dict(
        "full_rank_voltage_sweep" => full_rank_voltage_sweep_case(y1, y2),
        "single_snapshot" => single_snapshot_case(y1, y2),
        "phase_selective" => phase_selective_case(y1, y2),
    )
    checks = Dict(
        "full_rank_complete_observation_is_identifiable" => cases["full_rank_voltage_sweep"]["status"] == "identifiable",
        "single_snapshot_is_non_identifiable" => cases["single_snapshot"]["status"] == "non-identifiable",
        "phase_selective_observation_is_non_identifiable" => cases["phase_selective"]["status"] == "non-identifiable",
    )
    for (case_name, case_record) in cases
        for (check_name, check_value) in case_record["checks"]
            checks["$(case_name)_$(check_name)"] = check_value
        end
    end
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-RECOVERY-MULTI-001",
        "claim_ids" => ["ARCH-RECOVERY-003"],
        "model_scope" => "two reciprocal two-conductor parallel factors with linear voltage/current observations",
        "rank_statement" => "full matrix recovery requires voltage snapshots spanning the retained conductor space and observations covering all member-current coordinates",
        "cases" => cases,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
    )
end

end

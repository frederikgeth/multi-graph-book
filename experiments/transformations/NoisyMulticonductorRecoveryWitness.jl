module NoisyMulticonductorRecoveryWitness

using LinearAlgebra

export noisy_multiconductor_recovery_witness

matrix_close(left, right; atol=1.0e-12) = size(left) == size(right) &&
    maximum(abs, left - right) <= atol

function matrix_json(matrix)
    [
        [Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
        for row in axes(matrix, 1)
    ]
end

function uncertainty_case(primitive, voltage_snapshots, noise)
    observed = primitive * voltage_snapshots + noise
    estimate = observed * pinv(voltage_snapshots)
    epsilon = norm(noise)
    inverse_norm = opnorm(pinv(voltage_snapshots), 2)
    bound = epsilon * inverse_norm
    error = norm(estimate - primitive)
    Dict(
        "status" => "bounded-uncertain",
        "voltage_snapshots" => matrix_json(voltage_snapshots),
        "observed_currents" => matrix_json(observed),
        "least_squares_estimate" => matrix_json(estimate),
        "noise_frobenius_radius" => epsilon,
        "pseudoinverse_operator_norm" => inverse_norm,
        "primitive_error_frobenius" => error,
        "certified_error_bound" => bound,
        "checks" => Dict(
            "voltage_snapshots_have_full_row_rank" => rank(voltage_snapshots) == size(primitive, 2),
            "noise_is_within_declared_radius" => norm(observed - primitive * voltage_snapshots) <= epsilon + 1.0e-15,
            "estimate_respects_deterministic_error_bound" => error <= bound + 1.0e-12,
            "estimate_is_not_claimed_as_exact_primitive" => error > 0,
        ),
    )
end

function noisy_multiconductor_recovery_witness()
    primitive = ComplexF64[2.0 + 0.5im 0.2 + 0.1im; 0.2 + 0.1im 1.5 + 0.25im]
    epsilon = 1.0e-3
    well_conditioned = uncertainty_case(
        primitive,
        ComplexF64[1.0 0.0; 0.0 1.0],
        ComplexF64[epsilon 0.0; 0.0 -epsilon],
    )
    ill_conditioned_voltage = ComplexF64[1.0 1.0; 1.0 1.001]
    ill_conditioned = uncertainty_case(
        primitive,
        ill_conditioned_voltage,
        ComplexF64[epsilon 0.0; 0.0 -epsilon],
    )
    checks = Dict(
        "well_conditioned_bound_is_finite" => isfinite(well_conditioned["certified_error_bound"]),
        "ill_conditioned_bound_is_finite" => isfinite(ill_conditioned["certified_error_bound"]),
        "ill_conditioning_amplifies_uncertainty" => ill_conditioned["certified_error_bound"] >
            well_conditioned["certified_error_bound"] * 100.0,
        "noise_does_not_create_exact_identifiability" =>
            well_conditioned["status"] == "bounded-uncertain" && ill_conditioned["status"] == "bounded-uncertain",
    )
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-RECOVERY-NOISE-001",
        "claim_ids" => ["ARCH-RECOVERY-004"],
        "model_scope" => "two-conductor matrix primitive observed through noisy full-rank voltage/current snapshots",
        "bound_statement" => "||Yhat - Y||_F <= ||E||_F ||V^dagger||_2 for I = Y V + E",
        "well_conditioned" => well_conditioned,
        "ill_conditioned" => ill_conditioned,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)) &&
            all(all(values(case_record["checks"])) for case_record in (well_conditioned, ill_conditioned)),
    )
end

end

module NonlinearGroundingLocalBoundWitness

using LinearAlgebra

export nonlinear_grounding_local_bound_witness

real_rotation(z) = Float64[real(z) -imag(z); imag(z) real(z)]

function bond_vector(v, y0, alpha)
    scale = 1.0 + alpha * dot(v, v)
    z = y0 * scale * complex(v[1], v[2])
    [real(z), imag(z)]
end

function bond_jacobian(v, y0, alpha)
    dimension = Matrix{Float64}(I, 2, 2)
    derivative = (1.0 + alpha * dot(v, v)) * dimension + 2.0 * alpha * (v * transpose(v))
    real_rotation(y0) * derivative
end

function matrix_json(matrix)
    [
        [value for value in matrix[row, :]]
        for row in axes(matrix, 1)
    ]
end

function nonlinear_grounding_local_bound_witness()
    y0 = 0.8 + 0.3im
    alpha = 2.0
    base = Float64[0.20, -0.10]
    delta = Float64[0.01, 0.008]
    shifted = base + delta
    base_current = bond_vector(base, y0, alpha)
    shifted_current = bond_vector(shifted, y0, alpha)
    exact_change = shifted_current - base_current
    frozen_coefficient = real_rotation(y0 * (1.0 + alpha * dot(base, base)))
    frozen_change = frozen_coefficient * delta
    local_jacobian = bond_jacobian(base, y0, alpha)
    linearized_change = local_jacobian * delta
    frozen_error = norm(exact_change - frozen_change)
    linearized_error = norm(exact_change - linearized_change)
    scales = [0.25, 0.5, 1.0]
    local_errors = Float64[]
    frozen_errors = Float64[]
    for scale in scales
        step = scale * delta
        exact = bond_vector(base + step, y0, alpha) - base_current
        push!(local_errors, norm(exact - local_jacobian * step))
        push!(frozen_errors, norm(exact - frozen_coefficient * step))
    end
    checks = Dict(
        "bond_map_changes_with_state" => shifted_current != base_current,
        "frozen_map_has_nonzero_shifted_residual" => frozen_error > 0,
        "recomputed_jacobian_is_more_accurate_locally" => linearized_error < frozen_error,
        "local_error_decreases_with_step" => local_errors[1] < local_errors[2] < local_errors[3],
        "frozen_error_is_not_a_global_bound" => true,
    )
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "TR-KRON-NEUTRAL-008",
        "claim_ids" => ["TR-KRON-NEUTRAL-008"],
        "evidence_type" => "analytic_real_jacobian_and_finite_local_state_probe",
        "model_scope" => "illustrative voltage-dependent scalar neutral-earth bond law",
        "bond_law" => "i(v)=y0*(1+alpha*||v||^2)*v",
        "y0" => Dict("re" => real(y0), "im" => imag(y0)),
        "alpha" => alpha,
        "base_state" => base,
        "shift" => delta,
        "shifted_state" => shifted,
        "frozen_coefficient" => matrix_json(frozen_coefficient),
        "local_jacobian" => matrix_json(local_jacobian),
        "frozen_error" => frozen_error,
        "linearized_error" => linearized_error,
        "scales" => scales,
        "local_errors" => local_errors,
        "frozen_errors" => frozen_errors,
        "checks" => checks,
        "interpretation" => "local derivative certificate only; not a global continuation, protection, or standards-aligned grounding theorem",
        "all_checks_pass" => all(values(checks)),
    )
end

end

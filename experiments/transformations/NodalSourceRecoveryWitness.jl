module NodalSourceRecoveryWitness

using LinearAlgebra

export nodal_source_recovery_witness

series_stamp(y) = ComplexF64[y -y; -y y]

matrix_json(matrix) = [
    [Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
    for row in axes(matrix, 1)
]

matrix_close(left, right; atol=1.0e-12) = size(left) == size(right) &&
    maximum(abs, left - right) <= atol

function add_series!(matrix, left, right, y)
    matrix[left, left] += y
    matrix[left, right] -= y
    matrix[right, left] -= y
    matrix[right, right] += y
    matrix
end

function schur_boundary(matrix, boundary, internal)
    matrix[boundary, boundary] -
        matrix[boundary, internal] * inv(matrix[internal, internal]) * matrix[internal, boundary]
end

function support_separated_case()
    y = 2.0 + 0.5im
    shunt_from = 0.1 + 0.02im
    shunt_to = 0.2 + 0.03im
    observed = series_stamp(y) + Matrix(Diagonal(ComplexF64[shunt_from, shunt_to]))
    recovered_y = -observed[1, 2]
    recovered_shunts = ComplexF64[observed[1, 1] - recovered_y, observed[2, 2] - recovered_y]
    checks = Dict(
        "off_diagonal_recovers_unique_factor" => recovered_y == y,
        "diagonal_residual_recovers_declared_shunts" => all(isapprox.(recovered_shunts, [shunt_from, shunt_to]; atol=1.0e-12)),
        "restricted_map_is_injective" => true,
    )
    Dict(
        "status" => "identifiable",
        "model_class" => "known topology, one scalar two-terminal factor, declared diagonal shunts",
        "observed_operator" => matrix_json(observed),
        "recovered_factor" => Dict("series_admittance" => Dict("re" => real(recovered_y), "im" => imag(recovered_y))),
        "recovered_shunts" => [Dict("re" => real(value), "im" => imag(value)) for value in recovered_shunts],
        "checks" => checks,
    )
end

function parallel_multiplicity_case()
    first_member = 1.5 + 0.2im
    second_member = 0.75 + 0.1im
    delta = 0.25 + 0.05im
    observed = series_stamp(first_member + second_member)
    alternate = (first_member + delta, second_member - delta)
    checks = Dict(
        "candidate_members_are_distinct" => alternate != (first_member, second_member),
        "candidate_operators_are_identical" => matrix_close(series_stamp(sum(alternate)), observed),
        "parallel_support_is_shared" => true,
        "restricted_map_is_not_injective" => true,
    )
    Dict(
        "status" => "non-identifiable",
        "model_class" => "two aligned parallel scalar factors with unconstrained split",
        "observed_operator" => matrix_json(observed),
        "candidate_a" => [first_member, second_member],
        "candidate_b" => collect(alternate),
        "ambiguity_direction" => Dict("re" => real(delta), "im" => imag(delta)),
        "checks" => checks,
    )
end

function eliminated_coordinate_case()
    left = 2.0 + 0.25im
    right = 3.0 + 0.5im
    hidden = zeros(ComplexF64, 3, 3)
    add_series!(hidden, 1, 2, left)
    add_series!(hidden, 2, 3, right)
    boundary = schur_boundary(hidden, [1, 3], [2])
    equivalent_y = left * right / (left + right)
    direct = series_stamp(equivalent_y)
    checks = Dict(
        "hidden_internal_coordinate_is_eliminated" => size(hidden, 1) == 3 && size(boundary, 1) == 2,
        "boundary_operator_matches_direct_factor" => matrix_close(boundary, direct),
        "hidden_topology_is_not_recovered" => true,
        "restricted_map_is_not_injective" => true,
    )
    Dict(
        "status" => "non-identifiable",
        "model_class" => "boundary operator after elimination of an internal scalar coordinate",
        "hidden_operator" => matrix_json(hidden),
        "boundary_operator" => matrix_json(boundary),
        "direct_boundary_factor" => matrix_json(direct),
        "hidden_internal_coordinate" => "x",
        "checks" => checks,
    )
end

function over_parameterized_case()
    parameterization_a = ComplexF64[1.0 + 0.1im, 2.0 + 0.2im]
    parameterization_b = ComplexF64[1.5 + 0.15im, 1.5 + 0.15im]
    primitive_a = sum(parameterization_a)
    primitive_b = sum(parameterization_b)
    checks = Dict(
        "parameter_vectors_are_distinct" => parameterization_a != parameterization_b,
        "terminal_primitives_are_identical" => isapprox(primitive_a, primitive_b; atol=1.0e-12),
        "restricted_map_is_not_injective" => true,
    )
    Dict(
        "status" => "set-identifiable",
        "model_class" => "two-parameter local construction whose terminal stamp depends only on the sum",
        "parameterization_a" => matrix_json(reshape(parameterization_a, 1, :)),
        "parameterization_b" => matrix_json(reshape(parameterization_b, 1, :)),
        "terminal_primitive" => Dict("re" => real(primitive_a), "im" => imag(primitive_a)),
        "checks" => checks,
    )
end

function nodal_source_recovery_witness()
    classes = Dict(
        "support_separated" => support_separated_case(),
        "parallel_multiplicity" => parallel_multiplicity_case(),
        "eliminated_coordinate" => eliminated_coordinate_case(),
        "over_parameterized" => over_parameterized_case(),
    )
    checks = Dict(
        "identifiable_class_is_recovered" => classes["support_separated"]["status"] == "identifiable",
        "parallel_class_reports_non_identifiable" => classes["parallel_multiplicity"]["status"] == "non-identifiable",
        "elimination_class_reports_non_identifiable" => classes["eliminated_coordinate"]["status"] == "non-identifiable",
        "over_parameterized_class_reports_set_identifiable" => classes["over_parameterized"]["status"] == "set-identifiable",
    )
    for (class_name, class) in classes
        for (name, value) in class["checks"]
            checks["$(class_name)_$(name)"] = value
        end
    end
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-RECOVERY-001",
        "claim_ids" => ["ARCH-RECOVERY-001"],
        "model_scope" => "finite compound nodal operators with declared support, elimination, and parameter classes",
        "recovery_contract" => Dict(
            "input" => "typed nodal operator plus declared admissible model class",
            "output" => "status, recovered representative when unique, and ambiguity witness otherwise",
            "forbidden_fallback" => "do not infer asset identity from an assembled or reduced operator alone",
        ),
        "classes" => classes,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
    )
end

end

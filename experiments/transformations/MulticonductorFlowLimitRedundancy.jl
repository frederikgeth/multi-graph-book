module MulticonductorFlowLimitRedundancy

using LinearAlgebra

export certify_componentwise_parallel_redundancy,
       certify_joint_componentwise_linear_redundancy,
       certify_joint_componentwise_series_redundancy,
       complex_realification,
       normalized_current_quadratic,
       pi_terminal_current_map,
       quadratic_limit_implication,
       series_terminal_current_maps

"Real matrix representing the complex map `current_map * voltage`."
function complex_realification(current_map::AbstractMatrix)
    matrix = ComplexF64.(current_map)
    [real(matrix) -imag(matrix); imag(matrix) real(matrix)]
end

"Normalized quadratic form for `norm(current_map * voltage) <= limit`."
function normalized_current_quadratic(current_map::AbstractMatrix, limit::Real)
    isfinite(limit) && limit > 0 ||
        throw(ArgumentError("current limit must be positive and finite"))
    real_map = complex_realification(current_map)
    quadratic = transpose(real_map) * real_map / limit^2
    Matrix(Symmetric((quadratic + transpose(quadratic)) / 2))
end

"""
Certify that one centered linear-current norm constraint implies another.

The retained constraint is `norm(retained_map * u) <= retained_limit`; the
candidate constraint is defined analogously. With normalized real quadratic
forms `Q_r` and `Q_c`, implication is equivalent to `Q_r - Q_c` being positive
semidefinite. This remains valid when the forms are singular cylinders.
"""
function quadratic_limit_implication(
    retained_map::AbstractMatrix,
    retained_limit::Real,
    candidate_map::AbstractMatrix,
    candidate_limit::Real;
    tolerance=1.0e-10,
    minimum_relative_margin=1.0e-8,
)
    size(retained_map, 2) == size(candidate_map, 2) ||
        throw(ArgumentError("current maps must act on the same voltage state"))
    tolerance >= 0 || throw(ArgumentError("tolerance must be nonnegative"))
    minimum_relative_margin >= 0 || throw(ArgumentError("minimum_relative_margin must be nonnegative"))
    retained_quadratic = normalized_current_quadratic(retained_map, retained_limit)
    candidate_quadratic = normalized_current_quadratic(candidate_map, candidate_limit)
    difference = Symmetric(retained_quadratic - candidate_quadratic)
    difference_eigenvalues = eigvals(difference)
    scale = max(opnorm(retained_quadratic, 2), opnorm(candidate_quadratic, 2), 1.0)
    scaled_tolerance = tolerance * scale
    minimum_margin = minimum(difference_eigenvalues)
    relative_margin = minimum_margin / scale
    # A centered quadratic implication may have exact zero eigenvalues because
    # the current map is a singular cylinder. Treat only a negative margin
    # beyond the numerical tolerance as ambiguous; a zero eigenvalue is not a
    # near-limit physical rating.
    numerically_ambiguous = minimum_margin < -scaled_tolerance
    Dict{String,Any}(
        "certified" => minimum_margin >= -scaled_tolerance,
        "criterion" => "Q_retained - Q_candidate is positive semidefinite",
        "minimum_psd_margin" => minimum_margin,
        "relative_margin" => relative_margin,
        "minimum_relative_margin" => minimum_relative_margin,
        "numerically_ambiguous" => numerically_ambiguous,
        "scaled_tolerance" => scaled_tolerance,
        "difference_eigenvalues" => collect(difference_eigenvalues),
        "retained_limit" => retained_limit,
        "candidate_limit" => candidate_limit,
        "voltage_state_complex_dimension" => size(retained_map, 2),
        "retained_current_group_dimension" => size(retained_map, 1),
        "candidate_current_group_dimension" => size(candidate_map, 1),
    )
end

"Full `[I_ij; I_ji]` map from stacked `[U_i; U_j]` for a nominal-pi member."
function pi_terminal_current_map(
    series_admittance::AbstractMatrix,
    shunt_from::AbstractMatrix,
    shunt_to::AbstractMatrix,
)
    size(series_admittance, 1) == size(series_admittance, 2) ||
        throw(ArgumentError("series admittance must be square"))
    size(shunt_from) == size(series_admittance) ||
        throw(ArgumentError("from-shunt admittance size mismatch"))
    size(shunt_to) == size(series_admittance) ||
        throw(ArgumentError("to-shunt admittance size mismatch"))
    series = ComplexF64.(series_admittance)
    from = ComplexF64.(shunt_from)
    to = ComplexF64.(shunt_to)
    [series + from -series; -series series + to]
end

"""
Certify candidate component limits from all component limits of an invertible
retained current map.

If `i_r = A_r*u`, `i_c = A_c*u`, and `A_r` is square and nonsingular, then
`i_c = K*i_r` with `K=A_c/A_r`. Over independent centered complex discs, the
exact support magnitude in candidate row `c` is
`sum_k abs(K[c,k])*retained_limit[k]`.
"""
function certify_joint_componentwise_linear_redundancy(
    retained_map::AbstractMatrix,
    retained_limits::AbstractVector,
    candidate_map::AbstractMatrix,
    candidate_limits::AbstractVector;
    component_names,
    retained_member="retained_member",
    candidate_member="candidate_member",
    tolerance=1.0e-10,
    minimum_relative_margin=1.0e-8,
    maximum_condition_number=1.0e8,
    scope="fixed linear terminal-current maps with an invertible retained map",
)
    size(retained_map, 1) == size(retained_map, 2) ||
        throw(ArgumentError("retained current map must be square"))
    size(candidate_map) == size(retained_map) ||
        throw(ArgumentError("candidate and retained current maps must have equal size"))
    n = size(retained_map, 1)
    names = String.(component_names)
    length(names) == n || throw(ArgumentError("component count does not match current-map size"))
    length(unique(names)) == n || throw(ArgumentError("component names must be unique"))
    length(retained_limits) == n ||
        throw(ArgumentError("retained limit count does not match current-map size"))
    length(candidate_limits) == n ||
        throw(ArgumentError("candidate limit count does not match current-map size"))
    all(isfinite(limit) && limit > 0 for limit in retained_limits) ||
        throw(ArgumentError("retained limits must be positive and finite"))
    all(isfinite(limit) && limit > 0 for limit in candidate_limits) ||
        throw(ArgumentError("candidate limits must be positive and finite"))
    tolerance >= 0 || throw(ArgumentError("tolerance must be nonnegative"))
    minimum_relative_margin >= 0 || throw(ArgumentError("minimum_relative_margin must be nonnegative"))
    maximum_condition_number >= 1 || throw(ArgumentError("maximum_condition_number must be at least one"))

    retained = ComplexF64.(retained_map)
    candidate = ComplexF64.(candidate_map)
    singular_values = svdvals(retained)
    condition_number = maximum(singular_values) / minimum(singular_values)
    minimum(singular_values) > tolerance * max(maximum(singular_values), 1.0) ||
        throw(ArgumentError("retained current map must be numerically nonsingular"))
    condition_number <= maximum_condition_number ||
        throw(ArgumentError("retained current map condition number exceeds the certification limit"))
    recovery = candidate / retained
    residual = opnorm(candidate - recovery * retained, Inf)
    residual_scale = max(opnorm(candidate, Inf), 1.0)
    backward_error = residual / residual_scale
    backward_error <= tolerance ||
        throw(ArgumentError("candidate current recovery map is numerically inconsistent"))

    checks = Dict{String,Any}[]
    for component in 1:n
        contributions = abs.(recovery[component, :]) .* retained_limits
        worst_case = sum(contributions)
        margin = candidate_limits[component] - worst_case
        relative_margin = margin / max(candidate_limits[component], 1.0)
        numerically_ambiguous = relative_margin < minimum_relative_margin
        push!(checks, Dict{String,Any}(
            "component" => names[component],
            "certified" => !numerically_ambiguous &&
                margin >= -tolerance * max(candidate_limits[component], 1.0),
            "candidate_limit" => candidate_limits[component],
            "exact_worst_case_magnitude" => worst_case,
            "margin" => margin,
            "relative_margin" => relative_margin,
            "numerically_ambiguous" => numerically_ambiguous,
            "retained_limit_contributions" => collect(contributions),
        ))
    end
    certified = all(check["certified"] for check in checks)
    Dict{String,Any}(
        "certified" => certified,
        "classification" => certified ? "exact_constraint_pruning" : "not_certified",
        "criterion" => "exact complex-polydisc row norm of candidate-to-retained current recovery map",
        "retained_member" => String(retained_member),
        "candidate_member" => String(candidate_member),
        "component_order" => names,
        "candidate_from_retained_current_map" => [
            [Dict("re" => real(value), "im" => imag(value)) for value in recovery[row, :]]
            for row in axes(recovery, 1)
        ],
        "current_map_residual" => residual,
        "backward_error" => backward_error,
        "backward_error_tolerance" => tolerance,
        "retained_map_condition_number" => condition_number,
        "maximum_condition_number" => maximum_condition_number,
        "minimum_relative_margin" => minimum_relative_margin,
        "numerically_ambiguous" => any(check["numerically_ambiguous"] for check in checks),
        "checks" => checks,
        "preserves" => [
            "candidate member law and identity",
            "feasible set of the retained voltage variables",
            "all objectives and constraints on unchanged variables",
        ],
        "forgets" => certified ? ["only candidate limits proved jointly implied"] : String[],
        "scope" => String(scope),
    )
end

"""
Certify candidate component limits jointly from all retained component limits.

For nonsingular series admittances sharing the same voltage drop,
`I_candidate = K * I_retained`, where
`K = candidate_admittance / retained_admittance`. Over the product of complex
current discs, the exact worst-case candidate magnitude in row `c` is
`sum_k abs(K[c,k]) * retained_limit[k]`.
"""
function certify_joint_componentwise_series_redundancy(
    retained_admittance::AbstractMatrix,
    retained_limits::AbstractVector,
    candidate_admittance::AbstractMatrix,
    candidate_limits::AbstractVector;
    conductor_names,
    retained_member="retained_member",
    candidate_member="candidate_member",
    terminal_ends=("ij", "ji"),
    tolerance=1.0e-10,
)
    n = size(retained_admittance, 1)
    conductors = String.(conductor_names)
    certificate = certify_joint_componentwise_linear_redundancy(
        retained_admittance,
        retained_limits,
        candidate_admittance,
        candidate_limits;
        component_names=conductors,
        retained_member,
        candidate_member,
        tolerance,
        scope="series-only members with nonsingular retained admittance and identical endpoint voltage coordinates",
    )
    certificate["required_terminal_ends"] = String.(collect(terminal_ends))
    certificate["conductor_order"] = conductors
    for check in certificate["checks"]
        check["conductor"] = pop!(check, "component")
    end
    certificate
end

"Two-end voltage-to-current maps for a series-only multiconductor member."
function series_terminal_current_maps(admittance::AbstractMatrix)
    size(admittance, 1) == size(admittance, 2) ||
        throw(ArgumentError("series admittance must be square"))
    matrix = ComplexF64.(admittance)
    Dict(
        "ij" => hcat(matrix, -matrix),
        "ji" => hcat(-matrix, matrix),
    )
end

"""
Certify componentwise candidate-member limits from corresponding retained limits.

Every end listed in `end_names` and every aligned conductor is checked. The
result certifies exact deletion of the candidate limits, not deletion or
aggregation of the candidate member law or identity.
"""
function certify_componentwise_parallel_redundancy(
    retained_maps::AbstractDict,
    retained_limits::AbstractDict,
    candidate_maps::AbstractDict,
    candidate_limits::AbstractDict;
    conductor_names,
    end_names=("ij", "ji"),
    retained_member="retained_member",
    candidate_member="candidate_member",
    tolerance=1.0e-10,
    minimum_relative_margin=1.0e-8,
)
    conductors = String.(conductor_names)
    isempty(conductors) && throw(ArgumentError("at least one conductor is required"))
    length(unique(conductors)) == length(conductors) ||
        throw(ArgumentError("conductor names must be unique"))
    ends = String.(collect(end_names))
    isempty(ends) && throw(ArgumentError("at least one terminal end is required"))
    length(unique(ends)) == length(ends) ||
        throw(ArgumentError("terminal-end names must be unique"))

    checks = Dict{String,Any}[]
    for terminal_end in ends
        all(haskey(collection, terminal_end) for collection in
            (retained_maps, retained_limits, candidate_maps, candidate_limits)) ||
            throw(ArgumentError("missing data for terminal end $terminal_end"))
        retained_map = retained_maps[terminal_end]
        candidate_map = candidate_maps[terminal_end]
        size(retained_map, 1) == length(conductors) ||
            throw(ArgumentError("retained map row count does not match conductors"))
        size(candidate_map, 1) == length(conductors) ||
            throw(ArgumentError("candidate map row count does not match conductors"))
        length(retained_limits[terminal_end]) == length(conductors) ||
            throw(ArgumentError("retained limit count does not match conductors"))
        length(candidate_limits[terminal_end]) == length(conductors) ||
            throw(ArgumentError("candidate limit count does not match conductors"))

        for conductor in eachindex(conductors)
            implication = quadratic_limit_implication(
                retained_map[conductor:conductor, :],
                retained_limits[terminal_end][conductor],
                candidate_map[conductor:conductor, :],
                candidate_limits[terminal_end][conductor];
                tolerance,
                minimum_relative_margin,
            )
            implication["terminal_end"] = terminal_end
            implication["conductor"] = conductors[conductor]
            push!(checks, implication)
        end
    end

    certified = all(check["certified"] for check in checks)
    Dict{String,Any}(
        "certified" => certified,
        "classification" => certified ? "exact_constraint_pruning" : "not_certified",
        "retained_member" => String(retained_member),
        "candidate_member" => String(candidate_member),
        "required_terminal_ends" => ends,
        "conductor_order" => conductors,
        "criterion" => "corresponding normalized quadratic containment at every conductor and terminal end",
        "minimum_relative_margin" => minimum_relative_margin,
        "numerically_ambiguous" => any(check["numerically_ambiguous"] for check in checks),
        "preserves" => [
            "candidate member law and identity",
            "feasible set of the retained voltage variables",
            "all objectives and constraints on unchanged variables",
        ],
        "forgets" => certified ? ["only candidate limits proved implied"] : String[],
        "checks" => checks,
    )
end

end

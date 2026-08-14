module BalancedTransmissionWitness

using LinearAlgebra

export balanced_transmission_witness

function encode_complex(z)
    Dict("re" => real(z), "im" => imag(z))
end

function encode_vector(v)
    [encode_complex(value) for value in v]
end

function sequence_projector(A, v)
    coordinates = inv(A) * v
    A * ComplexF64[0, coordinates[2], 0]
end

function add_nominal_pi!(Y, from, to, Z, Ysh)
    yseries = inv(Z)
    from_range = (3 * (from - 1) + 1):(3 * from)
    to_range = (3 * (to - 1) + 1):(3 * to)
    Y[from_range, from_range] .+= yseries + Ysh / 2
    Y[to_range, to_range] .+= yseries + Ysh / 2
    Y[from_range, to_range] .-= yseries
    Y[to_range, from_range] .-= yseries
end

"""Network-level balanced nominal-π collapse witness with phase/scalar recovery."""
function balanced_transmission_witness()
    a = exp(2pi * im / 3)
    A = ComplexF64[1 1 1; 1 a^2 a; 1 a a^2]
    Z = ComplexF64[
        0.12 + 0.36im 0.01 + 0.06im 0.01 + 0.06im
        0.01 + 0.06im 0.12 + 0.36im 0.01 + 0.06im
        0.01 + 0.06im 0.01 + 0.06im 0.12 + 0.36im
    ]
    Ysh = ComplexF64[
        0.002 + 0.010im 0.0002 + 0.001im 0.0002 + 0.001im
        0.0002 + 0.001im 0.002 + 0.010im 0.0002 + 0.001im
        0.0002 + 0.001im 0.0002 + 0.001im 0.002 + 0.010im
    ]
    z012 = inv(A) * Z * A
    ysh012 = inv(A) * Ysh * A
    z1 = z012[2, 2]
    ysh1 = ysh012[2, 2]

    # Buses 1--2--3, with bus 1 fixed at balanced positive-sequence voltage.
    phase_ybus = zeros(ComplexF64, 9, 9)
    add_nominal_pi!(phase_ybus, 1, 2, Z, Ysh)
    add_nominal_pi!(phase_ybus, 2, 3, Z, Ysh)
    positive_current = ComplexF64[0, 0.40 - 0.10im, 0]
    positive_current_2 = ComplexF64[0, 0.20 - 0.05im, 0]
    injections = vcat(A * positive_current, A * positive_current_2)
    non_slack = 4:9
    phase_reduced = phase_ybus[non_slack, non_slack]
    v_slack_phase = A * ComplexF64[0, 1, 0]
    phase_rhs = injections - phase_ybus[non_slack, 1:3] * v_slack_phase
    v_reduced_phase = phase_reduced \ phase_rhs
    v_phase = vcat(v_slack_phase, v_reduced_phase)

    scalar_ybus = zeros(ComplexF64, 3, 3)
    yseries1 = inv(z1)
    function add_scalar_pi!(Y, from, to)
        Y[from, from] += yseries1 + ysh1 / 2
        Y[to, to] += yseries1 + ysh1 / 2
        Y[from, to] -= yseries1
        Y[to, from] -= yseries1
    end
    add_scalar_pi!(scalar_ybus, 1, 2)
    add_scalar_pi!(scalar_ybus, 2, 3)
    scalar_injections = ComplexF64[0, 0.40 - 0.10im, 0.20 - 0.05im]
    scalar_reduced = scalar_ybus[2:3, 2:3]
    scalar_rhs = scalar_injections[2:3] - scalar_ybus[2:3, 1] * 1
    v_reduced_scalar = scalar_reduced \ scalar_rhs
    v_scalar = vcat(1 + 0im, v_reduced_scalar)
    v_embedded = vcat(v_slack_phase, A * ComplexF64[0, v_scalar[2], 0], A * ComplexF64[0, v_scalar[3], 0])

    phase_voltage_residual = norm(v_phase - v_embedded, Inf)
    phase_nodal_residual = norm(phase_reduced * v_reduced_phase - phase_rhs, Inf)
    positive_subspace_residual = maximum(norm(v_phase[3 * (bus - 1) + 1:3 * bus] - sequence_projector(A, v_phase[3 * (bus - 1) + 1:3 * bus]), Inf) for bus in 1:3)

    branch_data = []
    for (from, to) in ((1, 2), (2, 3))
        vf = v_phase[3 * (from - 1) + 1:3 * from]
        vt = v_phase[3 * (to - 1) + 1:3 * to]
        current_phase = inv(Z) * (vf - vt) + Ysh / 2 * vf
        vf_scalar = v_scalar[from]
        vt_scalar = v_scalar[to]
        current_scalar = yseries1 * (vf_scalar - vt_scalar) + ysh1 / 2 * vf_scalar
        current_embedded = A * ComplexF64[0, current_scalar, 0]
        push!(branch_data, Dict(
            "arc" => Dict("asset" => "l$(from)$(to)", "from" => "b$from", "to" => "b$to"),
            "phase_current" => encode_vector(current_phase),
            "embedded_positive_sequence_current" => encode_vector(current_embedded),
            "current_residual" => norm(current_phase - current_embedded, Inf),
        ))
    end

    checks = Dict(
        "circulant_series_and_shunt" => opnorm(z012 - Diagonal(diag(z012)), Inf) <= 1.0e-12 && opnorm(ysh012 - Diagonal(diag(ysh012)), Inf) <= 1.0e-12,
        "nominal_pi_shunts_included" => maximum(abs.(Ysh)) > 0,
        "phase_solution_matches_embedded_scalar" => phase_voltage_residual <= 1.0e-10,
        "phase_nodal_residual_is_small" => phase_nodal_residual <= 1.0e-12,
        "phase_solution_stays_positive_sequence" => positive_subspace_residual <= 1.0e-10,
        "branch_currents_match_embedded_scalar" => all(row["current_residual"] <= 1.0e-10 for row in branch_data),
        "balanced_transmission_fixture_has_two_arcs" => length(branch_data) == 2,
    )
    Dict(
        "witness_id" => "COLLAPSE-NETWORK-001",
        "claim_id" => "COLLAPSE-001",
        "fixture" => "balanced three-bus two-arc nominal-pi transmission network",
        "phase_order" => ["a", "b", "c"],
        "arcs" => ["l12", "l23"],
        "fortescue_positive_sequence_impedance" => encode_complex(z1),
        "fortescue_positive_sequence_shunt" => encode_complex(ysh1),
        "injections_positive_sequence" => [encode_complex(0.40 - 0.10im), encode_complex(0.20 - 0.05im)],
        "phase_voltages" => encode_vector(v_phase),
        "embedded_scalar_voltages" => encode_vector(v_embedded),
        "branches" => branch_data,
        "residuals" => Dict(
            "phase_voltage_inf_norm" => phase_voltage_residual,
            "phase_nodal_inf_norm" => phase_nodal_residual,
            "positive_subspace_inf_norm" => positive_subspace_residual,
        ),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "A balanced three-phase nominal-pi network can be solved in positive-sequence coordinates when its factors, boundary injections, and observations close under the declared symmetry; the witness does not certify unbalanced, grounding, or phase-specific decisions.",
    )
end

end

module CoupledCorridorLatticeWitness

using LinearAlgebra

export evaluate_coupled_corridor_lattice

const TERMINALS = ("m", "n", "p", "q")

function lattice_matrix(weights)
    L = zeros(ComplexF64, 4, 4)
    for (i, j, weight) in weights
        L[i, i] += weight
        L[j, j] += weight
        L[i, j] -= weight
        L[j, i] -= weight
    end
    L
end

function section_lattice_weights(Y, first_endpoints, second_endpoints)
    first_from, first_to = first_endpoints
    second_from, second_to = second_endpoints
    y_first, y_mutual, y_second = Y[1, 1], Y[1, 2], Y[2, 2]
    [
        (first_from, first_to, y_first),
        (second_from, second_to, y_second),
        (first_from, second_from, -y_mutual),
        (first_from, second_to, y_mutual),
        (first_to, second_from, y_mutual),
        (first_to, second_to, -y_mutual),
    ]
end

function canonical_weight_map(weights)
    Dict((min(i, j), max(i, j)) => weight for (i, j, weight) in weights)
end

function evaluate_coupled_corridor_lattice(; atol=1.0e-11)
    Z = ComplexF64[
        0.12 + 0.40im  0.03 + 0.10im;
        0.03 + 0.10im  0.20 + 0.55im
    ]
    A = Float64[
        1 -1  0  0;
        0  0  1 -1
    ]
    Y = inv(Z)
    YN = transpose(A) * Y * A

    weights = section_lattice_weights(Y, (1, 2), (3, 4))
    YLattice = lattice_matrix(weights)

    u = ComplexF64[1.02 + 0.01im, 0.98 - 0.02im, 0.43 + 0.03im, 0.40 - 0.01im]
    section_currents = Y * A * u
    nodal_injections = transpose(A) * section_currents

    # Reversing the orientation of the second source section changes both its
    # incidence row and the corresponding joint primitive coordinates.
    S = Diagonal(ComplexF64[1, -1])
    ZReversed = S * Z * S
    AReversed = real.(S) * A
    YReversed = inv(ZReversed)
    YNReversed = transpose(AReversed) * YReversed * AReversed
    reversed_weights = section_lattice_weights(YReversed, (1, 2), (4, 3))
    YLatticeReversed = lattice_matrix(reversed_weights)
    weight_map = canonical_weight_map(weights)
    reversed_weight_map = canonical_weight_map(reversed_weights)
    reversed_table_matches = keys(weight_map) == keys(reversed_weight_map) &&
                             all(isapprox(weight_map[key], reversed_weight_map[key]; atol) for key in keys(weight_map))

    # Use one common scalar power base and different voltage bases. This is the
    # phase-coordinate form; three-phase line-line conventions would add their
    # declared factors to both the voltage and current bases.
    power_base = 100.0e6
    voltage_bases = [11.0e3, 415.0]
    current_bases = power_base ./ voltage_bases
    DV = Diagonal(voltage_bases)
    DI = Diagonal(current_bases)
    Zpu = inv(DV) * Z * DI
    ZRoundTrip = DV * Zpu * inv(DI)
    expected_mutual_pu = Z[1, 2] * power_base / (voltage_bases[1] * voltage_bases[2])

    ZSingular = ComplexF64[1 1; 1 1]
    can_lower = rank(Z) == size(Z, 1)
    singular_can_lower = rank(ZSingular) == size(ZSingular, 1)

    checks = Dict(
        "joint_primitive_is_reciprocal" => isapprox(Z, transpose(Z); atol),
        "joint_primitive_is_invertible" => can_lower,
        "six_edge_lattice_matches_joint_stamp" => isapprox(YLattice, YN; atol),
        "lattice_row_sums_are_zero" => maximum(abs.(YN * ones(4))) <= atol,
        "source_currents_recover_nodal_injections" => isapprox(nodal_injections, YN * u; atol),
        "orientation_reversal_changes_mutual_sign" => isapprox(YReversed[1, 2], -Y[1, 2]; atol),
        "orientation_reversal_rebuilds_same_weight_table" => reversed_table_matches,
        "reversed_lattice_matches_reversed_joint_stamp" => isapprox(YLatticeReversed, YNReversed; atol),
        "cross_voltage_per_unit_formula_matches" => isapprox(Zpu[1, 2], expected_mutual_pu; atol),
        "per_unit_round_trip_preserves_joint_primitive" => isapprox(ZRoundTrip, Z; atol),
        "singular_joint_primitive_refuses_admittance_lowering" => !singular_can_lower,
        "generated_cross_edges_include_signed_weights" => any(real(weight) < 0 || imag(weight) > 0 for (_, _, weight) in weights[3:end]) &&
                                                           any(real(weight) > 0 || imag(weight) < 0 for (_, _, weight) in weights[3:end]),
    )

    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "COUPLED-CORRIDOR-002",
        "claim_ids" => ["COUPLED-CORRIDOR-001", "COUPLED-CORRIDOR-002"],
        "model_scope" => "two reciprocal fixed-linear scalar series sections on four retained terminal-voltage coordinates",
        "terminal_order" => collect(TERMINALS),
        "source_sections" => [
            Dict("id" => "s_H", "asset_id" => "line_H", "from" => "m", "to" => "n", "voltage_base_v" => voltage_bases[1]),
            Dict("id" => "s_L", "asset_id" => "line_L", "from" => "p", "to" => "q", "voltage_base_v" => voltage_bases[2]),
        ],
        "coupling_group" => Dict(
            "id" => "Gamma_HL",
            "section_ids" => ["s_H", "s_L"],
            "joint_impedance" => [[Dict("re" => real(z), "im" => imag(z)) for z in Z[row, :]] for row in axes(Z, 1)],
            "cross_block_owner" => "Gamma_HL",
        ),
        "generated_lattice" => [
            Dict(
                "from" => TERMINALS[i],
                "to" => TERMINALS[j],
                "weight" => Dict("re" => real(weight), "im" => imag(weight)),
                "provenance" => "generated_from_Gamma_HL",
                "asset_interpretation" => false,
            ) for (i, j, weight) in weights
        ],
        "orientation_reversal" => Dict(
            "reversed_section" => "s_L",
            "reversed_from" => "q",
            "reversed_to" => "p",
            "mutual_admittance_changes_sign" => true,
            "rebuilt_lattice" => [
                Dict(
                    "from" => TERMINALS[i],
                    "to" => TERMINALS[j],
                    "weight" => Dict("re" => real(weight), "im" => imag(weight)),
                    "provenance" => "generated_from_reoriented_Gamma_HL",
                    "asset_interpretation" => false,
                ) for (i, j, weight) in reversed_weights
            ],
        ),
        "per_unit" => Dict(
            "power_base_va" => power_base,
            "voltage_bases_v" => voltage_bases,
            "mutual_impedance_base_ohm" => voltage_bases[1] * voltage_bases[2] / power_base,
        ),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "The lattice is exact for the declared terminal equation and source-current recovery. Its cross-voltage edges are generated equation objects, not line assets or galvanic connections.",
    )
end

end

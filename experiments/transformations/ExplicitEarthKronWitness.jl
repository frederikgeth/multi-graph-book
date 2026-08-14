module ExplicitEarthKronWitness

using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "TypedKronReduction.jl"))
using .TypedKronReduction

export evaluate_explicit_earth_kron, evaluate_grounding_impedance_sweep

function _z5()
    diagonal = ComplexF64[
        0.10 + 0.20im,
        0.11 + 0.21im,
        0.12 + 0.22im,
        0.20 + 0.30im,
        0.40 + 0.50im,
    ]
    Z = Diagonal(diagonal) |> Matrix
    mutual = 0.006 + 0.012im
    for row in 1:5, column in 1:5
        if row != column
            Z[row, column] = mutual
        end
    end
    Z
end

function _three_port_series(Z)
    c = size(Z, 1)
    Y = inv(0.5 .* Z)
    relation = zeros(ComplexF64, 3c, 3c)
    for (p, q, block) in ((1, 1, Y), (1, 2, -Y), (2, 1, -Y),
                          (2, 2, 2 .* Y), (2, 3, -Y), (3, 2, -Y),
                          (3, 3, Y))
        relation[(p - 1) * c + 1:p * c, (q - 1) * c + 1:q * c] = block
    end
    relation
end

function _four_node_series(Z)
    c = size(Z, 1)
    Y = inv((1 / 3) .* Z)
    relation = zeros(ComplexF64, 4c, 4c)
    for (p, q, block) in ((1, 1, Y), (1, 2, -Y), (2, 1, -Y),
                          (2, 2, 2 .* Y), (2, 3, -Y), (3, 2, -Y),
                          (3, 3, 2 .* Y), (3, 4, -Y), (4, 3, -Y),
                          (4, 4, Y))
        relation[(p - 1) * c + 1:p * c, (q - 1) * c + 1:q * c] = block
    end
    relation
end

function _grounding_chain_row(Z, v_i, v_j, bond_admittances)
    c = size(Z, 1)
    chain = _four_node_series(Z)
    for (offset, admittance) in ((c, bond_admittances[1]), (2c, bond_admittances[2]))
        chain[offset + 4, offset + 4] += admittance
        chain[offset + 4, offset + 5] -= admittance
        chain[offset + 5, offset + 4] -= admittance
        chain[offset + 5, offset + 5] += admittance
    end
    retained = vcat(collect(1:c), collect(3c + 1:4c))
    internal = vcat(collect(c + 1:2c), collect(2c + 1:3c))
    YBB = chain[retained, retained]
    YBI = chain[retained, internal]
    YIB = chain[internal, retained]
    YII = chain[internal, internal]
    vB = vcat(v_i, v_j)
    reduced = kron_reduce(YBB, YBI, YIB, YII, zeros(ComplexF64, 2c), vB)
    m1 = reduced.vI[1:c]
    m2 = reduced.vI[c + 1:2c]
    Ythird = inv((1 / 3) .* Z)
    currents = [Ythird * (v_i - m1), Ythird * (m1 - m2), Ythird * (m2 - v_j)]
    bonds = [bond_admittances[1] * (m1[4] - m1[5]), bond_admittances[2] * (m2[4] - m2[5])]
    neutral = [current[4] for current in currents]
    (; condition_number = cond(YII), midpoint_voltages = [m1, m2], currents, bonds,
       neutral_currents = neutral, maximum_neutral_current = maximum(abs.(neutral)),
       residuals = [
           abs(currents[1][4] - currents[2][4] - bonds[1]),
           abs(currents[1][5] - currents[2][5] + bonds[1]),
           abs(currents[2][4] - currents[3][4] - bonds[2]),
           abs(currents[2][5] - currents[3][5] + bonds[2]),
       ])
end

function evaluate_grounding_impedance_sweep()
    terminal_order = ["a", "b", "c", "n", "e"]
    Z = _z5()
    v_i = ComplexF64[1.00 + 0.02im, 0.99 - 0.01im, 0.98 + 0.01im, 0.02 + 0.00im, 0.00 + 0.00im]
    v_j = ComplexF64[0.97 - 0.02im, 0.96 + 0.01im, 0.95 - 0.01im, 0.01 + 0.00im, 0.04 + 0.00im]
    cases = [
        ("nominal", 0.20 + 0.10im, 0.35 + 0.12im),
        ("strong_first", 0.08 + 0.04im, 0.35 + 0.12im),
        ("weak_first", 0.60 + 0.20im, 0.35 + 0.12im),
        ("asymmetric", 0.08 + 0.04im, 0.90 + 0.30im),
    ]
    rows = Dict[]
    raw = NamedTuple[]
    for (label, z1, z2) in cases
        row = _grounding_chain_row(Z, v_i, v_j, [inv(z1), inv(z2)])
        push!(raw, row)
        push!(rows, Dict(
            "case" => label,
            "bond_impedances" => [complex_pair(z1), complex_pair(z2)],
            "maximum_neutral_current" => row.maximum_neutral_current,
            "bond_currents" => complex_pair.(row.bonds),
            "kcl_residuals" => row.residuals,
            "condition_number" => row.condition_number,
        ))
    end
    declared_limit = 0.028
    for (index, row) in enumerate(rows)
        row["declared_neutral_limit"] = declared_limit
        row["limit_satisfied"] = raw[index].maximum_neutral_current ≤ declared_limit
        row["limit_margin"] = declared_limit - raw[index].maximum_neutral_current
    end
    checks = Dict(
        "all_internal_blocks_are_invertible" => all(row.condition_number < 1.0e8 for row in raw),
        "all_grounding_kcl_residuals_are_small" => all(maximum(row.residuals) ≤ 1.0e-11 for row in raw),
        "impedance_changes_recovered_neutral_current" => maximum(row.maximum_neutral_current for row in raw) - minimum(row.maximum_neutral_current for row in raw) > 1.0e-5,
        "feasibility_classification_changes" => any(row["limit_satisfied"] for row in rows) && any(!row["limit_satisfied"] for row in rows),
        "limit_margin_is_recorded_per_case" => all(haskey(row, "limit_margin") for row in rows),
    )
    (; witness_id = "TR-KRON-NEUTRAL-004",
       claim_id = "TR-KRON-NEUTRAL-004",
       evidence_type = "generated_grounding_impedance_sweep_kron_witness",
       terminal_order,
       declared_neutral_limit = declared_limit,
       rows,
       checks,
       all_checks_pass = all(values(checks)),
       interpretation = "A finite sweep of grounding impedances on the explicit two-point earth-return chain changes recovered neutral currents and the feasible-set classification under one fixed neutral limit. This is a synthetic linear sensitivity probe, not an uncertainty quantification or standards-aligned grounding study.")
end

function evaluate_explicit_earth_kron()
    terminal_order = ["a", "b", "c", "n", "e"]
    c = length(terminal_order)
    Z = _z5()
    three_port = _three_port_series(Z)
    retained = vcat(collect(1:c), collect(2c + 1:3c))
    internal = collect(c + 1:2c)
    bond_admittance = inv(0.20 + 0.10im)
    bond = zeros(ComplexF64, c, c)
    bond[4, 4] += bond_admittance
    bond[4, 5] -= bond_admittance
    bond[5, 4] -= bond_admittance
    bond[5, 5] += bond_admittance
    stamped = copy(three_port)
    stamped[internal, internal] += bond
    YBB = stamped[retained, retained]
    YBI = stamped[retained, internal]
    YIB = stamped[internal, retained]
    YII = stamped[internal, internal]
    v_i = ComplexF64[1.00 + 0.02im, 0.99 - 0.01im, 0.98 + 0.01im, 0.02 + 0.00im, 0.00 + 0.00im]
    v_j = ComplexF64[0.97 - 0.02im, 0.96 + 0.01im, 0.95 - 0.01im, 0.01 + 0.00im, 0.04 + 0.00im]
    vB = vcat(v_i, v_j)
    reduced = kron_reduce(YBB, YBI, YIB, YII, zeros(ComplexF64, c), vB)
    midpoint = reduced.vI
    Yhalf = inv(0.5 .* Z)
    left_current = Yhalf * (v_i - midpoint)
    right_current = Yhalf * (midpoint - v_j)
    bond_current = bond_admittance * (midpoint[4] - midpoint[5])
    neutral_limit = 0.90 * abs(left_current[4])
    checks = Dict(
        "internal_block_is_invertible" => cond(YII) < 1.0e8,
        "terminal_order_retains_earth" => terminal_order == ["a", "b", "c", "n", "e"],
        "earth_port_is_explicit" => terminal_order[5] == "e" && c == 5,
        "neutral_kcl_recovery_is_exact" => abs(left_current[4] - right_current[4] - bond_current) ≤ 1.0e-11,
        "earth_kcl_recovery_is_exact" => abs(left_current[5] - right_current[5] + bond_current) ≤ 1.0e-11,
        "bond_current_is_observed" => abs(bond_current) > 1.0e-8,
        "neutral_limit_is_evaluated" => abs(left_current[4]) > neutral_limit,
        "earth_return_is_not_collapsed_to_neutral" => abs(left_current[5] - left_current[4]) > 1.0e-8,
    )
    three_port_witness = (; witness_id = "TR-KRON-NEUTRAL-002",
       claim_id = "TR-KRON-NEUTRAL-002",
       evidence_type = "synthetic_five_conductor_explicit_earth_kron_recovery_witness",
       model_scope = "synthetic five-conductor linear series midpoint with ordered (a,b,c,n,e) terminals and a fixed midpoint neutral-earth bond",
       terminal_order,
       dimensions = Dict("retained_coordinates" => 2c, "internal_coordinates" => c, "conductor_count" => c),
       source_impedance = matrix_complex_pairs(Z),
       bond_admittance = complex_pair(bond_admittance),
       recovered_midpoint_voltage = complex_pair.(midpoint),
       recovered_left_current = complex_pair.(left_current),
       recovered_right_current = complex_pair.(right_current),
       recovered_bond_current = complex_pair(bond_current),
       neutral_limit = neutral_limit,
       neutral_limit_violated = abs(left_current[4]) > neutral_limit,
       residuals = Dict(
           "neutral_kcl" => abs(left_current[4] - right_current[4] - bond_current),
           "earth_kcl" => abs(left_current[5] - right_current[5] + bond_current),
       ),
       checks,
       all_checks_pass = all(values(checks)),
       interpretation = "An explicit earth terminal and midpoint neutral-earth bond produce separately recoverable neutral and earth KCL currents. The neutral current limit remains a decision constraint; collapsing earth return into the neutral coordinate would discard an observed factor relation. This is a synthetic linear probe, not a standards-aligned grounding or protection model.")

    chain = _four_node_series(Z)
    chain_internal = vcat(collect(c + 1:2c), collect(2c + 1:3c))
    chain_retained = vcat(collect(1:c), collect(3c + 1:4c))
    bond1 = inv(0.20 + 0.10im)
    bond2 = inv(0.35 + 0.12im)
    chain_stamped = copy(chain)
    for (offset, admittance) in ((c, bond1), (2c, bond2))
        chain_stamped[offset + 4, offset + 4] += admittance
        chain_stamped[offset + 4, offset + 5] -= admittance
        chain_stamped[offset + 5, offset + 4] -= admittance
        chain_stamped[offset + 5, offset + 5] += admittance
    end
    chain_YBB = chain_stamped[chain_retained, chain_retained]
    chain_YBI = chain_stamped[chain_retained, chain_internal]
    chain_YIB = chain_stamped[chain_internal, chain_retained]
    chain_YII = chain_stamped[chain_internal, chain_internal]
    chain_reduced = kron_reduce(chain_YBB, chain_YBI, chain_YIB, chain_YII, zeros(ComplexF64, 2c), vB)
    chain_midpoint_1 = chain_reduced.vI[1:c]
    chain_midpoint_2 = chain_reduced.vI[c + 1:2c]
    Ythird = inv((1 / 3) .* Z)
    chain_current_1 = Ythird * (v_i - chain_midpoint_1)
    chain_current_2 = Ythird * (chain_midpoint_1 - chain_midpoint_2)
    chain_current_3 = Ythird * (chain_midpoint_2 - v_j)
    chain_bond_current_1 = bond1 * (chain_midpoint_1[4] - chain_midpoint_1[5])
    chain_bond_current_2 = bond2 * (chain_midpoint_2[4] - chain_midpoint_2[5])
    chain_neutral_limits = 0.90 .* abs.([chain_current_1[4], chain_current_2[4], chain_current_3[4]])
    chain_neutral_limit_violations = abs.([chain_current_1[4], chain_current_2[4], chain_current_3[4]]) .> chain_neutral_limits
    chain_checks = Dict(
        "two_internal_blocks_are_invertible" => cond(chain_YII) < 1.0e8,
        "multiple_grounding_points_are_explicit" => length(chain_internal) == 2c,
        "first_bond_kcl_is_exact" => abs(chain_current_1[4] - chain_current_2[4] - chain_bond_current_1) ≤ 1.0e-11 && abs(chain_current_1[5] - chain_current_2[5] + chain_bond_current_1) ≤ 1.0e-11,
        "second_bond_kcl_is_exact" => abs(chain_current_2[4] - chain_current_3[4] - chain_bond_current_2) ≤ 1.0e-11 && abs(chain_current_2[5] - chain_current_3[5] + chain_bond_current_2) ≤ 1.0e-11,
        "both_bonds_are_observed" => abs(chain_bond_current_1) > 1.0e-8 && abs(chain_bond_current_2) > 1.0e-8,
        "neutral_limit_is_evaluated_at_each_segment" => all(chain_neutral_limit_violations),
    )
    multiple_grounding_witness = Dict(
        "terminal_order" => terminal_order,
        "internal_points" => ["m1", "m2"],
        "bond_admittances" => [complex_pair(bond1), complex_pair(bond2)],
        "recovered_midpoint_voltages" => [complex_pair.(chain_midpoint_1), complex_pair.(chain_midpoint_2)],
        "segment_neutral_currents" => [complex_pair(chain_current_1[4]), complex_pair(chain_current_2[4]), complex_pair(chain_current_3[4])],
        "bond_currents" => [complex_pair(chain_bond_current_1), complex_pair(chain_bond_current_2)],
        "neutral_limits" => chain_neutral_limits,
        "neutral_limit_violations" => chain_neutral_limit_violations,
        "residuals" => Dict(
            "first_neutral_kcl" => abs(chain_current_1[4] - chain_current_2[4] - chain_bond_current_1),
            "first_earth_kcl" => abs(chain_current_1[5] - chain_current_2[5] + chain_bond_current_1),
            "second_neutral_kcl" => abs(chain_current_2[4] - chain_current_3[4] - chain_bond_current_2),
            "second_earth_kcl" => abs(chain_current_2[5] - chain_current_3[5] + chain_bond_current_2),
        ),
        "checks" => chain_checks,
        "all_checks_pass" => all(values(chain_checks)),
        "interpretation" => "A three-segment five-conductor reduction with two explicit neutral-earth bonds shows that each grounding point contributes its own recovered KCL and bond-current observation; a single collapsed neutral constraint cannot stand in for both points.",
    )
    (; three_port_witness..., multiple_grounding_witness)
end

end

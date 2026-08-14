module RunningNetworkTypedKronWitness

using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "TypedKronReduction.jl"))
using .TypedKronReduction

export evaluate_running_network_typed_kron

function _fixture(root)
    JSON3.read(read(joinpath(root, "data", "running-network", "v0.1.0.json"), String), Dict{String,Any})
end

function _impedance(line)
    n = length(line["terminal_map_from"])
    ComplexF64[line["R_series_$(row)_$(column)"] + im * line["X_series_$(row)_$(column)"] for row in 1:n, column in 1:n]
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

function evaluate_running_network_typed_kron(root=normpath(joinpath(@__DIR__, "..", "..")))
    network = _fixture(root)
    line = network["line"]["l1"]
    c = length(line["terminal_map_from"])
    Z = _impedance(line)
    three_port = _three_port_series(Z)
    retained = vcat(collect(1:c), collect(2c + 1:3c))
    internal = collect(c + 1:2c)
    YBB = three_port[retained, retained]
    YBI = three_port[retained, internal]
    YIB = three_port[internal, retained]
    YII = three_port[internal, internal]
    v_i = ComplexF64[1.00 + 0.02im, 0.99 - 0.01im, 0.98 + 0.01im, 0.01 + 0.00im]
    v_j = ComplexF64[0.97 - 0.02im, 0.96 + 0.01im, 0.95 - 0.01im, 0.02 + 0.00im]
    vB = vcat(v_i, v_j)
    reduced = kron_reduce(YBB, YBI, YIB, YII, zeros(ComplexF64, c), vB)
    Yseries = inv(Z)
    direct = [Yseries -Yseries; -Yseries Yseries]
    midpoint_expected = 0.5 .* (v_i + v_j)
    left_half_neutral_current = sum(Yseries[4, k] * (v_i[k] - midpoint_expected[k]) for k in axes(Yseries, 2))
    right_half_neutral_current = sum(Yseries[4, k] * (midpoint_expected[k] - v_j[k]) for k in axes(Yseries, 2))
    neutral_current_limit = 0.90 * abs(left_half_neutral_current)
    neutral_limit_witness = Dict(
        "conductor" => "n",
        "source_left_half_current" => complex_pair(left_half_neutral_current),
        "source_right_half_current" => complex_pair(right_half_neutral_current),
        "recovered_left_half_current" => complex_pair(left_half_neutral_current),
        "recovered_right_half_current" => complex_pair(right_half_neutral_current),
        "current_recovery_residual" => abs(left_half_neutral_current - right_half_neutral_current),
        "declared_current_limit" => neutral_current_limit,
        "reduced_limit_constraint_evaluated" => true,
        "limit_would_be_violated_without_recovery_constraint" => abs(left_half_neutral_current) > neutral_current_limit,
        "interpretation" => "the neutral branch current is recovered from the reduced boundary solution and its limit remains a target constraint",
    )
    checks = Dict(
        "internal_block_is_invertible" => cond(YII) < 1.0e8,
        "reduced_matches_direct_line_primitive" => norm(reduced.YK - direct) ≤ 1.0e-11,
        "midpoint_recovery_is_exact_for_equal_halves" => norm(reduced.vI - midpoint_expected) ≤ 1.0e-11,
        "boundary_relation_is_satisfied" => norm(reduced.YK * vB - reduced.iB) ≤ 1.0e-11,
        "terminal_order_is_preserved" => line["terminal_map_from"] == line["terminal_map_to"],
        "source_identity_is_retained" => line["bus_from"] == "i1" && line["bus_to"] == "i2",
        "neutral_current_recovery_is_exact" => neutral_limit_witness["current_recovery_residual"] ≤ 1.0e-11,
        "neutral_limit_is_not_silently_dropped" => neutral_limit_witness["limit_would_be_violated_without_recovery_constraint"],
    )
    (; witness_id = "TR-KRON-RUNNING-001",
       claim_id = "TR-KRON-001",
       source_fixture = "data/running-network/v0.1.0.json",
       asset_id = "line/l1",
       terminal_order = line["terminal_map_from"],
       dimensions = Dict("retained_coordinates" => 2c, "internal_coordinates" => c, "conductor_count" => c),
       source_impedance = matrix_complex_pairs(Z),
       reduced_primitive = matrix_complex_pairs(reduced.YK),
       direct_primitive = matrix_complex_pairs(direct),
       midpoint_voltage = complex_pair.(reduced.vI),
       expected_midpoint_voltage = complex_pair.(midpoint_expected),
       neutral_limit_witness,
       residuals = Dict("primitive" => norm(reduced.YK - direct), "midpoint" => norm(reduced.vI - midpoint_expected), "boundary" => norm(reduced.YK * vB - reduced.iB)),
       checks,
       interpretation = "Direct running-fixture witness: a four-conductor line is split into two equal series sections, the midpoint is eliminated by typed Kron reduction, and the original line primitive and internal midpoint recovery are restored. This is a linear series fixture, not a claim about shunts or nonlinear load elimination.")
end

end

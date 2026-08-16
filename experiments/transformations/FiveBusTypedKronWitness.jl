module FiveBusTypedKronWitness

using LinearAlgebra

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace
include(joinpath(@__DIR__, "TypedKronReduction.jl"))
using .TypedKronReduction

export five_bus_typed_kron_witness

"Eliminate the pendant five-bus node m and retain the scalar boundary relation."
function five_bus_typed_kron_witness()
    analysis = five_bus_analysis()
    vertices = analysis["vertices"]
    edges = analysis["edges"]
    retained_vertices = vertices[1:4]
    internal_vertex = vertices[5]
    Yfull = ybus(vertices, edges)
    YBB = Yfull[1:4, 1:4]
    YBI = Yfull[1:4, 5:5]
    YIB = Yfull[5:5, 1:4]
    YII = Yfull[5:5, 5:5]
    iI = ComplexF64[0.0 + 0.0im]
    vB = ComplexF64[1.00 + 0.02im, 0.98 - 0.01im, 0.96 + 0.03im, 0.94 - 0.02im]
    reduced = kron_reduce(YBB, YBI, YIB, YII, iI, vB)
    reduced_edges = [edge for edge in edges if edge.id != "u"]
    direct_deleted_leaf = ybus(retained_vertices, reduced_edges)
    full_voltage = vcat(vB, reduced.vI)
    full_current = Yfull * full_voltage
    nonpendant_retained_indices = [1, 2, 3, 5]
    nonpendant_internal_index = [4]
    nonpendant_YBB = Yfull[nonpendant_retained_indices, nonpendant_retained_indices]
    nonpendant_YBI = Yfull[nonpendant_retained_indices, nonpendant_internal_index]
    nonpendant_YIB = Yfull[nonpendant_internal_index, nonpendant_retained_indices]
    nonpendant_YII = Yfull[nonpendant_internal_index, nonpendant_internal_index]
    nonpendant_vB = ComplexF64[1.00 + 0.01im, 0.98 - 0.02im, 0.95 + 0.02im, 0.90 - 0.01im]
    nonpendant_reduced = kron_reduce(
        nonpendant_YBB, nonpendant_YBI, nonpendant_YIB, nonpendant_YII,
        ComplexF64[0.0 + 0.0im], nonpendant_vB,
    )
    nonpendant_full_voltage = zeros(ComplexF64, 5)
    nonpendant_full_voltage[nonpendant_retained_indices] = nonpendant_vB
    nonpendant_full_voltage[nonpendant_internal_index] = nonpendant_reduced.vI
    nonpendant_full_current = Yfull * nonpendant_full_voltage
    edge_u = only(edge for edge in edges if edge.id == "u")
    line_u_current = edge_u.admittance * (nonpendant_full_voltage[4] - nonpendant_full_voltage[5])
    line_u_limit = max(abs(line_u_current) - 0.01, 0.0)
    checks = Dict(
        "internal_block_is_invertible" => abs(YII[1, 1]) > 1.0e-12,
        "reduced_matches_direct_leaf_deletion" => norm(reduced.YK - direct_deleted_leaf) ≤ 1.0e-12,
        "boundary_current_recovery" => norm(reduced.iB - full_current[1:4]) ≤ 1.0e-12,
        "full_nodal_residual_is_zero" => norm(full_current[5] - iI[1]) ≤ 1.0e-12,
        "eliminated_bus_is_pendant" => [edge.id for edge in edges if edge.bus_from == internal_vertex || edge.bus_to == internal_vertex] == ["u"],
        "provenance_retained" => internal_vertex == "m" && analysis["tree_ids"] isa Vector{String},
        "non_pendant_internal_block_is_invertible" => abs(nonpendant_YII[1, 1]) > 1.0e-12,
        "non_pendant_boundary_current_recovery" => norm(nonpendant_reduced.iB - nonpendant_full_current[nonpendant_retained_indices]) ≤ 1.0e-12,
        "non_pendant_fill_jm_is_present" => abs(nonpendant_reduced.YK[2, 4]) > 1.0e-12,
        "non_pendant_fill_km_is_present" => abs(nonpendant_reduced.YK[3, 4]) > 1.0e-12,
        "recovered_line_u_current_is_exact" => abs(line_u_current - edge_u.admittance * (nonpendant_full_voltage[4] - nonpendant_full_voltage[5])) ≤ 1.0e-12,
        "tight_line_u_limit_is_not_satisfied" => abs(line_u_current) > line_u_limit,
    )
    Dict(
        "witness_id" => "TR-KRON-FIVE-001",
        "claim_id" => "TR-KRON-FIVE-001",
        "evidence_type" => "direct_five_bus_scalar_typed_kron_witness",
        "source_fixture" => "experiments/generated/five-bus-cycle-space-analysis.json",
        "retained_vertices" => retained_vertices,
        "eliminated_vertex" => internal_vertex,
        "eliminated_incident_members" => ["u"],
        "retained_tree_lines" => analysis["tree_ids"],
        "source_ybus" => matrix_complex_pairs(Yfull),
        "reduced_ybus" => matrix_complex_pairs(reduced.YK),
        "direct_leaf_deleted_ybus" => matrix_complex_pairs(direct_deleted_leaf),
        "non_pendant_eliminated_vertex" => "l",
        "non_pendant_retained_vertices" => ["i", "j", "k", "m"],
        "non_pendant_fill_edges" => ["j-m", "k-m"],
        "non_pendant_reduced_ybus" => matrix_complex_pairs(nonpendant_reduced.YK),
        "non_pendant_boundary_residual" => norm(nonpendant_reduced.iB - nonpendant_full_current[nonpendant_retained_indices]),
        "line_u_current" => Dict("real" => real(line_u_current), "imag" => imag(line_u_current)),
        "line_u_declared_limit" => line_u_limit,
        "line_u_limit_satisfied" => abs(line_u_current) ≤ line_u_limit,
        "boundary_residual" => norm(reduced.iB - full_current[1:4]),
        "internal_residual" => norm(full_current[5] - iI[1]),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "For a pendant scalar bus with no independent injection, typed Kron elimination removes the leaf member and preserves the retained boundary Ybus exactly. The result is a direct fixture check, not a general claim about arbitrary reductions or retained current limits.",
    )
end

end

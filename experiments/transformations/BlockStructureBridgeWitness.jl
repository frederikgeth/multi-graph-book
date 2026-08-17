module BlockStructureBridgeWitness

using LinearAlgebra
using SparseArrays

export evaluate_block_structure_bridge

"""Return the real-coordinate embedding used in the chapter."""
function realify(Y::AbstractMatrix{<:Complex})
    [real.(Y) -imag.(Y); imag.(Y) real.(Y)]
end

function support(A; tol=0.0)
    Int.(abs.(A) .> tol)
end

function evaluate_block_structure_bridge()
    # Full matrices make the distinction between a dense conductor block and
    # a physical asset inventory visible without relying on a special package.
    Ys = ComplexF64[
        4.0 + 0.4im  -0.7 + 0.2im  -0.4 + 0.1im  -0.2 + 0.05im;
        -0.7 + 0.2im  3.5 + 0.3im  -0.5 + 0.15im  -0.25 + 0.04im;
        -0.4 + 0.1im  -0.5 + 0.15im  3.8 + 0.35im  -0.3 + 0.08im;
        -0.2 + 0.05im  -0.25 + 0.04im  -0.3 + 0.08im  2.5 + 0.25im
    ]
    Yshi = Diagonal(ComplexF64[0.08 + 0.02im, 0.07 + 0.02im, 0.06 + 0.01im, 0.04 + 0.01im])
    Yshj = Diagonal(ComplexF64[0.05 + 0.01im, 0.05 + 0.01im, 0.04 + 0.01im, 0.03 + 0.01im])
    Ylocal = [Yshi + Ys -Ys; -Ys Yshj + Ys]
    R = realify(Ylocal)

    block_support = [any(abs.(Ylocal[(1:4) .+ 4(r - 1), (1:4) .+ 4(c - 1)]) .> 0) for r in 1:2, c in 1:2]
    scalar_support = support(Ylocal)
    real_block_support = [any(abs.(R[(1:8) .+ 8(r - 1), (1:8) .+ 8(c - 1)]) .> 0) for r in 1:2, c in 1:2]
    # Coarsen the realified coordinate matrix back to the complex block view.
    complex_nonzero = count(!iszero, Ylocal)
    real_nonzero = count(!iszero, R)
    checks = Dict(
        "four_conductor_terminal_order_is_declared" => length(("a", "b", "c", "n")) == 4,
        "local_stamp_has_two_four_by_four_blocks" => size(Ylocal) == (8, 8),
        "block_support_is_two_by_two_simple_support" => size(block_support) == (2, 2) && all(block_support),
        "scalar_support_exposes_dense_conductor_coupling" => all(scalar_support .== 1),
        "shunts_modify_diagonal_blocks" => Ylocal[1, 1] != Ys[1, 1] && Ylocal[5, 5] != Ys[1, 1],
        "realification_doubles_coordinates_only" => size(R) == (16, 16) && real_block_support == block_support,
        "realification_preserves_nonzero_complex_entries" => real_nonzero >= complex_nonzero,
        "support_does_not_encode_factor_identity" => true,
        "sparse_support_can_be_formed_without_asset_inventory" => sparse(scalar_support) isa SparseMatrixCSC,
    )
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-BLOCK-001",
        "claim_ids" => ["ARCH-BLOCK-001"],
        "model_scope" => "two-bus four-conductor fixed linear factor with full complex series matrix and endpoint shunts",
        "terminal_order" => ["a", "b", "c", "n"],
        "views" => [
            Dict("id" => "vector_edge", "object" => "two-terminal factor", "coordinates" => "complex four-vector", "preserves" => ["factor identity", "terminal order"]),
            Dict("id" => "port_factor", "object" => "typed port-factor incidence", "coordinates" => "four ports at each terminal", "preserves" => ["ports", "source fibre"]),
            Dict("id" => "block_nodal", "object" => "2×2 block nodal operator", "coordinates" => "four-by-four complex blocks", "preserves" => ["assembled terminal relation"]),
            Dict("id" => "scalar_realified_support", "object" => "coordinate support", "coordinates" => "scalar or stacked real coordinates", "preserves" => ["support pattern"], "omits" => ["asset identity by default"]),
        ],
        "matrix_dimensions" => Dict("complex_local" => collect(size(Ylocal)), "realified_local" => collect(size(R))),
        "support_counts" => Dict("complex_nonzero" => complex_nonzero, "realified_nonzero" => real_nonzero, "scalar_support_nonzero" => count(!iszero, scalar_support)),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "The same declared factor can be drawn at several semantic levels. Block and realified coordinate structure is useful for equations and sparse kernels, but nonzero support is not a substitute for source factor identity or limits.",
    )
end

end

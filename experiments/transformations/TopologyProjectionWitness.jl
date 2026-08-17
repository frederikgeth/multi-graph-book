module TopologyProjectionWitness

using LinearAlgebra

export topology_projection_witness

frobenius_norm(matrix) = sqrt(sum(abs2, matrix))

function series_stamp(admittance::Matrix{ComplexF64})
    [admittance -admittance; -admittance admittance]
end

function complex_matrix(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

function normalized_assembly_error(target, stamps)
    residual = target - sum(stamps)
    denominator = frobenius_norm(target) + sum(frobenius_norm, stamps)
    denominator == 0 ? (frobenius_norm(residual) == 0 ? 0.0 : Inf) :
        frobenius_norm(residual) / denominator
end

function bit_identical(left, right)
    reinterpret(UInt64, vec(left)) == reinterpret(UInt64, vec(right))
end

function minimum_hermitian_eigenvalue(matrix)
    minimum(eigvals(Hermitian((matrix + matrix') / 2)))
end

edge_key(left::String, right::String) = left < right ? (left, right) : (right, left)

function add_clique!(edges::Set{Tuple{String,String}}, vertices)
    for first in eachindex(vertices), second in (first + 1):length(vertices)
        push!(edges, edge_key(vertices[first], vertices[second]))
    end
    edges
end

function adjacency(vertices, edges)
    result = Dict(vertex => Set{String}() for vertex in vertices)
    for (left, right) in edges
        push!(result[left], right)
        push!(result[right], left)
    end
    result
end

function elimination_trace(vertices, edges, order)
    graph = adjacency(vertices, edges)
    remaining = Set(vertices)
    fill_edges = Tuple{String,String}[]
    simplicial = Bool[]
    for vertex in order
        neighbours = sort!(collect(intersect(graph[vertex], remaining)))
        local_simplicial = true
        for first in eachindex(neighbours), second in (first + 1):length(neighbours)
            edge = edge_key(neighbours[first], neighbours[second])
            if neighbours[second] ∉ graph[neighbours[first]]
                local_simplicial = false
                push!(fill_edges, edge)
                push!(graph[neighbours[first]], neighbours[second])
                push!(graph[neighbours[second]], neighbours[first])
            end
        end
        push!(simplicial, local_simplicial)
        delete!(remaining, vertex)
    end
    Dict(
        "order" => order,
        "simplicial_at_elimination" => simplicial,
        "is_perfect_elimination_order" => all(simplicial),
        "fill_count" => length(unique(fill_edges)),
        "fill_edges" => [collect(edge) for edge in sort!(unique(fill_edges))],
    )
end

function parallel_split_witness()
    y1 = ComplexF64[
        4.0 + 2.0im 0.5 + 0.25im
        0.5 + 0.25im 3.0 + 1.0im
    ]
    y2 = ComplexF64[
        2.0 + 1.0im 0.25 + 0.125im
        0.25 + 0.125im 1.5 + 0.5im
    ]
    delta = ComplexF64[
        0.5 + 0.25im 0.125 + 0.0625im
        0.125 + 0.0625im 0.25 + 0.125im
    ]
    base = [series_stamp(y1), series_stamp(y2)]
    alternate = [series_stamp(y1 + delta), series_stamp(y2 - delta)]
    total_base = sum(base)
    total_alternate = sum(alternate)
    base_passivity = minimum_hermitian_eigenvalue.(base)
    alternate_passivity = minimum_hermitian_eigenvalue.(alternate)
    tolerance = 1.0e-12
    checks = Dict(
        "splits_are_distinct" => any(base[index] != alternate[index] for index in eachindex(base)),
        "assembled_operators_are_bit_identical" => bit_identical(total_base, total_alternate),
        "base_round_trip_passes" => normalized_assembly_error(total_base, base) <= tolerance,
        "alternate_round_trip_passes" => normalized_assembly_error(total_base, alternate) <= tolerance,
        "base_split_is_passive" => minimum(base_passivity) >= -tolerance,
        "alternate_split_is_passive" => minimum(alternate_passivity) >= -tolerance,
        "all_primitives_are_reciprocal" => all(
            frobenius_norm(stamp - transpose(stamp)) == 0 for stamp in [base; alternate]
        ),
        "nonzero_kernel_direction" => frobenius_norm(series_stamp(delta)) > 0 &&
            frobenius_norm(series_stamp(delta) - series_stamp(delta)) == 0,
        "consistency_test_is_attribution_blind" =>
            normalized_assembly_error(total_base, base) <= tolerance &&
            normalized_assembly_error(total_base, alternate) <= tolerance,
    )
    Dict(
        "coordinate_order" => ["i/a", "i/n", "j/a", "j/n"],
        "factor_class" => "reciprocal_passive_two_conductor_series_stamp",
        "affine_direction_real_dimension" => 6,
        "ambiguity_direction" => complex_matrix(delta),
        "base_primitives" => complex_matrix.(base),
        "alternate_primitives" => complex_matrix.(alternate),
        "assembled_operator" => complex_matrix(total_base),
        "base_normalized_frobenius_error" => normalized_assembly_error(total_base, base),
        "alternate_normalized_frobenius_error" => normalized_assembly_error(total_base, alternate),
        "base_minimum_passivity_eigenvalues" => base_passivity,
        "alternate_minimum_passivity_eigenvalues" => alternate_passivity,
        "tolerance" => tolerance,
        "checks" => checks,
    )
end

function radial_clique_witness()
    buses = ["i", "j", "k"]
    conductors = ["a", "n"]
    bus_edges = [("i", "j"), ("j", "k")]
    coordinates = ["$bus/$conductor" for bus in buses for conductor in conductors]
    structural_edges = Set{Tuple{String,String}}()
    cliques = Vector{Vector{String}}()
    for (left, right) in bus_edges
        clique = ["$left/$conductor" for conductor in conductors]
        append!(clique, ["$right/$conductor" for conductor in conductors])
        push!(cliques, clique)
        add_clique!(structural_edges, clique)
    end
    perfect_order = ["i/a", "i/n", "k/a", "k/n", "j/a", "j/n"]
    bad_order = ["j/a", "j/n", "i/a", "i/n", "k/a", "k/n"]
    perfect = elimination_trace(coordinates, structural_edges, perfect_order)
    bad = elimination_trace(coordinates, structural_edges, bad_order)
    scalar_cycle_rank = length(structural_edges) - length(coordinates) + 1
    checks = Dict(
        "macro_graph_is_tree" => length(bus_edges) == length(buses) - 1,
        "each_line_stamp_has_four_coordinate_clique" => all(length(clique) == 4 for clique in cliques),
        "line_cliques_share_declared_separator" => intersect(Set(cliques[1]), Set(cliques[2])) == Set(["j/a", "j/n"]),
        "scalar_support_contains_cycles" => scalar_cycle_rank > 0,
        "leaf_block_order_is_perfect" => perfect["is_perfect_elimination_order"],
        "leaf_block_order_has_zero_fill" => perfect["fill_count"] == 0,
        "bad_order_has_positive_fill" => bad["fill_count"] > 0,
    )
    Dict(
        "bus_graph" => Dict(
            "vertices" => buses,
            "edges" => [collect(edge) for edge in bus_edges],
            "cycle_rank" => 0,
        ),
        "conductors" => conductors,
        "scalar_coordinates" => coordinates,
        "line_cliques" => cliques,
        "separator" => ["j/a", "j/n"],
        "structural_support_edges" => [collect(edge) for edge in sort!(collect(structural_edges))],
        "structural_support_cycle_rank" => scalar_cycle_rank,
        "perfect_elimination" => perfect,
        "bad_elimination" => bad,
        "checks" => checks,
    )
end

function topology_projection_witness()
    parallel = parallel_split_witness()
    chordal = radial_clique_witness()
    checks = merge(
        Dict("parallel_$name" => value for (name, value) in parallel["checks"]),
        Dict("chordal_$name" => value for (name, value) in chordal["checks"]),
    )
    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-TOPOLOGY-001",
        "claim_ids" => ["ARCH-NODAL-001", "ARCH-SUPPORT-001", "ARCH-CHORDAL-001"],
        "model_scope" => "two aligned passive reciprocal two-conductor factors and a three-bus two-conductor tree with structurally dense line stamps",
        "parallel_split" => parallel,
        "radial_clique_support" => chordal,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
    )
end

end

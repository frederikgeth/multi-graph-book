module TranslationTraps

using LinearAlgebra

export energization_witness,
       symmetry_witness,
       terminal_rating_witness,
       translation_trap_witnesses

function _reachable(vertices, edges, sources)
    adjacency = Dict(String(vertex) => String[] for vertex in vertices)
    for edge in edges
        push!(adjacency[String(edge[1])], String(edge[2]))
        push!(adjacency[String(edge[2])], String(edge[1]))
    end
    reached = Set(String.(sources))
    queue = collect(reached)
    while !isempty(queue)
        vertex = popfirst!(queue)
        for neighbor in adjacency[vertex]
            neighbor in reached && continue
            push!(reached, neighbor)
            push!(queue, neighbor)
        end
    end
    reached
end

"Show that inventory connectivity and active-state energization are different predicates."
function energization_witness()
    vertices = ["source", "bus_a", "bus_b", "load"]
    asset_edges = [("source", "bus_a"), ("bus_a", "bus_b"), ("bus_b", "load")]
    active_edges = [("source", "bus_a"), ("bus_b", "load")]
    asset_reached = _reachable(vertices, asset_edges, ["source"])
    active_reached = _reachable(vertices, active_edges, ["source"])
    Dict{String,Any}(
        "vertices" => vertices,
        "asset_edges" => [collect(edge) for edge in asset_edges],
        "active_edges" => [collect(edge) for edge in active_edges],
        "source_bus" => "source",
        "load_bus" => "load",
        "connected_in_asset_graph" => "load" in asset_reached,
        "energized_in_active_graph" => "load" in active_reached,
        "open_member" => "line_bus_a_bus_b",
    )
end

"Show that reciprocal complex matrices can be symmetric without being Hermitian."
function symmetry_witness()
    matrix = ComplexF64[1.0 + 1.0im 0.0 + 0.2im; 0.0 + 0.2im 2.0 + 0.5im]
    hermitian_part = (matrix + adjoint(matrix)) / 2
    eigenvalues = real.(eigvals(Hermitian(hermitian_part)))
    Dict{String,Any}(
        "matrix" => [[Dict("real" => real(matrix[row, column]), "imag" => imag(matrix[row, column]))
                       for column in axes(matrix, 2)] for row in axes(matrix, 1)],
        "complex_symmetric" => norm(matrix - transpose(matrix)) <= 1.0e-12,
        "hermitian" => norm(matrix - adjoint(matrix)) <= 1.0e-12,
        "hermitian_part_min_eigenvalue" => minimum(eigenvalues),
        "hermitian_part_positive_semidefinite" => minimum(eigenvalues) >= -1.0e-12,
    )
end

"Show that a nominal-pi factor has distinct series and terminal currents."
function terminal_rating_witness()
    z_series = 0.08 + 0.16im
    y_series = inv(z_series)
    y_shunt_from = 0.10im
    y_shunt_to = 0.06im
    voltage_from = 1.0 + 0.0im
    voltage_to = 0.78 - 0.12im
    series_current = y_series * (voltage_from - voltage_to)
    current_from = series_current + y_shunt_from * voltage_from
    current_to = -series_current + y_shunt_to * voltage_to
    from_magnitude = abs(current_from)
    to_magnitude = abs(current_to)
    rating = (from_magnitude + to_magnitude) / 2
    Dict{String,Any}(
        "voltage_from_pu" => Dict("real" => real(voltage_from), "imag" => imag(voltage_from)),
        "voltage_to_pu" => Dict("real" => real(voltage_to), "imag" => imag(voltage_to)),
        "series_current_pu" => abs(series_current),
        "from_terminal_current_pu" => from_magnitude,
        "to_terminal_current_pu" => to_magnitude,
        "illustrative_terminal_rating_pu" => rating,
        "terminal_magnitudes_differ" => abs(from_magnitude - to_magnitude) > 1.0e-12,
        "from_terminal_exceeds_rating" => from_magnitude > rating,
        "to_terminal_exceeds_rating" => to_magnitude > rating,
    )
end

function translation_trap_witnesses()
    witnesses = Dict{String,Any}(
        "energization" => energization_witness(),
        "matrix_symmetry" => symmetry_witness(),
        "terminal_ratings" => terminal_rating_witness(),
    )
    witnesses["all_witnesses_pass"] =
        witnesses["energization"]["connected_in_asset_graph"] &&
        !witnesses["energization"]["energized_in_active_graph"] &&
        witnesses["matrix_symmetry"]["complex_symmetric"] &&
        !witnesses["matrix_symmetry"]["hermitian"] &&
        witnesses["matrix_symmetry"]["hermitian_part_positive_semidefinite"] &&
        witnesses["terminal_ratings"]["terminal_magnitudes_differ"] &&
        witnesses["terminal_ratings"]["from_terminal_exceeds_rating"] !=
        witnesses["terminal_ratings"]["to_terminal_exceeds_rating"]
    witnesses
end

end

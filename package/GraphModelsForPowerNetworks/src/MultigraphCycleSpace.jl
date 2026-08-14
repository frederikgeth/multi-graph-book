module MultigraphCycleSpace

using LinearAlgebra

export IdentifiedEdge,
       canonical_pair,
       connected_components,
       cycle_rank,
       edge_bridges,
       fundamental_cycle_matrix,
       incidence_matrix,
       simple_projection,
       ybus,
       five_bus_analysis,
       analysis_dict

"A loopless identified edge with a declared orientation and scalar series admittance."
struct IdentifiedEdge
    id::String
    bus_from::String
    bus_to::String
    admittance::ComplexF64
    current_limit::Union{Nothing,Float64}

    function IdentifiedEdge(id, bus_from, bus_to, admittance; current_limit=nothing)
        bus_from == bus_to && throw(ArgumentError("self-loops are outside this example"))
        iszero(admittance) && throw(ArgumentError("edge admittance must be nonzero"))
        current_limit === nothing || current_limit > 0 ||
            throw(ArgumentError("current limit must be positive"))
        new(
            String(id),
            String(bus_from),
            String(bus_to),
            ComplexF64(admittance),
            current_limit === nothing ? nothing : Float64(current_limit),
        )
    end
end

canonical_pair(i::AbstractString, j::AbstractString) = i < j ? (String(i), String(j)) : (String(j), String(i))

function _validate_vertices(vertices, edges)
    length(unique(vertices)) == length(vertices) || throw(ArgumentError("bus identifiers must be unique"))
    bus_set = Set(String.(vertices))
    length(unique(edge.id for edge in edges)) == length(edges) ||
        throw(ArgumentError("edge identifiers must be unique"))
    for edge in edges
        edge.bus_from in bus_set || throw(ArgumentError("unknown from bus $(edge.bus_from)"))
        edge.bus_to in bus_set || throw(ArgumentError("unknown to bus $(edge.bus_to)"))
    end
end

"Oriented bus-by-edge incidence matrix: -1 at from and +1 at to."
function incidence_matrix(vertices, edges)
    _validate_vertices(vertices, edges)
    row = Dict(String(bus) => index for (index, bus) in enumerate(vertices))
    A = zeros(Int, length(vertices), length(edges))
    for (column, edge) in enumerate(edges)
        A[row[edge.bus_from], column] = -1
        A[row[edge.bus_to], column] = 1
    end
    A
end

function connected_components(vertices, edges)
    _validate_vertices(vertices, edges)
    adjacency = Dict(String(bus) => String[] for bus in vertices)
    for edge in edges
        push!(adjacency[edge.bus_from], edge.bus_to)
        push!(adjacency[edge.bus_to], edge.bus_from)
    end
    unseen = Set(String.(vertices))
    components = Vector{Vector{String}}()
    while !isempty(unseen)
        root = minimum(unseen)
        delete!(unseen, root)
        queue = [root]
        component = String[]
        while !isempty(queue)
            bus = popfirst!(queue)
            push!(component, bus)
            for neighbor in adjacency[bus]
                neighbor in unseen || continue
                delete!(unseen, neighbor)
                push!(queue, neighbor)
            end
        end
        push!(components, sort(component))
    end
    sort!(components; by=first)
end

"Dimension of the real cycle space of a loopless undirected multigraph."
function cycle_rank(vertices, edges)
    length(edges) - length(vertices) + length(connected_components(vertices, edges))
end

function simple_projection(vertices, edges)
    bundles = Dict{Tuple{String,String},Vector{IdentifiedEdge}}()
    for edge in edges
        push!(get!(bundles, canonical_pair(edge.bus_from, edge.bus_to), IdentifiedEdge[]), edge)
    end
    projected = IdentifiedEdge[]
    membership = Dict{String,Vector{String}}()
    for pair in sort(collect(keys(bundles)))
        members = bundles[pair]
        id = "e_$(pair[1])$(pair[2])"
        push!(projected, IdentifiedEdge(id, pair[1], pair[2], sum(edge.admittance for edge in members)))
        membership[id] = sort([edge.id for edge in members])
    end
    (edges=projected, membership=membership)
end

function ybus(vertices, edges)
    A = incidence_matrix(vertices, edges)
    ComplexF64.(A) * Diagonal([edge.admittance for edge in edges]) * transpose(A)
end

function _tree_path(vertices, edges, tree_indices, start, goal)
    adjacency = Dict(String(bus) => Tuple{Int,String}[] for bus in vertices)
    for index in tree_indices
        edge = edges[index]
        push!(adjacency[edge.bus_from], (index, edge.bus_to))
        push!(adjacency[edge.bus_to], (index, edge.bus_from))
    end
    parent = Dict(start => (0, ""))
    queue = [start]
    while !isempty(queue) && !haskey(parent, goal)
        bus = popfirst!(queue)
        for (edge_index, neighbor) in adjacency[bus]
            haskey(parent, neighbor) && continue
            parent[neighbor] = (edge_index, bus)
            push!(queue, neighbor)
        end
    end
    haskey(parent, goal) || throw(ArgumentError("tree does not connect chord endpoints $start and $goal"))
    path = Tuple{Int,String,String}[]
    current = goal
    while current != start
        edge_index, previous = parent[current]
        push!(path, (edge_index, previous, current))
        current = previous
    end
    reverse(path)
end

"Signed edge-by-cycle matrix induced by a declared spanning forest."
function fundamental_cycle_matrix(vertices, edges, tree_ids)
    _validate_vertices(vertices, edges)
    id_to_index = Dict(edge.id => index for (index, edge) in enumerate(edges))
    length(unique(tree_ids)) == length(tree_ids) || throw(ArgumentError("tree edge identifiers must be unique"))
    all(haskey(id_to_index, id) for id in tree_ids) || throw(ArgumentError("tree contains an unknown edge"))
    tree_indices = [id_to_index[id] for id in tree_ids]
    tree_edges = edges[tree_indices]
    cycle_rank(vertices, tree_edges) == 0 || throw(ArgumentError("declared tree edges contain a cycle"))
    length(connected_components(vertices, tree_edges)) == length(connected_components(vertices, edges)) ||
        throw(ArgumentError("declared tree is not a spanning forest"))

    chord_indices = [index for index in eachindex(edges) if index ∉ Set(tree_indices)]
    C = zeros(Int, length(edges), length(chord_indices))
    for (column, chord_index) in enumerate(chord_indices)
        chord = edges[chord_index]
        C[chord_index, column] = 1
        # The chord is traversed from bus_from to bus_to. Close the cycle along
        # the tree from bus_to back to bus_from.
        for (edge_index, from_bus, to_bus) in
            _tree_path(vertices, edges, tree_indices, chord.bus_to, chord.bus_from)
            edge = edges[edge_index]
            C[edge_index, column] =
                edge.bus_from == from_bus && edge.bus_to == to_bus ? 1 : -1
        end
    end
    (matrix=C, chord_ids=[edges[index].id for index in chord_indices])
end

function edge_bridges(vertices, edges)
    base_components = length(connected_components(vertices, edges))
    bridges = String[]
    for removed in eachindex(edges)
        retained = [edge for (index, edge) in enumerate(edges) if index != removed]
        length(connected_components(vertices, retained)) > base_components && push!(bridges, edges[removed].id)
    end
    sort(bridges)
end

function five_bus_analysis()
    vertices = ["i", "j", "k", "l", "m"]
    edges = [
        IdentifiedEdge("q", "j", "i", 10.0; current_limit=100.0),
        IdentifiedEdge("r", "i", "j", 1.0; current_limit=100.0),
        IdentifiedEdge("s", "j", "k", 5.0),
        IdentifiedEdge("t", "k", "i", 10 / 3),
        IdentifiedEdge("v", "l", "j", 2.5),
        IdentifiedEdge("w", "k", "l", 2.0),
        IdentifiedEdge("x", "l", "m", 5 / 3),
    ]
    tree_ids = ["r", "s", "w", "x"]
    A = incidence_matrix(vertices, edges)
    fundamental = fundamental_cycle_matrix(vertices, edges, tree_ids)
    projection = simple_projection(vertices, edges)
    A_simple = incidence_matrix(vertices, projection.edges)
    source_ybus = ybus(vertices, edges)
    projected_ybus = ybus(vertices, projection.edges)

    delta_u = 15.0
    parallel_members = edges[1:2]
    member_currents = [abs(edge.admittance * delta_u) for edge in parallel_members]
    member_limits = [only([edge.current_limit]) for edge in parallel_members]
    aggregate_current = sum(member_currents)
    aggregate_limit = sum(member_limits)
    source_voltage_limit = minimum(member_limits ./ abs.([edge.admittance for edge in parallel_members]))
    aggregate_voltage_limit = aggregate_limit / abs(sum(edge.admittance for edge in parallel_members))

    Dict{String,Any}(
        "vertices" => vertices,
        "edges" => edges,
        "tree_ids" => tree_ids,
        "incidence" => A,
        "incidence_rank" => rank(Float64.(A)),
        "cycle_rank" => cycle_rank(vertices, edges),
        "fundamental_cycle_matrix" => fundamental.matrix,
        "fundamental_chords" => fundamental.chord_ids,
        "cycle_residual" => maximum(abs, A * fundamental.matrix),
        "bridges" => edge_bridges(vertices, edges),
        "simple_edges" => projection.edges,
        "simple_membership" => projection.membership,
        "simple_incidence_rank" => rank(Float64.(A_simple)),
        "simple_cycle_rank" => cycle_rank(vertices, projection.edges),
        "ybus_max_difference" => maximum(abs, source_ybus - projected_ybus),
        "parallel_witness" => Dict(
            "voltage_difference_V" => delta_u,
            "member_currents_A" => member_currents,
            "member_limits_A" => member_limits,
            "aggregate_current_A" => aggregate_current,
            "aggregate_limit_A" => aggregate_limit,
            "source_voltage_limit_V" => source_voltage_limit,
            "aggregate_voltage_limit_V" => aggregate_voltage_limit,
            "aggregate_feasible" => aggregate_current <= aggregate_limit,
            "source_feasible" => all(member_currents .<= member_limits),
        ),
    )
end

function _matrix_rows(matrix)
    [collect(row) for row in eachrow(matrix)]
end

function analysis_dict(result=five_bus_analysis(); bmopf_extra_edges=nothing)
    edges = result["edges"]
    simple_edges = result["simple_edges"]
    Dict{String,Any}(
        "schema_version" => "1.0.0",
        "analysis_id" => "GRAPH-CYCLE-001",
        "model_scope" => "connected loopless scalar series bus-branch multigraph",
        "source" => Dict(
            "buses" => result["vertices"],
            "forward_topology" => [Dict(
                "line" => edge.id,
                "from" => edge.bus_from,
                "to" => edge.bus_to,
                "series_admittance_S" => real(edge.admittance),
                "current_limit_A" => edge.current_limit,
            ) for edge in edges],
        ),
        "cycle_space" => Dict(
            "incidence_rank" => result["incidence_rank"],
            "cycle_rank" => result["cycle_rank"],
            "spanning_tree_lines" => result["tree_ids"],
            "chord_lines" => result["fundamental_chords"],
            "line_order" => [edge.id for edge in edges],
            "fundamental_cycle_matrix" => _matrix_rows(result["fundamental_cycle_matrix"]),
            "incidence_cycle_residual" => result["cycle_residual"],
            "bridges" => result["bridges"],
        ),
        "simple_projection" => Dict(
            "edges" => [Dict(
                "id" => edge.id,
                "endpoints" => [edge.bus_from, edge.bus_to],
                "aggregate_series_admittance_S" => real(edge.admittance),
                "source_members" => result["simple_membership"][edge.id],
            ) for edge in simple_edges],
            "incidence_rank" => result["simple_incidence_rank"],
            "cycle_rank" => result["simple_cycle_rank"],
            "lost_cycle_dimension" => result["cycle_rank"] - result["simple_cycle_rank"],
        ),
        "electrical_check" => Dict(
            "maximum_ybus_difference" => result["ybus_max_difference"],
            "parallel_decision_witness" => result["parallel_witness"],
        ),
        "bmopftools_cross_check" => Dict(
            "n_extra_edges" => bmopf_extra_edges,
            "expected" => result["cycle_rank"],
        ),
        "interpretation" => Dict(
            "simple_projection" => "forgets the q/r member distinction and one cycle-space dimension",
            "electrical_aggregation" => "preserves the scalar series nodal admittance but requires member-current recovery for source limits",
            "spanning_tree" => "selects coordinates; chord lines q, t, and v remain in the source model",
            "physical_tree" => "would require a state change or a separate preservation certificate",
        ),
    )
end

end

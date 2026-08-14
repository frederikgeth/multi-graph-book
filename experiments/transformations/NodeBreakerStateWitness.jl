module NodeBreakerStateWitness

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export evaluate_node_breaker_states

const VERTICES = ["c1", "c2", "c3", "c4"]
const LINES = [
    IdentifiedEdge("l1", "c1", "c2", 1.0),
    IdentifiedEdge("l2", "c2", "c3", 1.0),
    IdentifiedEdge("l3", "c3", "c4", 1.0),
]
const SWITCHES = Dict(
    "s12" => IdentifiedEdge("s12", "c1", "c2", 1.0),
    "s13" => IdentifiedEdge("s13", "c1", "c3", 1.0),
)

function _union(parent, a, b)
    ra = parent[a]
    rb = parent[b]
    ra == rb && return
    parent[rb] = ra
end

function _components(closed)
    parent = Dict(vertex => vertex for vertex in VERTICES)
    for id in closed
        edge = SWITCHES[id]
        _union(parent, edge.bus_from, edge.bus_to)
    end
    roots = Dict(vertex => begin
        root = vertex
        while parent[root] != root
            root = parent[root]
        end
        root
    end for vertex in VERTICES)
    Dict(vertex => "N" * string(findfirst(==(roots[vertex]), unique(values(roots)))) for vertex in VERTICES)
end

function _state_assignments(states)
    unknown = [id for (id, state) in states if state == "unknown"]
    isempty(unknown) && return [states]
    assignments = Dict{String,String}[]
    for mask in 0:(2^length(unknown)-1)
        assignment = copy(states)
        for (index, id) in enumerate(unknown)
            assignment[id] = ((mask >> (index - 1)) & 1) == 1 ? "closed" : "open"
        end
        push!(assignments, assignment)
    end
    assignments
end

function _analyze(states)
    closed = [id for (id, state) in states if state == "closed"]
    active_switches = [SWITCHES[id] for id in closed]
    active_members = vcat(LINES, active_switches)
    simple = simple_projection(VERTICES, active_members)
    components = _components(closed)
    compiled_edges = IdentifiedEdge[]
    for edge in LINES
        from = components[edge.bus_from]
        to = components[edge.bus_to]
        from == to && continue
        push!(compiled_edges, IdentifiedEdge(edge.id, from, to, edge.admittance))
    end
    buses = unique(vcat(values(components)...))
    compiled_simple = simple_projection(buses, compiled_edges)
    Dict(
        "switch_states" => states,
        "closed_switches" => closed,
        "active_members" => [edge.id for edge in active_members],
        "connectivity_components" => components,
        "topological_buses" => buses,
        "active_member_cycle_rank" => cycle_rank(VERTICES, active_members),
        "active_adjacency_cycle_rank" => cycle_rank(VERTICES, simple.edges),
        "compiled_bus_cycle_rank" => cycle_rank(buses, compiled_simple.edges),
        "member_radial" => cycle_rank(VERTICES, active_members) == 0,
        "adjacency_radial" => cycle_rank(VERTICES, simple.edges) == 0,
        "compiled_bus_radial" => cycle_rank(buses, compiled_simple.edges) == 0,
        "compiled_edges" => [edge.id for edge in compiled_edges],
    )
end

function evaluate_node_breaker_states()
    scenarios = Dict(
        "radial_open" => Dict("s12" => "open", "s13" => "open"),
        "parallel_closed" => Dict("s12" => "closed", "s13" => "open"),
        "cycle_closed" => Dict("s12" => "open", "s13" => "closed"),
        "unknown_switch" => Dict("s12" => "unknown", "s13" => "open"),
    )
    rows = Dict{String,Any}[]
    for (name, states) in sort(collect(scenarios); by=first)
        realizations = _state_assignments(states)
        analyses = [_analyze(realization) for realization in realizations]
        push!(rows, Dict(
            "scenario" => name,
            "switch_states" => states,
            "realization_count" => length(analyses),
            "analysis" => length(analyses) == 1 ? analyses[1] : nothing,
            "possible_member_radial" => any(row["member_radial"] for row in analyses),
            "possible_nonradial_member" => any(!row["member_radial"] for row in analyses),
            "possible_adjacency_radial" => any(row["adjacency_radial"] for row in analyses),
            "possible_nonradial_adjacency" => any(!row["adjacency_radial"] for row in analyses),
            "classification" => length(analyses) == 1 ? "resolved" : "state-unknown; enumerate admissible realizations",
            "realizations" => length(analyses) == 1 ? Any[] : analyses,
        ))
    end
    by_name = Dict(row["scenario"] => row for row in rows)
    checks = Dict(
        "radial_open_is_resolved_radial" => by_name["radial_open"]["analysis"]["member_radial"] && by_name["radial_open"]["analysis"]["adjacency_radial"],
        "parallel_closed_separates_member_and_adjacency_radiality" => !by_name["parallel_closed"]["analysis"]["member_radial"] && by_name["parallel_closed"]["analysis"]["adjacency_radial"],
        "cycle_closed_is_nonradial" => !by_name["cycle_closed"]["analysis"]["member_radial"] && !by_name["cycle_closed"]["analysis"]["adjacency_radial"],
        "unknown_state_is_not_collapsed" => by_name["unknown_switch"]["classification"] == "state-unknown; enumerate admissible realizations" && by_name["unknown_switch"]["realization_count"] == 2,
        "unknown_state_has_both_radialities" => by_name["unknown_switch"]["possible_member_radial"] && by_name["unknown_switch"]["possible_nonradial_member"],
    )
    (; witness_id = "TOPO-NB-001",
       model_scope = "four-connectivity-node node-breaker fixture with two switch assets and state-conditioned bus compilation",
       vertices = VERTICES,
       line_members = [edge.id for edge in LINES],
       switch_assets = [Dict("id" => id, "from" => edge.bus_from, "to" => edge.bus_to, "states" => ["open", "closed", "unknown"]) for (id, edge) in sort(collect(SWITCHES); by=first)],
       rows,
       checks,
       interpretation = "Unknown switch states are not silently treated as open or closed. Adjacency-radiality, member-radiality, and compiled-bus radiality are separate predicates evaluated after the declared state and contraction map.")
end

end

module ActiveRadiality

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export active_radiality_witness

function _edges(ids, edges)
    selected = Set(String.(ids))
    [edge for edge in edges if edge.id in selected]
end

"Compare inventory and active-state radiality in both simple and member graphs."
function active_radiality_witness()
    vertices = ["source", "a", "b", "load"]
    edges = [
        IdentifiedEdge("s", "source", "a", 1.0),
        IdentifiedEdge("l1", "a", "b", 2.0),
        IdentifiedEdge("l2", "a", "b", 1.0),
        IdentifiedEdge("d", "b", "load", 1.0),
    ]
    active_ids = ["s", "l1", "d"]
    active = _edges(active_ids, edges)
    inventory_simple = simple_projection(vertices, edges)
    active_simple = simple_projection(vertices, active)
    Dict{String,Any}(
        "vertices" => vertices,
        "inventory_members" => [edge.id for edge in edges],
        "active_members" => active_ids,
        "open_members" => [edge.id for edge in edges if edge.id ∉ Set(active_ids)],
        "inventory_member_cycle_rank" => cycle_rank(vertices, edges),
        "active_member_cycle_rank" => cycle_rank(vertices, active),
        "inventory_adjacency_cycle_rank" => cycle_rank(vertices, inventory_simple.edges),
        "active_adjacency_cycle_rank" => cycle_rank(vertices, active_simple.edges),
        "inventory_member_radial" => cycle_rank(vertices, edges) == 0,
        "active_member_radial" => cycle_rank(vertices, active) == 0,
        "inventory_adjacency_radial" => cycle_rank(vertices, inventory_simple.edges) == 0,
        "active_adjacency_radial" => cycle_rank(vertices, active_simple.edges) == 0,
        "hidden_inventory_parallel_cycle" => cycle_rank(vertices, edges) > cycle_rank(vertices, inventory_simple.edges),
        "active_state_is_tree" => length(active) == length(vertices) - 1 &&
            cycle_rank(vertices, active) == 0,
    )
end

end

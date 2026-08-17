module ActiveRadiality

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export active_radiality_witness,
       five_bus_active_radiality_witness

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

"Record inventory and declared spanning-tree radiality for the five-bus multigraph."
function five_bus_active_radiality_witness()
    analysis = five_bus_analysis()
    vertices = analysis["vertices"]
    edges = analysis["edges"]
    inventory_ids = [edge.id for edge in edges]
    tree_ids = analysis["tree_ids"]
    states = Dict{String,Any}[]
    for (state, ids) in (("inventory", inventory_ids), ("declared_spanning_tree", tree_ids))
        active = _edges(ids, edges)
        simple = simple_projection(vertices, active)
        push!(states, Dict(
            "state" => state,
            "active_members" => ids,
            "member_cycle_rank" => cycle_rank(vertices, active),
            "adjacency_cycle_rank" => cycle_rank(vertices, simple.edges),
            "member_radial" => cycle_rank(vertices, active) == 0,
            "adjacency_radial" => cycle_rank(vertices, simple.edges) == 0,
            "active_member_count" => length(active),
        ))
    end
    inventory, tree = states
    checks = Dict(
        "inventory_member_cycle_rank_is_three" => inventory["member_cycle_rank"] == 3,
        "inventory_adjacency_cycle_rank_is_two" => inventory["adjacency_cycle_rank"] == 2,
        "inventory_is_not_radial" => !inventory["member_radial"] && !inventory["adjacency_radial"],
        "declared_tree_is_member_radial" => tree["member_radial"],
        "declared_tree_is_adjacency_radial" => tree["adjacency_radial"],
        "declared_tree_has_five_bus_tree_size" => tree["active_member_count"] == length(vertices) - 1,
    )
    Dict(
        "witness_id" => "TR-GRAPH-ACTIVE-001",
        "evidence_type" => "five_bus_inventory_and_active_radiality_witness",
        "source_fixture" => "experiments/generated/five-bus-cycle-space-analysis.json",
        "vertices" => vertices,
        "states" => states,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "Inventory and active-state radiality are evaluated separately on the identified multigraph and its simple endpoint projection; the declared spanning tree is radial at both levels.",
    )
end

end

module RunningNetworkRadialityWitness

using JSON3

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export evaluate_running_network_radiality

function _edge(id, from, to)
    IdentifiedEdge(id, from, to, 1.0)
end

function _fixture(root)
    JSON3.read(read(joinpath(root, "data", "running-network", "v0.1.0.json"), String), Dict{String,Any})
end

function _network_edges(network; switch_state="closed", omit_lines=String[])
    omitted = Set(omit_lines)
    lines = IdentifiedEdge[]
    terminal_objects = Dict{String,Any}[]
    for id in sort(collect(keys(network["line"])))
        id in omitted && continue
        line = network["line"][id]
        push!(lines, _edge("line/$id", line["bus_from"], line["bus_to"]))
        push!(terminal_objects, Dict(
            "asset" => "line/$id", "kind" => "line",
            "from" => Dict("bus" => line["bus_from"], "terminals" => line["terminal_map_from"]),
            "to" => Dict("bus" => line["bus_to"], "terminals" => line["terminal_map_to"]),
        ))
    end
    switch = network["switch"]["w0"]
    if switch_state == "closed"
        push!(lines, _edge("switch/w0", switch["bus_from"], switch["bus_to"]))
    end
    push!(terminal_objects, Dict(
        "asset" => "switch/w0", "kind" => "switch", "state" => switch_state,
        "from" => Dict("bus" => switch["bus_from"], "terminals" => switch["terminal_map_from"]),
        "to" => Dict("bus" => switch["bus_to"], "terminals" => switch["terminal_map_to"]),
    ))

    transformer = network["transformer"]["n_winding"]["x1"]
    windings = transformer["windings"]
    for index in 2:length(windings)
        winding = windings[index]
        id = "transformer/x1/w$(index)"
        push!(lines, _edge(id, windings[1]["bus"], winding["bus"]))
        push!(terminal_objects, Dict(
            "asset" => id, "kind" => "transformer_winding",
            "from" => Dict("bus" => windings[1]["bus"], "terminals" => windings[1]["terminal_map"]),
            "to" => Dict("bus" => winding["bus"], "terminals" => winding["terminal_map"]),
            "factor_parent" => "transformer/x1",
        ))
    end
    lines, terminal_objects
end

function _analyze(network; switch_state="closed", omit_lines=String[])
    vertices = sort(collect(keys(network["bus"])))
    edges, terminal_objects = _network_edges(network; switch_state, omit_lines)
    simple = simple_projection(vertices, edges)
    components = connected_components(vertices, edges)
    active_line_ids = sort([edge.id for edge in edges if startswith(edge.id, "line/")])
    active_switch_ids = sort([edge.id for edge in edges if startswith(edge.id, "switch/")])
    active_transformer_winding_ids = sort([edge.id for edge in edges if startswith(edge.id, "transformer/")])
    Dict(
        "switch_state" => switch_state,
        "omitted_lines" => omit_lines,
        "member_ids" => [edge.id for edge in edges],
        "active_inventory" => Dict(
            "line_ids" => active_line_ids,
            "switch_ids" => active_switch_ids,
            "transformer_winding_ids" => active_transformer_winding_ids,
            "member_edge_count" => length(edges),
            "simple_edge_count" => length(simple.edges),
            "component_count" => length(components),
        ),
        "terminal_objects" => terminal_objects,
        "terminal_object_count" => length(terminal_objects),
        "bus_components" => components,
        "member_cycle_rank" => cycle_rank(vertices, edges),
        "adjacency_cycle_rank" => cycle_rank(vertices, simple.edges),
        "member_radial" => cycle_rank(vertices, edges) == 0,
        "adjacency_radial" => cycle_rank(vertices, simple.edges) == 0,
        "simple_membership" => simple.membership,
    )
end

function evaluate_running_network_radiality(root=normpath(joinpath(@__DIR__, "..", "..")))
    network = _fixture(root)
    scenarios = [
        ("base_closed", "closed", String[]),
        ("switch_open", "open", String[]),
        ("l2_outage", "closed", ["l2"]),
        ("switch_open_l2_outage", "open", ["l2"]),
    ]
    rows = [Dict("scenario" => name, "analysis" => _analyze(network; switch_state, omit_lines)) for (name, switch_state, omit_lines) in scenarios]
    by_name = Dict(row["scenario"] => row["analysis"] for row in rows)
    checks = Dict(
        "base_preserves_parallel_member_cycle" => !by_name["base_closed"]["member_radial"] && by_name["base_closed"]["adjacency_radial"],
        "switch_open_preserves_member_cycle" => !by_name["switch_open"]["member_radial"] && by_name["switch_open"]["adjacency_radial"],
        "line_outage_removes_parallel_cycle" => by_name["l2_outage"]["member_radial"] && by_name["l2_outage"]["adjacency_radial"],
        "switch_and_line_outage_remain_radial" => by_name["switch_open_l2_outage"]["member_radial"],
        "terminal_provenance_retained" => all(analysis["terminal_object_count"] > 0 for analysis in values(by_name)),
        "transformer_factor_provenance_retained" => any(startswith(object["asset"], "transformer/") for object in by_name["base_closed"]["terminal_objects"]),
        "switch_state_changes_inventory" => by_name["base_closed"]["active_inventory"]["switch_ids"] != by_name["switch_open"]["active_inventory"]["switch_ids"],
        "line_outage_changes_inventory" => by_name["base_closed"]["active_inventory"]["line_ids"] != by_name["l2_outage"]["active_inventory"]["line_ids"],
        "switch_open_excludes_switch_member" => isempty(by_name["switch_open"]["active_inventory"]["switch_ids"]),
        "line_outage_excludes_l2_member" => !("line/l2" in by_name["l2_outage"]["active_inventory"]["line_ids"]),
        "transformer_windings_remain_explicit" => length(by_name["base_closed"]["active_inventory"]["transformer_winding_ids"]) == 2,
    )
    (; witness_id = "TOPO-RUNNING-001",
       model_scope = "running-network v0.1.0 bus/member graph with switch and line-outage variants plus conductor-terminal provenance",
       source_fixture = "data/running-network/v0.1.0.json",
       rows,
       checks,
       interpretation = "The running fixture preserves identified lines, the switch asset, multiwinding transformer winding provenance, and terminal maps. Radiality is reported both on the member multigraph and its simple adjacency projection; line outages change member cycles, while opening the existing switch does not remove the parallel-line cycle.")
end

end

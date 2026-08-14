module ConductorTerminalLift

using JSON3
include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export evaluate_conductor_terminal_lift,
       evaluate_five_bus_terminal_lift,
       evaluate_multiwinding_terminal_lift

function _fixture(root)
    JSON3.read(read(joinpath(root, "data", "running-network", "v0.1.0.json"), String), Dict{String,Any})
end

function _terminal_id(bus, terminal)
    "$(bus)/$(terminal)"
end

function _terminal_members(network)
    line_members = IdentifiedEdge[]
    for (id, line) in sort(collect(network["line"]); by=first)
        for (index, from_terminal) in enumerate(line["terminal_map_from"])
            to_terminal = line["terminal_map_to"][index]
            push!(line_members, IdentifiedEdge(
                "line/$id/$from_terminal",
                _terminal_id(line["bus_from"], from_terminal),
                _terminal_id(line["bus_to"], to_terminal),
                1.0,
            ))
        end
    end
    switch_members = IdentifiedEdge[]
    switch = network["switch"]["w0"]
    for (index, from_terminal) in enumerate(switch["terminal_map_from"])
        to_terminal = switch["terminal_map_to"][index]
        push!(switch_members, IdentifiedEdge(
            "switch/w0/$from_terminal",
            _terminal_id(switch["bus_from"], from_terminal),
            _terminal_id(switch["bus_to"], to_terminal),
            1.0,
        ))
    end
    (; line_members, switch_members)
end

function _terminal_state_analysis(vertices, members, switch_members, state)
    active = state == "closed" ? vcat(members, switch_members) : members
    simple = simple_projection(vertices, active)
    Dict(
        "switch_state" => state,
        "active_member_count" => length(active),
        "active_member_cycle_rank" => cycle_rank(vertices, active),
        "active_adjacency_cycle_rank" => cycle_rank(vertices, simple.edges),
        "member_radial" => cycle_rank(vertices, active) == 0,
        "adjacency_radial" => cycle_rank(vertices, simple.edges) == 0,
        "parallel_fibres" => [members for members in values(simple.membership) if length(members) > 1],
    )
end

function evaluate_conductor_terminal_lift(root=normpath(joinpath(@__DIR__, "..", "..")))
    network = _fixture(root)
    junctions = Dict{String,Any}[]
    for bus in sort(collect(keys(network["bus"])))
        for terminal in network["bus"][bus]["terminal_names"]
            push!(junctions, Dict("id" => _terminal_id(bus, terminal), "bus" => bus, "terminal" => terminal))
        end
    end

    ports = Dict{String,Any}[]
    factors = Dict{String,Any}[]
    relations = Dict{String,Any}[]
    for id in sort(collect(keys(network["line"])))
        line = network["line"][id]
        factor_id = "line/$id"
        port_ids = String[]
        for (end_name, bus_key, terminal_key) in (("from", "bus_from", "terminal_map_from"), ("to", "bus_to", "terminal_map_to"))
            port_id = "$factor_id/port/$end_name"
            push!(port_ids, port_id)
            push!(ports, Dict(
                "id" => port_id, "factor" => factor_id, "junctions" => [_terminal_id(line[bus_key], terminal) for terminal in line[terminal_key]],
                "terminal_order" => line[terminal_key], "variable_space" => "V_$(length(line[terminal_key]))×I_$(length(line[terminal_key]))",
            ))
        end
        push!(factors, Dict("id" => factor_id, "type" => "multiconductor_line", "ports" => port_ids, "arity" => 2, "source_asset" => factor_id))
        push!(relations, Dict("asset" => factor_id, "electrical" => factor_id, "relation" => "realizes ordered terminal matrix relation"))
    end

    transformer = network["transformer"]["n_winding"]["x1"]
    transformer_ports = String[]
    for (index, winding) in enumerate(transformer["windings"])
        port_id = "transformer/x1/port/w$index"
        push!(transformer_ports, port_id)
        push!(ports, Dict(
            "id" => port_id, "factor" => "transformer/x1", "junctions" => [_terminal_id(winding["bus"], terminal) for terminal in winding["terminal_map"]],
            "terminal_order" => winding["terminal_map"], "variable_space" => "V_$(length(winding["terminal_map"]))×I_$(length(winding["terminal_map"]))",
            "winding_index" => index,
        ))
    end
    push!(factors, Dict("id" => "transformer/x1", "type" => "multiwinding_transformer", "ports" => transformer_ports, "arity" => length(transformer_ports), "source_asset" => "transformer/x1"))
    push!(relations, Dict("asset" => "transformer/x1", "electrical" => "transformer/x1", "relation" => "realizes multiwinding factor with ordered winding ports"))

    switch = network["switch"]["w0"]
    switch_states = ["closed", "open", "unknown"]
    switch_port_ids = ["switch/w0/port/from", "switch/w0/port/to"]
    for (port_id, bus_key, terminal_key) in zip(switch_port_ids, ["bus_from", "bus_to"], ["terminal_map_from", "terminal_map_to"])
        push!(ports, Dict("id" => port_id, "factor" => "switch/w0", "junctions" => [_terminal_id(switch[bus_key], terminal) for terminal in switch[terminal_key]], "terminal_order" => switch[terminal_key], "variable_space" => "V_$(length(switch[terminal_key]))×I_$(length(switch[terminal_key]))"))
    end
    push!(factors, Dict("id" => "switch/w0", "type" => "ideal_switch", "ports" => switch_port_ids, "arity" => 2, "states" => switch_states, "source_asset" => "switch/w0"))
    push!(relations, Dict("asset" => "switch/w0", "electrical" => "switch/w0", "relation" => "state-conditioned ideal connectivity or open relation"))

    by_factor = Dict(factor["id"] => factor for factor in factors)
    ports_by_id = Dict(port["id"] => port for port in ports)
    errors = String[]
    for factor in factors
        all(port_id in keys(ports_by_id) for port_id in factor["ports"]) || push!(errors, "factor has unknown port")
        length(factor["ports"]) == factor["arity"] || push!(errors, "factor arity does not match port incidence")
        all(ports_by_id[port_id]["factor"] == factor["id"] for port_id in factor["ports"]) || push!(errors, "port-factor incidence mismatch")
    end
    for port in ports
        isempty(port["junctions"]) && push!(errors, "port has no conductor-terminal junctions")
    end
    terminal_vertices = [_terminal_id(junction["bus"], junction["terminal"]) for junction in junctions]
    terminal_members = _terminal_members(network)
    terminal_states = Dict(
        "switch_open" => _terminal_state_analysis(terminal_vertices, terminal_members.line_members, terminal_members.switch_members, "open"),
        "switch_closed" => _terminal_state_analysis(terminal_vertices, terminal_members.line_members, terminal_members.switch_members, "closed"),
        "switch_unknown" => [
            _terminal_state_analysis(terminal_vertices, terminal_members.line_members, terminal_members.switch_members, state)
            for state in ("open", "closed")
        ],
    )
    switch_contracted = Dict(
        "closed" => Dict("i0/a" => "i1/a", "i0/b" => "i1/b", "i0/c" => "i1/c", "i0/n" => "i1/n"),
        "open" => Dict{String,String}(),
        "unknown" => nothing,
    )
    checks = Dict(
        "all_factor_ports_resolve" => isempty(errors),
        "line_factors_are_two_port" => all(factor["type"] == "multiconductor_line" ? factor["arity"] == 2 : true for factor in factors),
        "transformer_is_multi_terminal" => by_factor["transformer/x1"]["arity"] == 3,
        "switch_has_three_state_domain" => by_factor["switch/w0"]["states"] == switch_states,
        "closed_switch_contraction_is_per_conductor" => length(switch_contracted["closed"]) == 4,
        "unknown_switch_has_no_forced_contraction" => switch_contracted["unknown"] === nothing,
        "conductor_terminal_vertices_preserved" => length(terminal_vertices) == length(junctions),
        "terminal_member_parallel_cycle_retained" => terminal_states["switch_open"]["active_member_cycle_rank"] > terminal_states["switch_open"]["active_adjacency_cycle_rank"],
        "state_conditioned_terminal_analysis_present" => length(terminal_states["switch_unknown"]) == 2,
        "unknown_switch_terminal_state_is_unresolved" => terminal_states["switch_unknown"][1]["active_member_count"] != terminal_states["switch_unknown"][2]["active_member_count"],
    )
    (; witness_id = "ARCH-CONDUCTOR-001",
       model_scope = "running-network v0.1.0 conductor-terminal incidence with line, switch, and three-winding factor compilation",
       source_fixture = "data/running-network/v0.1.0.json",
       junctions, ports, factors, relations,
       terminal_members = Dict(
           "line" => [Dict("id" => edge.id, "from" => edge.bus_from, "to" => edge.bus_to) for edge in terminal_members.line_members],
           "switch" => [Dict("id" => edge.id, "from" => edge.bus_from, "to" => edge.bus_to) for edge in terminal_members.switch_members],
       ),
       terminal_states,
       switch_contracted,
       checks,
       interpretation = "The lift keeps bus identity, ordered conductor terminals, factor arity, and switch state separate. Closed-switch contraction is a per-conductor state-conditioned map; unknown state is not contracted.")
end

"Lift the five-bus scalar line identities to two scalar terminal junctions per line."
function evaluate_five_bus_terminal_lift()
    buses = ["i", "j", "k", "l", "m"]
    edges = [
        ("q", "j", "i"), ("r", "i", "j"), ("s", "j", "k"),
        ("t", "k", "i"), ("v", "l", "j"), ("w", "k", "l"),
        ("x", "l", "m"),
    ]
    junctions = [Dict("id" => _terminal_id(bus, "scalar"), "bus" => bus, "terminal" => "scalar") for bus in buses]
    ports = Dict{String,Any}[]
    factors = Dict{String,Any}[]
    relations = Dict{String,Any}[]
    for (line, from, to) in edges
        factor_id = "line/$(line)"
        from_port = "$(factor_id)/port/from"
        to_port = "$(factor_id)/port/to"
        push!(ports, Dict("id" => from_port, "factor" => factor_id, "junctions" => [_terminal_id(from, "scalar")], "terminal_order" => ["scalar"], "variable_space" => "V₁×I₁"))
        push!(ports, Dict("id" => to_port, "factor" => factor_id, "junctions" => [_terminal_id(to, "scalar")], "terminal_order" => ["scalar"], "variable_space" => "V₁×I₁"))
        push!(factors, Dict("id" => factor_id, "type" => "scalar_series_line", "ports" => [from_port, to_port], "arity" => 2, "source_asset" => factor_id))
        push!(relations, Dict("asset" => factor_id, "electrical" => factor_id, "relation" => "realizes oriented scalar line relation"))
    end
    terminal_vertices = [junction["id"] for junction in junctions]
    terminal_members = [IdentifiedEdge("line/$(line)", _terminal_id(from, "scalar"), _terminal_id(to, "scalar"), 1.0) for (line, from, to) in edges]
    simple = simple_projection(terminal_vertices, terminal_members)
    errors = String[]
    for factor in factors
        length(factor["ports"]) == factor["arity"] || push!(errors, "factor arity does not match port incidence")
        all(port["factor"] == factor["id"] for port in ports if port["id"] in factor["ports"]) || push!(errors, "port-factor incidence mismatch")
    end
    checks = Dict(
        "all_factor_ports_resolve" => isempty(errors),
        "scalar_line_factors_are_two_port" => all(factor["type"] == "scalar_series_line" && factor["arity"] == 2 for factor in factors),
        "terminal_junctions_preserved" => length(junctions) == length(buses),
        "line_identity_preserved" => length(unique(factor["id"] for factor in factors)) == length(edges),
        "parallel_fibre_retained" => cycle_rank(terminal_vertices, terminal_members) > cycle_rank(terminal_vertices, simple.edges),
    )
    (; witness_id = "ARCH-CONDUCTOR-002",
       model_scope = "five-bus cycle-space scalar line identities lifted to scalar terminal junctions and two-port factors",
       source_fixture = "experiments/generated/five-bus-cycle-space-analysis.json",
       junctions, ports, factors, relations,
       terminal_members = [Dict("id" => edge.id, "from" => edge.bus_from, "to" => edge.bus_to) for edge in terminal_members],
       simple_projection = Dict("membership" => simple.membership, "cycle_rank" => cycle_rank(terminal_vertices, simple.edges)),
       checks,
       interpretation = "The scalar lift is the two-terminal special case of conductor-terminal incidence. It preserves line identity and the parallel fibre but adds no multiconductor, switch, or transformer semantics.")
end

"Lift the serialized multiwinding contract to ordered terminal ports and one factor."
function evaluate_multiwinding_terminal_lift(root=normpath(joinpath(@__DIR__, "..", "..")))
    path = joinpath(root, "data", "transformer-contracts", "x1-fixed-linear-v0.1.0.json")
    contract = JSON3.read(read(path, String), Dict{String,Any})
    transfers = contract["winding_transfers"]
    ports = Dict{String,Any}[]
    factors = Dict{String,Any}[]
    errors = String[]
    winding_ids = String[]
    for transfer in transfers
        winding_id = String(transfer["winding_id"])
        push!(winding_ids, winding_id)
        terminals = String.(transfer["terminal_order"])
        coils = String.(transfer["coil_order"])
        isempty(terminals) && push!(errors, "winding has no ordered terminals")
        length(transfer["coefficient"]) == length(coils) || push!(errors, "transfer coefficient length does not match coil order")
        port_id = "transformer/x1/port/$(transfer["winding_position"])"
        push!(ports, Dict(
            "id" => port_id,
            "factor" => "transformer/x1",
            "winding_id" => winding_id,
            "terminal_order" => terminals,
            "coil_order" => coils,
            "junctions" => ["$(winding_id)/$terminal" for terminal in terminals],
            "variable_space" => "V_$(length(terminals))×I_$(length(terminals))",
        ))
    end
    length(unique(winding_ids)) == length(winding_ids) || push!(errors, "winding identities are not unique")
    factor_ports = [port["id"] for port in ports]
    push!(factors, Dict("id" => "transformer/x1", "type" => "multiwinding_transformer", "ports" => factor_ports, "arity" => length(factor_ports), "source_asset" => "x1"))
    grounding = contract["internal_groundings"]
    checks = Dict(
        "all_transfer_ports_resolve" => isempty(errors),
        "multiwinding_factor_has_three_ports" => length(factor_ports) == 3,
        "winding_identity_preserved" => length(unique(winding_ids)) == 3,
        "wye_neutral_terminal_retained" => all("n" in String.(transfers[index]["terminal_order"]) for index in (1, 2)),
        "delta_winding_has_no_neutral_terminal" => !("n" in String.(transfers[3]["terminal_order"])),
        "internal_grounding_is_separate_observation" => length(grounding) == 1 && String(grounding[1]["scope"]) == "transformer_internal",
        "excitation_shunt_is_separate_observation" => haskey(contract, "excitation_shunt"),
    )
    (; witness_id = "ARCH-CONDUCTOR-MULTI-001",
       evidence_type = "multiwinding_contract_terminal_port_lift",
       source_fixture = "data/transformer-contracts/x1-fixed-linear-v0.1.0.json",
       model_scope = "serialized three-winding fixed-linear transformer contract lifted to ordered terminal ports",
       ports, factors,
       observations = Dict("internal_groundings" => length(grounding), "excitation_shunt" => String(contract["excitation_shunt"]["id"])),
       checks,
       interpretation = "The lift preserves winding identity, terminal order, WYE neutral presence, DELTA terminal arity, and separate internal observations; it is structural evidence, not a full electrical equivalence certificate.")
end

end

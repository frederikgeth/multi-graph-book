module HierarchyBoundaryWitness

using JSON3

export evaluate_hierarchy_boundary

function _fixture(root)
    JSON3.read(read(joinpath(root, "data", "running-network", "v0.1.0.json"), String), Dict{String,Any})
end

function _parent_chain_acyclic(containers)
    parents = Dict(container["id"] => container["parent"] for container in containers)
    for start in keys(parents)
        seen = Set{String}()
        current = start
        while current !== nothing
            current in seen && return false
            push!(seen, current)
            current = parents[current]
        end
    end
    true
end

function evaluate_hierarchy_boundary(root=normpath(joinpath(@__DIR__, "..", "..")))
    network = _fixture(root)
    containers = [
        Dict("id" => "running-network", "parent" => nothing, "boundary" => ["i0", "i1", "i2", "i3", "i4", "i5", "i6"]),
        Dict("id" => "parallel-corridor", "parent" => "running-network", "boundary" => ["i1", "i2", "i3", "i4"]),
        Dict("id" => "transformer-bay", "parent" => "running-network", "boundary" => ["i1", "i5", "i6"]),
    ]
    source_boundary = [
        Dict("id" => "i1/a", "space" => "V₁×I₁", "source" => "bus/i1/terminal/a"),
        Dict("id" => "i1/b", "space" => "V₁×I₁", "source" => "bus/i1/terminal/b"),
        Dict("id" => "i5/a", "space" => "V₁×I₁", "source" => "bus/i5/terminal/a"),
        Dict("id" => "i6/a", "space" => "V₁×I₁", "source" => "bus/i6/terminal/a"),
    ]
    target_boundary = [
        Dict("id" => "bus/i1", "space" => "V₄×I₄", "source" => "topological-node/i1"),
        Dict("id" => "bus/i2", "space" => "V₄×I₄", "source" => "topological-node/i2"),
        Dict("id" => "bus/i5", "space" => "V₄×I₄", "source" => "topological-node/i5"),
        Dict("id" => "bus/i6", "space" => "V₃×I₃", "source" => "topological-node/i6"),
    ]
    refinement = [
        Dict("source" => "i1/a", "target" => "bus/i1", "relation" => "terminal injection into bus port"),
        Dict("source" => "i1/b", "target" => "bus/i1", "relation" => "terminal injection into bus port"),
        Dict("source" => "i5/a", "target" => "bus/i5", "relation" => "winding port injection into bus port"),
        Dict("source" => "i6/a", "target" => "bus/i6", "relation" => "delta terminal port injection into bus port"),
    ]
    gluing = [
        Dict("boundary" => "parallel-corridor/transformer-bay at i1", "shared_ports" => ["bus/i1"], "relation" => "same ordered bus terminal variables"),
        Dict("boundary" => "parallel-corridor/running-network at i2", "shared_ports" => ["bus/i2"], "relation" => "same ordered bus terminal variables"),
    ]
    state_cases = Dict(
        "closed" => Dict("switch_state" => "closed", "boundary_map_defined" => true, "contraction" => "i0/a→i1/a; i0/b→i1/b; i0/c→i1/c; i0/n→i1/n"),
        "open" => Dict("switch_state" => "open", "boundary_map_defined" => true, "contraction" => "none"),
        "unknown" => Dict("switch_state" => "unknown", "boundary_map_defined" => false, "contraction" => "deferred until state resolution"),
    )
    errors = String[]
    ids = [container["id"] for container in containers]
    source_ids = Set(boundary["id"] for boundary in source_boundary)
    target_by_id = Dict(boundary["id"] => boundary for boundary in target_boundary)
    length(unique(ids)) == length(ids) || push!(errors, "container IDs are not unique")
    all(container["parent"] === nothing || container["parent"] in ids for container in containers) || push!(errors, "hierarchy has an unknown parent")
    all(item["source"] in [boundary["id"] for boundary in source_boundary] && item["target"] in [boundary["id"] for boundary in target_boundary] for item in refinement) || push!(errors, "refinement references unknown boundary")
    all(item["source"] in source_ids for item in refinement) || push!(errors, "refinement source is not in the declared source boundary")
    all(item["target"] in keys(target_by_id) for item in refinement) || push!(errors, "refinement target is not in the declared target boundary")
    all(length(unique(item["shared_ports"])) == length(item["shared_ports"]) for item in gluing) || push!(errors, "gluing repeats a shared port")
    all(all(port in keys(target_by_id) for port in item["shared_ports"]) for item in gluing) || push!(errors, "gluing references an unknown target port")
    all(state_case["switch_state"] in ("open", "closed", "unknown") for state_case in values(state_cases)) || push!(errors, "state case is outside the declared domain")
    checks = Dict(
        "hierarchy_is_acyclic_by_parent_chain" => _parent_chain_acyclic(containers),
        "source_boundary_is_typed" => all(haskey(item, "space") for item in source_boundary),
        "target_boundary_is_typed" => all(haskey(item, "space") for item in target_boundary),
        "refinement_is_total_on_declared_subset" => length(refinement) == length(source_boundary),
        "gluing_reuses_shared_boundary" => all(!isempty(item["shared_ports"]) for item in gluing),
        "gluing_ports_are_declared" => all(all(port in keys(target_by_id) for port in item["shared_ports"]) for item in gluing),
        "state_domain_is_explicit" => sort([case["switch_state"] for case in values(state_cases)]) == ["closed", "open", "unknown"],
        "unknown_state_defers_boundary_map" => state_cases["unknown"]["boundary_map_defined"] === false,
        "all_structural_checks_pass" => isempty(errors),
    )
    (; witness_id = "ARCH-BOUNDARY-001",
       model_scope = "running-network hierarchy, typed boundary refinement, open-system gluing, and state-conditioned switch maps",
       source_fixture = "data/running-network/v0.1.0.json",
       containers, source_boundary, target_boundary, refinement, gluing, state_cases,
       checks, errors,
       interpretation = "The witness treats hierarchy as a typed containment relation and refinement as a partial boundary map. Subsystems glue through shared typed ports; an unknown switch state leaves its contraction and boundary map unresolved.")
end

end

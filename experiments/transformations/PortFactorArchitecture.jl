module PortFactorArchitecture

export running_port_factor_bundle,
       five_bus_port_factor_bundle,
       validate_port_factor_bundle

"""Build a small, executable `(𝔓, Λ)` slice from the running-network identities.

The object is deliberately a data-level witness rather than a solver model.  It
contains enough typed incidence to test ownership, multi-terminal arity,
grounding, and the many-to-many asset/electrical link before adding a full
factor evaluator.
"""
function running_port_factor_bundle()
    ports = [
        Dict("id" => "line/l1/port/i1", "factor" => "line/l1", "junction" => "i1",
             "terminal" => "[a,b,c,n]", "variable_space" => "V₄×I₄",
             "source_assets" => ["line/l1"]),
        Dict("id" => "line/l1/port/i2", "factor" => "line/l1", "junction" => "i2",
             "terminal" => "[a,b,c,n]", "variable_space" => "V₄×I₄",
             "source_assets" => ["line/l1"]),
        Dict("id" => "line/l2/port/i1", "factor" => "line/l2", "junction" => "i1",
             "terminal" => "[a,b,c,n]", "variable_space" => "V₄×I₄",
             "source_assets" => ["line/l2"]),
        Dict("id" => "line/l2/port/i2", "factor" => "line/l2", "junction" => "i2",
             "terminal" => "[a,b,c,n]", "variable_space" => "V₄×I₄",
             "source_assets" => ["line/l2"]),
        Dict("id" => "transformer/x1/port/w1", "factor" => "transformer/x1",
             "junction" => "i1", "terminal" => "winding-1:[a,b,c,n]",
             "variable_space" => "V₄×I₄", "source_assets" => ["transformer/x1"]),
        Dict("id" => "transformer/x1/port/w2", "factor" => "transformer/x1",
             "junction" => "i5", "terminal" => "winding-2:[a,b,c,n]",
             "variable_space" => "V₄×I₄", "source_assets" => ["transformer/x1"]),
        Dict("id" => "transformer/x1/port/w3", "factor" => "transformer/x1",
             "junction" => "i6", "terminal" => "winding-3:[a,b,c]",
             "variable_space" => "V₃×I₃", "source_assets" => ["transformer/x1"]),
        Dict("id" => "shunt/hn/port/n", "factor" => "shunt/hn", "junction" => "i2",
             "terminal" => "[n]→earth", "variable_space" => "V₁×I₁",
             "source_assets" => ["shunt/hn"]),
    ]

    junctions = [
        Dict("id" => "i1", "relation" => "voltage compatibility plus signed KCL"),
        Dict("id" => "i2", "relation" => "voltage compatibility plus signed KCL"),
        Dict("id" => "i5", "relation" => "voltage compatibility plus signed KCL"),
        Dict("id" => "i6", "relation" => "voltage compatibility plus signed KCL"),
    ]

    factors = [
        Dict("id" => "line/l1", "factor_type" => "multiconductor_series_line",
             "ports" => ["line/l1/port/i1", "line/l1/port/i2"],
             "relation" => "I_l1ij = Y_l1 (U_i1 − U_i2)",
             "source_assets" => ["line/l1"]),
        Dict("id" => "line/l2", "factor_type" => "multiconductor_series_line",
             "ports" => ["line/l2/port/i1", "line/l2/port/i2"],
             "relation" => "I_l2ij = Y_l2 (U_i1 − U_i2)",
             "source_assets" => ["line/l2"]),
        Dict("id" => "transformer/x1", "factor_type" => "multiwinding_transformer",
             "ports" => ["transformer/x1/port/w1", "transformer/x1/port/w2",
                         "transformer/x1/port/w3"],
             "relation" => "R_x1(V_w1,V_w2,V_w3,I_w1,I_w2,I_w3)=0",
             "source_assets" => ["transformer/x1"]),
        Dict("id" => "shunt/hn", "factor_type" => "grounding_shunt",
             "ports" => ["shunt/hn/port/n"],
             "relation" => "I_hn = y_hn U_i2,n",
             "source_assets" => ["shunt/hn"]),
    ]

    hierarchy = [
        Dict("parent" => "running-network", "child" => "parallel-corridor"),
        Dict("parent" => "running-network", "child" => "transformer-bay"),
        Dict("parent" => "parallel-corridor", "child" => "line/l1"),
        Dict("parent" => "parallel-corridor", "child" => "line/l2"),
        Dict("parent" => "transformer-bay", "child" => "transformer/x1"),
        Dict("parent" => "running-network", "child" => "shunt/hn"),
    ]

    model = Dict(
        "object_type" => "hierarchical_port_factor_model",
        "notation" => "𝔓=(Q,J,Φ,j,f,H,X,R)",
        "ports" => ports,
        "junctions" => junctions,
        "factors" => factors,
        "hierarchy" => hierarchy,
        "boundary_ports" => ["line/l1/port/i1", "line/l1/port/i2",
                             "line/l2/port/i1", "line/l2/port/i2",
                             "transformer/x1/port/w2", "transformer/x1/port/w3"],
    )

    lambda = [
        Dict("asset" => "line/l1", "electrical" => "line/l1",
             "relation_type" => "realizes", "scope" => "series relation and limits"),
        Dict("asset" => "line/l2", "electrical" => "line/l2",
             "relation_type" => "realizes", "scope" => "series relation and limits"),
        Dict("asset" => "transformer/x1", "electrical" => "transformer/x1",
             "relation_type" => "realizes", "scope" => "three winding ports and leakage"),
        Dict("asset" => "transformer/x1", "electrical" => "transformer/x1/port/w1",
             "relation_type" => "owns_port", "scope" => "primary winding identity"),
        Dict("asset" => "transformer/x1", "electrical" => "transformer/x1/port/w2",
             "relation_type" => "owns_port", "scope" => "secondary winding identity"),
        Dict("asset" => "transformer/x1", "electrical" => "transformer/x1/port/w3",
             "relation_type" => "owns_port", "scope" => "tertiary winding identity"),
        Dict("asset" => "shunt/hn", "electrical" => "shunt/hn",
             "relation_type" => "realizes", "scope" => "neutral-to-earth admittance"),
    ]

    Dict("claim_id" => "ARCH-PORT-001", "model" => model, "lambda" => lambda,
         "source_fixture" => "data/running-network/v0.1.0.json")
end

"Build the scalar five-bus multigraph as a structural port--factor incidence bundle."
function five_bus_port_factor_bundle()
    edges = [
        ("q", "j", "i"), ("r", "i", "j"), ("s", "j", "k"),
        ("t", "k", "i"), ("v", "l", "j"), ("w", "k", "l"),
        ("u", "l", "m"),
    ]
    buses = ["i", "j", "k", "l", "m"]
    ports = Dict{String,Any}[]
    factors = Dict{String,Any}[]
    lambda = Dict{String,Any}[]
    for (line, from, to) in edges
        from_port = "line/$(line)/port/from"
        to_port = "line/$(line)/port/to"
        push!(ports, Dict(
            "id" => from_port, "factor" => "line/$(line)", "junction" => from,
            "terminal" => "scalar", "variable_space" => "V×I", "source_assets" => ["line/$(line)"],
        ))
        push!(ports, Dict(
            "id" => to_port, "factor" => "line/$(line)", "junction" => to,
            "terminal" => "scalar", "variable_space" => "V×I", "source_assets" => ["line/$(line)"],
        ))
        push!(factors, Dict(
            "id" => "line/$(line)", "factor_type" => "scalar_series_line",
            "ports" => [from_port, to_port],
            "relation" => "I_$(line) = Y_$(line) (U_$(from) − U_$(to))",
            "source_assets" => ["line/$(line)"],
        ))
        push!(lambda, Dict(
            "asset" => "line/$(line)", "electrical" => "line/$(line)",
            "relation_type" => "realizes", "scope" => "line identity, orientation, and limit",
        ))
    end
    junctions = [
        Dict("id" => bus, "relation" => "voltage compatibility plus signed KCL")
        for bus in buses
    ]
    hierarchy = [
        Dict("parent" => "five-bus-multigraph", "child" => "line/$(line)")
        for (line, _, _) in edges
    ]
    model = Dict(
        "object_type" => "hierarchical_port_factor_model",
        "notation" => "𝔓=(Q,J,Φ,j,f,H,X,R)",
        "ports" => ports,
        "junctions" => junctions,
        "factors" => factors,
        "hierarchy" => hierarchy,
        "boundary_ports" => [port["id"] for port in ports],
    )
    Dict(
        "claim_id" => "ARCH-PORT-002",
        "model" => model,
        "lambda" => lambda,
        "source_fixture" => "experiments/generated/five-bus-cycle-space-analysis.json",
        "interpretation" => "Structural lift of the identified scalar bus-branch multigraph; it preserves line identity and declared orientation but does not add a numerical factor evaluator.",
    )
end

"""Validate incidence and relational consistency of a `(𝔓, Λ)` bundle."""
function validate_port_factor_bundle(bundle::AbstractDict)
    model = bundle["model"]
    ports = model["ports"]
    junctions = model["junctions"]
    factors = model["factors"]
    lambda = bundle["lambda"]
    port_ids = [port["id"] for port in ports]
    junction_ids = Set(junction["id"] for junction in junctions)
    factor_ids = Set(factor["id"] for factor in factors)
    port_by_id = Dict(port["id"] => port for port in ports)
    asset_ids = Set{String}()
    errors = String[]

    length(unique(port_ids)) == length(port_ids) || push!(errors, "port IDs are not unique")
    for port in ports
        port["junction"] in junction_ids || push!(errors, "port $(port["id"]) has unknown junction")
        port["factor"] in factor_ids || push!(errors, "port $(port["id"]) has unknown factor")
        union!(asset_ids, port["source_assets"])
    end
    for factor in factors
        isempty(factor["ports"]) && push!(errors, "factor $(factor["id"]) has no ports")
        all(port_id in port_ids for port_id in factor["ports"]) ||
            push!(errors, "factor $(factor["id"]) has an unknown port")
        all(port_by_id[port_id]["factor"] == factor["id"] for port_id in factor["ports"]) ||
            push!(errors, "factor $(factor["id"]) has inconsistent port incidence")
        union!(asset_ids, factor["source_assets"])
    end
    for relation in lambda
        relation["asset"] in asset_ids || push!(errors, "Λ references unknown asset")
        relation["electrical"] in union(factor_ids, Set(port_ids)) ||
            push!(errors, "Λ references unknown electrical object")
    end
    Dict("valid" => isempty(errors), "errors" => errors,
         "n_ports" => length(ports), "n_junctions" => length(junctions),
         "n_factors" => length(factors), "n_lambda_relations" => length(lambda),
         "multi_asset_or_factor_link" => any(count(r -> r["asset"] == asset, lambda) > 1 for asset in asset_ids))
end

end

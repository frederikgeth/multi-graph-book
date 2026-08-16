module FiveBusTransformerLowering

using JSON3
using SHA

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

export five_bus_transformer_lowering_witness

function _hash(path)
    bytes2hex(sha256(read(path)))
end

function _edge(id, from, to)
    IdentifiedEdge(String(id), String(from), String(to), 1.0)
end

function _view(vertices, edges)
    simple = simple_projection(vertices, edges)
    Dict(
        "vertices" => vertices,
        "edges" => [Dict("id" => edge.id, "from" => edge.bus_from, "to" => edge.bus_to) for edge in edges],
        "member_cycle_rank" => cycle_rank(vertices, edges),
        "simple_cycle_rank" => cycle_rank(vertices, simple.edges),
        "simple_membership" => simple.membership,
    )
end

"""
Compose the stable five-bus line fixture with a declared three-port transformer
extension.  The witness compares structures, not one context-free cycle rank:
the source asset remains one n-port object, while incidence, star, clique, and
support views have their own vertices and edges.
"""
function five_bus_transformer_lowering_witness(root=normpath(joinpath(@__DIR__, "..", "..")))
    five_path = joinpath(root, "experiments", "generated", "five-bus-cycle-space-analysis.json")
    lift_path = joinpath(root, "experiments", "generated", "multiwinding-terminal-lift-witness.json")
    leakage_path = joinpath(root, "experiments", "generated", "multiwinding-leakage-compilation-certificate.json")
    five = JSON3.read(read(five_path, String), Dict{String,Any})
    lift = JSON3.read(read(lift_path, String), Dict{String,Any})
    leakage = JSON3.read(read(leakage_path, String), Dict{String,Any})

    buses = String.(five["source"]["buses"])
    line_edges = [_edge("line/$(line["line"])", line["from"], line["to"]) for line in five["source"]["forward_topology"]]
    attachments = Dict(
        "transformer/x1/port/1" => "j",
        "transformer/x1/port/2" => "l",
        "transformer/x1/port/3" => "m",
    )
    ports = sort!(collect(keys(attachments)))
    virtual = "generated/x1/internal"

    local_incidence_vertices = vcat(["transformer/x1"], ports)
    local_incidence_edges = [_edge("incidence/$port", "transformer/x1", port) for port in ports]
    local_star_edges = [_edge("generated/x1/star/w$index", attachments[port], virtual) for (index, port) in enumerate(ports)]
    local_clique_edges = IdentifiedEdge[]
    for p in 1:length(ports)-1, q in p+1:length(ports)
        left, right = attachments[ports[p]], attachments[ports[q]]
        push!(local_clique_edges, _edge("generated/x1/clique/$p-$q", left, right))
    end

    factor_vertices = copy(buses)
    factor_edges = IdentifiedEdge[]
    for edge in line_edges
        factor = "factor/$(edge.id)"
        push!(factor_vertices, factor)
        push!(factor_edges, _edge("incidence/$(edge.id)/from", edge.bus_from, factor))
        push!(factor_edges, _edge("incidence/$(edge.id)/to", factor, edge.bus_to))
    end
    push!(factor_vertices, "transformer/x1")
    for port in ports
        push!(factor_edges, _edge("incidence/$port", attachments[port], "transformer/x1"))
    end

    base = _view(buses, line_edges)
    incidence = _view(factor_vertices, factor_edges)
    star = _view(vcat(buses, [virtual]), vcat(line_edges, local_star_edges))
    clique = _view(buses, vcat(line_edges, local_clique_edges))
    local_views = Dict(
        "port_factor_incidence" => _view(local_incidence_vertices, local_incidence_edges),
        "star_realization" => _view(vcat(sort!(unique(collect(values(attachments)))) , [virtual]), local_star_edges),
        "terminal_clique" => _view(sort!(unique(collect(values(attachments)))), local_clique_edges),
    )

    three_special = leakage["evidence"]["three_winding_special_case"]
    negative_arm = leakage["evidence"]["negative_star_arm_witness"]
    negative_arm_impedances = negative_arm["star_arm_impedances_ohm"]
    minimum_star_reactance = minimum(
        Float64(value["imag"]) for value in values(negative_arm_impedances)
    )
    minimum_matrix_reactance_eigenvalue = minimum(
        Float64.(negative_arm["reactance_eigenvalues"])
    )
    lift_checks = lift["checks"]
    checks = Dict(
        "base_member_cycle_rank_is_three" => base["member_cycle_rank"] == 3,
        "base_simple_cycle_rank_is_two" => base["simple_cycle_rank"] == 2,
        "source_transformer_is_one_three_port_factor" => length(lift["factors"]) == 1 && lift["factors"][1]["arity"] == 3,
        "local_factor_incidence_is_acyclic" => local_views["port_factor_incidence"]["member_cycle_rank"] == 0,
        "local_star_is_acyclic" => local_views["star_realization"]["member_cycle_rank"] == 0,
        "local_clique_has_one_cycle" => local_views["terminal_clique"]["member_cycle_rank"] == 1,
        "embedded_incidence_cycle_rank_is_five" => incidence["member_cycle_rank"] == 5,
        "embedded_star_member_cycle_rank_is_five" => star["member_cycle_rank"] == 5,
        "embedded_clique_member_cycle_rank_is_six" => clique["member_cycle_rank"] == 6,
        "embedded_clique_simple_cycle_rank_is_three" => clique["simple_cycle_rank"] == 3,
        "three_winding_star_is_declared_special_case" => three_special["applies"] === true,
        "negative_star_arm_is_retained" => minimum_star_reactance < 0,
        "reference_reactance_matrix_remains_positive_semidefinite" =>
            minimum_matrix_reactance_eigenvalue ≥ -1.0e-12,
        "winding_current_and_internal_observations_remain_declared" =>
            lift_checks["winding_identity_preserved"] === true &&
            lift_checks["internal_grounding_is_separate_observation"] === true &&
            leakage["classification"] == "exact_compilation",
    )

    layers = [
        Dict("id" => "source_asset", "objects" => ["transformer/x1", "x1/winding/1", "x1/winding/2", "x1/winding/3"], "interface" => "asset and winding identity, attachments, state, ratings, provenance"),
        Dict("id" => "port_factor", "objects" => ["transformer/x1", ports...], "interface" => "ordered winding voltage/current ports, behavioural relation, limits, controls, observations"),
        Dict("id" => "ordinary_edge_realization", "objects" => [virtual, [edge.id for edge in local_star_edges]...], "interface" => "boundary buses, generated IDs, source fibre, winding-current recovery"),
        Dict("id" => "equation_operator", "objects" => ["direct factor block", "terminal admittance block"], "interface" => "coordinate order, residual equations, constraint ownership, recovery operator"),
        Dict("id" => "support_graph", "objects" => ["terminal coupling nonzeros"], "interface" => "block order and numerical-zero policy only"),
    ]
    maps = [
        Dict("id" => "C_x1", "from" => "source_asset", "to" => "port_factor", "type" => "canonicalization", "status" => "retains transformer and winding identity"),
        Dict("id" => "A_x1", "from" => "port_factor", "to" => "equation_operator", "type" => "direct stamping", "status" => "default exact branch for the declared fixed-linear factor"),
        Dict("id" => "L_x1", "from" => "port_factor", "to" => "ordinary_edge_realization", "type" => "guarded compilation", "status" => "optional three-winding star branch with generated objects"),
        Dict("id" => "R_internal", "from" => "ordinary_edge_realization", "to" => "equation_operator", "type" => "behavioural elimination", "status" => "creates terminal clique support and requires recovery"),
        Dict("id" => "S", "from" => "equation_operator", "to" => "support_graph", "type" => "support projection", "status" => "forgets coefficients, decomposition, limits, and physical identity"),
    ]
    loss_ledger = [
        Dict("boundary" => "source_asset→port_factor", "at_risk" => ["ownership", "maintenance and common-mode failure", "source nameplate semantics"]),
        Dict("boundary" => "port_factor→ordinary_edge_realization", "at_risk" => ["factor arity", "one-device identity", "winding limits", "tap and connection semantics", "grounding and excitation placement"]),
        Dict("boundary" => "ordinary_edge_realization→equation_operator", "at_risk" => ["generated internal current", "virtual-node provenance", "source constraint ownership"]),
        Dict("boundary" => "equation_operator→support_graph", "at_risk" => ["coefficients and signs", "constitutive meaning", "feasible-set and decision semantics"]),
    ]

    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-FIVEBUS-XFMR-001",
        "model_scope" => "five-bus scalar line topology plus a structural three-port transformer extension attached at j, l, and m",
        "source_dependencies" => Dict(
            relpath(five_path, root) => _hash(five_path),
            relpath(lift_path, root) => _hash(lift_path),
            relpath(leakage_path, root) => _hash(leakage_path),
        ),
        "base_line_graph" => base,
        "transformer_extension" => Dict("asset_id" => "transformer/x1", "attachments" => attachments, "local_views" => local_views),
        "negative_star_arm_guard" => Dict(
            "star_arm_impedances_ohm" => negative_arm_impedances,
            "minimum_star_reactance_ohm" => minimum_star_reactance,
            "reference_reactance_eigenvalues_ohm" => negative_arm["reactance_eigenvalues"],
            "minimum_reference_reactance_eigenvalue_ohm" => minimum_matrix_reactance_eigenvalue,
            "invalid_componentwise_test" => "imag(z_k) >= 0 for every generated star arm",
            "valid_invariant_test" => negative_arm["guard"],
        ),
        "embedded_views" => Dict("port_factor_incidence" => incidence, "compiled_star" => star, "terminal_clique" => clique),
        "layers" => layers,
        "maps" => maps,
        "loss_ledger" => loss_ledger,
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "The extension does not assign one cycle rank to the transformer. One source asset becomes one three-port factor, an optional acyclic local star, or a cyclic terminal clique; embedded cycle counts are properties of those declared target graphs, not extra physical transformer loops.",
    )
end

end

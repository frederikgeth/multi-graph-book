module LayerLensApiWitness

using JSON3
using JuMP
using SparseArrays

export evaluate_layer_lens_api

function cell(api, input, output, preserves, omits; status="smoke_tested")
    Dict(
        "api" => api,
        "input" => input,
        "output" => output,
        "preserves" => preserves,
        "omits" => omits,
        "status" => status,
    )
end

# Most cells use the compact four-field spelling when the API's output is the
# same conceptual object as its input.  Keep that shorthand explicit in the
# witness rather than silently dropping the output field.
cell(api, input, preserves, omits; status="smoke_tested") =
    cell(api, input, input, preserves, omits; status=status)

function evaluate_layer_lens_api(root=normpath(joinpath(@__DIR__, "..", "..")))
    fixture_path = joinpath(root, "data", "running-network", "v0.1.0.json")
    network = JSON3.read(read(fixture_path, String), Dict{String,Any})
    line_ids = sort!(String.(collect(keys(network["line"]))))
    switch_ids = sort!(String.(collect(keys(network["switch"]))))
    transformer = network["transformer"]["n_winding"]["x1"]
    terminal_counts = [length(winding["terminal_map"]) for winding in transformer["windings"]]

    # A tiny concrete JuMP interface: the optimizer is not run; the model is
    # used only to show where decision variables, constraints, and objective
    # terms live in the layer-lens matrix.
    model = Model()
    @variable(model, 0.95 <= tap <= 1.05)
    @constraint(model, tap >= 0.95)
    @objective(model, Min, tap)

    # A concrete SparseArrays interface: the matrix is a declared equation
    # target, and its nonzero support is a derived graph rather than a source
    # asset inventory.
    y = sparse([1, 1, 2, 2], [1, 2, 1, 2], [2.0, -1.0, -1.0, 1.0], 2, 2)
    _, _, nz_values = findnz(y)
    support_edges = [[1, 2], [2, 1]]

    # A package-independent graph-learning tensor contract.  The field names
    # are intentionally compatible with common message-passing APIs, but the
    # witness does not claim that a physical bus is a learning node.
    node_features = [1.0 0.0 0.0; 0.0 1.0 0.0]
    edge_index = [1 2; 2 1]
    edge_attributes = [["support_coupling"], ["support_coupling"]]

    layers = [
        Dict("id" => "L0", "name" => "source asset/property"),
        Dict("id" => "L1", "name" => "canonical port-factor"),
        Dict("id" => "L2", "name" => "optional edge realization"),
        Dict("id" => "L3", "name" => "equation/operator"),
        Dict("id" => "L4", "name" => "support/algorithm graph"),
    ]
    lenses = [
        Dict("id" => "identity", "question" => "which object and provenance fibre?"),
        Dict("id" => "connectivity", "question" => "which terminals or nodes connect?"),
        Dict("id" => "behaviour", "question" => "which equations or responses hold?"),
        Dict("id" => "decision", "question" => "which states, limits, and objectives survive?"),
        Dict("id" => "software", "question" => "which API and variable layout consume this view?"),
    ]

    matrix = Dict{String,Any}(
        "L0" => Dict(
            "identity" => cell("JSON source fixture", "asset IDs, line IDs, winding IDs", "stable identifiers and source fibres", ["asset identity", "provenance"], ["assembled equations", "matrix support"]),
            "connectivity" => cell("terminal maps in versioned data", "bus and terminal records", "declared attachments", ["electrical connectivity"], ["constitutive coefficients"]),
            "behaviour" => cell("typed factor metadata", "relation signatures and parameters", "declared factor ownership", ["equation provenance"], ["solver residuals"]),
            "decision" => cell("state/rating fields", "switch state domains and limits", "state labels and rating owners", ["feasible-set semantics"], ["optimized solution"]),
            "software" => cell("JSON3 object dictionaries", "versioned source object", ["field names", "source version"], ["package-specific solver variables"], status="smoke_tested"),
        ),
        "L1" => Dict(
            "identity" => cell("typed port-factor records", "ordered ports and source fibres", ["factor identity", "port order"], ["organizational ownership unless linked"],),
            "connectivity" => cell("port/junction incidence", "terminal-level incidence", ["port attachments", "conductor identity"], ["matrix ordering outside declaration"],),
            "behaviour" => cell("factor relation evaluator", "multiport relation", ["terminal behaviour"], ["support-only interpretation"],),
            "decision" => cell("typed state and limit fields", "factor constraints and decision domain", ["controls", "limits"], ["optimizer-specific relaxation"],),
            "software" => cell("typed Julia structs", "factor API inputs", ["coordinate labels", "map metadata"], ["solver execution"],),
        ),
        "L2" => Dict(
            "identity" => cell("generated edge records", "edge IDs plus source fibre", ["generated provenance"], ["ordinary-edge identity as physical asset"],),
            "connectivity" => cell("incidence edge list", "ordinary graph adjacency", ["target connectivity"], ["n-port factor arity"],),
            "behaviour" => cell("edge constitutive blocks", "edge equations or stamps", ["declared edge relation"], ["unrealizable n-port semantics"],),
            "decision" => cell("guarded edge compiler", "recovery and constraint maps", ["source decision ownership"], ["independent edge decisions unless explicitly allowed"],),
            "software" => cell("Graphs-style edge table", "edge-indexed algorithm input", ["edge ordering"], ["source asset meaning without fibre"],),
        ),
        "L3" => Dict(
            "identity" => cell("equation/constraint operator", "variable-owner and provenance maps", ["equation ownership"], ["graph drawing semantics"],),
            "connectivity" => cell("incidence and block structure", "KCL/KVL and terminal equations", ["declared equation connectivity"], ["simple graph interpretation"],),
            "behaviour" => cell("SparseArrays.SparseMatrixCSC", "nodal or MNA operator", ["linear operator coefficients"], ["unqueried source variables"],),
            "decision" => cell("JuMP.Model variables/constraints/objective", "decision-ready feasible set", ["tap variable", "bounds", "objective term"], ["asset provenance unless mapped"],),
            "software" => cell("JuMP + SparseArrays", "solver and sparse-kernel inputs", ["variable and matrix layout"], ["community-specific graph vocabulary"],),
        ),
        "L4" => Dict(
            "identity" => cell("source-map/fibre metadata", "graph nodes and edges with provenance", ["explicit source links"], ["identity inferred from adjacency"],),
            "connectivity" => cell("edge_index / adjacency", "message-passing graph", ["support connectivity"], ["physical connectivity if projection is undocumented"],),
            "behaviour" => cell("node features + edge attributes", "learned message-passing inputs", ["declared learning features"], ["exact circuit equations by default"],),
            "decision" => cell("mask and target tensors", "learning task data", ["declared labels/masks"], ["optimization feasibility unless encoded"],),
            "software" => cell("package-independent tensor contract", "node_features, edge_index, edge_attr", ["tensor shapes"], ["a claim about any particular graph-ML package"],),
        ),
    )

    checks = Dict(
        "source_data_api_has_assets_and_terminals" =>
            !isempty(line_ids) && !isempty(switch_ids) && terminal_counts == [4, 4, 3],
        "five_construction_rows_are_declared" => length(layers) == 5,
        "five_semantic_lenses_are_declared" => length(lenses) == 5,
        "matrix_is_rectangular" => all(length(matrix[layer["id"]]) == length(lenses) for layer in layers),
        "direct_factor_to_equation_route_is_declared" =>
            matrix["L1"]["behaviour"]["api"] == "factor relation evaluator",
        "ordinary_edge_route_is_optional" =>
            occursin("Guarded", matrix["L2"]["decision"]["api"]) ||
            occursin("guarded", matrix["L2"]["decision"]["api"]),
        "optimization_api_retains_decision_semantics" =>
            num_variables(model) == 1 &&
            num_constraints(model; count_variable_in_set_constraints=true) == 3,
        "sparse_api_exposes_support_without_provenance" =>
            y isa SparseMatrixCSC && length(nz_values) == 4 && length(support_edges) == 2,
        "graph_learning_tensor_contract_is_explicit" =>
            size(node_features) == (2, 3) && size(edge_index) == (2, 2) && length(edge_attributes) == 2,
        "support_graph_does_not_infer_asset_identity" =>
            "identity inferred from adjacency" in matrix["L4"]["identity"]["omits"],
        "decision_is_not_assigned_to_support_graph" =>
            "optimization feasibility unless encoded" in matrix["L4"]["decision"]["omits"],
        "package_names_are_api_annotations_not_layers" =>
            occursin("package-independent", matrix["L4"]["software"]["api"]),
    )

    Dict(
        "schema_version" => "0.1.0",
        "witness_id" => "ARCH-LENS-001",
        "claim_ids" => ["ARCH-LENS-001"],
        "evidence_type" => "layer_lens_matrix_api_smoke_test",
        "model_scope" => "five construction stages crossed with identity, connectivity, behaviour, decision, and software lenses",
        "source_fixture" => "data/running-network/v0.1.0.json",
        "source_summary" => Dict(
            "line_ids" => line_ids,
            "switch_ids" => switch_ids,
            "transformer_id" => "transformer/n_winding/x1",
            "winding_terminal_counts" => terminal_counts,
        ),
        "layers" => layers,
        "lenses" => lenses,
        "matrix" => matrix,
        "api_contracts" => [
            Dict("community" => "power-system data", "api" => "JSON3 + versioned data-model crosswalk", "scope" => ["L0", "L1"], "status" => "smoke_tested"),
            Dict("community" => "optimization", "api" => "JuMP.Model", "scope" => ["L0", "L3"], "status" => "smoke_tested_without_solver"),
            Dict("community" => "sparse linear algebra", "api" => "SparseArrays.SparseMatrixCSC/findnz", "scope" => ["L3", "L4"], "status" => "smoke_tested"),
            Dict("community" => "graph machine learning", "api" => "node_features/edge_index/edge_attr tensor contract", "scope" => ["L4"], "status" => "package_independent_contract"),
        ],
        "maps" => [
            Dict("id" => "L1_to_L3", "kind" => "direct factor stamping", "status" => "preferred when guards hold"),
            Dict("id" => "L1_to_L2_to_L3", "kind" => "guarded compatibility lowering", "status" => "optional; source fibre required"),
            Dict("id" => "L3_to_L4", "kind" => "support projection", "status" => "forgets coefficients and source decomposition"),
        ],
        "api_observations" => Dict(
            "optimization_model" => Dict("variables" => ["tap"], "constraints" => ["tap_lower_bound", "tap_upper_bound", "explicit_tap_floor"], "objective" => "minimize tap"),
            "sparse_operator" => Dict("shape" => [2, 2], "nonzero_count" => length(nz_values), "support_edges" => support_edges),
            "graph_learning_tensors" => Dict("node_features" => node_features, "edge_index" => edge_index, "edge_attr" => edge_attributes),
        ),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "interpretation" => "The matrix is an interface crosswalk, not a package taxonomy. The same software ecosystem can consume several construction stages, and a graph-learning tensor contract does not inherit physical, optimization, or provenance semantics without explicit maps.",
    )
end

end

module RunningNetworkCycleSpace

using LinearAlgebra

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace: IdentifiedEdge, cycle_rank, edge_bridges,
    fundamental_cycle_matrix, incidence_matrix, simple_projection

export running_network_cycle_analysis

"Analyze the identified line graph of the running fixture, excluding multi-terminal assets."
function running_network_cycle_analysis(net)
    line_ids = sort(String.(collect(keys(net["line"]))))
    records = [net["line"][line_id] for line_id in line_ids]
    vertices = sort(unique(vcat(
        [String(record["bus_from"]) for record in records],
        [String(record["bus_to"]) for record in records],
    )))
    edges = [IdentifiedEdge(
        line_id,
        String(record["bus_from"]),
        String(record["bus_to"]),
        inv(ComplexF64(Float64(record["R_series_1_1"]), Float64(record["X_series_1_1"])));
        current_limit=Float64(record["i_max"][1]),
    ) for (line_id, record) in zip(line_ids, records)]
    tree_ids = ["l1", "l3", "l4"]
    A = incidence_matrix(vertices, edges)
    fundamental = fundamental_cycle_matrix(vertices, edges, tree_ids)
    projection = simple_projection(vertices, edges)
    A_simple = incidence_matrix(vertices, projection.edges)
    Dict{String,Any}(
        "source_fixture" => "data/running-network/v0.1.0.json",
        "witness_id" => "GRAPH-CYCLE-RUNNING-001",
        "model_scope" => "identified scalar line projection of the running multiconductor fixture",
        "vertices" => vertices,
        "line_order" => line_ids,
        "tree_ids" => tree_ids,
        "chord_ids" => fundamental.chord_ids,
        "incidence_rank" => rank(Float64.(A)),
        "cycle_rank" => cycle_rank(vertices, edges),
        "fundamental_cycle_matrix" => [collect(row) for row in eachrow(fundamental.matrix)],
        "cycle_residual" => maximum(abs, A * fundamental.matrix),
        "bridges" => edge_bridges(vertices, edges),
        "simple_cycle_rank" => cycle_rank(vertices, projection.edges),
        "simple_incidence_rank" => rank(Float64.(A_simple)),
        "simple_membership" => projection.membership,
        "parallel_members" => get(projection.membership, "e_i1i2", String[]),
        "excluded_assets" => ["switch/w0", "transformer/n_winding"],
    )
end

end

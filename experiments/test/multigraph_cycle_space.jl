using LinearAlgebra
using BMOPFTools
using Test

if !isdefined(@__MODULE__, :MultigraphCycleSpace)
    include(joinpath(@__DIR__, "..", "transformations", "MultigraphCycleSpace.jl"))
end
using .MultigraphCycleSpace

@testset "five-bus multigraph cycle space" begin
    result = five_bus_analysis()
    A = result["incidence"]
    C = result["fundamental_cycle_matrix"]

    @test size(A) == (5, 7)
    @test result["incidence_rank"] == 4
    @test result["cycle_rank"] == 3
    @test size(C) == (7, 3)
    @test A * C == zeros(Int, 5, 3)
    @test rank(Float64.(C)) == 3
    @test result["fundamental_chords"] == ["q", "t", "v"]
    @test result["bridges"] == ["u"]

    line_order = [edge.id for edge in result["edges"]]
    cycles = [Set(line_order[index] for index in findall(!iszero, C[:, column]))
              for column in axes(C, 2)]
    @test cycles == [Set(["q", "r"]), Set(["r", "s", "t"]), Set(["s", "v", "w"])]

    @test length(result["simple_edges"]) == 6
    @test result["simple_membership"]["e_ij"] == ["q", "r"]
    @test result["simple_incidence_rank"] == 4
    @test result["simple_cycle_rank"] == 2
    @test result["ybus_max_difference"] <= 1.0e-14

    witness = result["parallel_witness"]
    @test witness["aggregate_feasible"]
    @test !witness["source_feasible"]
    @test witness["member_currents_A"] == [150.0, 15.0]
    @test witness["aggregate_current_A"] == 165.0
    @test witness["source_voltage_limit_V"] == 10.0
    @test witness["aggregate_voltage_limit_V"] ≈ 200 / 11

    net = Dict{String,Any}(
        "bus" => Dict(bus => Dict{String,Any}() for bus in result["vertices"]),
        "line" => Dict(edge.id => Dict{String,Any}(
            "bus_from" => edge.bus_from,
            "bus_to" => edge.bus_to,
        ) for edge in result["edges"]),
        "voltage_source" => Dict("source" => Dict("bus" => "i")),
    )
    connectivity = connectivity_analysis(net, Finding[])
    @test !connectivity["is_radial"]
    @test connectivity["n_extra_edges"] == result["cycle_rank"]
end

@testset "cycle-space guards" begin
    vertices = ["a", "b", "c"]
    edges = [
        IdentifiedEdge("l1", "a", "b", 1.0),
        IdentifiedEdge("l2", "b", "c", 1.0),
        IdentifiedEdge("l3", "c", "a", 1.0),
    ]
    @test cycle_rank(vertices, edges) == 1
    @test_throws ArgumentError fundamental_cycle_matrix(vertices, edges, ["l1", "l2", "l3"])
    @test_throws ArgumentError fundamental_cycle_matrix(vertices, edges, ["l1"])
    @test_throws ArgumentError IdentifiedEdge("loop", "a", "a", 1.0)
end

using LinearAlgebra
using Test

@testset "multigraph matrix conventions" begin
    # Edges: two parallel 1--2 members, one 2--3 member, and one loop at 2.
    incidence = [
         1 -1  0  0
        -1  1  1  0
         0  0 -1  0
    ]

    multiplicity_adjacency = [
        0  2  0
        2  2  1
        0  1  0
    ]
    incidence_degree = Diagonal([2, 5, 1])

    # With A[v,v] = twice the loop count, D - A agrees with B*B'.
    @test incidence_degree - multiplicity_adjacency == incidence * incidence'
    @test vec(sum(multiplicity_adjacency; dims=2)) == diag(incidence_degree)

    # One parallel-pair circuit and one graph-loop circuit.
    n_vertices = 3
    n_edges = 4
    n_components = 1
    @test n_edges - n_vertices + n_components == 2
    @test n_edges - rank(Float64.(incidence)) == 2

    # The loopless simple projection has only 1--2 and 2--3 and is a tree.
    simple_incidence = [
         1  0
        -1  1
         0 -1
    ]
    @test size(simple_incidence, 2) - rank(Float64.(simple_incidence)) == 0

    # A shunt is a grounded diagonal term, not a zero incidence-column loop.
    shunt = Diagonal([0.0, 3.0, 0.0])
    series_operator = incidence * incidence'
    grounded_operator = series_operator + shunt
    @test grounded_operator != series_operator
    @test grounded_operator[2, 2] == series_operator[2, 2] + 3.0
end

@testset "query-specific parallel aggregation" begin
    admittance = [10.0, 1.0]
    current_limit = [100.0, 100.0]
    route_length = [10.0, 1.0]
    availability = [0.9, 0.8]

    @test sum(admittance) == 11.0
    @test sum(current_limit) == 200.0
    @test minimum(route_length) == 1.0
    @test 1 - prod(1 .- availability) ≈ 0.98

    member_current = admittance .* 15.0
    @test sum(member_current) <= sum(current_limit)
    @test any(member_current .> current_limit)
end

@testset "deletion, contraction, and simplification" begin
    # e1,e2: u--v; e3: v--w; e4: w--u.
    source_incidence = [
        -1 -1  0  1
         1  1 -1  0
         0  0  1 -1
    ]
    @test size(source_incidence, 2) - rank(Float64.(source_incidence)) == 2

    deleted_incidence = source_incidence[:, 2:4]
    @test size(deleted_incidence, 2) - rank(Float64.(deleted_incidence)) == 1

    # Contract e1: e2 becomes a loop; e3 and e4 become parallel x--w edges.
    contracted_incidence = [
        0 -1  1
        0  1 -1
    ]
    @test size(contracted_incidence, 2) - rank(Float64.(contracted_incidence)) == 2
    @test contracted_incidence[:, 1] == zeros(Int, 2)

    simplified_incidence = [-1; 1;;]
    @test size(simplified_incidence, 2) - rank(Float64.(simplified_incidence)) == 0
end

@testset "collapsed linear pi factor" begin
    series_admittance = 2.0 + 0.5im
    from_shunt = 0.3 + 0.1im
    to_shunt = 0.4 + 0.2im
    pi_admittance = [
        from_shunt + series_admittance  -series_admittance
        -series_admittance               to_shunt + series_admittance
    ]
    same_node_map = reshape([1.0, 1.0], 2, 1)
    nodal_stamp = same_node_map' * pi_admittance * same_node_map
    series_only = [
         series_admittance  -series_admittance
        -series_admittance   series_admittance
    ]

    # Identifying the two terminals cancels the series path and preserves both
    # grounded shunts as a one-terminal constant-admittance stamp.
    @test nodal_stamp[1, 1] ≈ from_shunt + to_shunt
    @test (same_node_map' * series_only * same_node_map)[1, 1] ≈ 0.0 + 0.0im

    # The compiled diagonal term is not the zero column of a graph loop.
    graph_loop_incidence = zeros(2, 1)
    @test graph_loop_incidence * graph_loop_incidence' == zeros(2, 2)
    @test nodal_stamp[1, 1] != 0.0 + 0.0im
end

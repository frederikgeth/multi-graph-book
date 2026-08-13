using BMOPFTools
using Ipopt
using JSON3
using JuMP
using Test

include(joinpath(@__DIR__, "..", "running_network.jl"))

@testset "running-network fixture" begin
    source_net = running_network()
    net = mktemp() do _, io
        write_bmopf(source_net, io)
        seekstart(io)
        parse_bmopf(io)
    end

    schema_findings = Finding[]
    schema = schema_check(net, schema_findings)
    @test get(schema, "jsonschema_valid", false)
    @test isempty(filter(finding -> finding.severity == ERROR, schema_findings))

    spec_findings = Finding[]
    spec = spec_conformance_check(net, spec_findings)
    @test spec["n_voltage_sources"] == 1
    @test isempty(filter(finding -> finding.severity == ERROR, spec_findings))

    @test Set(keys(net["line"])) == Set(["l1", "l2", "l3", "l4"])
    @test net["line"]["l1"]["bus_from"] == net["line"]["l2"]["bus_from"]
    @test net["line"]["l1"]["bus_to"] == net["line"]["l2"]["bus_to"]
    @test net["line"]["l1"]["i_max"] != net["line"]["l2"]["i_max"]
    @test net["line"]["l4"]["terminal_map_from"] == ["a", "c", "n"]
    @test net["line"]["l4"]["terminal_map_to"] == ["c", "a", "n"]

    x1 = net["transformer"]["n_winding"]["x1"]
    @test length(x1["windings"]) == 3
    @test [w["configuration"] for w in x1["windings"]] == ["WYE", "WYE", "DELTA"]

    pf_net = deepcopy(net)
    delete!(pf_net, "generator")
    pf = solve_pf(pf_net; optimizer=Ipopt.Optimizer, per_unit=true)
    @test pf["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test pf["losses"]["p_loss"] > 0

    opf = solve_opf(net; optimizer=Ipopt.Optimizer, per_unit=true)
    @test opf["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
    @test all(opf["generator"]["g1"][phase]["pg"] >= -1.0e-4 for phase in ("a", "b", "c"))
    @test all(opf["generator"]["g1"][phase]["pg"] <= 55_000.1 for phase in ("a", "b", "c"))
end

@testset "parallel-branch witness" begin
    z = [0.1, 1.0]
    y = inv.(z)
    i_max = [100.0, 100.0]
    delta_u = 15.0
    member_current = y .* delta_u
    @test sum(member_current) <= sum(i_max)
    @test any(member_current .> i_max)
end

include(joinpath(@__DIR__, "series_elimination.jl"))
include(joinpath(@__DIR__, "coordinate_normalization.jl"))
include(joinpath(@__DIR__, "parallel_decision_comparison.jl"))

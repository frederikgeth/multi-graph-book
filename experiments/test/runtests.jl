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
    @test Set(keys(net["generator"])) == Set(["g1"])
    @test Set(keys(net["load"])) == Set(["d1", "d2a", "d2c", "d3", "d4"])
    @test haskey(net["shunt"], "href")
    semantic_spec = read(joinpath(@__DIR__, "..", "..", "docs", "src", "cases", "running-network.md"), String)
    @test occursin("d_4", semantic_spec)
    @test !occursin("g_2", semantic_spec)
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
include(joinpath(@__DIR__, "transformer_winding_normalization.jl"))
include(joinpath(@__DIR__, "multiwinding_leakage_compilation.jl"))
include(joinpath(@__DIR__, "multiwinding_terminal_assembly.jl"))
include(joinpath(@__DIR__, "transformer_factor_completion.jl"))
include(joinpath(@__DIR__, "transformer_tap_decision_compilation.jl"))
include(joinpath(@__DIR__, "transformer_tap_ac_decision.jl"))
include(joinpath(@__DIR__, "transformer_tap_ac_independent_reproduction.jl"))
include(joinpath(@__DIR__, "parallel_decision_comparison.jl"))
include(joinpath(@__DIR__, "multiconductor_flow_limit_redundancy.jl"))
include(joinpath(@__DIR__, "multiconductor_parallel_ac.jl"))
include(joinpath(@__DIR__, "four_wire_parallel_ac.jl"))
include(joinpath(@__DIR__, "pi_four_wire_parallel_ac.jl"))
include(joinpath(@__DIR__, "three_member_four_wire_parallel_ac.jl"))
include(joinpath(@__DIR__, "multigraph_cycle_space.jl"))
include(joinpath(@__DIR__, "running_network_cycle_space.jl"))
include(joinpath(@__DIR__, "five_bus_port_factor.jl"))
include(joinpath(@__DIR__, "translation_traps.jl"))
include(joinpath(@__DIR__, "load_grounding_witness.jl"))
include(joinpath(@__DIR__, "active_radiality.jl"))
include(joinpath(@__DIR__, "topology_projection_witness.jl"))
include(joinpath(@__DIR__, "nodal_source_recovery_witness.jl"))
include(joinpath(@__DIR__, "nodal_recovery_guards_witness.jl"))
include(joinpath(@__DIR__, "multiconductor_recovery_witness.jl"))
include(joinpath(@__DIR__, "noisy_multiconductor_recovery_witness.jl"))
include(joinpath(@__DIR__, "nonlinear_grounding_local_bound_witness.jl"))
include(joinpath(@__DIR__, "compiled_views_surgery_witness.jl"))
include(joinpath(@__DIR__, "five_bus_active_radiality.jl"))
include(joinpath(@__DIR__, "five_bus_typed_kron.jl"))
include(joinpath(@__DIR__, "conductor_terminal_lift.jl"))
include(joinpath(@__DIR__, "five_bus_terminal_lift.jl"))
include(joinpath(@__DIR__, "multiwinding_terminal_lift.jl"))
include(joinpath(@__DIR__, "multiwinding_typed_kron.jl"))
include(joinpath(@__DIR__, "running_network_radiality_witness.jl"))
include(joinpath(@__DIR__, "hierarchy_boundary_witness.jl"))
include(joinpath(@__DIR__, "port_factor_architecture.jl"))
include(joinpath(@__DIR__, "positive_sequence_collapse.jl"))
include(joinpath(@__DIR__, "four_wire_impedance_model_ladder.jl"))
include(joinpath(@__DIR__, "balanced_transmission_witness.jl"))
include(joinpath(@__DIR__, "public_api.jl"))
include(joinpath(@__DIR__, "state_space_units.jl"))
include(joinpath(@__DIR__, "certificate_api_matrix.jl"))
include(joinpath(@__DIR__, "solver_diagnostics_crosswalk.jl"))
include(joinpath(@__DIR__, "data_model_crosswalk.jl"))
include(joinpath(@__DIR__, "running_network_typed_kron.jl"))
include(joinpath(@__DIR__, "explicit_earth_kron.jl"))
include(joinpath(@__DIR__, "grounding_impedance_sweep.jl"))
include(joinpath(@__DIR__, "nonlinear_grounding_probe.jl"))
include(joinpath(@__DIR__, "nonlinear_two_point_grounding_probe.jl"))
include(joinpath(@__DIR__, "nonlinear_two_point_continuation.jl"))
include(joinpath(@__DIR__, "transformer_control_family_witness.jl"))
include(joinpath(@__DIR__, "australian_carson_reproduction.jl"))

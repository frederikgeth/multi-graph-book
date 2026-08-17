using LinearAlgebra
using Test
using BMOPFTools

if !isdefined(@__MODULE__, :FourWireParallelACDecision)
    include(joinpath(@__DIR__, "..", "transformations", "FourWireParallelACDecision.jl"))
end
using .FourWireParallelACDecision

@testset "nonproportional three-phase four-wire parallel AC decision" begin
    data = default_four_wire_parallel_data()
    @test all(opnorm(z - transpose(z), Inf) <= 1.0e-14 for z in data["impedance_pu"])
    for (line_number, impedance) in enumerate(data["impedance_pu"])
        linecode = Dict{String,Any}()
        for row in axes(impedance, 1), column in axes(impedance, 2)
            linecode["R_series_$(row)_$(column)"] = real(impedance[row, column])
            linecode["X_series_$(row)_$(column)"] = imag(impedance[row, column])
        end
        line = Dict{String,Any}(
            "bus_from" => "i",
            "bus_to" => "j",
            "terminal_map_from" => data["terminals"],
            "terminal_map_to" => data["terminals"],
            "linecode" => "lc",
            "length" => 1.0,
        )
        nodes, primitive = line_yprim(line, Dict("lc" => linecode))
        @test nodes == vcat([("i", terminal) for terminal in data["terminals"]],
                            [("j", terminal) for terminal in data["terminals"]])
        @test primitive[1:4, 1:4] ≈ data["admittance_pu"][line_number] atol=1.0e-12
        @test primitive[1:4, 5:8] ≈ -data["admittance_pu"][line_number] atol=1.0e-12
    end
    redundancy = four_wire_parallel_redundancy(; data)
    @test redundancy["certified"]
    @test redundancy["scalar_proportionality_residual"] > 0.1
    @test length(redundancy["checks"]) == 4
    @test minimum(check["margin"] for check in redundancy["checks"]) > 0.5

    source = solve_four_wire_parallel_formulation(:source; data)
    lifted = solve_four_wire_parallel_formulation(:exact_lifted; data)
    pruned = solve_four_wire_parallel_formulation(:exact_pruned; data)
    naive = solve_four_wire_parallel_formulation(:naive_aggregate; data)
    for result in (source, lifted, pruned, naive)
        @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
        @test result["neutral_kcl_residual_pu"] <= 1.0e-7
        @test all(0.88 - 1.0e-7 .<= result["phase_voltage_magnitude_pu"] .<= 1.05 + 1.0e-7)
    end
    @test lifted["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test pruned["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test naive["objective_served_fraction"] > source["objective_served_fraction"] + 0.1
    @test maximum(source["member_current_loading"][1]) ≈ 1.0 atol=1.0e-5
    @test maximum(pruned["member_current_loading"][2]) < 0.4
    @test pruned["neutral_voltage_magnitude_pu"] > 1.0e-4
    @test pruned["model_size"]["constraints"] + 4 == lifted["model_size"]["constraints"]

    independent = independently_reproduce_four_wire_boundary(; data)
    @test independent["bracket_width"] <= 1.0e-9
    @test independent["power_flow_residual"] <= 1.0e-9
    @test independent["boundary_served_fraction"] ≈ source["objective_served_fraction"] atol=2.0e-7
    @test independent["boundary_current_margin_pu"] >= -1.0e-8

    certificate = four_wire_parallel_certificate()
    @test certificate["classification"] == "exact_normalization"
    @test abs(certificate["evidence"]["pruned_objective_gap"]) <= 1.0e-7
    @test certificate["evidence"]["naive_objective_gap"] > 0.1
    @test abs(certificate["evidence"]["independent_source_objective_gap"]) <= 2.0e-7
end

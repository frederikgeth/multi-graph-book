using BMOPFTools
using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :PiFourWireParallelACDecision)
    include(joinpath(@__DIR__, "..", "transformations", "PiFourWireParallelACDecision.jl"))
end
using .PiFourWireParallelACDecision

@testset "nonproportional four-wire nominal-pi parallel AC decision" begin
    data = default_pi_four_wire_data()
    redundancy = pi_four_wire_redundancy(; data)
    @test redundancy["certified"]
    @test redundancy["required_terminal_ends"] == ["ij", "ji"]
    @test length(redundancy["checks"]) == 8
    @test maximum(check["exact_worst_case_magnitude"] for check in redundancy["checks"]) < 0.18
    @test redundancy["retained_map_condition_number"] < 3.0e3

    for line_number in 1:2
        impedance = data["impedance_pu"][line_number]
        shunt_from = data["shunt_from_pu"][line_number]
        shunt_to = data["shunt_to_pu"][line_number]
        linecode = Dict{String,Any}()
        for row in axes(impedance, 1), column in axes(impedance, 2)
            linecode["R_series_$(row)_$(column)"] = real(impedance[row, column])
            linecode["X_series_$(row)_$(column)"] = imag(impedance[row, column])
            linecode["G_from_$(row)_$(column)"] = real(shunt_from[row, column])
            linecode["B_from_$(row)_$(column)"] = imag(shunt_from[row, column])
            linecode["G_to_$(row)_$(column)"] = real(shunt_to[row, column])
            linecode["B_to_$(row)_$(column)"] = imag(shunt_to[row, column])
        end
        line = Dict{String,Any}(
            "bus_from" => "i", "bus_to" => "j",
            "terminal_map_from" => data["terminals"],
            "terminal_map_to" => data["terminals"],
            "linecode" => "lc", "length" => 1.0,
        )
        nodes, primitive = line_yprim(line, Dict("lc" => linecode))
        @test nodes == vcat([("i", terminal) for terminal in data["terminals"]],
                            [("j", terminal) for terminal in data["terminals"]])
        @test primitive ≈ PiFourWireParallelACDecision.member_primitive(data, line_number) atol=1.0e-12
    end

    source = solve_pi_four_wire_formulation(:source; data)
    lifted = solve_pi_four_wire_formulation(:exact_lifted; data)
    pruned = solve_pi_four_wire_formulation(:exact_pruned; data)
    naive = solve_pi_four_wire_formulation(:naive_aggregate; data)
    for result in (source, lifted, pruned, naive)
        @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
        @test result["neutral_kcl_residual_pu"] <= 1.0e-7
        @test all(0.88 - 1.0e-7 .<= result["phase_voltage_magnitude_pu"] .<= 1.05 + 1.0e-7)
    end
    @test lifted["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test pruned["objective_served_fraction"] ≈ source["objective_served_fraction"] atol=1.0e-7
    @test naive["objective_served_fraction"] > source["objective_served_fraction"] + 0.6
    @test maximum(vcat(source["member_current_loading"][1]["ij"], source["member_current_loading"][1]["ji"])) ≈ 1.0 atol=1.0e-5
    @test maximum(vcat(pruned["member_current_loading"][2]["ij"], pruned["member_current_loading"][2]["ji"])) < 0.2
    @test pruned["model_size"]["constraints"] + 8 == lifted["model_size"]["constraints"]

    independent = independently_reproduce_pi_boundary(; data)
    @test independent["bracket_width"] <= 1.0e-9
    @test independent["power_flow_residual"] <= 1.0e-9
    @test independent["boundary_served_fraction"] ≈ source["objective_served_fraction"] atol=2.0e-7

    certificate = pi_four_wire_certificate()
    @test certificate["classification"] == "exact_normalization"
    @test abs(certificate["evidence"]["pruned_objective_gap"]) <= 1.0e-7
    @test certificate["evidence"]["naive_objective_gap"] > 0.6
    @test abs(certificate["evidence"]["independent_source_objective_gap"]) <= 2.0e-7
    singular = singular_pi_guard()
    @test singular["realified_rank"] < singular["realified_dimension"]
    @test singular["rejected_by_recovery_guard"]
    singular_shunted = singular_shunted_pi_guard()
    @test singular_shunted["realified_rank"] < singular_shunted["realified_dimension"]
    @test abs(singular_shunted["retained_from_end_shunt_neutral"]) > 0
    @test singular_shunted["retained_to_end_shunt_neutral"] == 0
    @test singular_shunted["rejected_by_recovery_guard"]
    reduced = series_reduced_coordinate_guard()
    @test reduced["full_terminal_map_rank"] < reduced["full_terminal_map_dimension"]
    @test reduced["reduced_coordinate_recovery_residual"] ≤ 1.0e-12
    @test reduced["neutral_current_retained_as_zero"]
    @test occursin("endpoint-voltage-drop", reduced["classification"])
    state_guard = state_conditioned_pi_guard()
    @test state_guard["frozen_map_rejected_off_state"]
    @test state_guard["recomputed_map_consistent"]
    voltage_guard = voltage_dependent_pi_guard()
    @test voltage_guard["frozen_map_rejected_off_state"]
    @test voltage_guard["recomputed_map_consistent"]
    state_probe = state_conditioned_pi_decision_probe(; data)
    @test state_probe["base_map_redundancy_certified"]
    @test state_probe["shifted_map_redundancy_certified"]
    @test state_probe["state_changes_decision"]
    @test state_probe["shifted_pruning_remains_exact"]
    envelope = certificate["evidence"]["finite_state_decision_envelope"]
    @test envelope["declared_state_count"] == 3
    @test envelope["all_maps_certified"]
    @test envelope["maximum_absolute_pruned_objective_gap"] ≤ 1.0e-7
    @test envelope["minimum_relative_margin"] ≥ 9.0e-9
    @test all(record["source_status"] in ("LOCALLY_SOLVED", "OPTIMAL") for record in envelope["states"])
    @test all(record["pruned_status"] in ("LOCALLY_SOLVED", "OPTIMAL") for record in envelope["states"])
end

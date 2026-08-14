using Test
using BMOPFTools

include(joinpath(@__DIR__, "..", "transformations", "SolverDiagnosticsCrosswalk.jl"))
using .SolverDiagnosticsCrosswalk
include(joinpath(@__DIR__, "..", "running_network.jl"))

@testset "solver diagnostics crosswalk" begin
    result = evaluate_crosswalk(joinpath(@__DIR__, "..", "generated"))
    @test result.witness_id == "NUM-SOLVER-CROSSWALK-001"
    @test all(values(result.checks))
    @test result.solver_boundary["solver_internal_kkt_export"] === false
    @test result.comparisons["source_natural_fill_edges"] != result.comparisons["source_constraints_first_fill_edges"]
    probe = evaluate_solver_callback_probe(running_network())
    @test probe.diagnostic_status == "accepted"
    @test probe.diagnostic_dimension == 6
    @test probe.diagnostic_pivot_ratio ≈ 1.0
    @test probe.rejected_near_singular_probe
    diffopt_net = parse_bmopf("""
    {"bus":{
        "sourcebus":{"terminal_names":["1","n"],
                     "perfectly_grounded_terminals":["n"]},
        "bus1":{"terminal_names":["1","n"],
                "perfectly_grounded_terminals":["n"]}},
     "voltage_source":{"vs":{"bus":"sourcebus","terminal_map":["1"],
         "v_magnitude":[1000.0],"v_angle":[0.0]}},
     "linecode":{"lc":{"R_series_1_1":0.5}},
     "line":{"l1":{"bus_from":"sourcebus","bus_to":"bus1",
         "terminal_map_from":["1"],"terminal_map_to":["1"],
         "linecode":"lc","length":1.0}}}
    """; from_string=true)
    sensitivity = evaluate_diffopt_sensitivity(diffopt_net)
    @test sensitivity.solver_status in ("LOCALLY_SOLVED", "OPTIMAL")
    @test sensitivity.diagnostic_status == "accepted"
    @test sensitivity.forward_sensitivity ≈ 0.5 atol=1.0e-7
    @test sensitivity.central_sensitivity ≈ sensitivity.forward_sensitivity atol=1.0e-7
    @test sensitivity.sensitivity_residual ≤ 1.0e-7
    @test sensitivity.callback_invocations ≥ 1
    @test sensitivity.captured_kkt_rows == sensitivity.captured_kkt_columns
    @test sensitivity.captured_kkt_rows == sensitivity.diagnostic_dimension
    @test sensitivity.captured_kkt_nonzeros > 0
    @test 0.0 < sensitivity.captured_kkt_density ≤ 1.0
    @test sensitivity.kkt_unaccounted_rows == 4
    @test sensitivity.native_nlp_jacobian_rows == sensitivity.model_constraint_count
    @test sensitivity.native_nlp_jacobian_nonzeros > 0
    @test sensitivity.native_nlp_export_is_solver_internal === false
    @test length(sensitivity.model_variable_order) == sensitivity.model_variable_count
    @test length(sensitivity.model_constraint_order) == sensitivity.model_constraint_count
    @test all(!isempty, sensitivity.model_variable_order)
    @test all(!isempty, sensitivity.model_constraint_order)
    parallel_source, parallel_reduced = parallel_diffopt_networks()
    comparison = evaluate_diffopt_parallel_comparison(parallel_source, parallel_reduced)
    @test all(values(comparison.checks))
    @test comparison.source.forward_sensitivity ≈ 0.25 atol=1.0e-7
    @test comparison.reduced.forward_sensitivity ≈ 0.25 atol=1.0e-7
    @test comparison.source.captured_kkt_rows > comparison.reduced.captured_kkt_rows
    @test comparison.source.native_nlp_jacobian_nonzeros != comparison.reduced.native_nlp_jacobian_nonzeros
    @test sensitivity.differentiability_termination_status in ("LOCALLY_SOLVED", "OPTIMAL")
    @test sensitivity.inequality_constraint_count ≥ 0
    @test sensitivity.active_constraints isa Vector{String}
    @test sensitivity.near_active_constraints isa Vector{String}
    @test sensitivity.violated_constraints isa Vector{String}
end

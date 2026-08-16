using Test

include(joinpath(@__DIR__, "..", "transformations", "CircuitFormulationWitness.jl"))
using .CircuitFormulationWitness

@testset "circuit formulation witness" begin
    result = evaluate_circuit_formulation_witness()
    @test result.all_checks_pass
    @test result.lowering["plain_nodal_y_target"] == "unavailable_without_extra_variable_or_changed_query"
    @test result.checks["same_voltage_can_have_different_source_current"]
    @test result.checks["mna_residuals_are_zero"]
    @test result.checks["floating_nodal_operator_is_singular"]
    @test result.checks["declared_reference_does_not_imply_nonsingularity"]
    @test result.checks["grounded_rank_guard_passes"]
    @test result.checks["member_limit_is_lost_by_aggregate_y"]
    @test result.checks["voltage_loop_redundancy_is_detected"]
    @test result.checks["voltage_loop_contradiction_is_detected"]
    @test result.checks["current_cutset_redundancy_is_detected"]
    @test result.checks["current_cutset_contradiction_is_detected"]
    @test result.structural_diagnostics["voltage_source_loop"]["contradictory"]["classification"] == "contradictory_constraints"
    @test result.structural_diagnostics["current_source_cutset"]["consistent"]["classification"] == "consistent_redundant_constraints"
    @test result.nodal_rank_diagnostics["declared_reference_but_disconnected"]["rank"] == 1
    @test result.formulation_guards["phi_lin"] == "fixed linear factors only; unfixed decision-carrying factors remain in the equation/constraint operator"
    @test result.failure_cases["semantically_lossy_parallel_aggregation"]["diagnostic"] == "aggregate_y_forgets_member_current_limits"
end

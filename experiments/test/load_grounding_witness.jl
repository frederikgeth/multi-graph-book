using Test

include(joinpath(@__DIR__, "..", "transformations", "LoadGroundingWitness.jl"))
using .LoadGroundingWitness

@testset "load and grounding decision witnesses" begin
    result = evaluate_load_grounding_witnesses()
    @test result["all_witnesses_pass"]
    @test result["load_models"]["checks"]["same_bus_branch_graph"]
    @test result["load_models"]["checks"]["decision_margin_changes"]
    @test result["load_models"]["checks"]["zip_coefficients_are_normalized"]
    @test result["load_models"]["checks"]["zip_reactive_coefficients_are_distinct"]
    @test any(row["family"] == "ZIP" for row in result["load_models"]["rows"])
    @test result["connection_maps"]["checks"]["same_bus_branch_graph"]
    @test result["connection_maps"]["checks"]["wye_and_delta_observations_differ"]
    @test result["connection_maps"]["checks"]["delta_magnitudes_are_sqrt_three"]
    @test result["load_continuation"]["checks"]["constant_power_failure_is_observed"]
    @test result["load_continuation"]["checks"]["constant_power_fails_before_voltage_dependent_families"]
    @test result["load_continuation"]["checks"]["converged_rows_have_small_residuals"]
    @test result["grounding_models"]["checks"]["same_bus_branch_graph"]
    @test result["grounding_models"]["checks"]["grounding_changes_current_allocation"]
    @test result["explicit_earth"]["checks"]["earth_port_retained"]
    @test result["explicit_earth"]["checks"]["fault_crosses_protection_threshold"]
    @test result["explicit_earth"]["checks"]["outage_does_not_equal_ideal_reference"]
    @test result["explicit_earth"]["checks"]["asset_identity_retained"]
    @test result["explicit_earth"]["checks"]["touch_voltage_observation_changes"]
    @test result["explicit_earth"]["checks"]["maintenance_changes_availability"]
    @test result["explicit_earth"]["checks"]["multiple_fault_classes_retained"]
    @test result["explicit_earth"]["checks"]["ct_measurement_map_retained"]
    @test result["explicit_earth"]["checks"]["relay_curve_observation_retained"]
    @test result["explicit_earth"]["checks"]["relay_time_limit_is_evaluated"]
    @test result["explicit_earth"]["checks"]["ct_saturation_can_change_trip_decision"]
end

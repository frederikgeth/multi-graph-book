module LoadGroundingWitness

using LinearAlgebra

export evaluate_load_witness,
       evaluate_connection_map_witness,
       evaluate_grounding_witness,
       evaluate_explicit_earth_witness,
       evaluate_load_grounding_witnesses

complex_dict(value) = Dict("real" => real(value), "imag" => imag(value))

"Solve a small two-bus fixed-point load model at its high-voltage branch."
function _load_solution(z, s_nominal, family; voltage_nominal=1.0, zip_coefficients_p=(0.4, 0.3, 0.3), zip_coefficients_q=(0.2, 0.3, 0.5), scale=1.0, initial_voltage=1.0 + 0.0im, max_iterations=500)
    voltage = initial_voltage
    converged = false
    iterations = max_iterations
    for iteration in 1:max_iterations
        ratio = abs(voltage) / voltage_nominal
        factor_p = family == "CP" ? 1.0 : family == "CI" ? ratio : family == "CZ" ? ratio^2 : zip_coefficients_p[1] * ratio^2 + zip_coefficients_p[2] * ratio + zip_coefficients_p[3]
        factor_q = family == "CP" ? 1.0 : family == "CI" ? ratio : family == "CZ" ? ratio^2 : zip_coefficients_q[1] * ratio^2 + zip_coefficients_q[2] * ratio + zip_coefficients_q[3]
        power = complex(scale * real(s_nominal) * factor_p, scale * imag(s_nominal) * factor_q)
        current = conj(power / voltage)
        target = 1.0 - z * current
        updated = 0.5 * voltage + 0.5 * target
        if abs(updated - voltage) <= 1.0e-13
            voltage = updated
            converged = true
            iterations = iteration
            break
        end
        voltage = updated
    end
    ratio = abs(voltage) / voltage_nominal
    factor_p = family == "CP" ? 1.0 : family == "CI" ? ratio : family == "CZ" ? ratio^2 : zip_coefficients_p[1] * ratio^2 + zip_coefficients_p[2] * ratio + zip_coefficients_p[3]
    factor_q = family == "CP" ? 1.0 : family == "CI" ? ratio : family == "CZ" ? ratio^2 : zip_coefficients_q[1] * ratio^2 + zip_coefficients_q[2] * ratio + zip_coefficients_q[3]
    power = complex(scale * real(s_nominal) * factor_p, scale * imag(s_nominal) * factor_q)
    current = conj(power / voltage)
    Dict{String,Any}(
        "family" => family,
        "scale" => scale,
        "converged" => converged,
        "iterations" => iterations,
        "voltage_pu" => complex_dict(voltage),
        "voltage_magnitude_pu" => abs(voltage),
        "current_pu" => complex_dict(current),
        "current_magnitude_pu" => abs(current),
        "delivered_power_pu" => complex_dict(power),
        "residual_pu" => abs(1.0 - voltage - z * current),
    )
end

"Continue the scalar load branches in demand scale until the damped iteration fails."
function evaluate_load_continuation()
    z = 0.08 + 0.16im
    s_nominal = 0.90 + 0.25im
    scales = collect(0.2:0.1:3.0)
    rows = Dict{String,Any}[]
    last_converged = Dict{String,Any}()
    first_failed = Dict{String,Any}()
    ordered = true
    for family in ("CP", "CI", "CZ", "ZIP")
        previous = 1.0 + 0.0im
        family_rows = Dict{String,Any}[]
        for scale in scales
            row = _load_solution(z, s_nominal, family; scale=scale, initial_voltage=previous, max_iterations=2000)
            row["scale"] = scale
            push!(family_rows, row)
            if row["converged"]
                previous = ComplexF64(row["voltage_pu"]["real"], row["voltage_pu"]["imag"])
                last_converged[family] = scale
            else
                first_failed[family] = scale
                break
            end
        end
        ordered &= all(family_rows[index]["scale"] <= family_rows[index + 1]["scale"] for index in 1:(length(family_rows) - 1))
        append!(rows, family_rows)
    end
    Dict{String,Any}(
        "witness_id" => "LOAD-CONTINUATION-001",
        "claim_id" => "LOAD-CONTINUATION-001",
        "model_scope" => "two-bus scalar AC continuation probe using damped fixed-point branch tracking and demand scale",
        "scale_grid" => scales,
        "rows" => rows,
        "last_converged_scale" => last_converged,
        "first_failed_scale" => first_failed,
        "checks" => Dict(
            "same_bus_branch_graph" => true,
            "base_scale_converges_for_all_families" => all(row["converged"] for row in rows if row["scale"] == 0.2),
            "continuation_scales_are_ordered" => ordered,
            "converged_rows_have_small_residuals" => all(row["residual_pu"] <= 1.0e-9 for row in rows if row["converged"]),
            "constant_power_failure_is_observed" => haskey(first_failed, "CP"),
            "constant_power_fails_before_voltage_dependent_families" => last_converged["CP"] < last_converged["CI"] && last_converged["CP"] < last_converged["CZ"] && last_converged["CP"] < last_converged["ZIP"],
            "continuation_is_not_global_certificate" => true,
        ),
        "interpretation" => "The continuation probe records a branch-tracking and iteration-failure boundary for one scalar fixture; it is not a global voltage-collapse theorem or a ranking of load models.",
    )
end

"Compare wye phase-to-neutral and delta phase-to-phase connection maps on one bus."
function evaluate_connection_map_witness()
    a = exp(2pi * im / 3)
    phase_voltage = ComplexF64[1.0 + 0.0im, a^2, a]
    terminal_voltage = vcat(phase_voltage, 0.0 + 0.0im)
    wye_map = ComplexF64[
        1 0 0 -1;
        0 1 0 -1;
        0 0 1 -1;
    ]
    delta_map = ComplexF64[
        1 -1 0 0;
        0 1 -1 0;
        -1 0 1 0;
    ]
    wye_voltage = wye_map * terminal_voltage
    delta_voltage = delta_map * terminal_voltage
    Dict{String,Any}(
        "witness_id" => "LOAD-CONNECTION-001",
        "claim_id" => "LOAD-CONNECTION-001",
        "model_scope" => "one balanced three-phase bus with explicit phase and neutral terminals and fixed wye/delta connection maps",
        "terminal_order" => ["a", "b", "c", "n"],
        "phase_voltage" => [complex_dict(value) for value in phase_voltage],
        "wye_map" => [[real(value) for value in row] for row in eachrow(wye_map)],
        "delta_map" => [[real(value) for value in row] for row in eachrow(delta_map)],
        "wye_voltage" => [complex_dict(value) for value in wye_voltage],
        "delta_voltage" => [complex_dict(value) for value in delta_voltage],
        "checks" => Dict(
            "terminal_order_retained" => ["a", "b", "c", "n"] == ["a", "b", "c", "n"],
            "same_bus_branch_graph" => true,
            "wye_phase_to_neutral_map_is_explicit" => wye_map == ComplexF64[1 0 0 -1; 0 1 0 -1; 0 0 1 -1],
            "delta_phase_to_phase_map_is_explicit" => delta_map == ComplexF64[1 -1 0 0; 0 1 -1 0; -1 0 1 0],
            "wye_and_delta_observations_differ" => norm(wye_voltage - delta_voltage, Inf) > 1.0e-6,
            "wye_magnitudes_are_one" => all(isapprox(abs(value), 1.0; atol=1.0e-12) for value in wye_voltage),
            "delta_magnitudes_are_sqrt_three" => all(isapprox(abs(value), sqrt(3.0); atol=1.0e-12) for value in delta_voltage),
        ),
        "interpretation" => "A connection map is part of the constitutive factor semantics: wye and delta loads can share the same bus and graph while observing different terminal-voltage coordinates.",
    )
end

"Compare CP, CI, CZ, and ZIP on the same two-bus graph and decision limits."
function evaluate_load_witness()
    z = 0.08 + 0.16im
    s_nominal = 0.90 + 0.25im
    voltage_limit = 0.87
    current_limit = 1.00
    zip_coefficients_p = (0.4, 0.3, 0.3)
    zip_coefficients_q = (0.2, 0.3, 0.5)
    rows = [_load_solution(z, s_nominal, family; zip_coefficients_p=zip_coefficients_p, zip_coefficients_q=zip_coefficients_q) for family in ("CP", "CI", "CZ", "ZIP")]
    for row in rows
        row["voltage_limit_satisfied"] = row["voltage_magnitude_pu"] >= voltage_limit
        row["current_limit_satisfied"] = row["current_magnitude_pu"] <= current_limit
    end
    Dict{String,Any}(
        "witness_id" => "LOAD-DECISION-001",
        "model_scope" => "two-bus scalar AC load models with fixed source, series impedance, and nominal demand",
        "source_voltage_pu" => complex_dict(1.0 + 0.0im),
        "series_impedance_pu" => complex_dict(z),
        "nominal_load_pu" => complex_dict(s_nominal),
        "voltage_limit_pu" => voltage_limit,
        "current_limit_pu" => current_limit,
        "rows" => rows,
        "zip_coefficients" => Dict(
            "active_power" => Dict("alpha_Z" => zip_coefficients_p[1], "alpha_I" => zip_coefficients_p[2], "alpha_P" => zip_coefficients_p[3]),
            "reactive_power" => Dict("alpha_Z" => zip_coefficients_q[1], "alpha_I" => zip_coefficients_q[2], "alpha_P" => zip_coefficients_q[3]),
        ),
        "checks" => Dict(
            "same_bus_branch_graph" => true,
            "all_residuals_small" => all(row["residual_pu"] <= 1.0e-10 for row in rows),
            "families_produce_distinct_voltages" => length(unique(round(row["voltage_magnitude_pu"]; digits=8) for row in rows)) == 4,
            "decision_margin_changes" => length(unique((row["voltage_limit_satisfied"], row["current_limit_satisfied"]) for row in rows)) > 1,
            "constant_power_fails_both_limits" => !rows[1]["voltage_limit_satisfied"] && !rows[1]["current_limit_satisfied"],
            "constant_impedance_satisfies_both_limits" => rows[3]["voltage_limit_satisfied"] && rows[3]["current_limit_satisfied"],
            "zip_coefficients_are_normalized" => sum(zip_coefficients_p) == 1.0 && sum(zip_coefficients_q) == 1.0 && all(value >= 0 for value in zip_coefficients_p) && all(value >= 0 for value in zip_coefficients_q),
            "zip_reactive_coefficients_are_distinct" => zip_coefficients_p != zip_coefficients_q,
        ),
        "interpretation" => "The graph is fixed, but the constitutive load relation changes voltages, currents, and the decision-feasible set.",
    )
end

function _grounding_solution(z_phase, z_neutral, y_load, y_ground)
    y_phase = inv(z_phase)
    y_neutral = inv(z_neutral)
    matrix = ComplexF64[
        y_phase + y_load  -y_load;
        -y_load            y_neutral + y_ground + y_load;
    ]
    voltage = matrix \ ComplexF64[y_phase, 0.0 + 0.0im]
    v_phase, v_neutral = voltage
    load_voltage = v_phase - v_neutral
    load_current = y_load * load_voltage
    neutral_current = y_neutral * v_neutral
    ground_current = y_ground * v_neutral
    Dict{String,Any}(
        "phase_voltage_pu" => complex_dict(v_phase),
        "neutral_voltage_pu" => complex_dict(v_neutral),
        "load_voltage_pu" => complex_dict(load_voltage),
        "load_current_pu" => complex_dict(load_current),
        "neutral_current_pu" => complex_dict(neutral_current),
        "ground_current_pu" => complex_dict(ground_current),
        "neutral_voltage_magnitude_pu" => abs(v_neutral),
        "neutral_current_magnitude_pu" => abs(neutral_current),
        "ground_current_magnitude_pu" => abs(ground_current),
    )
end

"Compare floating, impedance-grounded, and ideal-grounded neutral relations."
function evaluate_grounding_witness()
    z_phase = 0.05 + 0.10im
    z_neutral = 0.08 + 0.16im
    y_load = inv(1.0 + 0.30im)
    states = [
        ("floating", 0.0 + 0.0im),
        ("impedance_grounded", inv(0.30 + 0.20im)),
        ("perfectly_grounded", 1.0e6 + 0.0im),
    ]
    rows = Dict{String,Any}[]
    for (state, y_ground) in states
        row = _grounding_solution(z_phase, z_neutral, y_load, y_ground)
        row["state"] = state
        push!(rows, row)
    end
    Dict{String,Any}(
        "witness_id" => "GROUND-SCOPE-002",
        "model_scope" => "one-phase two-conductor load with explicit neutral return and three customer-end grounding relations",
        "same_connectivity_graph" => true,
        "phase_impedance_pu" => complex_dict(z_phase),
        "neutral_impedance_pu" => complex_dict(z_neutral),
        "load_admittance_pu" => complex_dict(y_load),
        "rows" => rows,
        "checks" => Dict(
            "same_bus_branch_graph" => true,
            "floating_ground_current_zero" => rows[1]["ground_current_magnitude_pu"] <= 1.0e-12,
            "impedance_grounding_changes_neutral_voltage" => abs(rows[2]["neutral_voltage_magnitude_pu"] - rows[1]["neutral_voltage_magnitude_pu"]) > 1.0e-6,
            "ideal_grounding_neutral_voltage_small" => rows[3]["neutral_voltage_magnitude_pu"] <= 1.0e-5,
            "grounding_changes_current_allocation" => length(unique(round(row["ground_current_magnitude_pu"]; digits=8) for row in rows)) == 3,
        ),
        "interpretation" => "Changing the grounding relation leaves simple connectivity unchanged but changes neutral voltage, return-current allocation, and grounding observations.",
    )
end

function _explicit_earth_solution(z_phase, z_neutral, z_earth, y_load, y_bond, y_fault_phase, y_fault_neutral)
    y_phase = inv(z_phase)
    y_neutral = inv(z_neutral)
    y_earth = inv(z_earth)
    matrix = ComplexF64[
        y_phase + y_load + y_fault_phase  -y_load              -y_fault_phase;
        -y_load                      y_neutral + y_load + y_bond + y_fault_neutral  -y_bond - y_fault_neutral;
        -y_fault_phase               -y_bond - y_fault_neutral  y_earth + y_bond + y_fault_phase + y_fault_neutral;
    ]
    voltage = matrix \ ComplexF64[y_phase, 0.0 + 0.0im, 0.0 + 0.0im]
    v_phase, v_neutral, v_earth = voltage
    load_voltage = v_phase - v_neutral
    phase_fault_voltage = v_phase - v_earth
    neutral_fault_voltage = v_neutral - v_earth
    load_current = y_load * load_voltage
    neutral_current = y_neutral * v_neutral
    earth_conductor_current = y_earth * v_earth
    bond_current = y_bond * (v_neutral - v_earth)
    phase_fault_current = y_fault_phase * phase_fault_voltage
    neutral_fault_current = y_fault_neutral * neutral_fault_voltage
    fault_current = phase_fault_current + neutral_fault_current
    Dict{String,Any}(
        "phase_voltage_pu" => complex_dict(v_phase),
        "neutral_voltage_pu" => complex_dict(v_neutral),
        "earth_voltage_pu" => complex_dict(v_earth),
        "load_current_pu" => complex_dict(load_current),
        "neutral_current_pu" => complex_dict(neutral_current),
        "earth_conductor_current_pu" => complex_dict(earth_conductor_current),
        "bond_current_pu" => complex_dict(bond_current),
        "phase_fault_current_pu" => complex_dict(phase_fault_current),
        "neutral_fault_current_pu" => complex_dict(neutral_fault_current),
        "fault_current_pu" => complex_dict(fault_current),
        "earth_voltage_magnitude_pu" => abs(v_earth),
        "earth_conductor_current_magnitude_pu" => abs(earth_conductor_current),
        "fault_current_magnitude_pu" => abs(fault_current),
    )
end

"Compare explicit-earth conductor availability and a scoped fault/protection observation."
function evaluate_explicit_earth_witness()
    z_phase = 0.05 + 0.10im
    z_neutral = 0.08 + 0.16im
    y_load = inv(1.0 + 0.30im)
    y_bond = inv(0.30 + 0.20im)
    fault_limit = 0.50
    ct_ratio = 10.0
    ct_pickup_secondary = 0.20
    relay_curve_id = "illustrative_inverse_time_v0.1"
    relay_time_constant_s = 0.10
    relay_time_limit_s = 0.30
    ct_saturation_cap_secondary = 0.18
    touch_voltage_limit = 0.10
    asset_ids = [
        "asset/earth-conductor/e1",
        "asset/neutral-bond/b1",
        "asset/protection-zone/z1",
    ]
    states = [
        ("earth_in_service", "none", 0.12 + 0.24im, 0.0 + 0.0im, 0.0 + 0.0im, 0),
        ("earth_conductor_maintenance_outage", "none", 1.0e6 + 0.0im, 0.0 + 0.0im, 0.0 + 0.0im, 1),
        ("phase_to_earth_fault", "phase_earth", 0.12 + 0.24im, inv(0.02 + 0.04im), 0.0 + 0.0im, 0),
        ("neutral_to_earth_fault", "neutral_earth", 0.12 + 0.24im, 0.0 + 0.0im, inv(0.03 + 0.06im), 0),
    ]
    rows = Dict{String,Any}[]
    for (state, fault_class, z_earth, y_fault_phase, y_fault_neutral, maintenance_decision) in states
        row = _explicit_earth_solution(z_phase, z_neutral, z_earth, y_load, y_bond, y_fault_phase, y_fault_neutral)
        row["state"] = state
        row["fault_class"] = fault_class
        row["fault_current_limit_pu"] = fault_limit
        row["ct_ratio"] = ct_ratio
        row["ct_pickup_secondary_pu"] = ct_pickup_secondary
        row["ct_measured_current_magnitude_pu"] = row["fault_current_magnitude_pu"] / ct_ratio
        row["protection_trip_observed"] = row["ct_measured_current_magnitude_pu"] >= ct_pickup_secondary
        ratio = row["ct_measured_current_magnitude_pu"] / ct_pickup_secondary
        row["relay_curve_id"] = relay_curve_id
        row["relay_trip_time_s"] = ratio > 1.0 ? relay_time_constant_s / (ratio - 1.0) : nothing
        row["relay_operation_observed"] = row["protection_trip_observed"] &&
            row["relay_trip_time_s"] <= relay_time_limit_s
        row["maintenance_decision"] = maintenance_decision
        row["maintenance_cost"] = 1.0 * maintenance_decision
        row["touch_voltage_pu"] = row["earth_voltage_magnitude_pu"]
        row["touch_voltage_limit_pu"] = touch_voltage_limit
        row["touch_voltage_limit_satisfied"] = row["touch_voltage_pu"] <= touch_voltage_limit
        row["asset_state"] = maintenance_decision == 1 ? "e1=outage; b1=in_service" :
            fault_class != "none" ? "e1=in_service; b1=in_service; fault=applied" :
            "e1=in_service; b1=in_service"
        push!(rows, row)
    end
    phase_fault = rows[3]
    ideal_secondary = phase_fault["ct_measured_current_magnitude_pu"]
    saturated_secondary = min(ideal_secondary, ct_saturation_cap_secondary)
    Dict{String,Any}(
        "witness_id" => "GROUND-SCOPE-003",
        "model_scope" => "one-phase explicit-earth-conductor fixture with a finite neutral bond, maintenance outage, two fault classes, and CT-scaled protection observation",
        "same_bus_branch_graph" => true,
        "phase_impedance_pu" => complex_dict(z_phase),
        "neutral_impedance_pu" => complex_dict(z_neutral),
        "earth_bond_admittance_pu" => complex_dict(y_bond),
        "asset_ids" => asset_ids,
        "touch_voltage_limit_pu" => touch_voltage_limit,
        "ct_ratio" => ct_ratio,
        "ct_pickup_secondary_pu" => ct_pickup_secondary,
        "relay_curve_id" => relay_curve_id,
        "relay_time_constant_s" => relay_time_constant_s,
        "relay_time_limit_s" => relay_time_limit_s,
        "ct_saturation_cap_secondary" => ct_saturation_cap_secondary,
        "ct_saturation_probe" => Dict(
            "fault_class" => "phase_earth",
            "ideal_secondary_current_pu" => ideal_secondary,
            "saturated_secondary_current_pu" => saturated_secondary,
            "ideal_trip" => ideal_secondary >= ct_pickup_secondary,
            "saturated_trip" => saturated_secondary >= ct_pickup_secondary,
            "interpretation" => "A declared saturation cap can change the relay decision; it is a sensitivity probe, not a CT electromagnetic model.",
        ),
        "earth_conductor_is_explicit_port" => true,
        "rows" => rows,
        "checks" => Dict(
            "same_bus_branch_graph" => true,
            "earth_port_retained" => true,
            "outage_changes_earth_current" => abs(rows[2]["earth_conductor_current_magnitude_pu"] - rows[1]["earth_conductor_current_magnitude_pu"]) > 1.0e-6,
            "fault_increases_fault_current" => rows[3]["fault_current_magnitude_pu"] > rows[1]["fault_current_magnitude_pu"] + 1.0e-6,
            "fault_crosses_protection_threshold" => !rows[1]["protection_trip_observed"] && rows[3]["protection_trip_observed"],
            "outage_does_not_equal_ideal_reference" => rows[2]["earth_voltage_magnitude_pu"] > 1.0e-4,
            "maintenance_changes_availability" => rows[1]["maintenance_decision"] == 0 && rows[2]["maintenance_decision"] == 1 &&
                rows[1]["earth_conductor_current_magnitude_pu"] > rows[2]["earth_conductor_current_magnitude_pu"],
            "multiple_fault_classes_retained" => length(unique(row["fault_class"] for row in rows)) == 3,
            "ct_measurement_map_retained" => all(isapprox(row["ct_measured_current_magnitude_pu"] * ct_ratio,
                row["fault_current_magnitude_pu"]; atol=1.0e-12) for row in rows),
            "relay_curve_observation_retained" => rows[3]["relay_operation_observed"] &&
                !rows[4]["relay_operation_observed"],
            "relay_time_limit_is_evaluated" => rows[3]["relay_trip_time_s"] !== nothing &&
                rows[3]["relay_trip_time_s"] <= relay_time_limit_s,
            "ct_saturation_can_change_trip_decision" => ideal_secondary >= ct_pickup_secondary &&
                saturated_secondary < ct_pickup_secondary,
            "asset_identity_retained" => asset_ids == [
                "asset/earth-conductor/e1", "asset/neutral-bond/b1", "asset/protection-zone/z1",
            ],
            "touch_voltage_observation_changes" => rows[1]["touch_voltage_limit_satisfied"] &&
                !rows[2]["touch_voltage_limit_satisfied"] && !rows[3]["touch_voltage_limit_satisfied"],
        ),
        "interpretation" => "An explicit earth conductor and its outage/fault observations are not recoverable from a simple graph or an ideal reference alone; this is a scoped E_2 witness, not a complete protection model.",
    )
end

function evaluate_load_grounding_witnesses()
    load = evaluate_load_witness()
    continuation = evaluate_load_continuation()
    connection_maps = evaluate_connection_map_witness()
    grounding = evaluate_grounding_witness()
    explicit_earth = evaluate_explicit_earth_witness()
    Dict{String,Any}(
        "schema_version" => "0.1.0",
        "load_models" => load,
        "load_continuation" => continuation,
        "connection_maps" => connection_maps,
        "grounding_models" => grounding,
        "explicit_earth" => explicit_earth,
        "all_witnesses_pass" => all(values(load["checks"])) &&
            all(values(continuation["checks"])) &&
            all(values(connection_maps["checks"])) &&
            all(values(grounding["checks"])) && all(values(explicit_earth["checks"])),
        "source" => "experiments/transformations/LoadGroundingWitness.jl",
    )
end

end

module ThreeMemberFourWireParallelACDecision

using Ipopt
using JuMP
using LinearAlgebra

include(joinpath(@__DIR__, "FourWireParallelACDecision.jl"))
using .FourWireParallelACDecision

export three_member_data,
       three_member_joint_certificate,
       independently_reproduce_three_member_boundary,
       solve_three_member_formulation,
       three_member_certificate

function three_member_data()
    data = default_four_wire_parallel_data()
    y1, y2 = data["admittance_pu"]
    y3 = 0.10 .* (y1 + y2)
    data["impedance_pu"] = [inv(y1), inv(y2), inv(y3)]
    data["admittance_pu"] = [y1, y2, y3]
    data["current_limit_pu"] = [fill(0.72, 4), fill(0.72, 4), fill(0.15, 4)]
    data
end

function three_member_joint_certificate(; data=three_member_data())
    n = length(data["terminals"])
    recovery_1 = 0.10 .* Matrix{ComplexF64}(I, n, n)
    recovery_2 = 0.10 .* Matrix{ComplexF64}(I, n, n)
    worst_case = [
        sum(abs(recovery_1[row, column]) * data["current_limit_pu"][1][column] +
            abs(recovery_2[row, column]) * data["current_limit_pu"][2][column]
            for column in 1:n)
        for row in 1:n
    ]
    candidate_limits = data["current_limit_pu"][3]
    Dict{String,Any}(
        "retained_members" => ["l1", "l2"],
        "candidate_member" => "l3",
        "recovery_relation" => "I_l3 = 0.10 I_l1 + 0.10 I_l2",
        "recovery_maps" => [
            [[Dict("re" => real(recovery_1[row, column]), "im" => imag(recovery_1[row, column])) for column in 1:n] for row in 1:n],
            [[Dict("re" => real(recovery_2[row, column]), "im" => imag(recovery_2[row, column])) for column in 1:n] for row in 1:n],
        ],
        "exact_worst_case_component_magnitudes" => worst_case,
        "candidate_limits" => candidate_limits,
        "certified" => all(worst_case[row] <= candidate_limits[row] + 1.0e-12 for row in 1:n),
        "scope" => "fixed three-member series-only current maps with centered component discs; exact joint implication before nonlinear AC solve",
    )
end

function solve_three_member_formulation(kind::Symbol; data=three_member_data())
    kind in (:source, :exact_pruned) || throw(ArgumentError("unknown formulation $kind"))
    certificate = three_member_joint_certificate(; data)
    kind == :exact_pruned && !certificate["certified"] &&
        throw(ArgumentError("member-3 limits are not jointly certified redundant"))
    n = length(data["terminals"])
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    set_optimizer_attribute(model, "tol", 1.0e-9)
    set_optimizer_attribute(model, "constr_viol_tol", 1.0e-9)
    set_optimizer_attribute(model, "max_iter", 3000)
    @variable(model, voltage_real[1:n])
    @variable(model, voltage_imag[1:n])
    @variable(model, served >= 0)
    start = 0.96 .* data["slack_voltage_pu"]
    for conductor in 1:n
        set_start_value(voltage_real[conductor], real(start[conductor]))
        set_start_value(voltage_imag[conductor], imag(start[conductor]))
    end
    set_start_value(served, 0.7)

    member_real = Any[]
    member_imag = Any[]
    for admittance in data["admittance_pu"]
        re, im = FourWireParallelACDecision.current_expressions(
            model, admittance, voltage_real, voltage_imag, data["slack_voltage_pu"],
        )
        push!(member_real, re)
        push!(member_imag, im)
    end
    @expression(model, total_real[c=1:n], sum(member_real[line][c] for line in 1:3))
    @expression(model, total_imag[c=1:n], sum(member_imag[line][c] for line in 1:3))
    @constraint(model, sum(total_real) == 0)
    @constraint(model, sum(total_imag) == 0)
    for phase in 1:3
        load_voltage_real = voltage_real[phase] - voltage_real[4]
        load_voltage_imag = voltage_imag[phase] - voltage_imag[4]
        direction = data["load_direction_pu"][phase]
        @constraint(model,
            served * real(direction) ==
            load_voltage_real * total_real[phase] + load_voltage_imag * total_imag[phase]
        )
        @constraint(model,
            served * imag(direction) ==
            load_voltage_imag * total_real[phase] - load_voltage_real * total_imag[phase]
        )
        lower, upper = data["voltage_magnitude_bounds_pu"]
        @constraint(model, load_voltage_real^2 + load_voltage_imag^2 >= lower^2)
        @constraint(model, load_voltage_real^2 + load_voltage_imag^2 <= upper^2)
    end
    limited_lines = kind == :exact_pruned ? (1:2) : (1:3)
    for line in limited_lines, conductor in 1:n
        limit = data["current_limit_pu"][line][conductor]
        @constraint(model,
            member_real[line][conductor]^2 + member_imag[line][conductor]^2 <= limit^2
        )
    end
    @objective(model, Max, served)
    optimize!(model)

    voltage = value.(voltage_real) .+ im .* value.(voltage_imag)
    member_currents = [y * (data["slack_voltage_pu"] - voltage) for y in data["admittance_pu"]]
    total_current = sum(member_currents)
    phase_voltage = voltage[1:3] .- voltage[4]
    phase_power = phase_voltage .* conj.(total_current[1:3])
    Dict{String,Any}(
        "formulation" => String(kind),
        "termination_status" => string(termination_status(model)),
        "objective_served_fraction" => objective_value(model),
        "phase_voltage_magnitude_pu" => abs.(phase_voltage),
        "neutral_voltage_magnitude_pu" => abs(voltage[4]),
        "phase_power_pu" => [Dict("p" => real(s), "q" => imag(s)) for s in phase_power],
        "member_current_magnitude_pu" => [abs.(current) for current in member_currents],
        "member_current_loading" => [abs.(member_currents[line]) ./ data["current_limit_pu"][line] for line in 1:3],
        "neutral_kcl_residual_pu" => abs(sum(total_current)),
        "model_size" => Dict(
            "variables" => num_variables(model),
            "constraints" => sum(num_constraints(model, f, s) for (f, s) in list_of_constraint_types(model)),
        ),
    )
end

function independent_three_member_feasibility(served, start, data)
    power_flow = FourWireParallelACDecision.independent_power_flow(served, start, data)
    voltage = power_flow["voltage"]
    member_currents = [y * (data["slack_voltage_pu"] - voltage) for y in data["admittance_pu"]]
    phase_voltage = abs.(voltage[1:3] .- voltage[4])
    lower, upper = data["voltage_magnitude_bounds_pu"]
    current_margin = minimum(
        data["current_limit_pu"][line][conductor] - abs(member_currents[line][conductor])
        for line in 1:3, conductor in 1:4
    )
    voltage_margin = min(minimum(phase_voltage .- lower), minimum(upper .- phase_voltage))
    Dict{String,Any}(
        "served_fraction" => served,
        "converged" => power_flow["converged"],
        "residual_norm" => power_flow["residual_norm"],
        "voltage" => voltage,
        "phase_voltage_magnitude_pu" => phase_voltage,
        "member_current_magnitude_pu" => [abs.(current) for current in member_currents],
        "current_margin_pu" => current_margin,
        "voltage_margin_pu" => voltage_margin,
        "feasible" => power_flow["converged"] && current_margin >= -1.0e-8 && voltage_margin >= -1.0e-8,
    )
end

"Independent finite-difference continuation and bisection for the three-member source boundary."
function independently_reproduce_three_member_boundary(
    ; data=three_member_data(), scan_step=0.05, tolerance=1.0e-8,
)
    voltage = copy(data["slack_voltage_pu"])
    lower = independent_three_member_feasibility(0.0, voltage, data)
    upper = nothing
    served = scan_step
    while served <= 3.0
        point = independent_three_member_feasibility(served, voltage, data)
        point["converged"] && (voltage = point["voltage"])
        if !point["feasible"]
            upper = point
            break
        end
        lower = point
        served += scan_step
    end
    upper === nothing && throw(ArgumentError("independent scan did not bracket a boundary"))
    upper["converged"] || throw(ArgumentError("boundary was preceded by power-flow failure"))
    for _ in 1:80
        upper["served_fraction"] - lower["served_fraction"] <= tolerance && break
        midpoint = (lower["served_fraction"] + upper["served_fraction"]) / 2
        point = independent_three_member_feasibility(midpoint, lower["voltage"], data)
        point["converged"] || throw(ArgumentError("power flow failed inside boundary bracket"))
        if point["feasible"]
            lower = point
        else
            upper = point
        end
    end
    Dict{String,Any}(
        "method" => "finite-difference damped Newton continuation and bisection",
        "boundary_served_fraction" => lower["served_fraction"],
        "upper_bracket_served_fraction" => upper["served_fraction"],
        "bracket_width" => upper["served_fraction"] - lower["served_fraction"],
        "boundary_current_margin_pu" => lower["current_margin_pu"],
        "boundary_voltage_margin_pu" => lower["voltage_margin_pu"],
        "phase_voltage_magnitude_pu" => lower["phase_voltage_magnitude_pu"],
        "member_current_magnitude_pu" => lower["member_current_magnitude_pu"],
        "power_flow_residual" => lower["residual_norm"],
    )
end

function three_member_certificate()
    data = three_member_data()
    certificate = three_member_joint_certificate(; data)
    source = solve_three_member_formulation(:source; data)
    pruned = solve_three_member_formulation(:exact_pruned; data)
    independent = independently_reproduce_three_member_boundary(; data)
    merge(certificate, Dict(
        "source_solution" => source,
        "exact_pruned_solution" => pruned,
        "independent_source_boundary" => independent,
        "objective_gap" => pruned["objective_served_fraction"] - source["objective_served_fraction"],
        "independent_source_objective_gap" => independent["boundary_served_fraction"] - source["objective_served_fraction"],
        "classification" => "exact nonlinear AC constraint pruning under a fixed linear joint recovery map",
    ))
end

end

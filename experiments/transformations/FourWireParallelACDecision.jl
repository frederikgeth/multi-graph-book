module FourWireParallelACDecision

using Ipopt
using JuMP
using LinearAlgebra

include(joinpath(@__DIR__, "MulticonductorFlowLimitRedundancy.jl"))
using .MulticonductorFlowLimitRedundancy

export default_four_wire_parallel_data,
       four_wire_parallel_certificate,
       four_wire_parallel_redundancy,
       independently_reproduce_four_wire_boundary,
       solve_four_wire_parallel_formulation

function default_four_wire_parallel_data()
    impedance_1 = ComplexF64[
        0.040+0.080im 0.008+0.018im 0.007+0.016im 0.006+0.014im
        0.008+0.018im 0.043+0.084im 0.009+0.019im 0.007+0.015im
        0.007+0.016im 0.009+0.019im 0.046+0.088im 0.008+0.017im
        0.006+0.014im 0.007+0.015im 0.008+0.017im 0.060+0.105im
    ]
    impedance_2 = 4 .* ComplexF64[
        0.050+0.095im 0.006+0.014im 0.005+0.012im 0.004+0.010im
        0.006+0.014im 0.056+0.102im 0.007+0.015im 0.005+0.011im
        0.005+0.012im 0.007+0.015im 0.061+0.110im 0.006+0.013im
        0.004+0.010im 0.005+0.011im 0.006+0.013im 0.075+0.130im
    ]
    sequence = ComplexF64[1.0, cis(-2pi / 3), cis(2pi / 3)]
    Dict{String,Any}(
        "terminals" => ["a", "b", "c", "n"],
        "slack_voltage_pu" => vcat(sequence, 0.0 + 0.0im),
        "impedance_pu" => [impedance_1, impedance_2],
        "admittance_pu" => [inv(impedance_1), inv(impedance_2)],
        "current_limit_pu" => [fill(0.72, 4), fill(0.72, 4)],
        "load_direction_pu" => ComplexF64[0.70+0.14im, 0.55+0.12im, 0.42+0.09im],
        "voltage_magnitude_bounds_pu" => [0.88, 1.05],
    )
end

function power_flow_residual(voltage, served, data)
    total_current = sum(data["admittance_pu"]) * (data["slack_voltage_pu"] - voltage)
    phase_voltage = voltage[1:3] .- voltage[4]
    phase_power = phase_voltage .* conj.(total_current[1:3])
    complex_residual = vcat(
        phase_power .- served .* data["load_direction_pu"],
        sum(total_current),
    )
    vcat(real.(complex_residual), imag.(complex_residual))
end

function finite_difference_jacobian(residual, state; step=1.0e-7)
    base = residual(state)
    jacobian = zeros(length(base), length(state))
    for column in eachindex(state)
        increment = step * max(abs(state[column]), 1.0)
        perturbed = copy(state)
        perturbed[column] += increment
        jacobian[:, column] = (residual(perturbed) - base) / increment
    end
    jacobian
end

function independent_power_flow(served, start, data; tolerance=1.0e-10, max_iterations=50)
    state = vcat(real.(start), imag.(start))
    residual_function = x -> power_flow_residual(
        x[1:4] .+ im .* x[5:8], served, data,
    )
    residual_norm = Inf
    for iteration in 1:max_iterations
        residual = residual_function(state)
        residual_norm = norm(residual, Inf)
        if residual_norm <= tolerance
            return Dict{String,Any}(
                "converged" => true,
                "iterations" => iteration - 1,
                "residual_norm" => residual_norm,
                "voltage" => state[1:4] .+ im .* state[5:8],
            )
        end
        step = finite_difference_jacobian(residual_function, state) \ (-residual)
        accepted = false
        damping = 1.0
        for _ in 1:20
            candidate = state + damping * step
            if norm(residual_function(candidate), Inf) < residual_norm
                state = candidate
                accepted = true
                break
            end
            damping /= 2
        end
        accepted || break
    end
    Dict{String,Any}(
        "converged" => false,
        "iterations" => max_iterations,
        "residual_norm" => residual_norm,
        "voltage" => state[1:4] .+ im .* state[5:8],
    )
end

function independent_feasibility(served, start, data)
    power_flow = independent_power_flow(served, start, data)
    voltage = power_flow["voltage"]
    member_currents = [y * (data["slack_voltage_pu"] - voltage) for y in data["admittance_pu"]]
    phase_voltage = abs.(voltage[1:3] .- voltage[4])
    lower, upper = data["voltage_magnitude_bounds_pu"]
    current_margin = minimum(
        data["current_limit_pu"][line][conductor] - abs(member_currents[line][conductor])
        for line in 1:2, conductor in 1:4
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

"LinearAlgebra-only continuation and bisection reproduction of the source boundary."
function independently_reproduce_four_wire_boundary(
    ; data=default_four_wire_parallel_data(), scan_step=0.05, tolerance=1.0e-9,
)
    voltage = copy(data["slack_voltage_pu"])
    lower = independent_feasibility(0.0, voltage, data)
    upper = nothing
    scan = Dict{String,Any}[]
    served = scan_step
    while served <= 3.0
        point = independent_feasibility(served, voltage, data)
        push!(scan, point)
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
        point = independent_feasibility(midpoint, lower["voltage"], data)
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
        "scan_points" => length(scan),
    )
end

function four_wire_parallel_redundancy(; data=default_four_wire_parallel_data())
    certificate = certify_joint_componentwise_series_redundancy(
        data["admittance_pu"][1],
        data["current_limit_pu"][1],
        data["admittance_pu"][2],
        data["current_limit_pu"][2];
        conductor_names=data["terminals"],
        retained_member="l1",
        candidate_member="l2",
    )
    y1, y2 = data["admittance_pu"]
    ratio = dot(vec(y1), vec(y2)) / dot(vec(y1), vec(y1))
    certificate["best_scalar_ratio"] = Dict("re" => real(ratio), "im" => imag(ratio))
    certificate["scalar_proportionality_residual"] = opnorm(y2 - ratio * y1, Inf)
    certificate
end

function current_expressions(model, admittance, voltage_real, voltage_imag, slack)
    n = length(voltage_real)
    current_real = @expression(model, [c=1:n], sum(
        real(admittance[c, d]) * (real(slack[d]) - voltage_real[d]) -
        imag(admittance[c, d]) * (imag(slack[d]) - voltage_imag[d])
        for d in 1:n
    ))
    current_imag = @expression(model, [c=1:n], sum(
        imag(admittance[c, d]) * (real(slack[d]) - voltage_real[d]) +
        real(admittance[c, d]) * (imag(slack[d]) - voltage_imag[d])
        for d in 1:n
    ))
    current_real, current_imag
end

function solve_four_wire_parallel_formulation(kind::Symbol; data=default_four_wire_parallel_data())
    kind in (:source, :exact_lifted, :exact_pruned, :naive_aggregate) ||
        throw(ArgumentError("unknown formulation $kind"))
    if kind == :exact_pruned
        four_wire_parallel_redundancy(; data)["certified"] ||
            throw(ArgumentError("member-2 limits are not jointly certified redundant"))
    end
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
        re, im = current_expressions(
            model, admittance, voltage_real, voltage_imag, data["slack_voltage_pu"],
        )
        push!(member_real, re)
        push!(member_imag, im)
    end
    @expression(model, total_real[c=1:n], sum(member_real[line][c] for line in 1:2))
    @expression(model, total_imag[c=1:n], sum(member_imag[line][c] for line in 1:2))

    # Explicit neutral return and unbalanced phase-to-neutral constant-power equations.
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
    if kind == :naive_aggregate
        for conductor in 1:n
            limit = sum(data["current_limit_pu"][line][conductor] for line in 1:2)
            @constraint(model, total_real[conductor]^2 + total_imag[conductor]^2 <= limit^2)
        end
    else
        limited_lines = kind == :exact_pruned ? (1:1) : (1:2)
        for line in limited_lines, conductor in 1:n
            limit = data["current_limit_pu"][line][conductor]
            @constraint(model,
                member_real[line][conductor]^2 + member_imag[line][conductor]^2 <= limit^2
            )
        end
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
        "member_current_loading" => [
            abs.(member_currents[line]) ./ data["current_limit_pu"][line] for line in 1:2
        ],
        "neutral_kcl_residual_pu" => abs(sum(total_current)),
        "model_size" => Dict(
            "variables" => num_variables(model),
            "constraints" => sum(num_constraints(model, f, s) for (f, s) in list_of_constraint_types(model)),
        ),
    )
end

function matrix_records(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

function four_wire_parallel_certificate(; certificate_id="TR-PAR-006")
    data = default_four_wire_parallel_data()
    source = solve_four_wire_parallel_formulation(:source; data)
    lifted = solve_four_wire_parallel_formulation(:exact_lifted; data)
    pruned = solve_four_wire_parallel_formulation(:exact_pruned; data)
    naive = solve_four_wire_parallel_formulation(:naive_aggregate; data)
    redundancy = four_wire_parallel_redundancy(; data)
    independent = independently_reproduce_four_wire_boundary(; data)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "joint_componentwise_parallel_limit_pruning",
        "classification" => "exact_normalization",
        "source" => Dict(
            "model_category" => "nonproportional_three_phase_four_wire_parallel_member_ac_opf",
            "object_ids" => ["four_wire_parallel_l1", "four_wire_parallel_l2"],
            "detail" => Dict(
                "terminal_order" => data["terminals"],
                "impedance_pu" => [matrix_records(z) for z in data["impedance_pu"]],
                "current_limit_pu" => data["current_limit_pu"],
            ),
        ),
        "target" => Dict(
            "model_category" => "same_ac_opf_with_certified_redundant_limits_pruned",
            "object_ids" => ["four_wire_parallel_l1", "four_wire_parallel_l2"],
            "detail" => Dict("pruned_limit_owner" => "four_wire_parallel_l2"),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict("source" => ["U_j(a,b,c,n)", "I_l1ij", "I_l2ij"], "target" => ["U_j(a,b,c,n)", "recovered I_l1ij", "recovered I_l2ij"], "relation" => "member currents retain their original admittance recovery maps"),
            "constraints" => Dict("source" => ["both members' component current limits", "unbalanced AC power balance", "phase voltage bounds", "neutral KCL"], "target" => ["member-1 component current limits", "unchanged unbalanced AC power balance", "unchanged phase voltage bounds", "unchanged neutral KCL"], "relation" => "only jointly implied member-2 current limits are removed"),
            "decisions" => Dict("source" => ["served-load fraction alpha"], "target" => ["served-load fraction alpha"], "relation" => "identity"),
            "objectives" => Dict("source" => ["maximize alpha"], "target" => ["maximize alpha"], "relation" => "identity"),
            "units" => Dict("source" => ["per-unit voltage, current, and power"], "target" => ["per-unit voltage, current, and power"], "relation" => "identity"),
            "boundary_quantities" => Dict("source" => ["four conductor voltages and total terminal currents"], "target" => ["same four conductor voltages and total terminal currents"], "relation" => "identity"),
        ),
        "preconditions" => [
            "fixed nonsingular series admittances share the same four endpoint voltage coordinates",
            "member current limits are centered componentwise complex discs",
            "candidate-to-retained current recovery passes the exact complex-polydisc row-norm test",
        ],
        "preserves" => ["AC feasible set", "served-load objective", "member identities", "member-current recovery"],
        "forgets" => ["only member-2 component limits certified jointly implied"],
        "recovery_map" => Dict("member_currents" => "I_lij = Y_l * (U_i-U_j) for l in {1,2}"),
        "constraint_map" => Dict("member_2_limits" => "jointly implied by all member-1 component limits through I_l2ij=(Y_l2/Y_l1)I_l1ij at both ends"),
        "provenance" => Dict("implementation" => "experiments/transformations/FourWireParallelACDecision.jl", "solver" => "Ipopt through JuMP", "independent_primitive" => "impedance and admittance matrices use the BMOPFTools ordered four-wire line convention"),
        "evidence" => Dict(
            "redundancy" => redundancy,
            "source_solution" => source,
            "exact_lifted_solution" => lifted,
            "exact_pruned_solution" => pruned,
            "naive_aggregate_solution" => naive,
            "independent_source_boundary" => independent,
            "lifted_objective_gap" => lifted["objective_served_fraction"] - source["objective_served_fraction"],
            "pruned_objective_gap" => pruned["objective_served_fraction"] - source["objective_served_fraction"],
            "naive_objective_gap" => naive["objective_served_fraction"] - source["objective_served_fraction"],
            "independent_source_objective_gap" => independent["boundary_served_fraction"] - source["objective_served_fraction"],
        ),
    )
end

end

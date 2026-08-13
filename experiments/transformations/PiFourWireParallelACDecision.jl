module PiFourWireParallelACDecision

using Ipopt
using JuMP
using LinearAlgebra

include(joinpath(@__DIR__, "FourWireParallelACDecision.jl"))
using .FourWireParallelACDecision: default_four_wire_parallel_data
using .FourWireParallelACDecision.MulticonductorFlowLimitRedundancy

export default_pi_four_wire_data,
       independently_reproduce_pi_boundary,
       pi_four_wire_certificate,
       pi_four_wire_redundancy,
       solve_pi_four_wire_formulation

function default_pi_four_wire_data()
    data = default_four_wire_parallel_data()
    shunt_from_1 = Matrix(Diagonal(im .* [0.020, 0.018, 0.016, 0.010]))
    shunt_to_1 = Matrix(Diagonal(im .* [0.017, 0.015, 0.014, 0.009]))
    data["shunt_from_pu"] = [shunt_from_1, 0.20 .* shunt_from_1]
    data["shunt_to_pu"] = [shunt_to_1, 0.20 .* shunt_to_1]
    data
end

function member_primitive(data, line)
    pi_terminal_current_map(
        data["admittance_pu"][line],
        data["shunt_from_pu"][line],
        data["shunt_to_pu"][line],
    )
end

function pi_four_wire_redundancy(; data=default_pi_four_wire_data())
    terminals = data["terminals"]
    component_names = vcat(
        ["ij-$terminal" for terminal in terminals],
        ["ji-$terminal" for terminal in terminals],
    )
    certificate = certify_joint_componentwise_linear_redundancy(
        member_primitive(data, 1),
        vcat(data["current_limit_pu"][1], data["current_limit_pu"][1]),
        member_primitive(data, 2),
        vcat(data["current_limit_pu"][2], data["current_limit_pu"][2]);
        component_names,
        retained_member="l1",
        candidate_member="l2",
        scope="full nominal-pi terminal-current primitives with an invertible retained two-end map",
    )
    certificate["required_terminal_ends"] = ["ij", "ji"]
    certificate["terminal_order"] = terminals
    certificate
end

function member_currents(data, line, voltage_i, voltage_j)
    series = data["admittance_pu"][line]
    from = data["shunt_from_pu"][line]
    to = data["shunt_to_pu"][line]
    current_ij = (series + from) * voltage_i - series * voltage_j
    current_ji = -series * voltage_i + (series + to) * voltage_j
    current_ij, current_ji
end

function member_current_expressions(model, data, line, voltage_real, voltage_imag)
    n = length(voltage_real)
    primitive = member_primitive(data, line)
    slack = data["slack_voltage_pu"]
    full_real = Any[real(value) for value in slack]
    full_imag = Any[imag(value) for value in slack]
    append!(full_real, voltage_real)
    append!(full_imag, voltage_imag)
    current_real = @expression(model, [row=1:2n], sum(
        real(primitive[row, column]) * full_real[column] -
        imag(primitive[row, column]) * full_imag[column]
        for column in 1:2n
    ))
    current_imag = @expression(model, [row=1:2n], sum(
        imag(primitive[row, column]) * full_real[column] +
        real(primitive[row, column]) * full_imag[column]
        for column in 1:2n
    ))
    current_real, current_imag
end

function solve_pi_four_wire_formulation(kind::Symbol; data=default_pi_four_wire_data())
    kind in (:source, :exact_lifted, :exact_pruned, :naive_aggregate) ||
        throw(ArgumentError("unknown formulation $kind"))
    if kind == :exact_pruned
        pi_four_wire_redundancy(; data)["certified"] ||
            throw(ArgumentError("member-2 terminal limits are not certified redundant"))
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
    for line in 1:2
        real_current, imag_current = member_current_expressions(
            model, data, line, voltage_real, voltage_imag,
        )
        push!(member_real, real_current)
        push!(member_imag, imag_current)
    end
    # Current delivered into bus j is the negative of the member's ji current.
    @expression(model, delivered_real[c=1:n], -sum(member_real[line][n+c] for line in 1:2))
    @expression(model, delivered_imag[c=1:n], -sum(member_imag[line][n+c] for line in 1:2))
    @constraint(model, sum(delivered_real) == 0)
    @constraint(model, sum(delivered_imag) == 0)
    for phase in 1:3
        load_voltage_real = voltage_real[phase] - voltage_real[4]
        load_voltage_imag = voltage_imag[phase] - voltage_imag[4]
        direction = data["load_direction_pu"][phase]
        @constraint(model,
            served * real(direction) ==
            load_voltage_real * delivered_real[phase] +
            load_voltage_imag * delivered_imag[phase]
        )
        @constraint(model,
            served * imag(direction) ==
            load_voltage_imag * delivered_real[phase] -
            load_voltage_real * delivered_imag[phase]
        )
        lower, upper = data["voltage_magnitude_bounds_pu"]
        @constraint(model, load_voltage_real^2 + load_voltage_imag^2 >= lower^2)
        @constraint(model, load_voltage_real^2 + load_voltage_imag^2 <= upper^2)
    end

    if kind == :naive_aggregate
        for terminal_end in 0:1, conductor in 1:n
            index = terminal_end * n + conductor
            limit = sum(data["current_limit_pu"][line][conductor] for line in 1:2)
            @constraint(model,
                sum(member_real[line][index] for line in 1:2)^2 +
                sum(member_imag[line][index] for line in 1:2)^2 <= limit^2
            )
        end
    else
        limited_lines = kind == :exact_pruned ? (1:1) : (1:2)
        for line in limited_lines, terminal_end in 0:1, conductor in 1:n
            index = terminal_end * n + conductor
            limit = data["current_limit_pu"][line][conductor]
            @constraint(model,
                member_real[line][index]^2 + member_imag[line][index]^2 <= limit^2
            )
        end
    end
    @objective(model, Max, served)
    optimize!(model)

    voltage_j = value.(voltage_real) .+ im .* value.(voltage_imag)
    voltage_i = data["slack_voltage_pu"]
    currents = [member_currents(data, line, voltage_i, voltage_j) for line in 1:2]
    delivered = -sum(current[2] for current in currents)
    phase_voltage = voltage_j[1:3] .- voltage_j[4]
    phase_power = phase_voltage .* conj.(delivered[1:3])
    Dict{String,Any}(
        "formulation" => String(kind),
        "termination_status" => string(termination_status(model)),
        "objective_served_fraction" => objective_value(model),
        "phase_voltage_magnitude_pu" => abs.(phase_voltage),
        "neutral_voltage_magnitude_pu" => abs(voltage_j[4]),
        "phase_power_pu" => [Dict("p" => real(value), "q" => imag(value)) for value in phase_power],
        "member_current_magnitude_pu" => [Dict(
            "ij" => abs.(current[1]), "ji" => abs.(current[2]),
        ) for current in currents],
        "member_current_loading" => [Dict(
            "ij" => abs.(currents[line][1]) ./ data["current_limit_pu"][line],
            "ji" => abs.(currents[line][2]) ./ data["current_limit_pu"][line],
        ) for line in 1:2],
        "neutral_kcl_residual_pu" => abs(sum(delivered)),
        "model_size" => Dict(
            "variables" => num_variables(model),
            "constraints" => sum(num_constraints(model, f, s) for (f, s) in list_of_constraint_types(model)),
        ),
    )
end

function power_flow_residual(voltage, served, data)
    delivered = -sum(member_currents(data, line, data["slack_voltage_pu"], voltage)[2] for line in 1:2)
    phase_voltage = voltage[1:3] .- voltage[4]
    mismatch = vcat(
        phase_voltage .* conj.(delivered[1:3]) .- served .* data["load_direction_pu"],
        sum(delivered),
    )
    vcat(real.(mismatch), imag.(mismatch))
end

function independent_power_flow(served, start, data; tolerance=1.0e-10)
    state = vcat(real.(start), imag.(start))
    residual = x -> power_flow_residual(x[1:4] .+ im .* x[5:8], served, data)
    for iteration in 0:50
        value = residual(state)
        norm(value, Inf) <= tolerance && return (true, state[1:4] .+ im .* state[5:8], norm(value, Inf), iteration)
        jacobian = zeros(8, 8)
        for column in 1:8
            increment = 1.0e-7 * max(abs(state[column]), 1.0)
            point = copy(state); point[column] += increment
            jacobian[:, column] = (residual(point) - value) / increment
        end
        direction = jacobian \ (-value)
        accepted = false
        damping = 1.0
        for _ in 1:20
            point = state + damping * direction
            if norm(residual(point), Inf) < norm(value, Inf)
                state = point; accepted = true; break
            end
            damping /= 2
        end
        accepted || break
    end
    false, state[1:4] .+ im .* state[5:8], norm(residual(state), Inf), 50
end

function independent_feasibility(served, start, data)
    converged, voltage, residual, _ = independent_power_flow(served, start, data)
    currents = [member_currents(data, line, data["slack_voltage_pu"], voltage) for line in 1:2]
    current_margin = minimum(
        data["current_limit_pu"][line][conductor] - abs(currents[line][terminal_end][conductor])
        for line in 1:2, terminal_end in 1:2, conductor in 1:4
    )
    phase_voltage = abs.(voltage[1:3] .- voltage[4])
    lower, upper = data["voltage_magnitude_bounds_pu"]
    voltage_margin = min(minimum(phase_voltage .- lower), minimum(upper .- phase_voltage))
    Dict{String,Any}(
        "served_fraction" => served, "converged" => converged, "voltage" => voltage,
        "residual" => residual, "current_margin" => current_margin,
        "voltage_margin" => voltage_margin,
        "feasible" => converged && current_margin >= -1.0e-8 && voltage_margin >= -1.0e-8,
    )
end

function independently_reproduce_pi_boundary(; data=default_pi_four_wire_data(), tolerance=1.0e-9)
    voltage = copy(data["slack_voltage_pu"])
    lower = independent_feasibility(0.0, voltage, data)
    upper = nothing
    for served in 0.05:0.05:3.0
        point = independent_feasibility(served, voltage, data)
        point["converged"] && (voltage = point["voltage"])
        if !point["feasible"]
            upper = point; break
        end
        lower = point
    end
    upper === nothing && throw(ArgumentError("independent scan did not bracket a boundary"))
    upper["converged"] || throw(ArgumentError("boundary was preceded by power-flow failure"))
    for _ in 1:80
        upper["served_fraction"] - lower["served_fraction"] <= tolerance && break
        served = (lower["served_fraction"] + upper["served_fraction"]) / 2
        point = independent_feasibility(served, lower["voltage"], data)
        point["converged"] || throw(ArgumentError("power flow failed inside boundary bracket"))
        point["feasible"] ? (lower = point) : (upper = point)
    end
    Dict{String,Any}(
        "method" => "finite-difference damped Newton continuation and bisection",
        "boundary_served_fraction" => lower["served_fraction"],
        "upper_bracket_served_fraction" => upper["served_fraction"],
        "bracket_width" => upper["served_fraction"] - lower["served_fraction"],
        "boundary_current_margin_pu" => lower["current_margin"],
        "boundary_voltage_margin_pu" => lower["voltage_margin"],
        "power_flow_residual" => lower["residual"],
    )
end

function matrix_records(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]] for row in axes(matrix, 1)]
end

function pi_four_wire_certificate(; certificate_id="TR-PAR-007")
    data = default_pi_four_wire_data()
    source = solve_pi_four_wire_formulation(:source; data)
    lifted = solve_pi_four_wire_formulation(:exact_lifted; data)
    pruned = solve_pi_four_wire_formulation(:exact_pruned; data)
    naive = solve_pi_four_wire_formulation(:naive_aggregate; data)
    independent = independently_reproduce_pi_boundary(; data)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "full_nominal_pi_joint_component_limit_pruning",
        "classification" => "exact_normalization",
        "source" => Dict("model_category" => "nonproportional_three_phase_four_wire_parallel_nominal_pi_ac_opf", "object_ids" => ["pi_four_wire_l1", "pi_four_wire_l2"], "detail" => Dict("terminal_order" => data["terminals"], "impedance_pu" => [matrix_records(z) for z in data["impedance_pu"]], "shunt_from_pu" => [matrix_records(y) for y in data["shunt_from_pu"]], "shunt_to_pu" => [matrix_records(y) for y in data["shunt_to_pu"]], "current_limit_pu" => data["current_limit_pu"])),
        "target" => Dict("model_category" => "same_nominal_pi_ac_opf_with_certified_limits_pruned", "object_ids" => ["pi_four_wire_l1", "pi_four_wire_l2"], "detail" => Dict("pruned_limit_owner" => "pi_four_wire_l2")),
        "interfaces" => Dict(
            "state_variables" => Dict("source" => ["U_j(a,b,c,n)", "two-end member currents"], "target" => ["same voltages and recovered two-end currents"], "relation" => "identity on voltages and nominal-pi current recovery"),
            "constraints" => Dict("source" => ["both members' ij and ji component limits", "AC power balance", "voltage bounds", "neutral KCL"], "target" => ["member-1 ij and ji limits", "unchanged network constraints"], "relation" => "only certified member-2 limits are deleted"),
            "decisions" => Dict("source" => ["served fraction alpha"], "target" => ["served fraction alpha"], "relation" => "identity"),
            "objectives" => Dict("source" => ["maximize alpha"], "target" => ["maximize alpha"], "relation" => "identity"),
            "units" => Dict("source" => ["per-unit voltage, current, and power"], "target" => ["per-unit voltage, current, and power"], "relation" => "identity"),
            "boundary_quantities" => Dict("source" => ["both-end terminal currents including shunts"], "target" => ["same both-end terminal currents"], "relation" => "identity"),
        ),
        "preconditions" => ["fixed nominal-pi members share ordered endpoint coordinates", "retained full two-end terminal-current primitive is nonsingular", "component limits are centered complex discs", "all candidate rows pass the exact recovery-map row norm"],
        "preserves" => ["AC feasible set", "served-load objective", "member identity", "both-end series and shunt currents"],
        "forgets" => ["only member-2 terminal limits certified jointly implied"],
        "recovery_map" => Dict("terminal_currents" => "[I_lij;I_lji]=Yprim_l*[U_i;U_j]"),
        "constraint_map" => Dict("member_2_limits" => "jointly implied by all member-1 ij and ji component limits through the full primitive recovery map"),
        "provenance" => Dict("implementation" => "experiments/transformations/PiFourWireParallelACDecision.jl", "solver" => "Ipopt through JuMP", "primitive_cross_check" => "BMOPFTools line_yprim"),
        "evidence" => Dict(
            "redundancy" => pi_four_wire_redundancy(; data),
            "source_solution" => source, "exact_lifted_solution" => lifted,
            "exact_pruned_solution" => pruned, "naive_aggregate_solution" => naive,
            "independent_source_boundary" => independent,
            "lifted_objective_gap" => lifted["objective_served_fraction"] - source["objective_served_fraction"],
            "pruned_objective_gap" => pruned["objective_served_fraction"] - source["objective_served_fraction"],
            "naive_objective_gap" => naive["objective_served_fraction"] - source["objective_served_fraction"],
            "independent_source_objective_gap" => independent["boundary_served_fraction"] - source["objective_served_fraction"],
        ),
    )
end

end

module MulticonductorParallelACDecision

using Ipopt
using JuMP
using LinearAlgebra

export default_ac_parallel_data,
       closed_form_current_limited_optima,
       multiconductor_ac_certificate,
       proportional_parallel_redundancy,
       solve_multiconductor_ac_formulation

function default_ac_parallel_data()
    impedances = [
        ComplexF64[0.040+0.080im 0.010+0.020im; 0.010+0.020im 0.040+0.080im],
        ComplexF64[0.400+0.800im 0.100+0.200im; 0.100+0.200im 0.400+0.800im],
    ]
    Dict{String,Any}(
        "terminals" => ["a", "n"],
        "slack_voltage_pu" => ComplexF64[1.0+0.0im, 0.0+0.0im],
        "impedance_pu" => impedances,
        "admittance_pu" => inv.(impedances),
        "current_limit_pu" => [[0.60, 0.60], [0.60, 0.60]],
        "load_direction_pu" => 1.0+0.20im,
        "voltage_magnitude_bounds_pu" => [0.70, 1.05],
    )
end

"Certified current-limit redundancy for the recorded proportional pair."
function proportional_parallel_redundancy(; data=default_ac_parallel_data(), tolerance=1.0e-10)
    length(data["admittance_pu"]) == 2 ||
        throw(ArgumentError("the proportional redundancy check requires two members"))
    stronger = data["admittance_pu"][1]
    weaker = data["admittance_pu"][2]
    ratio = dot(vec(stronger), vec(weaker)) / dot(vec(stronger), vec(stronger))
    residual = opnorm(weaker - ratio * stronger, Inf)
    residual <= tolerance || throw(ArgumentError("member admittances are not proportional"))
    limit_ratio = minimum(
        data["current_limit_pu"][2][conductor] /
        data["current_limit_pu"][1][conductor]
        for conductor in eachindex(data["terminals"])
    )
    abs(ratio) <= limit_ratio + tolerance ||
        throw(ArgumentError("member 2 limits are not implied by member 1 limits"))
    Dict{String,Any}(
        "retained_member" => 1,
        "redundant_member" => 2,
        "current_map_ratio" => Dict("real" => real(ratio), "imag" => imag(ratio)),
        "maximum_proportionality_residual" => residual,
        "minimum_limit_ratio" => limit_ratio,
        "implication" =>
            "abs(I_l1ij,c)<=Imax_l1,c implies abs(I_l2ij,c)<=Imax_l2,c for every conductor c",
    )
end

"Loop impedance seen by a phase-to-neutral current `[I, -I]`."
loop_impedance(matrix) = matrix[1, 1] + matrix[2, 2] - matrix[1, 2] - matrix[2, 1]

"""
Closed-form optima for this proportional two-wire example.

For total-current magnitude `C`, fixed complex load direction `s`, and loop
impedance `z`, the receiving magnitude `v` satisfies
`1 = v^2 + 2*C*v*(r*p+x*q)/abs(s) + abs(z)^2*C^2`.
"""
function closed_form_current_limited_optima(; data=default_ac_parallel_data())
    loop_impedances = loop_impedance.(data["impedance_pu"])
    loop_admittances = inv.(loop_impedances)
    total_loop_admittance = sum(loop_admittances)
    equivalent_loop_impedance = inv(total_loop_admittance)
    member_fraction = abs.(loop_admittances ./ total_loop_admittance)
    source_limit = minimum(
        data["current_limit_pu"][line][1] / member_fraction[line]
        for line in eachindex(member_fraction)
    )
    naive_limit = sum(limit[1] for limit in data["current_limit_pu"])
    load_direction = data["load_direction_pu"]
    k = (real(equivalent_loop_impedance) * real(load_direction) +
         imag(equivalent_loop_impedance) * imag(load_direction)) / abs(load_direction)

    function optimum(current_limit)
        curvature = abs2(equivalent_loop_impedance) - k^2
        discriminant = 1 - current_limit^2 * curvature
        discriminant >= 0 || throw(ArgumentError("current-limited branch has no real voltage solution"))
        voltage_magnitude = -current_limit * k + sqrt(discriminant)
        served_fraction_derivative = (
            -2 * current_limit * k + sqrt(discriminant) -
            current_limit^2 * curvature / sqrt(discriminant)
        ) / abs(load_direction)
        Dict{String,Any}(
            "total_current_limit_pu" => current_limit,
            "load_voltage_magnitude_pu" => voltage_magnitude,
            "objective_served_fraction" =>
                current_limit * voltage_magnitude / abs(load_direction),
            "served_fraction_derivative_at_limit" => served_fraction_derivative,
        )
    end

    Dict{String,Any}(
        "equivalent_loop_impedance_pu" => Dict(
            "re" => real(equivalent_loop_impedance),
            "im" => imag(equivalent_loop_impedance),
        ),
        "member_current_fractions" => member_fraction,
        "source" => optimum(source_limit),
        "naive_aggregate" => optimum(naive_limit),
    )
end

function branch_current_expressions(model, admittance, voltage_real, voltage_imag, slack)
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

function start_member_currents!(current_real, current_imag, admittances, voltage, slack)
    for line in eachindex(admittances)
        current = admittances[line] * (slack - voltage)
        for conductor in eachindex(current)
            set_start_value(current_real[line, conductor], real(current[conductor]))
            set_start_value(current_imag[line, conductor], imag(current[conductor]))
        end
    end
end

function solution_dict(kind, model, served, voltage_real, voltage_imag, data)
    voltage = value.(voltage_real) .+ im .* value.(voltage_imag)
    slack = data["slack_voltage_pu"]
    member_currents = [admittance * (slack - voltage) for admittance in data["admittance_pu"]]
    total_current = sum(member_currents)
    load_voltage = voltage[1] - voltage[2]
    load_power = load_voltage * conj(total_current[1])
    Dict{String,Any}(
        "formulation" => String(kind),
        "termination_status" => string(termination_status(model)),
        "objective_served_fraction" => objective_value(model),
        "served_active_power_pu" => real(load_power),
        "served_reactive_power_pu" => imag(load_power),
        "receiving_voltage" => [
            Dict("terminal" => data["terminals"][k], "re" => real(voltage[k]), "im" => imag(voltage[k]))
            for k in eachindex(voltage)
        ],
        "load_voltage_magnitude_pu" => abs(load_voltage),
        "member_currents" => [
            [Dict(
                "terminal" => data["terminals"][k],
                "re" => real(current[k]),
                "im" => imag(current[k]),
                "magnitude_pu" => abs(current[k]),
                "limit_pu" => data["current_limit_pu"][line][k],
            ) for k in eachindex(current)]
            for (line, current) in enumerate(member_currents)
        ],
        "total_current" => [
            Dict("terminal" => data["terminals"][k], "re" => real(total_current[k]),
                 "im" => imag(total_current[k]), "magnitude_pu" => abs(total_current[k]))
            for k in eachindex(total_current)
        ],
        "current_balance_residual_pu" => abs(sum(total_current)),
        "model_size" => Dict(
            "variables" => num_variables(model),
            "constraints" => sum(num_constraints(model, function_type, set_type)
                for (function_type, set_type) in list_of_constraint_types(model)),
        ),
    )
end

"""
Solve a two-bus, two-conductor AC maximum-served-load problem.

`source` retains member-current variables; `naive_aggregate` uses summed
admittance and summed componentwise limits; `exact_lifted` uses the aggregate
terminal relation but recovers each member current for its original limit;
`exact_pruned` additionally removes only member-2 limits proved redundant by
the proportional current map.
"""
function solve_multiconductor_ac_formulation(kind::Symbol; data=default_ac_parallel_data())
    kind in (:source, :naive_aggregate, :exact_lifted, :exact_pruned) ||
        throw(ArgumentError("unknown formulation $kind"))
    terminals = data["terminals"]
    n = length(terminals)
    length(data["slack_voltage_pu"]) == n || throw(ArgumentError("slack arity mismatch"))
    all(size(admittance) == (n, n) for admittance in data["admittance_pu"]) ||
        throw(ArgumentError("admittance arity mismatch"))

    model = Model(Ipopt.Optimizer)
    set_silent(model)
    set_optimizer_attribute(model, "tol", 1.0e-9)
    set_optimizer_attribute(model, "constr_viol_tol", 1.0e-9)
    @variable(model, voltage_real[1:n])
    @variable(model, voltage_imag[1:n])
    @variable(model, served >= 0)
    start_voltage = ComplexF64[0.94-0.04im, 0.01-0.01im]
    for conductor in 1:n
        set_start_value(voltage_real[conductor], real(start_voltage[conductor]))
        set_start_value(voltage_imag[conductor], imag(start_voltage[conductor]))
    end
    set_start_value(served, 0.5)

    member_real = Any[]
    member_imag = Any[]
    if kind == :source
        n_line = length(data["admittance_pu"])
        @variable(model, current_real[1:n_line, 1:n])
        @variable(model, current_imag[1:n_line, 1:n])
        start_member_currents!(
            current_real, current_imag, data["admittance_pu"], start_voltage,
            data["slack_voltage_pu"],
        )
        for line in 1:n_line
            expression_real, expression_imag = branch_current_expressions(
                model, data["admittance_pu"][line], voltage_real, voltage_imag,
                data["slack_voltage_pu"],
            )
            @constraint(model, [conductor=1:n], current_real[line, conductor] == expression_real[conductor])
            @constraint(model, [conductor=1:n], current_imag[line, conductor] == expression_imag[conductor])
            push!(member_real, current_real[line, :])
            push!(member_imag, current_imag[line, :])
        end
        @expression(model, total_real[conductor=1:n], sum(current_real[line, conductor] for line in 1:n_line))
        @expression(model, total_imag[conductor=1:n], sum(current_imag[line, conductor] for line in 1:n_line))
    else
        aggregate_admittance = sum(data["admittance_pu"])
        total_real, total_imag = branch_current_expressions(
            model, aggregate_admittance, voltage_real, voltage_imag,
            data["slack_voltage_pu"],
        )
        if kind in (:exact_lifted, :exact_pruned)
            for admittance in data["admittance_pu"]
                expression_real, expression_imag = branch_current_expressions(
                    model, admittance, voltage_real, voltage_imag,
                    data["slack_voltage_pu"],
                )
                push!(member_real, expression_real)
                push!(member_imag, expression_imag)
            end
        end
    end

    @constraint(model, total_real[1] + total_real[2] == 0)
    @constraint(model, total_imag[1] + total_imag[2] == 0)
    load_voltage_real = voltage_real[1] - voltage_real[2]
    load_voltage_imag = voltage_imag[1] - voltage_imag[2]
    load_direction = data["load_direction_pu"]
    @constraint(model,
        served * real(load_direction) ==
        load_voltage_real * total_real[1] + load_voltage_imag * total_imag[1]
    )
    @constraint(model,
        served * imag(load_direction) ==
        load_voltage_imag * total_real[1] - load_voltage_real * total_imag[1]
    )
    voltage_min, voltage_max = data["voltage_magnitude_bounds_pu"]
    @constraint(model, load_voltage_real^2 + load_voltage_imag^2 >= voltage_min^2)
    @constraint(model, load_voltage_real^2 + load_voltage_imag^2 <= voltage_max^2)

    if kind in (:source, :exact_lifted, :exact_pruned)
        limited_lines = kind == :exact_pruned ? (1:1) : eachindex(member_real)
        for line in limited_lines, conductor in 1:n
            limit = data["current_limit_pu"][line][conductor]
            @constraint(model,
                member_real[line][conductor]^2 + member_imag[line][conductor]^2 <= limit^2
            )
        end
    else
        aggregate_limit = [sum(limit[conductor] for limit in data["current_limit_pu"])
                           for conductor in 1:n]
        @constraint(model, [conductor=1:n],
            total_real[conductor]^2 + total_imag[conductor]^2 <= aggregate_limit[conductor]^2
        )
    end

    @objective(model, Max, served)
    optimize!(model)
    solution_dict(kind, model, served, voltage_real, voltage_imag, data)
end

function complex_matrix_rows(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

function multiconductor_ac_certificate(; certificate_id="TR-PAR-004")
    data = default_ac_parallel_data()
    source = solve_multiconductor_ac_formulation(:source; data)
    naive = solve_multiconductor_ac_formulation(:naive_aggregate; data)
    exact = solve_multiconductor_ac_formulation(:exact_lifted; data)
    pruned = solve_multiconductor_ac_formulation(:exact_pruned; data)
    closed_form = closed_form_current_limited_optima(; data)
    redundancy = proportional_parallel_redundancy(; data)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "multiconductor_parallel_admittance_with_summed_current_limits",
        "classification" => "outer_relaxation",
        "source" => Dict(
            "model_category" => "two_bus_multiconductor_ac_parallel_member_opf",
            "object_ids" => ["ac_parallel_member_l1", "ac_parallel_member_l2"],
            "detail" => Dict(
                "terminal_order" => data["terminals"],
                "impedance_pu" => [complex_matrix_rows(matrix) for matrix in data["impedance_pu"]],
                "current_limit_pu" => data["current_limit_pu"],
                "load_direction_pu" => Dict(
                    "re" => real(data["load_direction_pu"]),
                    "im" => imag(data["load_direction_pu"]),
                ),
            ),
        ),
        "target" => Dict(
            "model_category" => "naive_multiconductor_ac_parallel_aggregate_opf",
            "object_ids" => ["naive_ac_parallel_aggregate_l"],
            "detail" => Dict(
                "aggregate_admittance_pu" => complex_matrix_rows(sum(data["admittance_pu"])),
                "summed_current_limit_pu" => [sum(limit[k] for limit in data["current_limit_pu"])
                                              for k in eachindex(data["terminals"])],
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["U_j conductor phasors", "I_lij member conductor phasors"],
                "target" => ["U_j conductor phasors", "I_eqij aggregate conductor phasor"],
                "relation" => "aggregate current is the member sum and member currents recover from U_i-U_j",
            ),
            "constraints" => Dict(
                "source" => ["member conductor current circles", "voltage magnitude bounds", "AC power balance"],
                "target" => ["summed aggregate current circles", "voltage magnitude bounds", "AC power balance"],
                "relation" => "the naive target replaces member circles; the exact lift retains recovered member circles",
            ),
            "decisions" => Dict(
                "source" => ["served-load fraction alpha"], "target" => ["served-load fraction alpha"],
                "relation" => "the same scalar load decision is optimized",
            ),
            "objectives" => Dict(
                "source" => ["maximize alpha"], "target" => ["maximize alpha"],
                "relation" => "objective is unchanged while feasibility differs",
            ),
            "units" => Dict(
                "source" => ["per-unit voltage", "per-unit current", "per-unit power"],
                "target" => ["per-unit voltage", "per-unit current", "per-unit power"],
                "relation" => "the same per-unit bases are used",
            ),
            "boundary_quantities" => Dict(
                "source" => ["U_i", "U_j", "sum of member terminal currents"],
                "target" => ["U_i", "U_j", "aggregate terminal current"],
                "relation" => "complex terminal current-voltage behaviour is equal before constraints",
            ),
        ),
        "preconditions" => [
            "parallel members share both endpoint terminal-voltage coordinates",
            "each member has a linear complex multiconductor series relation",
            "the receiving load is a phase-to-neutral constant-power direction scaled by one decision",
        ],
        "preserves" => ["unconstrained_complex_terminal_current_voltage_relation"],
        "forgets" => ["member_current_limits", "member_identity", "independent_member_current_state"],
        "recovery_map" => Dict(
            "member_currents" => "I_lij = Y_l * (U_i - U_j)",
        ),
        "constraint_map" => Dict(
            "naive_aggregate" => "abs(sum_l I_lij,c) <= sum_l I_max_l,c for each conductor c",
            "exact_lifted" => "recover every I_lij and retain abs(I_lij,c) <= I_max_l,c",
            "exact_pruned" => "after proving I_l2ij=0.1*I_l1ij with equal limits, retain only member-1 current circles while keeping both recovery maps",
        ),
        "provenance" => Dict(
            "solver" => "Ipopt through JuMP",
            "implementation" => "experiments/transformations/MulticonductorParallelACDecision.jl",
            "coordinate_system" => "per-unit rectangular complex conductor voltages and currents",
        ),
        "evidence" => Dict(
            "source_solution" => source,
            "naive_aggregate_solution" => naive,
            "exact_lifted_solution" => exact,
            "exact_pruned_solution" => pruned,
            "certified_redundancy" => redundancy,
            "naive_served_fraction_gap" =>
                naive["objective_served_fraction"] - source["objective_served_fraction"],
            "exact_lifted_served_fraction_gap" =>
                exact["objective_served_fraction"] - source["objective_served_fraction"],
            "exact_pruned_served_fraction_gap" =>
                pruned["objective_served_fraction"] - source["objective_served_fraction"],
            "closed_form_current_limited_check" => closed_form,
            "source_solver_minus_closed_form" => source["objective_served_fraction"] -
                closed_form["source"]["objective_served_fraction"],
            "naive_solver_minus_closed_form" => naive["objective_served_fraction"] -
                closed_form["naive_aggregate"]["objective_served_fraction"],
        ),
    )
end

end

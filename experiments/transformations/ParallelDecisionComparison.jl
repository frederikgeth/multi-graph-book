module ParallelDecisionComparison

using Ipopt
using JuMP

export parallel_decision_certificate, solve_parallel_formulation

function solved_values(model, delta, served, flows)
    Dict{String,Any}(
        "termination_status" => string(termination_status(model)),
        "objective_MW" => objective_value(model),
        "served_power_MW" => value(served),
        "angle_difference_rad" => value(delta),
        "member_flows_MW" => flows === nothing ? nothing : value.(flows),
    )
end

"Solve a two-bus maximum-served-load problem in one of three formulations."
function solve_parallel_formulation(kind::Symbol; susceptance=[1000.0, 100.0], limit=[100.0, 100.0])
    length(susceptance) == length(limit) || throw(ArgumentError("member data lengths differ"))
    all(susceptance .> 0) || throw(ArgumentError("susceptances must be positive"))
    all(limit .>= 0) || throw(ArgumentError("limits must be nonnegative"))

    model = Model(Ipopt.Optimizer)
    set_silent(model)
    @variable(model, delta >= 0)
    @variable(model, served >= 0)

    if kind == :source
        @variable(model, flow[eachindex(susceptance)] >= 0)
        @constraint(model, [k in eachindex(susceptance)], flow[k] == susceptance[k] * delta)
        @constraint(model, [k in eachindex(limit)], flow[k] <= limit[k])
        @constraint(model, served == sum(flow))
        @objective(model, Max, served)
        optimize!(model)
        return solved_values(model, delta, served, flow)
    elseif kind == :naive_aggregate
        @constraint(model, served == sum(susceptance) * delta)
        @constraint(model, served <= sum(limit))
        @objective(model, Max, served)
        optimize!(model)
        return solved_values(model, delta, served, nothing)
    elseif kind == :exact_lifted
        @variable(model, recovered_flow[eachindex(susceptance)] >= 0)
        @constraint(model, served == sum(susceptance) * delta)
        @constraint(model, [k in eachindex(susceptance)], recovered_flow[k] == susceptance[k] * delta)
        @constraint(model, [k in eachindex(limit)], recovered_flow[k] <= limit[k])
        @objective(model, Max, served)
        optimize!(model)
        return solved_values(model, delta, served, recovered_flow)
    end
    throw(ArgumentError("unknown formulation $kind"))
end

function parallel_decision_certificate(; certificate_id="TR-PAR-003")
    susceptance = [1000.0, 100.0]
    limit = [100.0, 100.0]
    source = solve_parallel_formulation(:source; susceptance, limit)
    naive = solve_parallel_formulation(:naive_aggregate; susceptance, limit)
    exact = solve_parallel_formulation(:exact_lifted; susceptance, limit)
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "parallel_admittance_with_summed_rating",
        "classification" => "outer_relaxation",
        "source" => Dict(
            "model_category" => "two_bus_parallel_member_decision_model",
            "object_ids" => ["parallel_member_l1", "parallel_member_l2"],
            "detail" => Dict(
                "susceptance_MW_per_rad" => susceptance,
                "flow_limit_MW" => limit,
            ),
        ),
        "target" => Dict(
            "model_category" => "two_bus_naive_aggregate_decision_model",
            "object_ids" => ["naive_parallel_aggregate_l"],
            "detail" => Dict(
                "susceptance_MW_per_rad" => sum(susceptance),
                "flow_limit_MW" => sum(limit),
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["delta_ij", "f_l1ij", "f_l2ij"],
                "target" => ["delta_ij", "f_eqij"],
                "relation" => "aggregate flow is the sum of member flows; member flows recover from delta_ij",
            ),
            "constraints" => Dict(
                "source" => ["member flow limits"], "target" => ["summed aggregate flow limit"],
                "relation" => "the naive target drops member limits; the exact lift retains them",
            ),
            "decisions" => Dict(
                "source" => ["served power"], "target" => ["served power"],
                "relation" => "the same served-power decision is optimized in all formulations",
            ),
            "objectives" => Dict(
                "source" => ["maximize served power"], "target" => ["maximize served power"],
                "relation" => "objective expression is identical but feasible sets differ",
            ),
            "units" => Dict(
                "source" => ["MW", "rad"], "target" => ["MW", "rad"],
                "relation" => "units and bases are unchanged",
            ),
            "boundary_quantities" => Dict(
                "source" => ["delta_ij", "sum of member terminal flows"],
                "target" => ["delta_ij", "aggregate terminal flow"],
                "relation" => "the unconstrained terminal power-angle relation is equal",
            ),
        ),
        "preconditions" => [
            "parallel members have common endpoint voltage coordinates",
            "member flows are linear in the common angle difference",
            "member susceptances are positive",
        ],
        "preserves" => ["unconstrained_terminal_power_angle_relation"],
        "forgets" => ["member_flow_limits", "member_identity", "independent_member_flow_state"],
        "recovery_map" => Dict(
            "member_flows" => "f_lij = b_l * delta_ij",
        ),
        "constraint_map" => Dict(
            "naive_aggregate" => "sum_l f_lij <= sum_l f_max_l",
            "exact_lifted" => "retain f_lij = b_l * delta_ij and f_lij <= f_max_l for every l",
        ),
        "provenance" => Dict(
            "solver" => "Ipopt through JuMP",
            "implementation" => "experiments/transformations/ParallelDecisionComparison.jl",
        ),
        "evidence" => Dict(
            "source_solution" => source,
            "naive_aggregate_solution" => naive,
            "exact_lifted_solution" => exact,
            "naive_objective_gap_MW" => naive["objective_MW"] - source["objective_MW"],
            "exact_lifted_objective_gap_MW" => exact["objective_MW"] - source["objective_MW"],
        ),
    )
end

end

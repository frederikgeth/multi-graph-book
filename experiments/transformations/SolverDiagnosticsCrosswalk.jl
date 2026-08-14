module SolverDiagnosticsCrosswalk

using BMOPFTools
using DiffOpt
using JSON3
using JuMP
using Ipopt
using LinearAlgebra

export evaluate_crosswalk, evaluate_solver_callback_probe, evaluate_diffopt_sensitivity,
       parallel_diffopt_networks, evaluate_diffopt_parallel_comparison

function read_json(path)
    JSON3.read(read(path, String), Dict{String,Any})
end

"Build a regular JuMP mirror and export its model-level nonlinear Jacobian structure."
function native_nlp_jacobian_summary(net)
    model = JuMP.Model(Ipopt.Optimizer)
    JuMP.set_silent(model)
    ctx = BMOPFTools.build_opf_model(net; model=model, per_unit=false,
                                     add_objective=false, softplus=:builtin,
                                     verbose=false)
    theta = JuMP.@variable(model, theta_I in JuMP.Parameter(10.0))
    cr = JuMP.@variable(model, base_name="custom_cr")
    ci = JuMP.@variable(model, base_name="custom_ci")
    cr_key = BMOPFTools.OpfModelKey(:variable, :custom_current_r, ("bus1", "1"))
    BMOPFTools.register_opf_object!(ctx, cr_key, cr)
    BMOPFTools.bind_opf_parameter!(ctx,
        BMOPFTools.OpfModelKey(:parameter, :terminal_current, ("bus1", "1")),
        theta, cr_key; aliases=[:theta_I], input_unit=:A, working_unit=:A)
    JuMP.@constraint(model, ci == 0.0)
    BMOPFTools.add_terminal_injection!(ctx, "bus1", "1", cr, ci)
    JuMP.@objective(model, Min, 0.0)
    BMOPFTools.enforce_kcl!(ctx)
    evaluator = JuMP.NLPEvaluator(model)
    JuMP.MOI.initialize(evaluator, [:Jac])
    constraint_count = sum(length(JuMP.all_constraints(model, F, S))
                           for (F, S) in JuMP.list_of_constraint_types(model))
    support_nonzeros = 0
    for (F, S) in JuMP.list_of_constraint_types(model)
        for constraint in JuMP.all_constraints(model, F, S)
            function_expression = JuMP.constraint_object(constraint).func
            variables = Set{Any}()
            if function_expression isa JuMP.QuadExpr
                union!(variables, keys(function_expression.aff.terms))
                for pair in keys(function_expression.terms)
                    push!(variables, pair.a)
                    push!(variables, pair.b)
                end
            elseif function_expression isa JuMP.AffExpr
                union!(variables, keys(function_expression.terms))
            end
            support_nonzeros += length(variables)
        end
    end
    (; rows = constraint_count,
       nonzeros = support_nonzeros,
       evaluator_structure_nonzeros = length(JuMP.MOI.jacobian_structure(evaluator)),
       source = "regular JuMP mirror / native affine-quadratic variable support plus JuMP.NLPEvaluator")
end

"""Exercise BMOPFTools' public checked-KKT callback on a staged OPF context.

The callback is the supported boundary for DiffOpt integration. This probe does
not pretend that BMOPFTools exports Ipopt's internal KKT matrix or ordering;
those remain downstream/solver observations.
"""
function evaluate_solver_callback_probe(net)
    model = JuMP.Model(Ipopt.Optimizer)
    JuMP.set_silent(model)
    ctx = BMOPFTools.build_opf_model(net; model=model, per_unit=false,
                                     add_objective=false, verbose=false)
    BMOPFTools.enforce_kcl!(ctx)
    JuMP.optimize!(model)
    status = string(JuMP.termination_status(model))
    differentiability = BMOPFTools.opf_differentiability_report(ctx)
    callback = BMOPFTools.opf_checked_kkt_factorization(ctx)
    matrix = Matrix(Diagonal(ones(Float64, 6)))
    factorization = callback(matrix, nothing)
    diagnostic = BMOPFTools.opf_kkt_diagnostic(ctx)
    rejected = false
    try
        callback(Diagonal(Float64[1, 1, 1, 1, 1, 1e-14]), nothing)
    catch error
        rejected = error isa BMOPFTools.OpfDifferentiationError
    end
    (; solver_status = status,
       callback_matrix_dimension = size(matrix, 1),
       callback_factorization_type = string(typeof(factorization)),
       diagnostic_status = String(diagnostic.status),
       diagnostic_dimension = diagnostic.dimension,
       diagnostic_pivot_ratio = diagnostic.pivot_ratio,
       diagnostic_tolerance = diagnostic.tolerance,
       rejected_near_singular_probe = rejected,
       callback_api = "BMOPFTools.opf_checked_kkt_factorization",
       diagnostic_api = "BMOPFTools.opf_kkt_diagnostic")
end

"""Run one parameterized IVR-EN sensitivity through DiffOpt and BMOPFTools.

The network is intentionally a two-bus, one-line fixture. The custom current
injection is parameterized by ``theta``; analytically, the receiving voltage
changes by ``0.5 theta`` in SI units. The test compares DiffOpt's forward
sensitivity with a central finite difference and records the checked-KKT
diagnostic installed through the public callback.
"""
function evaluate_diffopt_sensitivity(net)
    model = DiffOpt.nonlinear_diff_model(Ipopt.Optimizer)
    JuMP.set_silent(model)
    ctx = BMOPFTools.build_opf_model(net; model=model, per_unit=false,
                                     add_objective=false, softplus=:builtin,
                                     verbose=false)
    theta = JuMP.@variable(model, theta_I in JuMP.Parameter(10.0))
    cr = JuMP.@variable(model, base_name="custom_cr")
    ci = JuMP.@variable(model, base_name="custom_ci")
    cr_key = BMOPFTools.OpfModelKey(:variable, :custom_current_r, ("bus1", "1"))
    BMOPFTools.register_opf_object!(ctx, cr_key, cr)
    BMOPFTools.bind_opf_parameter!(ctx,
        BMOPFTools.OpfModelKey(:parameter, :terminal_current, ("bus1", "1")),
        theta, cr_key; aliases=[:theta_I], input_unit=:A, working_unit=:A)
    JuMP.@constraint(model, ci == 0.0)
    BMOPFTools.add_terminal_injection!(ctx, "bus1", "1", cr, ci)
    JuMP.@objective(model, Min, 0.0)
    BMOPFTools.enforce_kcl!(ctx)
    variable_order = [begin
        label = JuMP.name(variable)
        isempty(label) ? "variable[$index]" : label
    end for (index, variable) in enumerate(JuMP.all_variables(model))]
    fixed_variable_count = count(JuMP.is_fixed, JuMP.all_variables(model))
    constraint_order = String[]
    for (F, S) in JuMP.list_of_constraint_types(model)
        for (ordinal, constraint) in enumerate(JuMP.all_constraints(model, F, S))
            label = JuMP.name(constraint)
            isempty(label) && (label = "$(F)/$(S)[$ordinal]")
            push!(constraint_order, label)
        end
    end
    JuMP.optimize!(model)
    status = string(JuMP.termination_status(model))
    differentiability = BMOPFTools.opf_differentiability_report(ctx)
    vr = BMOPFTools.opf_object(ctx,
        BMOPFTools.OpfModelKey(:variable, :vr, ("bus1", "1")))
    base_voltage = JuMP.value(vr)
    checked_callback = BMOPFTools.opf_checked_kkt_factorization(ctx)
    captured = Ref{Any}(nothing)
    callback_invocations = Ref(0)
    capturing_callback = function (matrix, diffopt_model)
        captured[] = matrix
        callback_invocations[] += 1
        checked_callback(matrix, diffopt_model)
    end
    JuMP.MOI.set(model, DiffOpt.NonLinearKKTJacobianFactorization(), capturing_callback)
    DiffOpt.set_forward_parameter(model, theta, 1.0)
    DiffOpt.forward_differentiate!(model)
    forward = DiffOpt.get_forward_variable(model, vr)
    diagnostic = BMOPFTools.opf_kkt_diagnostic(ctx)
    captured_matrix = captured[]
    captured_matrix === nothing && error("DiffOpt did not invoke the KKT factorization callback")
    captured_rows, captured_columns = size(captured_matrix)
    captured_nonzeros = count(!iszero, captured_matrix)
    declared_kkt_block = length(variable_order) - fixed_variable_count + length(constraint_order)
    DiffOpt.empty_input_sensitivities!(model)
    theta0 = JuMP.parameter_value(theta)
    h = 1.0e-3
    JuMP.set_parameter_value(theta, theta0 + h)
    JuMP.optimize!(model)
    v_plus = JuMP.value(vr)
    JuMP.set_parameter_value(theta, theta0 - h)
    JuMP.optimize!(model)
    v_minus = JuMP.value(vr)
    central = (v_plus - v_minus) / (2h)
    native_jacobian = native_nlp_jacobian_summary(net)
    (; solver_status = status,
       base_voltage,
       forward_sensitivity = forward,
       central_sensitivity = central,
       sensitivity_residual = abs(forward - central),
       diagnostic_status = String(diagnostic.status),
       diagnostic_dimension = diagnostic.dimension,
       diagnostic_pivot_ratio = diagnostic.pivot_ratio,
       differentiability_ready = differentiability.ready,
       differentiability_lifecycle = String(differentiability.lifecycle),
       differentiability_termination_status = differentiability.termination_status,
       inequality_constraint_count = differentiability.inequality_constraints,
       active_constraints = differentiability.active_constraints,
       near_active_constraints = differentiability.near_active_constraints,
       weakly_active_constraints = differentiability.weakly_active_constraints,
       violated_constraints = differentiability.violated_constraints,
       minimum_inactive_slack = differentiability.minimum_inactive_slack,
       differentiability_qualifications = differentiability.qualifications,
       callback_invocations = callback_invocations[],
       captured_kkt_rows = captured_rows,
       captured_kkt_columns = captured_columns,
       captured_kkt_nonzeros = captured_nonzeros,
       captured_kkt_density = captured_nonzeros / (captured_rows * captured_columns),
       captured_kkt_source = "DiffOpt NonLinearKKTJacobianFactorization callback",
       native_nlp_jacobian_rows = native_jacobian.rows,
       native_nlp_jacobian_nonzeros = native_jacobian.nonzeros,
       native_nlp_evaluator_structure_nonzeros = native_jacobian.evaluator_structure_nonzeros,
       native_nlp_jacobian_source = native_jacobian.source,
       native_nlp_export_is_solver_internal = false,
       model_variable_count = length(variable_order),
       model_fixed_variable_count = fixed_variable_count,
       model_constraint_count = length(constraint_order),
       kkt_unaccounted_rows = captured_rows - declared_kkt_block,
       model_variable_order = variable_order,
       model_constraint_order = constraint_order,
       kkt_ordering_basis = "JuMP non-fixed variable order followed by declared JuMP constraint order; fixed variables are excluded by the solver, and remaining callback rows are DiffOpt/solver-internal rather than independently row-labelled",
       callback_api = "BMOPFTools.opf_checked_kkt_factorization",
       differentiation_api = "DiffOpt.forward_differentiate!")
end

"Return a two-parallel-line source and its scalar exact equivalent fixture."
function parallel_diffopt_networks()
    source = parse_bmopf("""
    {"bus":{
        "sourcebus":{"terminal_names":["1","n"],"perfectly_grounded_terminals":["n"]},
        "bus1":{"terminal_names":["1","n"],"perfectly_grounded_terminals":["n"]}},
     "voltage_source":{"vs":{"bus":"sourcebus","terminal_map":["1"],"v_magnitude":[1000.0],"v_angle":[0.0]}},
     "linecode":{"lc":{"R_series_1_1":0.5}},
     "line":{"l1":{"bus_from":"sourcebus","bus_to":"bus1","terminal_map_from":["1"],"terminal_map_to":["1"],"linecode":"lc","length":1.0},
             "l2":{"bus_from":"sourcebus","bus_to":"bus1","terminal_map_from":["1"],"terminal_map_to":["1"],"linecode":"lc","length":1.0}}}
    """; from_string=true)
    reduced = parse_bmopf("""
    {"bus":{
        "sourcebus":{"terminal_names":["1","n"],"perfectly_grounded_terminals":["n"]},
        "bus1":{"terminal_names":["1","n"],"perfectly_grounded_terminals":["n"]}},
     "voltage_source":{"vs":{"bus":"sourcebus","terminal_map":["1"],"v_magnitude":[1000.0],"v_angle":[0.0]}},
     "linecode":{"lc":{"R_series_1_1":0.25}},
     "line":{"l_eq":{"bus_from":"sourcebus","bus_to":"bus1","terminal_map_from":["1"],"terminal_map_to":["1"],"linecode":"lc","length":1.0}}}
    """; from_string=true)
    (; source, reduced)
end

"Compare source and scalar-equivalent parallel-line OPF sensitivities and KKT structure."
function evaluate_diffopt_parallel_comparison(source_net, reduced_net)
    source = evaluate_diffopt_sensitivity(source_net)
    reduced = evaluate_diffopt_sensitivity(reduced_net)
    checks = Dict(
        "source_and_reduced_solve" => source.solver_status in ("LOCALLY_SOLVED", "OPTIMAL") &&
            reduced.solver_status in ("LOCALLY_SOLVED", "OPTIMAL"),
        "sensitivity_is_preserved" => abs(source.forward_sensitivity - reduced.forward_sensitivity) ≤ 1.0e-7,
        "finite_difference_is_preserved" => source.sensitivity_residual ≤ 1.0e-7 &&
            reduced.sensitivity_residual ≤ 1.0e-7,
        "kkt_structure_changes" => source.captured_kkt_rows != reduced.captured_kkt_rows ||
            source.captured_kkt_nonzeros != reduced.captured_kkt_nonzeros,
        "native_jacobian_support_changes" => source.native_nlp_jacobian_nonzeros !=
            reduced.native_nlp_jacobian_nonzeros,
    )
    (; source, reduced,
       checks,
       interpretation = "Scoped exact scalar parallel-line fixture: the equivalent resistance preserves the tested voltage sensitivity while changing the solver KKT structure. This does not establish equivalence for multiconductor, nonlinear, or decision-rich models.")
end

function evaluate_crosswalk(generated_directory)
    ybus = read_json(joinpath(generated_directory, "ybus-jacobian-witness.json"))
    kkt = read_json(joinpath(generated_directory, "nonlinear-kkt-witness.json"))
    source = kkt["source"]
    natural = source["kkt"]["orders"]["natural"]
    constraints_first = source["kkt"]["orders"]["constraints_first"]
    checks = Dict(
        "ybus_uses_bmopftools_builders" => ybus["package_contract"]["builder"] == "BMOPFTools.ybus_passive" &&
            ybus["package_contract"]["linearized_builder"] == "BMOPFTools.ybus_linearized",
        "realified_jacobian_has_declared_dimension" => ybus["checks"]["realification_dimension_doubles"] === true,
        "kkt_source_and_aggregate_are_both_present" => haskey(kkt, "source") && haskey(kkt, "aggregate"),
        "ordering_diagnostics_are_recorded" => haskey(source["kkt"]["orders"], "natural") &&
            haskey(source["kkt"]["orders"], "constraints_first"),
        "ordering_changes_symbolic_fill" => natural["fill_edges"] != constraints_first["fill_edges"],
        "crosswalk_retains_node_order" => !isempty(ybus["node_order"]),
    )
    (; witness_id = "NUM-SOLVER-CROSSWALK-001",
       model_scope = "package-level BMOPFTools Ybus/Jacobian plus finite-difference nonlinear KKT diagnostics",
       source_witnesses = [ybus["witness_id"], kkt["witness_id"]],
       node_order = ybus["node_order"],
       diagnostic_layers = [
           "physical fixture node/terminal order",
           "BMOPFTools passive and constant-Z linearized Ybus",
           "realified current Jacobian",
           "finite-difference nonlinear residual Jacobian",
           "symbolic KKT graph under declared elimination orders",
       ],
       solver_boundary = Dict(
           "package_level_builders" => ["BMOPFTools.ybus_passive", "BMOPFTools.ybus_linearized"],
           "solver_internal_kkt_export" => false,
           "checked_kkt_callback_api" => "BMOPFTools.opf_checked_kkt_factorization",
           "required_next_export" => "capture the solver-provided KKT matrix, linear-solver ordering, pivot/inertia, and factorization statistics",
       ),
       comparisons = Dict(
           "ybus_realified_dimension" => ybus["realified_current_jacobian"]["rows"],
           "kkt_source_dimension" => source["kkt"]["dimension"],
           "kkt_aggregate_dimension" => kkt["aggregate"]["kkt"]["dimension"],
           "source_natural_fill_edges" => natural["fill_edges"],
           "source_constraints_first_fill_edges" => constraints_first["fill_edges"],
           "source_natural_factor_edges" => natural["factor_edges"],
           "source_constraints_first_factor_edges" => constraints_first["factor_edges"],
       ),
       checks,
       interpretation = "This crosswalk composes package-level electrical matrix diagnostics with a symbolic nonlinear KKT witness. It does not claim an Ipopt or other solver-internal derivative or factorization export.")
end

end

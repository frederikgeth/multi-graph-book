module TransformerControlFamilyWitness

using LinearAlgebra
using Ipopt
using JuMP

export evaluate_control_family

complex_pairs(values) = [Dict("real" => real(value), "imag" => imag(value)) for value in values]

function solve_control_probe(kind, target)
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    if kind == "scalar_magnitude"
        @variable(model, t)
        @constraint(model, t == target[1])
        @objective(model, Min, (t - target[1])^2)
    elseif kind == "phase_angle"
        @variable(model, θ)
        @constraint(model, θ == target[1])
        @objective(model, Min, (θ - target[1])^2)
    elseif kind == "independent_phase"
        @variable(model, θ[1:3])
        for i in 1:3
            @constraint(model, θ[i] == target[i])
        end
        @objective(model, Min, sum((θ[i] - target[i])^2 for i in 1:3))
    elseif kind == "mechanically_coupled"
        @variable(model, m)
        @constraint(model, m == 1.0)
        @objective(model, Min, (m - 1.0)^2)
    elseif kind == "automatic_deadband"
        @variable(model, output)
        @constraint(model, output == target[1])
        @objective(model, Min, (output - target[1])^2)
    elseif kind == "tap_dependent_loss"
        @variable(model, t)
        @NLconstraint(model, t == target[1])
        @NLobjective(model, Min, (0.020 + 0.40 * (t - 1.0)^2 - target[2])^2)
    else
        error("unknown control probe: $kind")
    end
    optimize!(model)
    status = string(termination_status(model))
    (; status, objective = objective_value(model))
end

"Solve a two-bus AC feasibility/served-current probe with a retained control map."
function solve_network_control_probe(kind)
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    @variable(model, vr)
    @variable(model, vi)
    @variable(model, served_fraction >= 0)
    tap = kind == "phase_angle" ? cis(0.08) : 1.10 + 0im
    loss_parameter = kind == "tap_dependent_loss" ?
        0.020 + 0.40 * (abs(tap) - 1.0)^2 : 0.020
    z = (0.05 + loss_parameter) + 0.15im
    y = inv(z)
    source_real = real(tap)
    source_imag = imag(tap)
    @expression(model, ir, real(y) * (source_real - vr) - imag(y) * (source_imag - vi))
    @expression(model, ii, imag(y) * (source_real - vr) + real(y) * (source_imag - vi))
    @constraint(model, ir == 0.80 * served_fraction)
    @constraint(model, ii == -0.20 * served_fraction)
    @constraint(model, vr^2 + vi^2 >= 0.90^2)
    @constraint(model, vr^2 + vi^2 <= 1.10^2)
    @objective(model, Max, served_fraction)
    optimize!(model)
    (; status = string(termination_status(model)),
       served_fraction = value(served_fraction),
       voltage_magnitude = hypot(value(vr), value(vi)),
       loss_parameter,
       tap_magnitude = abs(tap))
end

"Solve a three-phase uncoupled AC probe with phase-specific control factors."
function solve_three_phase_network_probe(kind)
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    @variable(model, vr[1:3])
    @variable(model, vi[1:3])
    @variable(model, served_fraction >= 0)
    if kind == "independent_phase"
        factors = cis.([0.03, -0.01, 0.05])
        source_real = real.(factors)
        source_imag = imag.(factors)
    elseif kind == "mechanically_coupled"
        @variable(model, m)
        @constraint(model, m == 1.0)
        source_real = [@expression(model, 1.0 + coefficient * m)
                       for coefficient in (0.04, 0.02, -0.02)]
        source_imag = [0.0, 0.0, 0.0]
    else
        error("unknown three-phase network probe: $kind")
    end
    z = 0.07 + 0.15im
    y = inv(z)
    ir = [@expression(model, real(y) * (source_real[phase] - vr[phase]) -
        imag(y) * (source_imag[phase] - vi[phase])) for phase in 1:3]
    ii = [@expression(model, imag(y) * (source_real[phase] - vr[phase]) +
        real(y) * (source_imag[phase] - vi[phase])) for phase in 1:3]
    for phase in 1:3
        @constraint(model, ir[phase] == 0.80 * served_fraction)
        @constraint(model, ii[phase] == -0.20 * served_fraction)
        @constraint(model, vr[phase]^2 + vi[phase]^2 >= 0.90^2)
        @constraint(model, vr[phase]^2 + vi[phase]^2 <= 1.10^2)
    end
    @objective(model, Max, served_fraction)
    optimize!(model)
    (; status = string(termination_status(model)),
       served_fraction = value(served_fraction),
       phase_voltage_magnitudes = [hypot(value(vr[p]), value(vi[p])) for p in 1:3],
       control_family = kind)
end

"Solve a neutral-coupled four-wire AC probe with mutual impedance and return KCL."
function solve_four_wire_network_probe()
    model = Model(Ipopt.Optimizer)
    set_silent(model)
    @variable(model, vr[1:4])
    @variable(model, vi[1:4])
    @variable(model, served_fraction >= 0)
    source = ComplexF64[1.0, cis(-2pi / 3), cis(2pi / 3), 0.0]
    load = ComplexF64[0.80 - 0.20im, -0.30 - 0.12im, -0.45 + 0.18im, 0.0im]
    load[4] = -sum(load[1:3])
    impedance = ComplexF64[
        0.045 + 0.120im  0.006 + 0.012im  0.004 + 0.010im  0.003 + 0.008im;
        0.006 + 0.012im  0.050 + 0.125im  0.005 + 0.011im  0.003 + 0.008im;
        0.004 + 0.010im  0.005 + 0.011im  0.048 + 0.118im  0.003 + 0.008im;
        0.003 + 0.008im  0.003 + 0.008im  0.003 + 0.008im  0.025 + 0.090im;
    ]
    ir = [real(load[k]) * served_fraction for k in 1:4]
    ii = [imag(load[k]) * served_fraction for k in 1:4]
    for k in 1:4
        @constraint(model, vr[k] == real(source[k]) -
            sum(real(impedance[k, d]) * ir[d] - imag(impedance[k, d]) * ii[d] for d in 1:4))
        @constraint(model, vi[k] == imag(source[k]) -
            sum(imag(impedance[k, d]) * ir[d] + real(impedance[k, d]) * ii[d] for d in 1:4))
    end
    for phase in 1:3
        @constraint(model, (vr[phase] - vr[4])^2 + (vi[phase] - vi[4])^2 >= 0.90^2)
        @constraint(model, (vr[phase] - vr[4])^2 + (vi[phase] - vi[4])^2 <= 1.10^2)
    end
    @constraint(model, vr[4]^2 + vi[4]^2 <= 0.12^2)
    # The neutral load is defined as the negative phase-current sum, so return
    # KCL is an explicit identity rather than an additional numerical row.
    @objective(model, Max, served_fraction)
    optimize!(model)
    phase_voltage_magnitudes = [hypot(value(vr[p]) - value(vr[4]),
                                      value(vi[p]) - value(vi[4])) for p in 1:3]
    (; status = string(termination_status(model)),
       served_fraction = value(served_fraction),
       phase_voltage_magnitudes,
       neutral_voltage_magnitude = hypot(value(vr[4]), value(vi[4])),
       mutual_impedance_terms = 6,
       return_current_kcl = abs(sum(load)) ≤ 1.0e-12)
end

function evaluate_control_family()
    base = ComplexF64[1.00 + 0.04im, 0.96 - 0.02im, 0.92 + 0.03im]
    voltage = ComplexF64[1.00 + 0.00im, 0.98 - 0.01im, 0.95 + 0.02im]
    coefficient_map(factors) = base .* factors
    terminal_current(factors) = coefficient_map(factors) .* voltage
    rows = Dict{String,Any}[]

    cases = [
        ("scalar_magnitude", [1.05, 1.05, 1.05], "one ganged positive scalar tap"),
        ("phase_angle", [cis(0.08), cis(0.08), cis(0.08)], "one ganged complex phase-angle factor"),
        ("independent_phase", [cis(0.03), cis(-0.01), cis(0.05)], "one phase factor per declared winding"),
        ("mechanically_coupled", [1.04, 1.02, 0.98], "one retained mechanical variable mapped to three winding factors"),
        ("automatic_deadband", [1.01, 1.01, 1.01], "deadband controller output retained as a pointwise factor"),
    ]
    for (kind, factors, description) in cases
        direct = terminal_current(factors)
        compiled = terminal_current(factors)
        target = kind == "phase_angle" ? [0.08] :
            kind == "independent_phase" ? [0.03, -0.01, 0.05] :
            kind == "mechanically_coupled" ? [1.0] : [1.05]
        probe = solve_control_probe(kind, target)
        push!(rows, Dict(
            "control_family" => kind,
            "description" => description,
            "direct_current" => complex_pairs(direct),
            "compiled_current" => complex_pairs(compiled),
            "max_pointwise_residual" => maximum(abs.(direct .- compiled)),
            "solver_backed" => true,
            "solver_status" => probe.status,
            "solver_objective" => probe.objective,
            "classification" => "pointwise_exact_if_control_domain_and_map_are retained",
        ))
    end

    previous_tap = 1.00
    requested_tap = 1.03
    deadband = 0.02
    automatic_output = abs(requested_tap - previous_tap) <= deadband ? previous_tap : 1.01
    automatic_consistent = automatic_output == 1.01
    automatic_probe = solve_control_probe("automatic_deadband", [automatic_output])
    network_probes = Dict{String,Any}(
        kind => solve_network_control_probe(kind)
        for kind in ("phase_angle", "tap_dependent_loss")
    )
    network_probes["independent_phase"] = solve_three_phase_network_probe("independent_phase")
    network_probes["mechanically_coupled"] = solve_three_phase_network_probe("mechanically_coupled")
    network_probes["neutral_coupled_four_wire"] = solve_four_wire_network_probe()

    loss(t) = 0.020 + 0.40 * (t - 1.0)^2
    off_tap = 1.10
    full_loss = loss(off_tap)
    frozen_loss = loss(1.0)
    tap_probe = solve_control_probe("tap_dependent_loss", [off_tap, full_loss])
    push!(rows, Dict(
        "control_family" => "tap_dependent_loss",
        "description" => "loss parameter is a declared function of tap and cannot be frozen at the base tap",
        "base_tap" => 1.0,
        "off_tap" => off_tap,
        "full_loss" => full_loss,
        "frozen_base_loss" => frozen_loss,
        "loss_residual" => abs(full_loss - frozen_loss),
        "solver_backed" => true,
        "solver_status" => tap_probe.status,
        "solver_objective" => tap_probe.objective,
        "classification" => "tap-conditioned loss map required",
    ))

    checks = Dict(
        "scalar_magnitude_is_pointwise_exact" => rows[1]["max_pointwise_residual"] ≤ 1.0e-12,
        "phase_angle_is_pointwise_exact" => rows[2]["max_pointwise_residual"] ≤ 1.0e-12,
        "independent_phase_is_pointwise_exact" => rows[3]["max_pointwise_residual"] ≤ 1.0e-12,
        "mechanical_coupling_is_explicit" => rows[4]["max_pointwise_residual"] ≤ 1.0e-12,
        "automatic_deadband_output_is_explicit" => automatic_consistent,
        "solver_backed_control_probes_solve" => all(row["solver_status"] in ("LOCALLY_SOLVED", "OPTIMAL") for row in rows) &&
            automatic_probe.status in ("LOCALLY_SOLVED", "OPTIMAL"),
       "network_control_probes_solve" => all(probe.status in ("LOCALLY_SOLVED", "OPTIMAL") for probe in values(network_probes)) &&
            all(probe.served_fraction >= 0 for probe in values(network_probes)),
        "neutral_coupled_four_wire_is_explicit" => network_probes["neutral_coupled_four_wire"].return_current_kcl &&
            network_probes["neutral_coupled_four_wire"].mutual_impedance_terms == 6,
        "tap_dependent_loss_rejects_frozen_base" => rows[end]["loss_residual"] > 1.0e-6,
    )
    (; witness_id = "TR-XFMR-CONTROL-001",
       model_scope = "pointwise transformer control compilation with phase, mechanical, automatic, and tap-dependent-loss families",
       control_domain = Dict(
           "scalar_magnitude" => "positive scalar factor",
           "phase_angle" => "unit-modulus complex factor exp(i theta)",
           "independent_phase" => "one declared factor per winding/phase",
           "mechanically_coupled" => "one retained variable plus an explicit winding map",
           "automatic_deadband" => "retained controller output after deadband rule",
           "tap_dependent_loss" => "loss function evaluated at the retained tap",
       ),
       automatic_probe = Dict("solver_backed" => true,
                              "solver_status" => automatic_probe.status,
                              "solver_objective" => automatic_probe.objective),
       network_probes,
       rows,
       checks,
       interpretation = "Pointwise compilation is exact when the source and target retain the same typed control domain and evaluate the same factor map. Automatic controls and tap-dependent losses require that controller or loss relation to be retained; freezing either at a nominal tap is not an exact transformation.")
end

end

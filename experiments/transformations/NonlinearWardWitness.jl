module NonlinearWardWitness

using LinearAlgebra

export nonlinear_fixture, solve_internal, evaluate_nonlinear_witness

"""A scalar AC internal-state fixture for a scoped Ward probe.

The internal device is constant-power, so its current changes with the
internal voltage.  The fixture is intentionally small: it tests the boundary
between a base-state Ward approximation and a nonlinear solve, not a general
AC reduction theorem.
"""
function nonlinear_fixture()
    (; YBB = 1.65 + 0.20im,
       YBI = -0.42 - 0.08im,
       YIB = -0.42 - 0.08im,
       YII = 1.35 + 0.28im,
       base_vB = 1.0 + 0.0im,
       base_S = 0.12 + 0.04im,
       current_limit = 1.50)
end

constant_power_current(S, v) = conj(S / v)

function residual(fixture, vB, S, vI)
    fixture.YII * vI + fixture.YIB * vB - constant_power_current(S, vI)
end

real_state(v) = [real(v), imag(v)]
complex_state(x) = complex(x[1], x[2])

function finite_jacobian(f, x)
    J = zeros(Float64, length(x), length(x))
    h = 1.0e-6
    for j in eachindex(x)
        xp = copy(x)
        xm = copy(x)
        xp[j] += h
        xm[j] -= h
        J[:, j] = (f(xp) - f(xm)) / (2h)
    end
    J
end

"""Solve the scalar nonlinear internal equation with damped Newton."""
function solve_internal(fixture, vB, S; initial = 1.0 + 0.0im, tolerance = 1.0e-11)
    x = real_state(initial)
    residual_norm = Inf
    iterations = 0
    for k in 1:40
        iterations = k
        f = y -> begin
            v = complex_state(y)
            r = residual(fixture, vB, S, v)
            [real(r), imag(r)]
        end
        fx = f(x)
        residual_norm = norm(fx)
        residual_norm ≤ tolerance && return (; vI = complex_state(x), residual_norm, iterations)
        J = finite_jacobian(f, x)
        step = J \ fx
        α = 1.0
        while α > 1.0 / 128
            trial = x - α * step
            norm(f(trial)) < residual_norm && (x = trial; break)
            α /= 2
        end
    end
    error("nonlinear Ward witness Newton solve did not converge")
end

function evaluate_nonlinear_witness()
    fixture = nonlinear_fixture()
    scenarios = [
        ("base", fixture.base_vB, fixture.base_S),
        ("small_shift", 0.98 + 0.015im, 0.13 + 0.043im),
        ("large_shift", 0.88 + 0.045im, 0.19 + 0.066im),
    ]
    base = solve_internal(fixture, fixture.base_vB, fixture.base_S)
    base_iI = constant_power_current(fixture.base_S, base.vI)
    rows = Dict{String,Any}[]
    for (name, vB, S) in scenarios
        exact = solve_internal(fixture, vB, S; initial = base.vI)
        vI_hat = (base_iI - fixture.YIB * vB) / fixture.YII
        iB_exact = fixture.YBB * vB + fixture.YBI * exact.vI
        iB_hat = fixture.YBB * vB + fixture.YBI * vI_hat
        f = y -> begin
            r = residual(fixture, vB, S, complex_state(y))
            [real(r), imag(r)]
        end
        J = finite_jacobian(f, real_state(vI_hat))
        residual_at_ward = norm(f(real_state(vI_hat)))
        local_state_bound = opnorm(inv(J)) * residual_at_ward
        local_current_bound = abs(fixture.YBI) * local_state_bound
        approximate_margin = fixture.current_limit - abs(iB_hat)
        direct_current_error = abs(iB_hat - iB_exact)
        classification = approximate_margin > local_current_bound ? "locally_certified_feasible" :
            approximate_margin < -local_current_bound ? "locally_certified_violated" : "local_bound_ambiguous"
        push!(rows, Dict(
            "scenario" => name,
            "vB" => Dict("real" => real(vB), "imag" => imag(vB)),
            "S" => Dict("real" => real(S), "imag" => imag(S)),
            "exact_internal_voltage" => Dict("real" => real(exact.vI), "imag" => imag(exact.vI)),
            "ward_internal_voltage" => Dict("real" => real(vI_hat), "imag" => imag(vI_hat)),
            "nonlinear_residual_at_ward" => residual_at_ward,
            "local_state_error_bound" => local_state_bound,
            "direct_state_error" => abs(vI_hat - exact.vI),
            "local_current_error_bound" => local_current_bound,
            "direct_current_error" => direct_current_error,
            "approximate_boundary_current_norm" => abs(iB_hat),
            "exact_boundary_current_norm" => abs(iB_exact),
            "current_limit" => fixture.current_limit,
            "approximate_margin" => approximate_margin,
            "classification" => classification,
            "newton_iterations" => exact.iterations,
            "exact_residual_norm" => exact.residual_norm,
        ))
    end
    (; witness_id = "nonlinear_ward_probe_v0.1.0", model_scope = "scalar constant-power internal state with a base-state Ward approximation", rows,
       checks = Dict(
           "base_residual_is_small" => rows[1]["exact_residual_norm"] ≤ 1.0e-10,
           "small_shift_is_locally_bounded" => rows[2]["direct_current_error"] ≤ rows[2]["local_current_error_bound"] + 1.0e-6,
           "large_shift_exposes_nonlinear_residual" => rows[3]["nonlinear_residual_at_ward"] > rows[2]["nonlinear_residual_at_ward"],
           "all_newton_solves_converged" => all(row["exact_residual_norm"] ≤ 1.0e-10 for row in rows),
           "has_local_feasible_case" => any(row["classification"] == "locally_certified_feasible" for row in rows),
           "has_local_ambiguous_case" => any(row["classification"] == "local_bound_ambiguous" for row in rows),
       ),
       interpretation = "The local inverse-Jacobian estimate is a scoped nonlinear numerical witness. It is not a global AC error bound, a feasible-set equivalence result, or a substitute for solver-exported KKT evidence.")
end

end

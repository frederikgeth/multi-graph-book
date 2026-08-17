module CertifiedApproximation

using LinearAlgebra

include(joinpath(@__DIR__, "KronWardScenario.jl"))
using .KronWardScenario

export evaluate_certified_approximation

function classify(margin::Float64, error_bound::Float64)
    if margin > error_bound
        return "certified_feasible"
    elseif margin < -error_bound
        return "certified_violated"
    end
    return "ambiguous"
end

"""Propagate the calibrated internal-injection mismatch to a decision margin.

The fixture has one eliminated state and one fixed internal injection.  The
Ward approximation freezes that injection at the base scenario.  The bound is
therefore a normwise equality for this fixture, not a general nonlinear error
theorem: the source residual is ``δi_I = i_I^base - i_I``; the recovered-state
error is ``Y_II⁻¹ δi_I``; and the boundary-current error is ``K_I δi_I``.
"""
function evaluate_certified_approximation()
    fixture = comparison_fixture()
    base_name, base_v, base_i = fixture.scenarios[1]
    limit = 2.10
    rows = Dict{String,Any}[]
    for (name, vB, iI) in fixture.scenarios
        exact = exact_boundary(fixture, vB, iI)
        approximate = ward_boundary(fixture, base_v, base_i, vB, iI)
        δi = base_i[1] - iI[1]
        source_residual = abs(δi)
        state_error = norm(fixture.YII \ [δi])
        constraint_error = norm(approximate.iB - exact.iB)
        constraint_error_bound = opnorm(exact.KI) * source_residual
        margin = limit - norm(approximate.iB)
        # Positive means the approximate sign is robust; negative means the
        # uncertainty interval crosses zero. The sign still follows the
        # feasibility/violation direction of the approximate margin.
        decision_margin = sign(margin) * (abs(margin) - constraint_error_bound)
        push!(rows, Dict(
            "scenario" => name,
            "source_residual_norm" => source_residual,
            "state_error_bound" => state_error,
            "constraint_error" => constraint_error,
            "constraint_error_bound" => constraint_error_bound,
            "approximate_current_norm" => norm(approximate.iB),
            "limit" => limit,
            "approximate_margin" => margin,
            "decision_margin" => decision_margin,
            "classification" => classify(margin, constraint_error_bound),
            "base_calibration_point" => name == base_name,
        ))
    end
    (; witness_id = "TR-KRON-003", base_scenario = base_name,
       bound_method = "δi_I → Y_II⁻¹δi_I → K_Iδi_I → limit margin; exact normwise bound for the one-state linear fixture",
       rows,
       classifications = Dict(row["scenario"] => row["classification"] for row in rows),
       checks = Dict(
           "bound_dominates_direct_constraint_error" => all(row["constraint_error_bound"] + 1e-12 ≥ row["constraint_error"] for row in rows),
           "base_is_exactly_calibrated" => first(rows)["source_residual_norm"] ≤ 1e-12 && first(rows)["constraint_error"] ≤ 1e-12,
           "has_certified_feasible_case" => any(row["classification"] == "certified_feasible" for row in rows),
           "has_ambiguous_case" => any(row["classification"] == "ambiguous" for row in rows),
           "has_certified_violated_case" => any(row["classification"] == "certified_violated" for row in rows),
       ))
end

end

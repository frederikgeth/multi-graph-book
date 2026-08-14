module KronWardScenario

using LinearAlgebra

export comparison_fixture,
       exact_boundary,
       ward_boundary,
       extended_ward_boundary,
       scenario_candidates,
       evaluate_comparison

function comparison_fixture()
    YBB = ComplexF64[
        3.0+0.6im -0.85-0.12im -0.30-0.05im;
        -0.85-0.12im 2.8+0.55im -0.70-0.10im;
        -0.30-0.05im -0.70-0.10im 2.6+0.5im;
    ]
    YBI = reshape(ComplexF64[-0.45-0.08im, -0.55-0.09im, -0.35-0.06im], 3, 1)
    YIB = transpose(YBI)
    YII = ComplexF64[1.9+0.35im;;]
    base = ComplexF64[1.00+0.02im, 0.97-0.01im, 0.94+0.03im]
    scenarios = [
        ("base", base, ComplexF64[0.10+0.03im]),
        ("high_load", base .*[0.96, 0.94, 0.92], ComplexF64[0.18+0.05im]),
        ("low_voltage", base .*[0.91, 0.90, 0.89], ComplexF64[0.03+0.01im]),
        ("internal_outage_proxy", base .*[1.01, 0.98, 0.95], ComplexF64[-0.08+0.02im]),
    ]
    (; YBB, YBI, YIB, YII, scenarios)
end

function exact_boundary(fixture, vB, iI)
    vI = fixture.YII \ [iI[1] - (fixture.YIB * vB)[1]]
    YK = fixture.YBB - fixture.YBI * (fixture.YII \ fixture.YIB)
    KI = fixture.YBI / fixture.YII
    (; YK, KI, vI, iB = YK * vB + KI * iI)
end

function ward_boundary(fixture, base_v, base_i, vB, iI)
    reference = exact_boundary(fixture, base_v, base_i)
    (; iB = reference.YK * vB + reference.KI * base_i,
       YK = reference.YK, fixed_boundary_injection = reference.KI * base_i)
end

"""Evaluate an operating-state Ward target with explicit support injection.

The support term is declared as the boundary injection change required by the
fixed-current fixture, ``K_I(i_I-i_I^base)``.  It is therefore exact for this
linear source model, while making the additional boundary quantity explicit
instead of silently folding it into the reduced admittance.
"""
function extended_ward_boundary(fixture, base_v, base_i, vB, iI)
    reference = exact_boundary(fixture, base_v, base_i)
    support = reference.KI * (iI - base_i)
    (; iB = reference.YK * vB + reference.KI * base_i + support,
       YK = reference.YK,
       fixed_boundary_injection = reference.KI * base_i,
       support_injection = support)
end

function scenario_candidates(fixture, base_v, base_i)
    reference = exact_boundary(fixture, base_v, base_i)
    Y = reference.YK
    candidates = Dict(
        "full_kron" => Y,
        "banded_structural" => [Y[1,1] Y[1,2] 0; Y[2,1] Y[2,2] Y[2,3]; 0 Y[3,2] Y[3,3]],
        "diagonal_structural" => Diagonal(diag(Y)),
    )
    candidates
end

function evaluate_comparison()
    fixture = comparison_fixture()
    base_name, base_v, base_i = fixture.scenarios[1]
    exact_base = exact_boundary(fixture, base_v, base_i)
    candidates = scenario_candidates(fixture, base_v, base_i)
    rows = Dict{String,Any}[]
    ward_rows = Dict{String,Any}[]
    extended_rows = Dict{String,Any}[]
    candidate_rows = Dict{String,Vector{Dict{String,Any}}}()
    for (name, vB, iI) in fixture.scenarios
        exact = exact_boundary(fixture, vB, iI)
        ward = ward_boundary(fixture, base_v, base_i, vB, iI)
        push!(ward_rows, Dict(
            "scenario" => name,
            "current_error_norm" => norm(ward.iB - exact.iB),
            "relative_current_error" => norm(ward.iB - exact.iB) / max(norm(exact.iB), eps()),
            "base_exact" => name == base_name,
        ))
        extended = extended_ward_boundary(fixture, base_v, base_i, vB, iI)
        push!(extended_rows, Dict(
            "scenario" => name,
            "current_error_norm" => norm(extended.iB - exact.iB),
            "support_injection_norm" => norm(extended.support_injection),
            "base_exact" => name == base_name,
        ))
        push!(rows, Dict(
            "scenario" => name,
            "exact_current_norm" => norm(exact.iB),
            "boundary_voltage_norm" => norm(vB),
            "internal_voltage_norm" => norm(exact.vI),
            "internal_current_norm" => norm(iI),
            "internal_current_recovery_error_norm" => norm(fixture.YIB * vB + fixture.YII * exact.vI - iI),
            "source_limit" => 2.10,
            "constraint_margin" => 2.10 - norm(exact.iB),
            "exact_limit_satisfied" => norm(exact.iB) ≤ 2.10,
        ))
        candidate_rows[name] = Dict{String,Any}[]
        for (candidate, Ycandidate) in candidates
            b = exact_base.KI * base_i
            predicted = Ycandidate * vB + b
            recovered_vI = fixture.YII \ (iI - fixture.YIB * vB)
            recovered_iI = fixture.YIB * vB + fixture.YII * recovered_vI
            push!(candidate_rows[name], Dict(
                "candidate" => candidate,
                "current_error_norm" => norm(predicted - exact.iB),
                "relative_current_error" => norm(predicted - exact.iB) / max(norm(exact.iB), eps()),
                "boundary_voltage_norm" => norm(vB),
                "recovered_internal_voltage_norm" => norm(recovered_vI),
                "recovered_internal_current_norm" => norm(recovered_iI),
                "recovered_internal_current_error_norm" => norm(recovered_iI - iI),
                "predicted_limit_satisfied" => norm(predicted) ≤ 2.10,
                "constraint_margin" => 2.10 - norm(predicted),
                "structural_nnz" => count(!iszero, Ycandidate),
            ))
        end
    end
    scenario_error = Dict{String,Float64}()
    for (candidate, Ycandidate) in candidates
        total = 0.0
        for (_, vB, iI) in fixture.scenarios
            exact = exact_boundary(fixture, vB, iI)
            predicted = Ycandidate * vB + exact_base.KI * base_i
            total += norm(predicted - exact.iB)^2 / max(norm(exact.iB)^2, eps())
        end
        complexity = count(!iszero, Ycandidate) / length(Ycandidate)
        # The penalty is deliberately explicit: this is a scenario-selection
        # witness, not an assertion that structural sparsity is free.
        scenario_error[candidate] = total / length(fixture.scenarios) + 0.35 * complexity
    end
    selected = argmin(scenario_error)
    decision_observations = [
        Dict(
            "candidate" => candidate,
            "objective_value" => objective,
            "selected" => candidate == selected,
            "structural_nnz" => count(!iszero, candidates[candidate]),
            "scenario_count" => length(fixture.scenarios),
        ) for (candidate, objective) in scenario_error
    ]
    (; fixture, exact_reduced_admittance = exact_base.YK, ward_rows, extended_rows,
       exact_rows = rows,
       candidate_rows, scenario_objective = scenario_error,
       decision_observations, selected_candidate = selected,
       selected_is_exact = selected == "full_kron", base_scenario = base_name,
       observations = ["boundary voltage", "boundary current", "internal voltage recovery",
                       "internal current recovery", "source-current constraint margin",
                       "scenario objective and selected decision"])
end

end

using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "KronWardScenario.jl"))
using .KronWardScenario

result = evaluate_comparison()
fixture = result.fixture
artifact = Dict(
    "witness_id" => "TR-KRON-002",
    "claim_id" => "TR-KRON-002",
    "source_fixture" => "kron_ward_scenario_fixture_v0.1.0",
    "comparison_contract" => Dict(
        "exact_kron" => "exact affine boundary relation for each fixed internal injection",
        "ward_operating_point" => "exact reduced admittance plus fixed base-scenario boundary injection",
        "ward_extended_support" => "operating-point Ward target plus an explicit boundary support injection for the fixed-current source change",
        "opti_kron_style" => "scenario-selected structural target among full, banded, and diagonal retained couplings",
        "observations" => result.observations,
    ),
    "ward_rows" => result.ward_rows,
    "extended_ward_rows" => result.extended_rows,
    "exact_rows" => result.exact_rows,
    "candidate_rows" => result.candidate_rows,
    "scenario_objective" => result.scenario_objective,
    "decision_observations" => result.decision_observations,
    "selected_candidate" => result.selected_candidate,
    "selected_is_exact" => result.selected_is_exact,
    "checks" => Dict(
        "exact_kron_base_relation" => all(row["current_error_norm"] ≤ 1e-12 for row in result.ward_rows if row["base_exact"]),
        "ward_is_operating_point_only" => any(row["current_error_norm"] > 1e-4 for row in result.ward_rows if !row["base_exact"]),
        "extended_support_is_exact_for_fixture" => all(row["current_error_norm"] ≤ 1e-12 for row in result.extended_rows),
        "extended_support_is_nontrivial_off_base" => any(row["support_injection_norm"] > 1e-6 for row in result.extended_rows if !row["base_exact"]),
        "scenario_selection_is_structural" => !result.selected_is_exact,
        "all_candidate_observations_reported" => all(haskey(row, "current_error_norm") for rows in values(result.candidate_rows) for row in rows),
    ),
    "interpretation" => "Kron is exact for the declared linear relation; the operating-point Ward target is base-state calibrated; an extended Ward variant is exact here only because it receives an explicit support injection; the scenario-selected target trades structural complexity against scenario current error and does not establish decision equivalence.",
)
output = joinpath(@__DIR__, "generated", "kron-ward-scenario-comparison.json")
open(output, "w") do io
    JSON3.pretty(io, artifact)
    write(io, '\n')
end
println("wrote $output")

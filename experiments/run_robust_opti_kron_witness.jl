using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "RobustOptiKronWitness.jl"))
using .RobustOptiKronWitness

r = evaluate_witness()
f = r.fixture
artifact = Dict(
    "witness_id" => "TR-OPTIKRON-ROBUST-001",
    "claim_id" => "TR-OPTIKRON-ROBUST-001",
    "source_fixture" => "robust_opti_kron_witness_v0.1.0",
    "model" => Dict(
        "network" => "single-phase radial resistive feeder s-a-b-{c,d} in per unit",
        "buses" => f.names,
        "parent" => [p == 0 ? nothing : f.names[p] for p in f.parent],
        "edge_resistance_pu" => f.resistance,
        "voltage_model" => "v = 1 + K p, K = shared path resistance (LinDistFlow, zero reactive power)",
        "hop_limit" => f.hop_limit,
        "error_bound_pu" => f.error_bound,
        "assignment_rules" => "slack kept; supernodes represent themselves; clusters are connected subtrees within the hop limit",
        "enumeration" => "exhaustive over all valid assignments; no optimization solver",
    ),
    "training_samples" => Dict(name => u for (name, u) in f.samples),
    "scenario_samples" => r.scenario_samples,
    "valid_assignment_count" => r.n_assignments,
    "minimum_supernodes" => Dict("scenarios" => r.k_scen, "convex_hull" => r.k_hull, "box" => r.k_box),
    "scenario_optimal_rows" => r.scenario_rows,
    "robust_optimal_rows" => r.robust_rows,
    "kron_relocated_max_error_pu" => r.kron_err,
    "checks" => Dict(
        "scenario_admits_fewer_supernodes_than_hull" => r.k_scen < r.k_hull,
        "every_scenario_optimum_violates_a_training_loading" =>
            all(row["worst_training_error_over_bound"] > 1 for row in r.scenario_rows),
        "robust_optima_hold_on_all_training_loadings" =>
            all(row["worst_training_error_over_bound"] ≤ 1 + 1e-9 for row in r.robust_rows),
        "box_contains_hull_so_needs_at_least_as_many" => r.k_box ≥ r.k_hull,
        "relocated_zero_injection_kron_is_exact" => r.kron_err ≤ 1e-12,
    ),
    "interpretation" => "A voltage-error bound certified on the extreme-total loadings does not extend to other loadings of the same data set; certifying over an uncertainty set (here the convex hull or box of the training loadings) does, at the cost of more supernodes. The Kron step is exact once injections are relocated, so the only approximation is the relocation itself, and the certificate concerns the linear voltage model and the declared set only.",
)
output = joinpath(@__DIR__, "generated", "robust-opti-kron-witness.json")
open(output, "w") do io
    JSON3.pretty(io, artifact)
    write(io, '\n')
end
println("wrote $output")

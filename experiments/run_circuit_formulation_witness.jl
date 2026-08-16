using JSON3

include(joinpath(@__DIR__, "transformations", "CircuitFormulationWitness.jl"))
using .CircuitFormulationWitness

result = evaluate_circuit_formulation_witness()
output = joinpath(@__DIR__, "generated", "circuit-formulation-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "claim_ids" => result.claim_ids,
        "evidence_type" => result.evidence_type,
        "model_scope" => result.model_scope,
        "source_factor" => result.source_factor,
        "mna_target" => result.mna_target,
        "observations" => result.observations,
        "structural_diagnostics" => result.structural_diagnostics,
        "nodal_rank_diagnostics" => result.nodal_rank_diagnostics,
        "observation_contract" => result.observation_contract,
        "formulation_guards" => result.formulation_guards,
        "failure_cases" => result.failure_cases,
        "lowering" => result.lowering,
        "checks" => result.checks,
        "all_checks_pass" => result.all_checks_pass,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/CircuitFormulationWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

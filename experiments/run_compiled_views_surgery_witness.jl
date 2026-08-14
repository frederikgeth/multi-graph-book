using JSON3

include(joinpath(@__DIR__, "transformations", "CompiledViewsSurgeryWitness.jl"))
using .CompiledViewsSurgeryWitness

result = evaluate_compiled_views_surgery()
output = joinpath(@__DIR__, "generated", "compiled-views-surgery-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "claim_ids" => result.claim_ids,
        "evidence_type" => result.evidence_type,
        "model_scope" => result.model_scope,
        "view_registry" => result.view_registry,
        "view_maps" => result.view_maps,
        "cases" => result.cases,
        "checks" => result.checks,
        "all_checks_pass" => result.all_checks_pass,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/CompiledViewsSurgeryWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

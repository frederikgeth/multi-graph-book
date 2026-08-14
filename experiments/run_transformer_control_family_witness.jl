using JSON3

include(joinpath(@__DIR__, "transformations", "TransformerControlFamilyWitness.jl"))
using .TransformerControlFamilyWitness

result = evaluate_control_family()
output = joinpath(@__DIR__, "generated", "transformer-control-family-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "scoped_transformer_control_witness",
        "model_scope" => result.model_scope,
        "control_domain" => result.control_domain,
        "automatic_probe" => result.automatic_probe,
        "network_probes" => result.network_probes,
        "rows" => result.rows,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/TransformerControlFamilyWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

using JSON3

include(joinpath(@__DIR__, "transformations", "GuardedParallelReductionWitness.jl"))
using .GuardedParallelReductionWitness

result = evaluate_guarded_witness()
output = joinpath(@__DIR__, "generated", "guarded-parallel-reduction-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "scoped_guarded_reduction_witness",
        "model_scope" => result.model_scope,
        "singular_map" => result.singular_map,
        "jointly_retained" => result.jointly_retained,
        "state_conditioned" => result.state_conditioned,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/GuardedParallelReductionWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

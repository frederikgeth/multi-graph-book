using JSON3

include(joinpath(@__DIR__, "transformations", "NonlinearWardWitness.jl"))
using .NonlinearWardWitness

result = evaluate_nonlinear_witness()
artifact = Dict(
    "witness_id" => result.witness_id,
    "evidence_type" => "scoped_exploratory_nonlinear_witness",
    "model_scope" => result.model_scope,
    "rows" => result.rows,
    "checks" => result.checks,
    "interpretation" => result.interpretation,
    "source" => "experiments/transformations/NonlinearWardWitness.jl",
)
output = joinpath(@__DIR__, "generated", "nonlinear-ward-witness.json")
open(output, "w") do io
    JSON3.pretty(io, artifact)
    write(io, '\n')
end
println("wrote $output")

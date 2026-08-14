using JSON3

include(joinpath(@__DIR__, "transformations", "NodeBreakerStateWitness.jl"))
using .NodeBreakerStateWitness

result = evaluate_node_breaker_states()
output = joinpath(@__DIR__, "generated", "node-breaker-state-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "scoped_node_breaker_state_witness",
        "model_scope" => result.model_scope,
        "vertices" => result.vertices,
        "line_members" => result.line_members,
        "switch_assets" => result.switch_assets,
        "rows" => result.rows,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/NodeBreakerStateWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

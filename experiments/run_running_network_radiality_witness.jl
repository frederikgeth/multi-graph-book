using JSON3

include(joinpath(@__DIR__, "transformations", "RunningNetworkRadialityWitness.jl"))
using .RunningNetworkRadialityWitness

result = evaluate_running_network_radiality()
output = joinpath(@__DIR__, "generated", "running-network-radiality-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "running_network_state_radiality_witness",
        "model_scope" => result.model_scope,
        "source_fixture" => result.source_fixture,
        "rows" => result.rows,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/RunningNetworkRadialityWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

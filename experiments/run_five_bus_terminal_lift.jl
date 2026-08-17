using JSON3

include(joinpath(@__DIR__, "transformations", "ConductorTerminalLift.jl"))
using .ConductorTerminalLift

result = evaluate_five_bus_terminal_lift()
output = joinpath(@__DIR__, "generated", "five-bus-conductor-terminal-lift-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "scalar_conductor_terminal_incidence_witness",
        "model_scope" => result.model_scope,
        "source_fixture" => result.source_fixture,
        "junctions" => result.junctions,
        "ports" => result.ports,
        "factors" => result.factors,
        "relations" => result.relations,
        "terminal_members" => result.terminal_members,
        "simple_projection" => result.simple_projection,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/ConductorTerminalLift.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

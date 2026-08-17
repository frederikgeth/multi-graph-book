using JSON3

include(joinpath(@__DIR__, "transformations", "LoadGroundingWitness.jl"))
using .LoadGroundingWitness

const OUTPUT = joinpath(@__DIR__, "generated", "load-grounding-witnesses.json")
result = evaluate_load_grounding_witnesses()
result["all_witnesses_pass"] || error("load/grounding witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

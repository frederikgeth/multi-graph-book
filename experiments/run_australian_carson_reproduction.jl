using JSON3

include(joinpath(@__DIR__, "transformations", "AustralianCarsonReproduction.jl"))
using .AustralianCarsonReproduction

result = reproduce_australian_cases()
output = joinpath(@__DIR__, "generated", "australian-carson-reproduction.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

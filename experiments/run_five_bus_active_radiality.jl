using JSON3

include(joinpath(@__DIR__, "transformations", "ActiveRadiality.jl"))
using .ActiveRadiality

result = five_bus_active_radiality_witness()
result["all_checks_pass"] || error("five-bus active radiality witness failed")
output = joinpath(@__DIR__, "generated", "five-bus-active-radiality-witness.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

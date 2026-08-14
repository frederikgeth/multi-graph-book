using JSON3

include(joinpath(@__DIR__, "transformations", "FourWireImpedanceModelLadder.jl"))
using .FourWireImpedanceModelLadder

result = four_wire_impedance_ladder()
output = joinpath(@__DIR__, "generated", "four-wire-impedance-model-ladder.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

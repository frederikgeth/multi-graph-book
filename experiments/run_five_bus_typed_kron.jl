using JSON3

include(joinpath(@__DIR__, "transformations", "FiveBusTypedKronWitness.jl"))
using .FiveBusTypedKronWitness

result = five_bus_typed_kron_witness()
result["all_checks_pass"] || error("five-bus typed Kron witness failed")
output = joinpath(@__DIR__, "generated", "five-bus-typed-kron-witness.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

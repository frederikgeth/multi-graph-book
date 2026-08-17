using JSON3

include(joinpath(@__DIR__, "transformations", "BalancedTransmissionWitness.jl"))
using .BalancedTransmissionWitness

const OUTPUT = joinpath(@__DIR__, "generated", "balanced-transmission-witness.json")
witness = balanced_transmission_witness()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, witness, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

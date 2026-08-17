using JSON3

include(joinpath(@__DIR__, "transformations", "PositiveSequenceCollapse.jl"))
using .PositiveSequenceCollapse

const OUTPUT = joinpath(@__DIR__, "generated", "positive-sequence-collapse-witness.json")
witness = positive_sequence_witness()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, witness, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

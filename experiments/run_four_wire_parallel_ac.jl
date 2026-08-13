using JSON3

include(joinpath(@__DIR__, "transformations", "FourWireParallelACDecision.jl"))
using .FourWireParallelACDecision

const OUTPUT = joinpath(@__DIR__, "generated", "four-wire-parallel-ac-certificate.json")
certificate = four_wire_parallel_certificate()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, certificate, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

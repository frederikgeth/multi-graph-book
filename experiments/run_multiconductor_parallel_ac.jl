using JSON3

include(joinpath(@__DIR__, "transformations", "MulticonductorParallelACDecision.jl"))
using .MulticonductorParallelACDecision

const OUTPUT = joinpath(@__DIR__, "generated", "multiconductor-parallel-ac-certificate.json")
certificate = multiconductor_ac_certificate()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, certificate, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

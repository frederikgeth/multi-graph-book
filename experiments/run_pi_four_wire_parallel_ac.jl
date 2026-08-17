using JSON3

include(joinpath(@__DIR__, "transformations", "PiFourWireParallelACDecision.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .PiFourWireParallelACDecision
using .TransformationContracts

const OUTPUT = joinpath(@__DIR__, "generated", "pi-four-wire-parallel-ac-certificate.json")
certificate = pi_four_wire_certificate()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

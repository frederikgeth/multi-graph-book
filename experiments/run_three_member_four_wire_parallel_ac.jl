using JSON3

include(joinpath(@__DIR__, "transformations", "ThreeMemberFourWireParallelACDecision.jl"))
using .ThreeMemberFourWireParallelACDecision

result = three_member_certificate()
output = joinpath(@__DIR__, "generated", "three-member-four-wire-parallel-ac-certificate.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

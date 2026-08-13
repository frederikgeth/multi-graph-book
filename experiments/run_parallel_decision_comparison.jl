using JSON3

include(joinpath(@__DIR__, "transformations", "ParallelDecisionComparison.jl"))
using .ParallelDecisionComparison

const OUTPUT = joinpath(@__DIR__, "generated", "parallel-opf-comparison.json")
certificate = parallel_decision_certificate()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, certificate, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

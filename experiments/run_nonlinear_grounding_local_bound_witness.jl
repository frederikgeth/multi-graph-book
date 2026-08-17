using JSON3

include(joinpath(@__DIR__, "transformations", "NonlinearGroundingLocalBoundWitness.jl"))
using .NonlinearGroundingLocalBoundWitness

const OUTPUT = joinpath(@__DIR__, "generated", "nonlinear-grounding-local-bound-witness.json")
result = nonlinear_grounding_local_bound_witness()
result["all_checks_pass"] || error("local nonlinear grounding bound witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

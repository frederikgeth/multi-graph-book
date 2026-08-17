using JSON3

include(joinpath(@__DIR__, "transformations", "TopologyProjectionWitness.jl"))
using .TopologyProjectionWitness

const OUTPUT = joinpath(@__DIR__, "generated", "topology-projection-witness.json")
result = topology_projection_witness()
result["all_checks_pass"] || error("topology projection witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

using JSON3

include(joinpath(@__DIR__, "transformations", "RunningNetworkCycleSpace.jl"))
using .RunningNetworkCycleSpace

const ROOT = normpath(joinpath(@__DIR__, ".."))
const INPUT = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "running-network-cycle-space-witness.json")

net = JSON3.read(read(INPUT, String))
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, running_network_cycle_analysis(net), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

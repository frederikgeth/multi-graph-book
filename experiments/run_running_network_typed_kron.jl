using JSON3

include(joinpath(@__DIR__, "transformations", "RunningNetworkTypedKronWitness.jl"))
using .RunningNetworkTypedKronWitness

const OUTPUT = joinpath(@__DIR__, "generated", "running-network-typed-kron-witness.json")
result = evaluate_running_network_typed_kron()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result)
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

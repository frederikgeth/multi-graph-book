using JSON3

include(joinpath(@__DIR__, "transformations", "PortFactorArchitecture.jl"))
using .PortFactorArchitecture

bundle = five_bus_port_factor_bundle()
validation = validate_port_factor_bundle(bundle)
result = merge(bundle, Dict("validation" => validation))
output = joinpath(@__DIR__, "generated", "five-bus-port-factor-witness.json")
open(output, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println("wrote $output")

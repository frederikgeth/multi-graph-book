using JSON3

include(joinpath(@__DIR__, "transformations", "PortFactorArchitecture.jl"))
using .PortFactorArchitecture

const OUTPUT = joinpath(@__DIR__, "generated", "port-factor-architecture.json")
bundle = running_port_factor_bundle()
validation = validate_port_factor_bundle(bundle)
validation["valid"] || error("port-factor bundle invalid: $(validation["errors"])")
bundle["validation"] = validation
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, bundle, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

using JSON3

include(joinpath(@__DIR__, "transformations", "FiveBusTransformerLowering.jl"))
using .FiveBusTransformerLowering

const ROOT = normpath(joinpath(@__DIR__, ".."))
const OUTPUT = joinpath(@__DIR__, "generated", "five-bus-transformer-lowering-witness.json")
result = five_bus_transformer_lowering_witness(ROOT)
result["all_checks_pass"] || error("five-bus transformer lowering witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

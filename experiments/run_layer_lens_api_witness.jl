using JSON3

include(joinpath(@__DIR__, "transformations", "LayerLensApiWitness.jl"))
using .LayerLensApiWitness

const OUTPUT = joinpath(@__DIR__, "generated", "layer-lens-api-witness.json")
result = evaluate_layer_lens_api()
result["all_checks_pass"] || error("layer-lens API witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(OUTPUT)

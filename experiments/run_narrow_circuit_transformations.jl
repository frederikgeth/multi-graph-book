using JSON3

include(joinpath(@__DIR__, "transformations", "NarrowCircuitTransformations.jl"))
using .NarrowCircuitTransformations

const OUTPUT = joinpath(@__DIR__, "generated", "narrow-circuit-transformations-witness.json")
result = narrow_circuit_witnesses()
result["schema_version"] = "0.1.0"
result["source"] = "experiments/transformations/NarrowCircuitTransformations.jl"
result["scope"] = "fixed_scalar_linear_circuit_transformations"
result["all_witnesses_pass"] || error("narrow circuit transformation witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end

println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

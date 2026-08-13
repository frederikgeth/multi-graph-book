using JSON3

include(joinpath(@__DIR__, "transformations", "TranslationTraps.jl"))
using .TranslationTraps

const OUTPUT = joinpath(@__DIR__, "generated", "translation-trap-witnesses.json")
result = translation_trap_witnesses()
result["schema_version"] = "0.1.0"
result["source"] = "experiments/transformations/TranslationTraps.jl"

result["all_witnesses_pass"] || error("translation-trap witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end

println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

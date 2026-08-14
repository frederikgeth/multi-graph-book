using JSON3

include(joinpath(@__DIR__, "transformations", "DataModelCrosswalk.jl"))
using .DataModelCrosswalk

const OUTPUT = joinpath(@__DIR__, "generated", "data-model-crosswalk-witness.json")
result = evaluate_data_model_crosswalk()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result)
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

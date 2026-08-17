using JSON3

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "transformations", "FourWindingLoweringWitness.jl"))
using .FourWindingLoweringWitness

const OUTPUT = joinpath(@__DIR__, "generated", "four-winding-lowering-witness.json")
result = evaluate_four_winding_lowering()
result["all_checks_pass"] || error("four-winding lowering witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(OUTPUT)

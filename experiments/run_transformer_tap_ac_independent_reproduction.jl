using JSON3

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerTapDecisionCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerTapACDecision.jl"))
include(joinpath(
    @__DIR__, "transformations", "TransformerTapACIndependentReproduction.jl",
))
using .TransformerTapACDecision
using .TransformerTapACIndependentReproduction

const OUTPUT = joinpath(
    @__DIR__, "generated", "transformer-tap-ac-independent-certificate.json",
)
case = load_transformer_tap_ac_case()
certificate = independent_transformer_tap_certificate(case)
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, certificate, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

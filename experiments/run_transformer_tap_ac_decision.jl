using JSON3

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerTapDecisionCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerTapACDecision.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TransformerTapACDecision
using .TransformationContracts

const OUTPUT = joinpath(
    @__DIR__, "generated", "transformer-tap-ac-decision-certificate.json",
)
certificate = transformer_tap_ac_certificate()
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

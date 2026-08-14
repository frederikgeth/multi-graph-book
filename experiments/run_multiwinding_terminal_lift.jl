using JSON3

include(joinpath(@__DIR__, "transformations", "ConductorTerminalLift.jl"))
using .ConductorTerminalLift

const ROOT = normpath(joinpath(@__DIR__, ".."))
const OUTPUT = joinpath(@__DIR__, "generated", "multiwinding-terminal-lift-witness.json")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, evaluate_multiwinding_terminal_lift(ROOT), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

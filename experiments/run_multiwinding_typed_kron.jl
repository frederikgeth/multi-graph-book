using JSON3

include(joinpath(@__DIR__, "transformations", "MultiwindingTypedKronWitness.jl"))
using .MultiwindingTypedKronWitness

const ROOT = normpath(joinpath(@__DIR__, ".."))
const OUTPUT = joinpath(@__DIR__, "generated", "multiwinding-typed-kron-witness.json")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, evaluate_multiwinding_typed_kron(ROOT), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

using JSON3

include(joinpath(@__DIR__, "transformations", "BlockStructureBridgeWitness.jl"))
using .BlockStructureBridgeWitness

const OUTPUT = joinpath(@__DIR__, "generated", "block-structure-bridge-witness.json")
result = evaluate_block_structure_bridge()
result["all_checks_pass"] || error("block-structure bridge witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(OUTPUT)

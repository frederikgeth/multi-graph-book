using JSON3

include(joinpath(@__DIR__, "transformations", "NodalSourceRecoveryWitness.jl"))
using .NodalSourceRecoveryWitness

const OUTPUT = joinpath(@__DIR__, "generated", "nodal-source-recovery-witness.json")
result = nodal_source_recovery_witness()
result["all_checks_pass"] || error("nodal source recovery witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

using JSON3

include(joinpath(@__DIR__, "transformations", "NodalRecoveryGuardsWitness.jl"))
using .NodalRecoveryGuardsWitness

const OUTPUT = joinpath(@__DIR__, "generated", "nodal-recovery-guards-witness.json")
result = nodal_recovery_guards_witness()
result["all_checks_pass"] || error("guarded nodal source recovery witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

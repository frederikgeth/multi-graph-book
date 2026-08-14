using JSON3

include(joinpath(@__DIR__, "transformations", "NoisyMulticonductorRecoveryWitness.jl"))
using .NoisyMulticonductorRecoveryWitness

const OUTPUT = joinpath(@__DIR__, "generated", "noisy-multiconductor-recovery-witness.json")
result = noisy_multiconductor_recovery_witness()
result["all_checks_pass"] || error("noisy multiconductor recovery witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

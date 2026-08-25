using JSON3

include(joinpath(@__DIR__, "transformations", "CoupledCorridorLatticeWitness.jl"))
using .CoupledCorridorLatticeWitness

const OUTPUT = joinpath(@__DIR__, "generated", "coupled-corridor-lattice-witness.json")
result = evaluate_coupled_corridor_lattice()
result["all_checks_pass"] || error("coupled-corridor lattice witness failed")
mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(OUTPUT)

using JSON3

include(joinpath(@__DIR__, "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

root = normpath(joinpath(@__DIR__, ".."))
result = evaluate_grounding_impedance_sweep()
output = joinpath(root, "experiments", "generated", "grounding-impedance-sweep-witness.json")
open(output, "w") do io
    JSON3.write(io, result; allow_inf = false)
    write(io, '\n')
end
println(output)
if !result.all_checks_pass
    error("grounding impedance sweep witness failed")
end

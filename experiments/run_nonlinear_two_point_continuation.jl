using JSON3

include(joinpath(@__DIR__, "transformations", "ExplicitEarthKronWitness.jl"))
using .ExplicitEarthKronWitness

root = normpath(joinpath(@__DIR__, ".."))
result = evaluate_nonlinear_two_point_continuation()
output = joinpath(root, "experiments", "generated", "nonlinear-two-point-grounding-continuation.json")
open(output, "w") do io
    JSON3.write(io, result; allow_inf = false)
    write(io, '\n')
end
println(output)
if !result.all_checks_pass
    error("nonlinear two-point continuation failed")
end

using JSON3

include(joinpath(@__DIR__, "transformations", "ActiveRadiality.jl"))
using .ActiveRadiality

const OUTPUT = joinpath(@__DIR__, "generated", "active-radiality-witness.json")
result = active_radiality_witness()
result["schema_version"] = "0.1.0"
result["source"] = "experiments/transformations/ActiveRadiality.jl"
result["all_checks_pass"] = result["inventory_adjacency_radial"] &&
    !result["inventory_member_radial"] && result["active_member_radial"] &&
    result["active_adjacency_radial"] && result["hidden_inventory_parallel_cycle"] &&
    result["active_state_is_tree"]
result["all_checks_pass"] || error("active radiality witness failed")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

using BMOPFTools
using JSON3

include(joinpath(@__DIR__, "transformations", "MultigraphCycleSpace.jl"))
using .MultigraphCycleSpace

const OUTPUT = joinpath(@__DIR__, "generated", "five-bus-cycle-space-analysis.json")

result = five_bus_analysis()
net = Dict{String,Any}(
    "bus" => Dict(bus => Dict{String,Any}() for bus in result["vertices"]),
    "line" => Dict(edge.id => Dict{String,Any}(
        "bus_from" => edge.bus_from,
        "bus_to" => edge.bus_to,
    ) for edge in result["edges"]),
    "voltage_source" => Dict("source" => Dict("bus" => "i")),
)
connectivity = connectivity_analysis(net, Finding[])

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(
        io,
        analysis_dict(result; bmopf_extra_edges=connectivity["n_extra_edges"]),
        JSON3.AlignmentContext(; indent=UInt16(2)),
    )
    write(io, '\n')
end

println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))

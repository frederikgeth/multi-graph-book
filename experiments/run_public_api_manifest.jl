using JSON3
using GraphModelsForPowerNetworks

output = joinpath(@__DIR__, "generated", "public-api-manifest.json")
open(output, "w") do io
    JSON3.pretty(io, api_manifest())
    write(io, '\n')
end
println("wrote $output")

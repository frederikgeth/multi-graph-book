using JSON3

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TransformerWindingNormalization
using .TransformationContracts

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "transformer-winding-normalization-certificate.json")

network = JSON3.read(read(FIXTURE, String), Dict{String,Any})
winding = network["transformer"]["n_winding"]["x1"]["windings"][3]
terminals = String.(winding["terminal_map"])
source = WindingFactor(
    "x1/winding/3",
    "x1",
    3,
    winding["bus"],
    terminals,
    winding["configuration"],
    delta_incidence(terminals; roll=Int(winding["delta_roll"])),
    fill(Float64(winding["i_max"]), length(terminals));
    coil_labels=terminals,
    attributes=Dict(
        "v_nom_V" => winding["v_nom"],
        "r_winding_ohm" => winding["r_winding"],
        "delta_roll" => winding["delta_roll"],
    ),
)

result = normalize_winding_terminals(
    source, ["c", "a", "b"]; certificate_id="TR-XFMR-001",
)
result isa WindingNormalizationResult || error("expected winding normalization to apply")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(result.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

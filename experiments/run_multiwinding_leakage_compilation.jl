using JSON3

include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .MultiwindingLeakageCompilation
using .TransformationContracts

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "multiwinding-leakage-compilation-certificate.json")

network = JSON3.read(read(FIXTURE, String), Dict{String,Any})
transformer = network["transformer"]["n_winding"]["x1"]
windings = transformer["windings"]
pairwise = Dict{Tuple{Int,Int},Float64}()
for (key, value) in transformer["x_sc"]
    i, j = parse.(Int, split(key, "_"))
    pairwise[(i, j)] = Float64(value)
end
data = MultiwindingLeakageData(
    "x1",
    ["x1/winding/$k" for k in eachindex(windings)],
    [winding["v_nom"] for winding in windings],
    [winding["r_winding"] for winding in windings],
    [winding["i_max"] for winding in windings],
    pairwise,
    short_circuit_reference_winding=1,
)
result = compile_pairwise_leakage(data)
result isa MultiwindingLeakageResult || error("multiwinding leakage compilation was rejected: $(result.failed_guards)")
result.certificate["evidence"]["reference_choice_invariance"] =
    reference_invariance_report(data)
result.certificate["provenance"]["source_short_circuit_reference_convention"] =
    "BMOPFTools n_winding x_sc values use winding 1 as their impedance reference"

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(result.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

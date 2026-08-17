using JSON3
using LinearAlgebra

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

# Keep the pedagogical negative-arm guard in the generated certificate rather
# than leaving it only in the unit-test source.  The pairwise tests are all
# positive, while one star coordinate is negative and the invariant reactance
# matrix remains positive definite.
negative_data = MultiwindingLeakageData(
    "negative-star-arm",
    ["w1", "w2", "w3"],
    [1.0, 1.0, 1.0],
    [0.1, 0.1, 0.1],
    [100.0, 100.0, 100.0],
    Dict((1, 2) => 1.0, (1, 3) => 1.0, (2, 3) => 3.0),
)
negative_result = compile_pairwise_leakage(negative_data)
negative_result isa MultiwindingLeakageResult ||
    error("negative star-arm witness was rejected: $(negative_result.failed_guards)")
negative_star = negative_result.certificate["evidence"]["three_winding_special_case"]
result.certificate["evidence"]["negative_star_arm_witness"] = Dict(
    "source_pairwise_reactance_ohm" => Dict("12" => 1.0, "13" => 1.0, "23" => 3.0),
    "star_arm_impedances_ohm" => negative_star["star_arm_impedances_ohm"],
    "reactance_eigenvalues" => collect(eigvals(Symmetric(imag.(negative_result.reference_impedance)))),
    "all_pairwise_reactances_positive" => true,
    "negative_arm_is_accepted" => true,
    "guard" => "minimum eigenvalue of imag(Z_B) is nonnegative",
    "interpretation" => "a negative star coordinate is a valid reference-coordinate representation; componentwise arm positivity is not the physical guard",
)

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(result.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "multiwinding-terminal-assembly-certificate.json")

network = JSON3.read(read(FIXTURE, String), Dict{String,Any})
transformer = network["transformer"]["n_winding"]["x1"]
source_windings = transformer["windings"]
pairwise = Dict{Tuple{Int,Int},Float64}()
for (key, value) in transformer["x_sc"]
    i, j = parse.(Int, split(key, "_"))
    pairwise[(i, j)] = Float64(value)
end

leakage_data = MultiwindingLeakageData(
    "x1",
    ["x1/winding/$k" for k in eachindex(source_windings)],
    [winding["v_nom"] for winding in source_windings],
    [winding["r_winding"] for winding in source_windings],
    [winding["i_max"] for winding in source_windings],
    pairwise;
    short_circuit_reference_winding=1,
)
leakage = compile_pairwise_leakage(leakage_data)
leakage isa MultiwindingLeakageResult || error("leakage compilation was rejected")

winding_factors = WindingFactor[]
for (position, winding) in enumerate(source_windings)
    terminals = String.(winding["terminal_map"])
    connection = String(winding["configuration"])
    if connection == "WYE"
        coil_labels = [label for label in terminals if label != "n"]
        incidence = wye_incidence(terminals)
    elseif connection == "DELTA"
        coil_labels = copy(terminals)
        incidence = delta_incidence(terminals; roll=Int(winding["delta_roll"]))
    else
        error("unsupported fixture connection $connection")
    end
    push!(winding_factors, WindingFactor(
        "x1/winding/$position", "x1", position, winding["bus"], terminals,
        connection, incidence, fill(Float64(winding["i_max"]), length(coil_labels));
        coil_labels=coil_labels,
    ))
end

result = assemble_terminal_leakage(leakage, winding_factors)
result isa MultiwindingTerminalAssemblyResult ||
    error("terminal assembly was rejected: $(result.failed_guards)")

terminal_voltage = ComplexF64[complex(cos(0.37k), sin(0.23k)) for k in 1:size(result.terminal_admittance, 1)]
coil_voltage = result.terminal_to_coil * terminal_voltage
coil_current = result.coil_admittance * coil_voltage
terminal_current = result.terminal_admittance * terminal_voltage
reference_2 = assemble_terminal_leakage(
    compile_pairwise_leakage(leakage_data; reference_winding=2),
    winding_factors,
)
result.certificate["evidence"]["complex_power_balance_residual_VA"] =
    abs(dot(terminal_voltage, terminal_current) - dot(coil_voltage, coil_current))
result.certificate["evidence"]["terminal_current_recovery_residual_A"] =
    maximum(abs.(terminal_current - result.terminal_to_coil' * coil_current))
result.certificate["evidence"]["reference_choice_terminal_admittance_difference_S"] =
    maximum(abs.(result.terminal_admittance - reference_2.terminal_admittance))

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, result.certificate, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))


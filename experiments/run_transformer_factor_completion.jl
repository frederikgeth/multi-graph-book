using BMOPFTools
using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformerFactorCompletion
using .TransformationContracts

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const CONTRACT = joinpath(ROOT, "data", "transformer-contracts", "x1-fixed-linear-v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "transformer-factor-completion-certificate.json")

network = JSON3.read(read(FIXTURE, String), Dict{String,Any})
raw_contract = JSON3.read(read(CONTRACT, String), Dict{String,Any})
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
    incidence = connection == "WYE" ?
        wye_incidence(terminals) :
        delta_incidence(terminals; roll=Int(winding["delta_roll"]))
    coil_labels = connection == "WYE" ? filter(!=("n"), terminals) : copy(terminals)
    push!(winding_factors, WindingFactor(
        "x1/winding/$position", "x1", position, winding["bus"], terminals,
        connection, incidence, fill(Float64(winding["i_max"]), length(coil_labels));
        coil_labels=coil_labels,
    ))
end

terminal_leakage = assemble_terminal_leakage(leakage, winding_factors)
terminal_leakage isa MultiwindingTerminalAssemblyResult || error("terminal leakage assembly was rejected")
completion_data = completion_data_from_dict(raw_contract)
result = assemble_complete_transformer(terminal_leakage, completion_data)
result isa TransformerCompletionResult ||
    error("transformer completion was rejected: $(result.failed_guards)")

terminal_voltage = ComplexF64[
    complex(cos(0.29k), sin(0.17k)) for k in axes(result.terminal_admittance, 1)
]
leakage_voltage = result.leakage_voltage_map * terminal_voltage
leakage_current = result.leakage_current_map * terminal_voltage
excitation_voltage = result.excitation_voltage_map * terminal_voltage
excitation_current = result.excitation_current_map * terminal_voltage
ground_current = result.ground_current_map * terminal_voltage
terminal_current = result.terminal_admittance * terminal_voltage
recovered_terminal_current = result.leakage_voltage_map' * leakage_current +
                             result.excitation_voltage_map' * excitation_current +
                             ground_current
result.certificate["evidence"]["component_current_recovery_residual_A"] =
    maximum(abs.(terminal_current - recovered_terminal_current))
result.certificate["evidence"]["complex_power_balance_residual_VA"] = abs(
    dot(terminal_voltage, terminal_current) -
    dot(leakage_voltage, leakage_current) -
    dot(excitation_voltage, excitation_current) -
    dot(terminal_voltage, ground_current)
)

# BMOPFTools independently constructs the n-winding primitive. It does not
# currently stamp n-winding neutral grounding, so compare after removing that
# separately retained contribution.
independent_transformer = deepcopy(transformer)
y0 = completion_data.excitation_shunt.admittance[1, 1]
independent_transformer["g_no_load"] = real(y0)
independent_transformer["b_no_load"] = imag(y0)
_, independent_yprim = BMOPFTools.nwinding_yprim(independent_transformer)
result.certificate["evidence"]["bmopftools_yprim_difference_excluding_internal_ground_S"] =
    maximum(abs.(result.terminal_admittance - result.ground_current_map - independent_yprim))
result.certificate["provenance"]["independent_implementation"] =
    "BMOPFTools.nwinding_yprim on the same leakage and excitation data"

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(result.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

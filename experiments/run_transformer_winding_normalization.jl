using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
using .CoordinateActions
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
    terminal_current_limit=Float64[280.0, 260.0, 240.0],
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

action = coordinate_action(source.terminals, result.target.terminals)
u_source = ComplexF64[1.0 + 0.1im, -0.4 - 0.8im, -0.6 + 0.7im]
i_coil = ComplexF64[0.8 - 0.2im, -0.3 + 0.5im, 0.4 + 0.1im]
u_target = pushforward_vector(action, u_source)
i_source = transpose(source.terminal_to_coil) * i_coil
i_target = action.permutation * i_source
coil_voltage_source = source.terminal_to_coil * u_source
coil_voltage_target = result.target.terminal_to_coil * u_target
power_source = dot(u_source, i_source)
power_target = dot(u_target, i_target)
power_coil = dot(coil_voltage_source, i_coil)
result.certificate["evidence"]["checks"] = Dict(
    "terminal_voltage_recovery_exact" =>
        norm(coil_voltage_source - coil_voltage_target) <= 1.0e-12,
    "terminal_current_dual_map_exact" =>
        norm(i_target - action.permutation * i_source) <= 1.0e-12,
    "coil_voltage_identity_exact" =>
        norm(coil_voltage_source - coil_voltage_target) <= 1.0e-12,
    "complex_power_source_target_invariant" =>
        abs(power_source - power_target) <= 1.0e-12,
    "complex_power_terminal_coil_invariant" =>
        abs(power_source - power_coil) <= 1.0e-12,
    "coil_current_limits_unchanged" =>
        source.coil_current_limit == result.target.coil_current_limit,
    "terminal_current_limits_follow_dual_map" =>
        result.target.terminal_current_limit ≈ action.permutation * source.terminal_current_limit,
)
result.certificate["evidence"]["witness"] = Dict(
    "source_terminal_voltage" => u_source,
    "target_terminal_voltage" => u_target,
    "source_terminal_current" => i_source,
    "target_terminal_current" => i_target,
    "coil_current" => i_coil,
    "complex_power_source_VA" => power_source,
    "complex_power_target_VA" => power_target,
    "complex_power_coil_VA" => power_coil,
)

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(result.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

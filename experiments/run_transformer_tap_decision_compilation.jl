using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "CoordinateActions.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerWindingNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingLeakageCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "MultiwindingTerminalAssembly.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerFactorCompletion.jl"))
include(joinpath(@__DIR__, "transformations", "TransformerTapDecisionCompilation.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformerFactorCompletion
using .TransformerTapDecisionCompilation
using .TransformationContracts

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const CONTRACT = joinpath(ROOT, "data", "transformer-contracts", "x1-discrete-tap-v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "transformer-tap-decision-certificate.json")

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
    "x1", ["x1/winding/$k" for k in eachindex(source_windings)],
    [winding["v_nom"] for winding in source_windings],
    [winding["r_winding"] for winding in source_windings],
    [winding["i_max"] for winding in source_windings], pairwise,
)
leakage = compile_pairwise_leakage(leakage_data)
leakage isa MultiwindingLeakageResult || error("leakage compilation was rejected")

winding_factors = WindingFactor[]
for (position, winding) in enumerate(source_windings)
    terminals = String.(winding["terminal_map"])
    connection = String(winding["configuration"])
    incidence = connection == "WYE" ? wye_incidence(terminals) :
        delta_incidence(terminals; roll=Int(winding["delta_roll"]))
    coil_labels = connection == "WYE" ? filter(!=("n"), terminals) : copy(terminals)
    push!(winding_factors, WindingFactor(
        "x1/winding/$position", "x1", position, winding["bus"], terminals,
        connection, incidence, fill(Float64(winding["i_max"]), length(coil_labels));
        coil_labels=coil_labels,
    ))
end

terminal_leakage = assemble_terminal_leakage(leakage, winding_factors)
terminal_leakage isa MultiwindingTerminalAssemblyResult ||
    error("terminal leakage assembly was rejected")
completion_data = completion_data_from_dict(raw_contract)
factor = compile_parameterized_transformer(terminal_leakage, completion_data)
factor isa ParameterizedTransformerFactor ||
    error("tap-factor compilation was rejected: $(factor.failed_guards)")
domain = only(factor.decisions)

function fixed_source_snapshot(data, decision_value)
    transfers = WindingTransfer[]
    for transfer in data.winding_transfers
        coefficient = transfer.control_mode == "fixed" ? transfer.coefficient :
            transfer.coefficient .* decision_value
        push!(transfers, WindingTransfer(
            transfer.id, transfer.transformer_id, transfer.winding_id,
            transfer.winding_position, transfer.coil_labels, "fixed", coefficient;
            terminal_labels=transfer.terminal_labels,
            attributes=transfer.attributes,
        ))
    end
    TransformerCompletionData(
        "$(data.id)/direct-source/$decision_value", data.transformer_id,
        "direct_source_snapshot", data.voltage_transfer_convention, transfers;
        excitation_shunt=data.excitation_shunt,
        internal_groundings=data.internal_groundings,
        metadata=data.metadata,
    )
end

sequence = ComplexF64[1.0, cis(-2pi / 3), cis(2pi / 3)]
terminal_voltage = vcat(
    7199.557856794634 .* sequence, 0.0 + 0.0im,
    (0.97 * 277.1281292110204) .* sequence, 0.0 + 0.0im,
    (4160.0 / sqrt(3)) .* cis(pi / 6) .* sequence,
)
limit = terminal_leakage.coil_current_limit[4]
results = Dict{String,Any}()
max_pointwise_difference = Ref(0.0)
max_power_residual = Ref(0.0)
for tap in domain.positions
    evaluated = evaluate_parameterized_transformer(factor, Dict(domain.decision_id => tap))
    evaluated isa TransformerCompletionResult || error("valid tap $tap was rejected")
    direct = assemble_complete_transformer(
        terminal_leakage,
        fixed_source_snapshot(completion_data, tap),
    )
    direct isa TransformerCompletionResult || error("direct snapshot $tap was rejected")
    difference = maximum(abs.(evaluated.terminal_admittance - direct.terminal_admittance))
    max_pointwise_difference[] = max(max_pointwise_difference[], difference)
    winding_current = evaluated.winding_leakage_current_map * terminal_voltage
    stress = maximum(abs.(winding_current[4:6]))
    leakage_voltage = evaluated.leakage_voltage_map * terminal_voltage
    leakage_current = evaluated.leakage_current_map * terminal_voltage
    excitation_voltage = evaluated.excitation_voltage_map * terminal_voltage
    excitation_current = evaluated.excitation_current_map * terminal_voltage
    ground_current = evaluated.ground_current_map * terminal_voltage
    terminal_current = evaluated.terminal_admittance * terminal_voltage
    power_residual = abs(
        dot(terminal_voltage, terminal_current) -
        dot(leakage_voltage, leakage_current) -
        dot(excitation_voltage, excitation_current) -
        dot(terminal_voltage, ground_current)
    )
    max_power_residual[] = max(max_power_residual[], power_residual)
    results[string(tap)] = Dict(
        "maximum_winding_2_leakage_current_A" => stress,
        "current_limit_A" => limit,
        "feasible" => stress <= limit,
        "direct_source_terminal_admittance_difference_S" => difference,
        "complex_power_balance_residual_VA" => power_residual,
    )
end

feasible_taps = [tap for tap in domain.positions if results[string(tap)]["feasible"]]
optimal_tap = feasible_taps[argmin(
    results[string(tap)]["maximum_winding_2_leakage_current_A"] for tap in feasible_taps
)]
optimal_tap == 1.05 || error("unexpected tap optimum $optimal_tap")
frozen_stress = results[string(domain.start_value)]["maximum_winding_2_leakage_current_A"]
optimal_stress = results[string(optimal_tap)]["maximum_winding_2_leakage_current_A"]

factor.certificate["evidence"]["decision_witness"] = Dict(
    "description" => "minimize maximum winding-2 leakage current at fixed boundary voltage subject to the original 2200 A winding limit",
    "winding_2_voltage_scale" => 0.97,
    "tap_position_results" => results,
    "source_feasible_taps" => feasible_taps,
    "parameterized_target_feasible_taps" => feasible_taps,
    "source_optimal_tap" => optimal_tap,
    "parameterized_target_optimal_tap" => optimal_tap,
    "frozen_start_tap" => domain.start_value,
    "frozen_start_objective_A" => frozen_stress,
    "optimal_objective_A" => optimal_stress,
    "frozen_start_objective_gap_A" => frozen_stress - optimal_stress,
)
factor.certificate["evidence"]["maximum_pointwise_source_target_difference_S"] =
    max_pointwise_difference[]
factor.certificate["evidence"]["maximum_complex_power_balance_residual_VA"] =
    max_power_residual[]

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(factor.certificate), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))

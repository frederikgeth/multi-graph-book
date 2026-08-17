using JSON3
using BMOPFTools
using JuMP

include(joinpath(@__DIR__, "transformations", "SolverDiagnosticsCrosswalk.jl"))
using .SolverDiagnosticsCrosswalk
include(joinpath(@__DIR__, "running_network.jl"))

diffopt_net = parse_bmopf("""
{"bus":{
    "sourcebus":{"terminal_names":["1","n"],
                 "perfectly_grounded_terminals":["n"]},
    "bus1":{"terminal_names":["1","n"],
            "perfectly_grounded_terminals":["n"]}},
 "voltage_source":{"vs":{"bus":"sourcebus","terminal_map":["1"],
     "v_magnitude":[1000.0],"v_angle":[0.0]}},
 "linecode":{"lc":{"R_series_1_1":0.5}},
 "line":{"l1":{"bus_from":"sourcebus","bus_to":"bus1",
     "terminal_map_from":["1"],"terminal_map_to":["1"],
     "linecode":"lc","length":1.0}}}
"""; from_string=true)

generated = joinpath(@__DIR__, "generated")
result = evaluate_crosswalk(generated)
callback_probe = evaluate_solver_callback_probe(running_network())
diffopt_probe = evaluate_diffopt_sensitivity(diffopt_net)
parallel_source, parallel_reduced = parallel_diffopt_networks()
parallel_comparison = evaluate_diffopt_parallel_comparison(parallel_source, parallel_reduced)
output = joinpath(generated, "solver-diagnostics-crosswalk.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "model_scope" => result.model_scope,
        "source_witnesses" => result.source_witnesses,
        "node_order" => result.node_order,
        "diagnostic_layers" => result.diagnostic_layers,
        "solver_boundary" => result.solver_boundary,
        "solver_callback_probe" => callback_probe,
        "diffopt_sensitivity_probe" => diffopt_probe,
        "diffopt_parallel_comparison" => parallel_comparison,
        "comparisons" => result.comparisons,
        "checks" => result.checks,
        "interpretation" => result.interpretation,
    ))
    write(io, '\n')
end
println("wrote $output")

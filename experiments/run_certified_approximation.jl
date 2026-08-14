using JSON3

include(joinpath(@__DIR__, "transformations", "CertifiedApproximation.jl"))
using .CertifiedApproximation

result = evaluate_certified_approximation()
artifact = Dict(
    "witness_id" => result.witness_id,
    "claim_id" => result.witness_id,
    "source_fixture" => "kron_ward_scenario_fixture_v0.1.0",
    "base_scenario" => result.base_scenario,
    "bound_method" => result.bound_method,
    "chain" => [
        "parameter/model residual",
        "recovered-state error bound",
        "constraint error bound",
        "approximate constraint margin",
        "decision classification",
    ],
    "rows" => result.rows,
    "classifications" => result.classifications,
    "checks" => result.checks,
    "interpretation" => "The Ward target is classified using a declared normwise error bound. The bound is exact for the one-state linear fixture and is not a general nonlinear or parameter-uncertainty theorem.",
)
output = joinpath(@__DIR__, "generated", "certified-approximation-witness.json")
open(output, "w") do io
    JSON3.pretty(io, artifact)
    write(io, '\n')
end
println("wrote $output")

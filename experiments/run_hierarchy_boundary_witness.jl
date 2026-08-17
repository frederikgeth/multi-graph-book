using JSON3

include(joinpath(@__DIR__, "transformations", "HierarchyBoundaryWitness.jl"))
using .HierarchyBoundaryWitness

result = evaluate_hierarchy_boundary()
output = joinpath(@__DIR__, "generated", "hierarchy-boundary-witness.json")
open(output, "w") do io
    JSON3.pretty(io, Dict(
        "witness_id" => result.witness_id,
        "evidence_type" => "hierarchy_boundary_refinement_witness",
        "model_scope" => result.model_scope,
        "source_fixture" => result.source_fixture,
        "containers" => result.containers,
        "source_boundary" => result.source_boundary,
        "target_boundary" => result.target_boundary,
        "refinement" => result.refinement,
        "gluing" => result.gluing,
        "state_cases" => result.state_cases,
        "checks" => result.checks,
        "errors" => result.errors,
        "interpretation" => result.interpretation,
        "source" => "experiments/transformations/HierarchyBoundaryWitness.jl",
    ))
    write(io, '\n')
end
println("wrote $output")

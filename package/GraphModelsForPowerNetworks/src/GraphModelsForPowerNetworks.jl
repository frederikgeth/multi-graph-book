module GraphModelsForPowerNetworks

"""Dependency-light public core for graph models of power networks.

Solver-backed examples and literature-specific adapters remain under
`experiments/`; this package contains the representation, typed reduction,
state-space, and certificate-contract layers that are intended to be stable.
"""

include(joinpath(@__DIR__, "MultigraphCycleSpace.jl"))
include(joinpath(@__DIR__, "TypedKronReduction.jl"))
include(joinpath(@__DIR__, "TypedStateSpace.jl"))
include(joinpath(@__DIR__, "TransformationContracts.jl"))

using .MultigraphCycleSpace
using .TypedKronReduction
using .TypedStateSpace
using .TransformationContracts

export IdentifiedEdge,
       canonical_pair,
       connected_components,
       cycle_rank,
       incidence_matrix,
       simple_projection,
       kron_reduce,
       transform_blocks,
       recovered_current,
       UnitSpec,
       UnitSystem,
       VariableSpec,
       StateDomain,
       BoundarySpec,
       StateSpaceSpec,
       convert_value,
       to_per_unit,
       from_per_unit,
       state_variables,
       boundary_variables,
       validate_state_space,
       state_space_dict,
       running_state_space,
       attach_typed_interfaces,
       validate_certificate,
       compose_certificates,
       api_manifest

"Return the versioned public API boundary and its intentionally excluded tiers."
function api_manifest()
    Dict(
        "package" => "GraphModelsForPowerNetworks",
        "version" => "0.1.0",
        "stable_exports" => [
            "IdentifiedEdge", "canonical_pair", "connected_components",
            "cycle_rank", "incidence_matrix", "simple_projection",
            "kron_reduce", "transform_blocks", "recovered_current",
            "UnitSpec", "UnitSystem", "VariableSpec", "StateDomain",
            "BoundarySpec", "StateSpaceSpec", "convert_value", "to_per_unit",
            "from_per_unit", "state_variables", "boundary_variables",
            "validate_state_space", "state_space_dict", "running_state_space",
            "attach_typed_interfaces", "validate_certificate", "compose_certificates",
            "api_manifest",
        ],
        "stable_layers" => [
            "multigraph primitives", "typed linear Kron reduction", "typed state-space and units",
            "certificate contracts",
        ],
        "experimental_layers" => [
            "solver-backed AC decision cases", "generated figures", "benchmark witnesses",
            "literature-specific adapters", "BMOPFTools integration adapters",
        ],
        "boundary_rule" => "Only dependency-light, representation-level functions with declared inputs/outputs are exported; generated evidence remains runnable but is not a package API promise.",
        "source_modules" => [
            "src/MultigraphCycleSpace.jl",
            "src/TypedKronReduction.jl",
            "src/TypedStateSpace.jl",
            "src/TransformationContracts.jl",
        ],
    )
end

end

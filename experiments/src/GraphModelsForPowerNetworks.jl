module GraphModelsForPowerNetworks

"""Compatibility facade for the standalone dependency-light package core.

The implementation modules are canonical under `package/`; this facade keeps
the existing experiments project importable without making the experiment
project itself the release boundary.
"""

const PACKAGE_SRC = joinpath(@__DIR__, "..", "..", "package", "GraphModelsForPowerNetworks", "src")
include(joinpath(PACKAGE_SRC, "MultigraphCycleSpace.jl"))
include(joinpath(PACKAGE_SRC, "TypedKronReduction.jl"))
include(joinpath(PACKAGE_SRC, "TypedStateSpace.jl"))
include(joinpath(PACKAGE_SRC, "TransformationContracts.jl"))

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
            "package/GraphModelsForPowerNetworks/src/MultigraphCycleSpace.jl",
            "package/GraphModelsForPowerNetworks/src/TypedKronReduction.jl",
            "package/GraphModelsForPowerNetworks/src/TypedStateSpace.jl",
            "package/GraphModelsForPowerNetworks/src/TransformationContracts.jl",
        ],
    )
end

end
